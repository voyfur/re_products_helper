import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RunReportTests(unittest.TestCase):
    def test_load_scores_rejects_malformed_critical_failure_tags(self):
        score = {
            "case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5",
            "factual_accuracy": 2, "uncertainty": 2, "scope": 2, "language_quality": 2,
            "total": 8, "critical_failure_tags": [["wrong_number"]],
        }
        with tempfile.TemporaryDirectory() as directory:
            score_path = Path(directory) / "scores.jsonl"
            score_path.write_text(json.dumps(score) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "critical_failure_tags entries must be unique non-empty strings"):
                self._load_report_module().load_scores(score_path)

    def test_report_separates_answer_availability_and_manual_scores(self):
        runs = [
            {
                "case_id": "case-1", "product": "RE89157", "language": "ru",
                "category": "fact_retrieval", "model_requested": "model-a", "prompt_version": "v5", "status": "answered",
                "model_done": True, "answer": "Answer", "http_status": 200,
            },
            {
                "case_id": "case-2", "product": "RE1687", "language": "uk",
                "category": "availability", "model_requested": "model-a", "prompt_version": "v5", "status": "provider_error",
                "model_done": True, "answer": None, "http_status": 429,
            },
            {
                "case_id": "case-1", "product": "RE89157", "language": "ru",
                "category": "fact_retrieval", "model_requested": "model-b", "prompt_version": "v5", "status": "answered",
                "model_done": True, "answer": "Answer", "http_status": 200,
            },
        ]
        scores = [
            {
                "case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5",
                "factual_accuracy": 2, "uncertainty": 2, "scope": 2, "language_quality": 2,
                "total": 8, "critical_failure_tags": [], "notes": "",
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            run_path = Path(directory) / "run.jsonl"
            score_path = Path(directory) / "scores.jsonl"
            run_path.write_text("".join(json.dumps(row) + "\n" for row in runs), encoding="utf-8")
            score_path.write_text("".join(json.dumps(row) + "\n" for row in scores), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "evals" / "report_runs.py"),
                    "--runs", str(run_path),
                    "--scores", str(score_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        model_a = report["by_model"]["model-a|v5"]
        self.assertEqual(model_a["completed_cases"], 2)
        self.assertEqual(model_a["answered"], 1)
        self.assertEqual(model_a["provider_errors"], 1)
        self.assertEqual(model_a["mean_score"], 8)
        self.assertEqual(model_a["critical_failures"], 0)
        self.assertEqual(report["by_model"]["model-b|v5"]["unscored_answered"], 1)
        self.assertIn("model-a|v5|RE89157|ru", report["by_product_language"])
        self.assertIn("model-a|v5|fact_retrieval", report["by_category"])

    def test_fallback_summary_counts_one_latest_outcome_per_case(self):
        module = self._load_report_module()
        rows = [
            {"case_id": "case-1", "mode": "fallback", "model_requested": "model-a", "status": "provider_error", "model_done": True, "case_done": False},
            {"case_id": "case-1", "mode": "fallback", "model_requested": "model-a", "status": "provider_error", "model_done": False, "case_done": True, "stop_reason": "daily_quota_exhausted"},
            {"case_id": "case-1", "mode": "fallback", "model_requested": "model-b", "status": "answered", "model_done": True, "case_done": True},
            {"case_id": "case-2", "mode": "fallback", "model_requested": "model-a", "status": "empty", "model_done": True, "case_done": True},
        ]
        report = module.build_report(rows, {})
        self.assertEqual(report["fallback"]["completed_cases"], 2)
        self.assertEqual(report["fallback"]["answered"], 1)
        self.assertEqual(report["fallback"]["unanswered"], 1)
        self.assertEqual(report["fallback"]["answered_by_model"], {"model-b": 1})

    def test_report_rejects_mixed_prompt_or_context_for_same_case(self):
        module = self._load_report_module()
        rows = [
            {"case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5", "prompt_sha256": "p1", "context_sha256": "c1", "mode": "compare", "status": "answered", "model_done": True},
            {"case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5", "prompt_sha256": "p2", "context_sha256": "c2", "mode": "compare", "status": "answered", "model_done": True},
        ]
        with self.assertRaisesRegex(ValueError, "multiple prompt/context hashes"):
            module.build_report(rows, {})

    def test_report_rejects_mixed_compare_and_fallback_runs(self):
        module = self._load_report_module()
        rows = [
            {"case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5", "mode": "compare", "status": "answered", "model_done": True},
            {"case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5", "mode": "fallback", "status": "answered", "model_done": True, "case_done": True},
        ]
        with self.assertRaisesRegex(ValueError, "mix compare and fallback"):
            module.build_report(rows, {})

    @staticmethod
    def _load_report_module():
        import importlib

        return importlib.import_module("evals.report_runs")


if __name__ == "__main__":
    unittest.main()
