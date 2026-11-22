#!/usr/bin/env python3
"""Run reproducible product-QA comparisons or model fallback checks."""

import argparse
import email.utils
import hashlib
import json
import os
import re
import sys
import time
import random
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .validate_eval import read_jsonl
else:
    from validate_eval import read_jsonl


DEFAULT_MODELS = (
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "nvidia/nemotron-3.5-super-vl:free",
)
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"
DEFAULT_OPENAI_MODEL = "gpt-6-luna"
GEMINI_REQUESTS_PER_MINUTE = 10


class BothProvidersUnavailable(RuntimeError):
    pass


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def model_text(message):
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return ""


def classify_response(response):
    http_status = response.get("http_status")
    data = response.get("data") or {}
    error = response.get("error")
    choices = data.get("choices") or []
    choice = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = choice.get("message") or {}
    answer = model_text(message)
    finish_reason = choice.get("finish_reason")
    if error or http_status is None or http_status < 200 or http_status >= 300:
        status = "provider_error"
    elif finish_reason == "length":
        status = "truncated"
    elif answer.strip():
        status = "answered"
    else:
        status = "empty"
    return {
        "status": status,
        "answer": answer or None,
        "finish_reason": finish_reason,
        "model_returned": data.get("model"),
        "usage": data.get("usage"),
        "error": error,
    }


def is_daily_quota_exhausted(response):
    if response.get("http_status") != 429:
        return False
    data = response.get("data") or {}
    api_error = data.get("error") or {}
    message = " ".join(
        str(value or "")
        for value in (
            response.get("error"),
            api_error.get("message"),
            api_error.get("code"),
            api_error.get("status"),
            json.dumps(api_error.get("details") or [], ensure_ascii=False),
        )
    ).casefold()
    markers = (
        "daily",
        "per-day",
        "per day",
        "every day",
        "each day",
        "today",
        "free-models-per-day",
        "day quota",
        "quota for the day",
        "requests_per_day",
        "requests per day",
        "per_day",
    )
    return any(marker in message for marker in markers)


def is_retryable_response(response, status, max_retry_delay=60):
    if status in ("empty", "truncated"):
        return True
    if status != "provider_error":
        return False
    if is_daily_quota_exhausted(response):
        return False
    http_status = response.get("http_status")
    if http_status is None:
        return True
    if http_status not in (408, 409, 425, 429, 500, 502, 503, 504):
        return False
    retry_after = response.get("retry_after")
    return retry_after is None or float(retry_after) <= max_retry_delay


def is_zero_price_free_model(model):
    if not isinstance(model, dict) or not str(model.get("id", "")).endswith(":free"):
        return False
    pricing = model.get("pricing") or {}
    architecture = model.get("architecture") or {}
    try:
        zero_price = float(pricing.get("prompt")) == 0 and float(pricing.get("completion")) == 0
    except (TypeError, ValueError):
        return False
    return (
        zero_price
        and "text" in (architecture.get("input_modalities") or [])
        and "text" in (architecture.get("output_modalities") or [])
    )


def load_api_key(env=None, dotenv_path=Path(".env")):
    return load_provider_api_key("openrouter", env=env, dotenv_path=dotenv_path)


def load_provider_api_key(provider, env=None, dotenv_path=Path(".env")):
    names = {"openrouter": "OPENROUTER_API_KEY", "gemini": "GEMINI_API", "openai": "OPENAI"}
    if provider not in names:
        raise ValueError("provider must be openrouter, gemini, or openai")
    env = os.environ if env is None else env
    env_name = names[provider]
    api_key = env.get(env_name)
    if api_key:
        return api_key
    if dotenv_path.is_file():
        for line in dotenv_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(env_name + "="):
                return stripped.split("=", 1)[1].strip().strip("\"'") or None
    return None


def gemini_retry_after(headers, payload):
    retry_after = headers.get("Retry-After") if headers else None
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except (TypeError, ValueError):
            try:
                retry_at = email.utils.parsedate_to_datetime(str(retry_after))
                return max(0.0, (retry_at - datetime.now(retry_at.tzinfo or timezone.utc)).total_seconds())
            except (TypeError, ValueError, OverflowError):
                pass
    error = payload.get("error") if isinstance(payload, dict) else None
    details = error.get("details") if isinstance(error, dict) else None
    for detail in details or []:
        if not isinstance(detail, dict):
            continue
        delay = detail.get("retryDelay")
        match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)s\s*", str(delay or ""))
        if match:
            return float(match.group(1))
    return None


