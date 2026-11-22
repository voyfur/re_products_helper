#!/usr/bin/env python3
"""Create an editable human-review queue for completed model answers."""

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from .report_runs import final_model_rows
    from .validate_eval import read_jsonl
else:
    from report_runs import final_model_rows
    from validate_eval import read_jsonl


SCORE_FIELDS = ("factual_accuracy", "uncertainty", "scope", "language_quality")


def build_review_queue(run_rows, cases, contexts):
    cases_by_id = {case["id"]: case for case in cases}
    queue = []
    for result in final_model_rows(run_rows):
        if result.get("status") != "answered":
            continue
        case_id = result.get("case_id")
        case = cases_by_id.get(case_id)
        if case is None:
            raise ValueError(f"run result references missing case: {case_id}")
        context_id = result.get("context_id") or case.get("context_id")
        context = contexts.get(context_id)
        if not isinstance(context, str):
            raise ValueError(f"review context is missing: {context_id}")
        context_hash = result.get("context_sha256")
        if context_hash and hashlib.sha256(context.encode("utf-8")).hexdigest() != context_hash:
            raise ValueError(f"review context hash does not match run: {case_id}")
        row = {
            "case_id": case_id,
            "model_requested": result.get("model_requested"),
            "prompt_version": result.get("prompt_version"),
            "prompt_sha256": result.get("prompt_sha256"),
            "context_sha256": result.get("context_sha256"),
            "product": result.get("product") or case.get("product"),
            "language": result.get("language") or case.get("language"),
            "category": result.get("category") or case.get("category"),
            "context_id": context_id,
            "pair_id": case.get("pair_id"),
            "context": context,
            "question": case["question"],
            "expected_behavior": case.get("expected_behavior"),
            "must_cover": case.get("must_cover", []),
            "must_not_claim": case.get("must_not_claim", []),
            "critical_fail_tags_expected": case.get("critical_fail_tags", []),
            "source_ref": case.get("source_ref"),
            "answer": result.get("answer"),
        }
        row.update({field: None for field in SCORE_FIELDS})
        row.update({"total": None, "critical_failure_tags": [], "notes": ""})
        queue.append(row)
    return queue


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--cases", type=Path, default=Path("evals/product-qa-cases.jsonl"))
    parser.add_argument("--contexts", type=Path, default=Path("evals/model-contexts.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"output already exists; choose a new path: {args.output}")
    try:
        context_data = json.loads(args.contexts.read_text(encoding="utf-8"))
        contexts = context_data.get("contexts")
        if not isinstance(contexts, dict):
            raise ValueError("contexts file must contain a contexts object")
        queue = build_review_queue(read_jsonl(args.runs), read_jsonl(args.cases), contexts)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in queue),
        encoding="utf-8",
    )
    print(f"Prepared {len(queue)} answers for manual scoring: {args.output}")


if __name__ == "__main__":
    main()
