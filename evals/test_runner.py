import unittest
import importlib
import io
import json
import tempfile
import subprocess
import sys
from contextlib import redirect_stdout
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RunnerCliTests(unittest.TestCase):
    def test_help_runs_when_invoked_as_a_script(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "evals" / "run_eval.py"), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--mode", result.stdout)
        self.assertIn("--provider", result.stdout)
        self.assertIn("--gemini-rpm", result.stdout)


class RunnerPersistenceTests(unittest.TestCase):
    def test_persists_each_attempt_once_and_marks_only_the_final_case_row(self):
        module = importlib.import_module("evals.run_eval")
        persist_case_rows = getattr(module, "persist_case_rows", None)
        self.assertTrue(callable(persist_case_rows), "persist_case_rows is not implemented yet")
        rows = [
            {"case_id": "case-1", "attempt": 1, "model_done": True, "case_done": False, "http_status": 429},
            {"case_id": "case-1", "attempt": 1, "model_done": True, "case_done": True, "http_status": 200},
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run.jsonl"
            persist_case_rows(output, rows, {"prompt_version": "v5"})
            saved = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(saved), 2)
        self.assertEqual([row["attempt"] for row in saved], [1, 1])
        self.assertEqual([row["case_done"] for row in saved], [False, True])
        self.assertTrue(all(row["prompt_version"] == "v5" for row in saved))

    def test_timeout_attempt_is_counted_even_without_http_status(self):
        from evals.run_eval import persist_case_rows

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run.jsonl"
            persist_case_rows(
                output,
                [{"case_id": "case-1", "model_requested": "model-a:free", "http_status": None}],
                {},
            )
            saved = json.loads(output.read_text(encoding="utf-8"))
        self.assertTrue(saved["api_call_made"])

    def test_runner_imports_as_a_package_for_unittest(self):
        result = subprocess.run(
            [sys.executable, "-c", "import evals.run_eval"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_resume_rejects_a_different_run_fingerprint(self):
        module = importlib.import_module("evals.run_eval")
        load_resume_state = getattr(module, "load_resume_state", None)
        self.assertTrue(callable(load_resume_state), "load_resume_state is not implemented yet")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run.jsonl"
            output.write_text(json.dumps({"run_fingerprint": "old"}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "different run fingerprint"):
                load_resume_state(output, "new", "compare")

    def test_resume_reuses_only_matching_fingerprinted_rows(self):
        module = importlib.import_module("evals.run_eval")
        load_resume_state = getattr(module, "load_resume_state", None)
        self.assertTrue(callable(load_resume_state), "load_resume_state is not implemented yet")
        rows = [
            {"run_fingerprint": "same", "case_id": "case-1", "model_requested": "model-a", "model_done": True, "mode": "fallback"},
            {"run_fingerprint": "same", "case_id": "case-1", "model_requested": "model-b", "mode": "fallback", "case_done": True, "status": "answered"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "run.jsonl"
            output.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            done, completed = load_resume_state(output, "same", "fallback")
        self.assertEqual(done["case-1"], {"model-a"})
        self.assertEqual(completed, {"case-1"})


class RunnerPresenceTests(unittest.TestCase):
    def test_reusable_runner_exists(self):
        self.assertTrue((ROOT / "evals" / "run_eval.py").is_file(), "evals/run_eval.py is not implemented yet")


class RunnerQuotaTests(unittest.TestCase):
    def test_uses_live_free_quota_to_cap_an_invocation(self):
        from evals.run_eval import effective_request_cap, parse_free_model_quota

        quota = parse_free_model_quota({
            "data": {
                "free_model_daily_requests": {"used": 47, "limit": 50, "remaining": 3},
                "usage": 123.45,
                "label": "do not expose",
            }
        })
        self.assertEqual(quota, {"used": 47, "limit": 50, "remaining": 3})
        self.assertEqual(effective_request_cap(45, quota["remaining"]), 3)
        self.assertEqual(effective_request_cap(2, quota["remaining"]), 2)
        self.assertEqual(effective_request_cap(45, 0), 0)

    def test_rejects_missing_or_invalid_live_free_quota(self):
        from evals.run_eval import parse_free_model_quota

        with self.assertRaisesRegex(ValueError, "did not return"):
            parse_free_model_quota({"data": {}})
        with self.assertRaisesRegex(ValueError, "invalid"):
            parse_free_model_quota({"data": {"free_model_daily_requests": {"used": -1, "limit": 50, "remaining": 3}}})

    def test_default_comparison_models_have_recent_answer_evidence(self):
        from evals.run_eval import DEFAULT_MODELS

        self.assertEqual(
            DEFAULT_MODELS,
            (
                "nvidia/nemotron-3-ultra-550b-a55b:free",
                "nvidia/nemotron-3.5-lightning:free",
                "nvidia/nemotron-3.5-super-vl:free",
            ),
        )


class GeminiProviderTests(unittest.TestCase):
    def test_reads_only_named_gemini_key_from_dotenv(self):
        from evals.run_eval import load_provider_api_key

        with tempfile.TemporaryDirectory() as directory:
            dotenv = Path(directory) / ".env"
            dotenv.write_text("HOST=ssh.example\nGEMINI_API='gemini-secret'\nPASSWORD=ssh-secret\n", encoding="utf-8")
            self.assertEqual(
                load_provider_api_key("gemini", env={}, dotenv_path=dotenv),
                "gemini-secret",
            )

    def test_normalizes_gemini_generate_content_response(self):
        from evals.run_eval import normalize_gemini_response

        response = normalize_gemini_response(
            {
                "modelVersion": "gemini-3.1-flash-lite",
                "candidates": [{
                    "content": {"parts": [{"text": "Ответ о товаре"}]},
                    "finishReason": "STOP",
                }],
                "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 8},
            },
            http_status=200,
        )
        self.assertEqual(response["data"]["choices"][0]["message"]["content"], "Ответ о товаре")
        self.assertEqual(response["data"]["choices"][0]["finish_reason"], "stop")
        self.assertEqual(response["data"]["model"], "gemini-3.1-flash-lite")
        self.assertEqual(response["data"]["usage"]["prompt_tokens"], 12)

    def test_gemini_request_uses_api_key_header_and_generate_content_payload(self):
        from evals.run_eval import gemini_request

        class FakeResponse:
            status = 200
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            @staticmethod
            def read():
                return json.dumps({
                    "modelVersion": "gemini-3.1-flash-lite",
                    "candidates": [{"content": {"parts": [{"text": "ok"}]}, "finishReason": "STOP"}],
                }).encode()

        with patch("evals.run_eval.urllib.request.urlopen", return_value=FakeResponse()) as urlopen:
            response = gemini_request(
                "test-secret",
                "gemini-3.1-flash-lite",
                [{"role": "system", "content": "system"}, {"role": "user", "content": "question"}],
                128,
            )
        request = urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(request.get_header("X-goog-api-key"), "test-secret")
        self.assertTrue(request.full_url.endswith("/models/gemini-3.1-flash-lite:generateContent"))
        self.assertEqual(body["systemInstruction"]["parts"][0]["text"], "system")
        self.assertEqual(body["contents"][0]["parts"][0]["text"], "question")
        self.assertEqual(response["data"]["choices"][0]["message"]["content"], "ok")

    def test_gemini_preflight_requires_selected_model_to_support_generate_content(self):
        from evals.run_eval import gemini_preflight

        with patch("evals.run_eval.gemini_catalog_models", return_value=[{
            "name": "models/gemini-3.1-flash-lite",
            "supportedGenerationMethods": ["generateContent"],
        }]):
            result = gemini_preflight("test-secret", "gemini-3.1-flash-lite")
        self.assertEqual(result["models"], ["gemini-3.1-flash-lite"])
        self.assertEqual(result["api_key"], "test-secret")

    def test_auto_output_path_keeps_each_provider_run_separate(self):
        from evals.run_eval import provider_output_path

        base = Path("evals/runs/compare-v6-auto.jsonl")
        self.assertEqual(
            provider_output_path(base, "gemini", automatic=True),
            Path("evals/runs/compare-v6-auto-gemini.jsonl"),
        )
        self.assertEqual(
            provider_output_path(base, "gemini", automatic=False),
            base,
        )

    def test_provider_failure_requires_all_models_to_fail_for_that_case(self):
        from evals.run_eval import provider_run_unavailable

        self.assertTrue(provider_run_unavailable([
            {"status": "provider_error", "http_status": 503},
            {"status": "provider_error", "http_status": None},
        ]))
        self.assertFalse(provider_run_unavailable([
            {"status": "answered", "http_status": 200},
            {"status": "provider_error", "http_status": 503},
        ]))

    def test_reads_retry_delay_from_gemini_error_details(self):
        from evals.run_eval import gemini_retry_after

        self.assertEqual(
            gemini_retry_after({}, {
                "error": {
                    "details": [{
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "7s",
                    }]
                }
            }),
            7,
        )

    def test_classifies_gemini_daily_quota_without_retrying_it(self):
        from evals.run_eval import is_daily_quota_exhausted

        self.assertTrue(is_daily_quota_exhausted({
            "http_status": 429,
            "data": {"error": {
                "status": "RESOURCE_EXHAUSTED",
                "message": "Request quota exceeded for requests_per_day on this model.",
            }},
        }))

    def test_gemini_per_minute_429_uses_retry_delay_but_daily_quota_does_not(self):
        from evals.run_eval import is_retryable_response

        rate_limit = {
            "http_status": 429,
            "data": {"error": {"status": "RESOURCE_EXHAUSTED", "message": "per minute request limit"}},
            "retry_after": 45,
        }
        self.assertTrue(is_retryable_response(rate_limit, "provider_error", max_retry_delay=60))
        daily_limit = {
            "http_status": 429,
            "data": {"error": {"status": "RESOURCE_EXHAUSTED", "message": "requests_per_day exceeded"}},
            "retry_after": 45,
        }
        self.assertFalse(is_retryable_response(daily_limit, "provider_error", max_retry_delay=60))

    def test_gemini_rate_limiter_keeps_requests_below_configured_rpm(self):
        from evals.run_eval import RateLimiter

        now = [0.0]
        sleeps = []

        def fake_sleep(delay):
            sleeps.append(delay)
            now[0] += delay

        limiter = RateLimiter(10, monotonic=lambda: now[0], sleep=fake_sleep)
        limiter.wait()
        now[0] += 0.2
        limiter.wait()
        self.assertAlmostEqual(sleeps[0], 5.8)

    def test_auto_provider_prefers_openrouter_then_falls_back_to_gemini(self):
        from evals.run_eval import resolve_provider

        calls = []
        provider = resolve_provider(
            "auto",
            openrouter_probe=lambda: calls.append("openrouter") or False,
            gemini_probe=lambda: calls.append("gemini") or True,
            timeout_seconds=120,
            poll_interval=15,
        )
        self.assertEqual(provider, "gemini")
        self.assertEqual(calls, ["openrouter", "gemini"])

    def test_auto_provider_pauses_after_both_providers_stay_down_for_two_minutes(self):
        from evals.run_eval import BothProvidersUnavailable, resolve_provider

        now = [0.0]

        def fake_sleep(delay):
            now[0] += delay

        with self.assertRaises(BothProvidersUnavailable):
            resolve_provider(
                "auto",
                openrouter_probe=lambda: False,
                gemini_probe=lambda: False,
                timeout_seconds=120,
                poll_interval=30,
                monotonic=lambda: now[0],
                sleep=fake_sleep,
            )
        self.assertEqual(now[0], 120)

    def test_cli_auto_preflight_falls_back_to_gemini_when_openrouter_is_down(self):
        from evals.run_eval import DEFAULT_GEMINI_MODEL, main

        output = io.StringIO()
        calls = []

        def missing_openrouter(*_args, **_kwargs):
            calls.append("openrouter")
            raise OSError("network unavailable")

        def available_gemini(*_args, **_kwargs):
            calls.append("gemini")
            return {"api_key": "test-secret", "models": [DEFAULT_GEMINI_MODEL]}

        with patch("evals.run_eval.load_provider_api_key", return_value="test-secret"), \
                patch("evals.run_eval.openrouter_preflight", side_effect=missing_openrouter), \
                patch("evals.run_eval.gemini_preflight", side_effect=available_gemini), \
                redirect_stdout(output):
            status = main(["--preflight-only"])
        self.assertEqual(status, 0)
        self.assertEqual(calls, ["openrouter", "gemini"])
        self.assertIn(DEFAULT_GEMINI_MODEL, output.getvalue())


@unittest.skipUnless((ROOT / "evals" / "run_eval.py").is_file(), "runner implementation is not present")
class RunnerPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from evals.run_eval import classify_response, is_zero_price_free_model, run_case

        cls.run_case = staticmethod(run_case)
        cls.classify_response = staticmethod(classify_response)
        cls.is_zero_price_free_model = staticmethod(is_zero_price_free_model)

    @staticmethod
    def successful_response(model, content, finish_reason="stop"):
        return {
            "http_status": 200,
            "data": {
                "id": "gen-test",
                "provider": "test-provider",
                "model": model,
                "object": "chat.completion",
                "created": 1794316800,
                "choices": [
                    {
                        "logprobs": None,
                        "finish_reason": finish_reason,
                        "native_finish_reason": finish_reason,
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content,
                            "refusal": None,
                            "reasoning": None,
                        },
                    }
                ],
                "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
            },
            "error": None,
            "latency_seconds": 0.01,
            "retry_after": None,
        }

    @staticmethod
    def rate_limited_response():
        return {
            "http_status": 429,
            "data": {"error": {"message": "temporary rate limit"}},
            "error": "temporary rate limit",
            "latency_seconds": 0.01,
            "retry_after": 0,
        }

    def test_retries_same_model_after_429_and_records_each_attempt(self):
        queue = [self.rate_limited_response(), self.successful_response("model-a", "Ответ")]
        calls = []

        def requester(model, _max_tokens):
            calls.append(model)
            return queue.pop(0)

        rows = self.run_case(
            "case-1", ["model-a"], requester, mode="compare", retries=1, max_tokens=2048, retry_delay=0
        )
        self.assertEqual(calls, ["model-a", "model-a"])
        self.assertEqual([row["status"] for row in rows], ["provider_error", "answered"])
        self.assertEqual([row["attempt"] for row in rows], [1, 2])
        self.assertTrue(rows[-1]["model_done"])

    def test_fallback_uses_next_model_after_retries_are_exhausted(self):
        queues = {
            "model-a": [self.rate_limited_response(), self.rate_limited_response()],
            "model-b": [self.successful_response("model-b", "Резервный ответ")],
        }
        calls = []

        def requester(model, _max_tokens):
            calls.append(model)
            return queues[model].pop(0)

        rows = self.run_case(
            "case-1", ["model-a", "model-b"], requester, mode="fallback", retries=1, max_tokens=2048, retry_delay=0
        )
        self.assertEqual(calls, ["model-a", "model-a", "model-b"])
        self.assertEqual([row["model_requested"] for row in rows], calls)
        self.assertEqual(rows[-1]["status"], "answered")
        self.assertTrue(rows[-1]["case_done"])

    def test_truncated_answer_retries_with_doubled_token_limit(self):
        queue = [
            self.successful_response("model-a", "", "length"),
            self.successful_response("model-a", "Полный ответ"),
        ]
        token_limits = []

        def requester(model, max_tokens):
            token_limits.append(max_tokens)
            return queue.pop(0)

        rows = self.run_case(
            "case-1", ["model-a"], requester, mode="compare", retries=1, max_tokens=2048, retry_delay=0
        )
        self.assertEqual([row["status"] for row in rows], ["truncated", "answered"])
        self.assertEqual(token_limits, [2048, 4096])

    def test_compare_mode_runs_every_model_even_after_an_answer(self):
        calls = []

        def requester(model, _max_tokens):
            calls.append(model)
            return self.successful_response(model, "Ответ")

        self.run_case(
            "case-1", ["model-a", "model-b"], requester, mode="compare", retries=0, max_tokens=2048, retry_delay=0
        )
        self.assertEqual(calls, ["model-a", "model-b"])

    def test_classifies_provider_errors_and_truncated_empty_answers_separately(self):
        self.assertEqual(
            self.classify_response({"http_status": 429, "data": {}, "error": "rate limited"})["status"],
            "provider_error",
        )
        truncated = self.successful_response("model-a", "", "length")
        self.assertEqual(self.classify_response(truncated)["status"], "truncated")
        empty = self.successful_response("model-a", "")
        self.assertEqual(self.classify_response(empty)["status"], "empty")

    def test_daily_free_quota_stops_without_retry_or_model_fallback(self):
        calls = []

        def requester(model, _max_tokens):
            calls.append(model)
            return {
                "http_status": 429,
                "data": {"error": {"message": "Free model usage limit exceeded for today"}},
                "error": "Free model usage limit exceeded for today",
                "latency_seconds": 0.01,
                "retry_after": 1,
            }

        rows = self.run_case(
            "case-1", ["model-a", "model-b"], requester, mode="fallback", retries=2,
            max_tokens=2048, retry_delay=0,
        )
        self.assertEqual(calls, ["model-a"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["stop_reason"], "daily_quota_exhausted")
        self.assertTrue(rows[0]["case_done"])
        self.assertFalse(rows[0]["model_done"])

    def test_permanent_model_error_skips_retry_and_uses_next_fallback(self):
        calls = []

        def requester(model, _max_tokens):
            calls.append(model)
            if model == "model-a":
                return {"http_status": 404, "data": {}, "error": "model unavailable", "retry_after": None}
            return self.successful_response(model, "Резервный ответ")

        rows = self.run_case(
            "case-1", ["model-a", "model-b"], requester, mode="fallback", retries=2,
            max_tokens=2048, retry_delay=0,
        )
        self.assertEqual(calls, ["model-a", "model-b"])
        self.assertEqual(rows[0]["error_class"], "non_retryable_provider_error")
        self.assertEqual(rows[-1]["status"], "answered")

    def test_authentication_error_stops_the_whole_fallback_chain(self):
        calls = []

        def requester(model, _max_tokens):
            calls.append(model)
            return {"http_status": 401, "data": {}, "error": "invalid API key", "retry_after": None}

        rows = self.run_case(
            "case-1", ["model-a", "model-b"], requester, mode="fallback", retries=2,
            max_tokens=2048, retry_delay=0,
        )
        self.assertEqual(calls, ["model-a"])
        self.assertEqual(rows[0]["stop_reason"], "authentication_error")

    def test_free_model_gate_rejects_paid_or_non_free_ids(self):
        text_architecture = {"input_modalities": ["text"], "output_modalities": ["text"]}
        free = {
            "id": "provider/model:free",
            "pricing": {"prompt": "0", "completion": "0"},
            "architecture": text_architecture,
        }
        paid = {
            "id": "provider/model:free",
            "pricing": {"prompt": "0.001", "completion": "0"},
            "architecture": text_architecture,
        }
        paid_alias = {
            "id": "provider/model",
            "pricing": {"prompt": "0", "completion": "0"},
            "architecture": text_architecture,
        }
        self.assertTrue(self.is_zero_price_free_model(free))
        self.assertFalse(self.is_zero_price_free_model(paid))
        self.assertFalse(self.is_zero_price_free_model(paid_alias))


if __name__ == "__main__":
    unittest.main()