def normalize_gemini_response(payload, http_status=200, retry_after=None, latency_seconds=None):
    payload = payload if isinstance(payload, dict) else {}
    error = payload.get("error")
    if error or http_status < 200 or http_status >= 300:
        message = error.get("message") if isinstance(error, dict) else None
        return {
            "http_status": http_status,
            "data": payload,
            "error": message or "HTTP error",
            "retry_after": retry_after,
            "latency_seconds": latency_seconds,
        }

    candidates = payload.get("candidates") or []
    candidate = candidates[0] if candidates and isinstance(candidates[0], dict) else {}
    content = candidate.get("content") or {}
    parts = content.get("parts") or []
    answer = "".join(
        str(part.get("text", ""))
        for part in parts
        if isinstance(part, dict) and isinstance(part.get("text", ""), str)
    )
    finish_reason = str(candidate.get("finishReason") or "").casefold()
    if finish_reason == "max_tokens":
        finish_reason = "length"
    usage = payload.get("usageMetadata") or {}
    return {
        "http_status": http_status,
        "data": {
            "model": payload.get("modelVersion"),
            "choices": [{
                "message": {"content": answer},
                "finish_reason": finish_reason,
            }] if candidate else [],
            "usage": {
                "prompt_tokens": usage.get("promptTokenCount"),
                "completion_tokens": usage.get("candidatesTokenCount"),
                "total_tokens": usage.get("totalTokenCount"),
            } if usage else None,
        },
        "error": None,
        "retry_after": retry_after,
        "latency_seconds": latency_seconds,
    }


def gemini_request(api_key, model, messages, max_tokens, base_url=GEMINI_BASE_URL, timeout=60):
    system_text = "\n\n".join(
        message["content"] for message in messages if message.get("role") == "system"
    )
    user_text = "\n\n".join(
        message["content"] for message in messages if message.get("role") != "system"
    )
    body = {
        "systemInstruction": {"parts": [{"text": system_text}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": max_tokens},
    }
    model_path = urllib.parse.quote(model.removeprefix("models/"), safe="-._")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/models/{model_path}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
            return normalize_gemini_response(
                payload,
                http_status=response.status,
                retry_after=gemini_retry_after(response.headers, payload),
                latency_seconds=round(time.monotonic() - started, 3),
            )
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8", "replace"))
        except (json.JSONDecodeError, AttributeError):
            payload = {}
        result = normalize_gemini_response(
            payload,
            http_status=exc.code,
            retry_after=gemini_retry_after(exc.headers, payload),
            latency_seconds=round(time.monotonic() - started, 3),
        )
        result["error"] = str(result["error"] or "HTTP error").replace(api_key, "[REDACTED]")[:300]
        return result
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "http_status": None,
            "data": {},
            "error": type(exc).__name__,
            "retry_after": None,
            "latency_seconds": round(time.monotonic() - started, 3),
        }


def openai_preflight(api_key, model, base_url=OPENAI_BASE_URL, timeout=15):
    model_path = urllib.parse.quote(model, safe="-._")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/models/{model_path}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read())
    if payload.get("id") != model:
        raise ValueError(f"OpenAI model is missing or inaccessible: {model}")
    return {"api_key": api_key, "models": [model]}


def normalize_openai_response(payload, http_status=200, retry_after=None, latency_seconds=None):
    payload = payload if isinstance(payload, dict) else {}
    error = payload.get("error")
    if error or http_status < 200 or http_status >= 300:
        message = error.get("message") if isinstance(error, dict) else None
        return {
            "http_status": http_status,
            "data": payload,
            "error": message or "HTTP error",
            "retry_after": retry_after,
            "latency_seconds": latency_seconds,
        }

    output = payload.get("output") or []
    text_parts = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for part in item.get("content") or []:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
            elif part.get("type") == "refusal" and isinstance(part.get("refusal"), str):
                text_parts.append(part["refusal"])
    answer = payload.get("output_text")
    if not isinstance(answer, str):
        answer = "".join(text_parts)
    incomplete = payload.get("incomplete_details") or {}
    finish_reason = "length" if incomplete.get("reason") == "max_output_tokens" else payload.get("status")
    usage = payload.get("usage") or None
    return {
        "http_status": http_status,
        "data": {
            "model": payload.get("model"),
            "choices": [{
                "message": {"content": answer},
                "finish_reason": finish_reason,
            }] if answer else [],
            "usage": usage,
        },
        "error": None,
        "retry_after": retry_after,
        "latency_seconds": latency_seconds,
    }


