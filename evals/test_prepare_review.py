import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PrepareReviewTests(unittest.TestCase):
    def test_review_queue_contains_only_final_answered_cases_with_questions(self):
        runs = [
            {
                "case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5",
                "model_done": False, "status": "provider_error", "answer": None,
            },
            {
                "case_id": "case-1", "model_requested": "model-a", "prompt_version": "v5",
                "model_done": True, "status": "answered", "answer": "Можно мыть вручную.",
                "product": "RE0731", "language": None, "category": None,
                "context_id": "RE0731_ru", "prompt_sha256": "abc",
                "context_sha256": hashlib.sha256("Тестовый контекст карточки.".encode("utf-8")).hexdigest(),
            },
            {
                "case_id": "case-2", "model_requested": "model-b", "prompt_version": "v5",
                "model_done": True, "status": "provider_error", "answer": None,
            },
        ]
        cases = [
            {
                "id": "case-1", "question": "Можно мыть в посудомойке?", "product": "RE0731",
                "language": "ru", "category": "cleaning", "context_id": "RE0731_ru",
                "expected_behavior": "Точный тип крышки в контексте не указан.",
                "must_cover": ["точный тип не указан"],
                "must_not_claim": ["Не выбирать тип крышки."],
                "critical_fail_tags": ["invented_feature"],
            },
            {"id": "case-2", "question": "Есть в наличии?"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            run_path = Path(directory) / "runs.jsonl"
            cases_path = Path(directory) / "cases.jsonl"
            contexts_path = Path(directory) / "contexts.json"
            output_path = Path(directory) / "review.jsonl"
            run_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in runs), encoding="utf-8")
            cases_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in cases), encoding="utf-8")
            contexts_path.write_text(json.dumps({"contexts": {"RE0731_ru": "Тестовый контекст карточки."}}, ensure_ascii=False), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "evals" / "prepare_review.py"), "--runs", str(run_path),
                 "--cases", str(cases_path), "--contexts", str(contexts_path), "--output", str(output_path)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["question"], "Можно мыть в посудомойке?")
        self.assertEqual(rows[0]["context"], "Тестовый контекст карточки.")
        self.assertEqual(rows[0]["context_sha256"], hashlib.sha256("Тестовый контекст карточки.".encode("utf-8")).hexdigest())
        self.assertEqual(rows[0]["expected_behavior"], "Точный тип крышки в контексте не указан.")
        self.assertEqual(rows[0]["must_cover"], ["точный тип не указан"])
        self.assertEqual(rows[0]["must_not_claim"], ["Не выбирать тип крышки."])
        self.assertEqual(rows[0]["critical_fail_tags_expected"], ["invented_feature"])
        self.assertEqual(rows[0]["answer"], "Можно мыть вручную.")
        self.assertEqual(rows[0]["language"], "ru")
        self.assertEqual(rows[0]["category"], "cleaning")
        self.assertIsNone(rows[0]["factual_accuracy"])
        self.assertIsNone(rows[0]["language_quality"])
        self.assertEqual(rows[0]["critical_failure_tags"], [])

    def test_does_not_overwrite_an_existing_manual_review_file(self):
        with tempfile.TemporaryDirectory() as directory:
            run_path = Path(directory) / "runs.jsonl"
            cases_path = Path(directory) / "cases.jsonl"
            output_path = Path(directory) / "review.jsonl"
            run_path.write_text("", encoding="utf-8")
            cases_path.write_text("", encoding="utf-8")
            output_path.write_text("manual scores\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "evals" / "prepare_review.py"), "--runs", str(run_path),
                 "--cases", str(cases_path), "--output", str(output_path)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            saved_content = output_path.read_text(encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)
        self.assertEqual(saved_content, "manual scores\n")


if __name__ == "__main__":
    unittest.main()