def openai_request(api_key, model, messages, max_tokens, base_url=OPENAI_BASE_URL, timeout=60):
    instructions = "\n\n".join(
        message["content"] for message in messages if message.get("role") == "system"
    )
    user_input = "\n\n".join(
        message["content"] for message in messages if message.get("role") != "system"
    )
    body = json.dumps({
        "model": model,
        "instructions": instructions,
        "input": user_input,
        "max_output_tokens": max_tokens,
        "store": False,
    }).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
            return normalize_openai_response(
                payload,
                http_status=response.status,
                latency_seconds=round(time.monotonic() - started, 3),
            )
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8", "replace"))
        except json.JSONDecodeError:
            payload = {}
        error = (payload.get("error") or {}).get("message") or "HTTP error"
        error = str(error).replace(api_key, "[REDACTED]")[:300]
        try:
            retry_after = float(exc.headers.get("Retry-After"))
        except (TypeError, ValueError):
            retry_after = None
        return {
            "http_status": exc.code,
            "data": payload,
            "error": error,
            "retry_after": retry_after,
            "latency_seconds": round(time.monotonic() - started, 3),
        }
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "http_status": None,
            "data": {},
            "error": type(exc).__name__,
            "retry_after": None,
            "latency_seconds": round(time.monotonic() - started, 3),
        }


def gemini_catalog_models(api_key, base_url=GEMINI_BASE_URL, timeout=15):
    request = urllib.request.Request(
        base_url.rstrip("/") + "/models",
        headers={"x-goog-api-key": api_key},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read()).get("models", [])


def verify_gemini_model(requested, catalog):
    for model in catalog:
        if not isinstance(model, dict):
            continue
        model_id = str(model.get("name", "")).removeprefix("models/")
        methods = model.get("supportedGenerationMethods") or []
        if model_id == requested and "generateContent" in methods:
            return
    raise ValueError(f"Gemini model is missing or does not support generateContent: {requested}")


class RateLimiter:
    def __init__(self, requests_per_minute, monotonic=time.monotonic, sleep=time.sleep):
        if requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be positive")
        self.interval = 60.0 / requests_per_minute
        self.monotonic = monotonic
        self.sleep = sleep
        self.last_request_at = None

    def wait(self):
        now = self.monotonic()
        if self.last_request_at is not None:
            delay = self.interval - (now - self.last_request_at)
            if delay > 0:
                self.sleep(delay)
                now = self.monotonic()
        self.last_request_at = now


def resolve_provider(
    mode,
    openrouter_probe,
    gemini_probe,
    timeout_seconds=120,
    poll_interval=15,
    monotonic=time.monotonic,
    sleep=time.sleep,
    preferred=None,
):
    if mode not in ("auto", "openrouter", "gemini"):
        raise ValueError("provider must be auto, openrouter, or gemini")
    probes = {
        "openrouter": openrouter_probe,
        "gemini": gemini_probe,
    }
    candidates = ("openrouter", "gemini") if mode == "auto" else (mode,)
    if mode == "auto" and preferred in candidates:
        candidates = (preferred,) + tuple(provider for provider in candidates if provider != preferred)
    started = monotonic()
    while True:
        for provider in candidates:
            if probes[provider]():
                return provider
        elapsed = monotonic() - started
        if elapsed >= timeout_seconds:
            unavailable = " and ".join(candidates)
            raise BothProvidersUnavailable(
                f"{unavailable} stayed unavailable for {timeout_seconds:g} seconds"
            )
        sleep(min(poll_interval, timeout_seconds - elapsed))


def catalog_models(api_key, base_url=DEFAULT_BASE_URL, timeout=30):
    request = urllib.request.Request(
        base_url.rstrip("/") + "/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read()).get("data", [])


def verify_free_models(requested, catalog):
    by_id = {row.get("id"): row for row in catalog if isinstance(row, dict)}
    invalid = []
    for model_id in requested:
        model = by_id.get(model_id)
        if not model or not is_zero_price_free_model(model):
            invalid.append(model_id)
    if invalid:
        raise ValueError("Models are missing or not verified text-in/text-out at zero price: " + ", ".join(invalid))


def openrouter_request(api_key, model, messages, max_tokens, base_url, timeout):
    body = json.dumps(
        {"model": model, "messages": messages, "temperature": 0, "max_tokens": max_tokens}
    ).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read())
            return {
                "http_status": response.status,
                "data": data,
                "error": None,
                "retry_after": None,
                "latency_seconds": round(time.monotonic() - started, 3),
            }
    except urllib.error.HTTPError as exc:
        try:
            data = json.loads(exc.read().decode("utf-8", "replace"))
            error = (data.get("error") or {}).get("message") or "HTTP error"
        except (json.JSONDecodeError, AttributeError):
            data = {}
            error = "HTTP error"
        error = str(error).replace(api_key, "[REDACTED]")[:300]
        try:
            retry_after = float(exc.headers.get("Retry-After"))
        except (TypeError, ValueError):
            retry_after = None
        return {
            "http_status": exc.code,
            "data": data,
            "error": error,
            "retry_after": retry_after,
            "latency_seconds": round(time.monotonic() - started, 3),
        }
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "http_status": None,
            "data": {},
            "error": type(exc).__name__,
            "retry_after": None,
            "latency_seconds": round(time.monotonic() - started, 3),
        }


def run_case(
    case_id,
    models,
    requester,
    mode="compare",
    retries=1,
    max_tokens=2048,
    retry_delay=2,
    max_retry_delay=60,
    jitter=random.uniform,
):
    if mode not in ("compare", "fallback"):
        raise ValueError("mode must be compare or fallback")
    attempts = []
    for model_index, model in enumerate(models):
        current_max_tokens = max_tokens
        model_rows = []
        for attempt_number in range(1, retries + 2):
            response = requester(model, current_max_tokens)
            result = classify_response(response)
            daily_quota = is_daily_quota_exhausted(response)
            auth_error = response.get("http_status") in (401, 403)
            retryable = is_retryable_response(response, result["status"], max_retry_delay=max_retry_delay)
            is_final_attempt = result["status"] == "answered" or not retryable or attempt_number == retries + 1
            row = {
                "case_id": case_id,
                "model_requested": model,
                "model_returned": result["model_returned"],
                "model_index": model_index,
                "attempt": attempt_number,
                "status": result["status"],
                "answer": result["answer"],
                "finish_reason": result["finish_reason"],
                "http_status": response.get("http_status"),
                "latency_seconds": response.get("latency_seconds"),
                "usage": result["usage"],
                "error": result["error"],
                "error_class": (
                    "daily_quota_exhausted" if daily_quota else
                    "authentication_error" if auth_error else
                    "non_retryable_provider_error" if result["status"] == "provider_error" and not retryable else
                    None
                ),
                "retry_after_seconds": response.get("retry_after"),
                "request_parameters": {"temperature": 0, "max_tokens": current_max_tokens},
                "model_done": is_final_attempt and not daily_quota and not auth_error,
                "case_done": False,
            }
            attempts.append(row)
            model_rows.append(row)
            if daily_quota:
                row["stop_reason"] = "daily_quota_exhausted"
                row["case_done"] = True
                return attempts
            if auth_error:
                row["stop_reason"] = "authentication_error"
                row["case_done"] = True
                return attempts
            if result["status"] == "answered" or is_final_attempt:
                break
            if result["status"] == "truncated":
                current_max_tokens = min(current_max_tokens * 2, 8192)
            else:
                backoff = response.get("retry_after")
                if backoff is None:
                    base_delay = retry_delay * (2 ** (attempt_number - 1))
                    backoff = jitter(base_delay * 0.75, base_delay * 1.25) if base_delay else 0
                time.sleep(min(max(float(backoff), 0), max_retry_delay))
        if mode == "fallback" and model_rows[-1]["status"] == "answered":
            break
    if attempts:
        attempts[-1]["case_done"] = True
    return attempts


def prompt_version(path):
    match = re.search(r"-v(\d+)\.md$", str(path))
    return f"v{match.group(1)}" if match else "unversioned"


def append_jsonl(path, row):
    encoded = json.dumps(row, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as output:
        output.write(encoded)
        output.flush()


def persist_case_rows(path, rows, metadata):
    for row in rows:
        row.update(metadata)
        # A timeout can happen after OpenRouter received the request, so every
        # requester invocation consumes the local free-request budget.
        row["api_call_made"] = True
        append_jsonl(path, row)


def parse_free_model_quota(payload):
    data = payload.get("data") if isinstance(payload, dict) else None
    quota = data.get("free_model_daily_requests") if isinstance(data, dict) else None
    if not isinstance(quota, dict):
        raise ValueError("OpenRouter did not return free-model daily quota status")
    values = {name: quota.get(name) for name in ("used", "limit", "remaining")}
    if any(type(value) is not int or value < 0 for value in values.values()):
        raise ValueError("OpenRouter returned invalid free-model daily quota values")
    return values


def free_model_quota(api_key, base_url=DEFAULT_BASE_URL, timeout=30):
    request = urllib.request.Request(
        base_url.rstrip("/") + "/key",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_free_model_quota(json.loads(response.read()))


def effective_request_cap(invocation_cap, quota_remaining):
    return max(0, min(invocation_cap, quota_remaining))


def openrouter_preflight(api_key, models, base_url=DEFAULT_BASE_URL, timeout=15):
    catalog = catalog_models(api_key, base_url, timeout)
    verify_free_models(models, catalog)
    quota = free_model_quota(api_key, base_url, timeout)
    if quota["remaining"] == 0:
        raise ValueError("OpenRouter reports no free-model requests remaining today")
    return {"api_key": api_key, "models": list(models), "quota": quota}


def gemini_preflight(api_key, model, base_url=GEMINI_BASE_URL, timeout=15):
    catalog = gemini_catalog_models(api_key, base_url, timeout)
    verify_gemini_model(model, catalog)
    return {"api_key": api_key, "models": [model]}


def provider_run_unavailable(rows):
    if not rows or any(row.get("status") == "answered" for row in rows):
        return False
    outage_statuses = (None, 401, 403, 408, 425, 429, 500, 502, 503, 504)
    return all(
        row.get("stop_reason") in ("daily_quota_exhausted", "authentication_error")
        or (row.get("status") == "provider_error" and row.get("http_status") in outage_statuses)
        for row in rows
    )


def provider_output_path(base_path, provider, automatic):
    if not automatic:
        return base_path
    return base_path.with_name(f"{base_path.stem}-{provider}{base_path.suffix}")


def run_fingerprint(prompt_hash, contexts_hash, cases, args, provider=None, models=None):
    effective_retries = args.gemini_retries if provider == "gemini" else args.retries
    effective_retry_delay = args.gemini_retry_delay if provider == "gemini" else args.retry_delay
    base_url = {
        "openrouter": args.api_base_url.rstrip("/"),
        "gemini": GEMINI_BASE_URL,
        "openai": OPENAI_BASE_URL,
    }.get(provider, args.api_base_url.rstrip("/"))
    inputs = {
        "prompt_sha256": prompt_hash,
        "contexts_sha256": contexts_hash,
        "cases_sha256": digest(json.dumps(cases, ensure_ascii=False, sort_keys=True)),
        "provider": provider or "openrouter",
        "models": list(models if models is not None else args.models),
        "mode": args.mode,
        "max_tokens": args.max_tokens,
        "retries": effective_retries,
        "retry_delay": effective_retry_delay,
        "api_base_url": base_url,
        "gemini_requests_per_minute": getattr(args, "gemini_rpm", None) if provider == "gemini" else None,
        "gemini_max_retry_delay": getattr(args, "gemini_max_retry_delay", None) if provider == "gemini" else None,
    }
    if provider == "openai":
        inputs["request_parameters"] = {
            "temperature": "model_default",
            "reasoning_effort": "medium",
            "max_output_tokens": args.max_tokens,
            "store": False,
        }
    canonical = json.dumps(inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return digest(canonical)


def load_resume_state(path, expected_fingerprint, mode):
    done = {}
    finished_fallback_cases = set()
    if not path.is_file() or not path.stat().st_size:
        return done, finished_fallback_cases
    for row in read_jsonl(path):
        if row.get("run_fingerprint") != expected_fingerprint or row.get("mode") != mode:
            raise ValueError("output contains a different run fingerprint; use a new output file")
        if row.get("model_done"):
            done.setdefault(row.get("case_id"), set()).add(row.get("model_requested"))
        if mode == "fallback" and row.get("case_done") and row.get("status") == "answered":
            finished_fallback_cases.add(row.get("case_id"))
    return done, finished_fallback_cases


def run_provider_eval(args, provider, config, cases, contexts, prompt, output_path):
    models = config["models"]
    api_key = config["api_key"]
    if provider == "openrouter":
        base_url = args.api_base_url
        retries = args.retries
        retry_delay = args.retry_delay
        max_retry_delay = 30
        daily_limit = config["quota"]["remaining"]
        invocation_cap = args.request_cap if args.request_cap is not None else 45
        limiter = None
    elif provider == "gemini":
        base_url = GEMINI_BASE_URL
        retries = args.gemini_retries
        retry_delay = args.gemini_retry_delay
        max_retry_delay = args.gemini_max_retry_delay
        daily_limit = args.gemini_daily_limit
        invocation_cap = args.request_cap if args.request_cap is not None else len(cases) * (retries + 1)
        limiter = RateLimiter(args.gemini_rpm)
    else:
        base_url = OPENAI_BASE_URL
        retries = args.retries
        retry_delay = args.retry_delay
        max_retry_delay = 60
        invocation_cap = args.request_cap if args.request_cap is not None else len(cases) * (retries + 1)
        daily_limit = invocation_cap
        limiter = None
    effective_cap = effective_request_cap(invocation_cap, daily_limit)
    if effective_cap == 0:
        print(f"{provider} has no request capacity available; looking for another provider.", file=sys.stderr)
        return "provider_unavailable"
    print(
        f"Provider: {provider}; this invocation may make at most {effective_cap} generation calls.",
        flush=True,
    )

    prompt_hash = digest(prompt)
    contexts_hash = digest(json.dumps(contexts, ensure_ascii=False, sort_keys=True))
    fingerprint = run_fingerprint(prompt_hash, contexts_hash, cases, args, provider=provider, models=models)
    done, finished_fallback_cases = {}, set()
    if args.resume:
        try:
            done, finished_fallback_cases = load_resume_state(output_path, fingerprint, args.mode)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return "invalid_resume"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request_count = completed_cases = 0
    for case in cases:
        if args.mode == "fallback" and case["id"] in finished_fallback_cases:
            continue
        context = contexts.get(case["context_id"])
        if not context:
            print(f"missing context: {case['context_id']}", file=sys.stderr)
            return "invalid_input"
        selected_models = [model for model in models if model not in done.get(case["id"], set())]
        if not selected_models:
            continue
        worst_case_calls = len(selected_models) * (retries + 1)
        if request_count + worst_case_calls > effective_cap:
            print(
                f"Stopped before {case['id']}: invocation cap {effective_cap} preserves room for retries; "
                f"made {request_count} calls. Re-run with --resume.",
                file=sys.stderr,
            )
            return "partial"
        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Контекст товара:\n{context}\n\nВопрос покупателя: {case['question']}",
            },
        ]

        def requester(model, max_tokens):
            nonlocal request_count
            if limiter:
                limiter.wait()
            request_count += 1
            if provider == "gemini":
                return gemini_request(api_key, model, messages, max_tokens, base_url, args.timeout)
            if provider == "openai":
                return openai_request(api_key, model, messages, max_tokens, base_url, args.timeout)
            return openrouter_request(api_key, model, messages, max_tokens, base_url, args.timeout)

        context_hash = digest(context)
        version = prompt_version(args.prompt)
        case_rows = run_case(
            case["id"],
            selected_models,
            requester,
            mode=args.mode,
            retries=retries,
            max_tokens=args.max_tokens,
            retry_delay=retry_delay,
            max_retry_delay=max_retry_delay,
        )
        metadata = {
            "product": case["product"],
            "language": case["language"],
            "category": case["category"],
            "context_id": case["context_id"],
            "prompt_version": version,
            "provider": provider,
            "prompt_sha256": prompt_hash,
            "context_sha256": context_hash,
            "run_fingerprint": fingerprint,
            "mode": args.mode,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        if provider == "openai":
            metadata["request_parameters"] = {
                "temperature": "model_default",
                "reasoning_effort": "medium",
                "max_output_tokens": args.max_tokens,
                "store": False,
            }
        persist_case_rows(output_path, case_rows, metadata)
        for row in case_rows:
            print(
                f"{row['case_id']} {row['model_requested']} attempt={row['attempt']} "
                f"status={row['status']} latency={row['latency_seconds']}s",
                flush=True,
            )
        if provider_run_unavailable(case_rows):
            return "provider_unavailable"
        stop_reason = next((row.get("stop_reason") for row in case_rows if row.get("stop_reason")), None)
        if case_rows and case_rows[-1]["case_done"] and not stop_reason:
            completed_cases += 1
    print(f"Finished: {request_count} API calls, {completed_cases} completed cases; output={output_path}")
    return "completed"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("evals/product-qa-cases.jsonl"))
    parser.add_argument("--contexts", type=Path, default=Path("evals/model-contexts.json"))
    parser.add_argument("--prompt", type=Path, default=Path("prompts/product-assistant-system-v6.md"))
    parser.add_argument("--provider", choices=("auto", "openrouter", "gemini", "openai"), default="auto")
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS))
    parser.add_argument("--gemini-model", default=DEFAULT_GEMINI_MODEL)
    parser.add_argument("--openai-model", default=DEFAULT_OPENAI_MODEL)
    parser.add_argument("--mode", choices=("compare", "fallback"), default="compare")
    parser.add_argument("--case-ids", nargs="*", help="optional explicit case IDs for targeted retries")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--preflight-only", action="store_true", help="verify provider access without inference")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay", type=float, default=2)
    parser.add_argument("--gemini-retries", type=int, default=2)
    parser.add_argument("--gemini-retry-delay", type=float, default=5)
    parser.add_argument("--gemini-max-retry-delay", type=float, default=60)
    parser.add_argument("--gemini-rpm", type=float, default=GEMINI_REQUESTS_PER_MINUTE)
    parser.add_argument("--gemini-daily-limit", type=int, default=500)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--request-cap", type=int, help="maximum API calls in this invocation")
    parser.add_argument("--unavailable-timeout", type=float, default=120)
    parser.add_argument("--availability-poll-interval", type=float, default=15)
    parser.add_argument("--api-base-url", default=DEFAULT_BASE_URL, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if not args.preflight_only and args.output is None:
        parser.error("--output is required unless --preflight-only is used")
    if (
        args.max_tokens < 1
        or args.retries < 0
        or args.gemini_retries < 0
        or (args.request_cap is not None and args.request_cap < 1)
        or args.gemini_rpm <= 0
        or args.gemini_daily_limit < 1
        or args.unavailable_timeout <= 0
        or args.availability_poll_interval <= 0
    ):
        parser.error("token limits, request limits, retry counts, provider rates, and timeouts must be positive")

    try:
        prompt = args.prompt.read_text(encoding="utf-8")
        contexts = json.loads(args.contexts.read_text(encoding="utf-8"))["contexts"]
        cases = read_jsonl(args.cases)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        parser.error(f"could not load evaluation inputs: {type(exc).__name__}")
    if args.case_ids:
        requested = set(args.case_ids)
        cases = [case for case in cases if case["id"] in requested]
        missing = requested - {case["id"] for case in cases}
        if missing:
            parser.error("unknown case IDs: " + ", ".join(sorted(missing)))

    configs, errors = {}, {}

    def probe_openrouter():
        try:
            api_key = load_provider_api_key("openrouter")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY is missing")
            configs["openrouter"] = openrouter_preflight(
                api_key, args.models, args.api_base_url, min(args.timeout, 15)
            )
            errors.pop("openrouter", None)
            return True
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            configs.pop("openrouter", None)
            errors["openrouter"] = type(exc).__name__
            return False

    def probe_gemini():
        try:
            api_key = load_provider_api_key("gemini")
            if not api_key:
                raise ValueError("GEMINI_API is missing")
            configs["gemini"] = gemini_preflight(
                api_key, args.gemini_model, GEMINI_BASE_URL, min(args.timeout, 15)
            )
            errors.pop("gemini", None)
            return True
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            configs.pop("gemini", None)
            errors["gemini"] = type(exc).__name__
            return False

    def probe_openai():
        try:
            api_key = load_provider_api_key("openai")
            if not api_key:
                raise ValueError("OPENAI is missing")
            configs["openai"] = openai_preflight(
                api_key, args.openai_model, OPENAI_BASE_URL, min(args.timeout, 15)
            )
            errors.pop("openai", None)
            return True
        except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
            configs.pop("openai", None)
            errors["openai"] = type(exc).__name__
            return False

    if args.provider == "openai":
        if not probe_openai():
            print(
                f"OpenAI preflight failed ({errors.get('openai', 'unknown error')}); "
                "no generation requests were sent.",
                file=sys.stderr,
            )
            return 75
        provider = "openai"
    else:
        try:
            provider = resolve_provider(
                args.provider,
                probe_openrouter,
                probe_gemini,
                timeout_seconds=args.unavailable_timeout,
                poll_interval=args.availability_poll_interval,
            )
        except BothProvidersUnavailable:
            print(
                f"PAUSED: OpenRouter and Gemini APIs unavailable for more than "
                f"{args.unavailable_timeout:g} seconds. No generation requests were sent.",
                file=sys.stderr,
            )
            return 75

    if args.preflight_only:
        if provider == "openrouter":
            quota = configs[provider]["quota"]
            print(
                f"PASS: OpenRouter verified {len(args.models)} zero-price text models; "
                f"free quota remaining={quota['remaining']}/{quota['limit']} (UTC day)"
            )
        elif provider == "gemini":
            print(
                f"PASS: Gemini verified {args.gemini_model} for generateContent; "
                f"configured pacing={args.gemini_rpm:g} RPM, observed project limit="
                f"{args.gemini_rpm * 1.5:g} RPM, {args.gemini_daily_limit} RPD. "
                "Live remaining daily quota is not exposed by the model-list API."
            )
        else:
            print(f"PASS: OpenAI verified {args.openai_model} for Responses API; no generation sent.")
        return 0

    output_path = provider_output_path(args.output, provider, automatic=args.provider == "auto")
    if output_path.exists() and output_path.stat().st_size and not args.resume:
        parser.error(f"output exists; pass --resume or choose another path: {output_path}")
    status = run_provider_eval(args, provider, configs[provider], cases, contexts, prompt, output_path)
    if status in ("completed", "partial"):
        return 0
    if status == "provider_unavailable" and args.provider == "auto":
        other = "gemini" if provider == "openrouter" else "openrouter"
        if (probe_gemini if other == "gemini" else probe_openrouter)():
            fallback_output = provider_output_path(args.output, other, automatic=True)
            if fallback_output.exists() and fallback_output.stat().st_size:
                args.resume = True
            return 0 if run_provider_eval(
                args, other, configs[other], cases, contexts, prompt, fallback_output
            ) in ("completed", "partial") else 75
        try:
            recovered = resolve_provider(
                "auto",
                probe_openrouter,
                probe_gemini,
                timeout_seconds=args.unavailable_timeout,
                poll_interval=args.availability_poll_interval,
            preferred=other,
            )
        except BothProvidersUnavailable:
            print(
                f"PAUSED: OpenRouter and Gemini APIs unavailable for more than "
                f"{args.unavailable_timeout:g} seconds. No further generation requests were sent.",
                file=sys.stderr,
            )
            return 75
        recovered_output = provider_output_path(args.output, recovered, automatic=True)
        if recovered_output.exists() and recovered_output.stat().st_size:
            args.resume = True
        return 0 if run_provider_eval(
            args, recovered, configs[recovered], cases, contexts, prompt, recovered_output
        ) in ("completed", "partial") else 75
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
