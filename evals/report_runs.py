#!/usr/bin/env python3
"""Aggregate model availability and human QA scores from JSONL run files."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

if __package__:
    from .validate_eval import read_jsonl
else:
    from validate_eval import read_jsonl


SCORE_FIELDS = ("factual_accuracy", "uncertainty", "scope", "language_quality")


def load_scores(path):
    scores = {}
    if not path:
        return scores
    for row in read_jsonl(path):
        missing = [field for field in ("case_id", "model_requested", "prompt_version", *SCORE_FIELDS, "total", "critical_failure_tags") if field not in row]
        if missing:
            raise ValueError(f"score row missing fields: {', '.join(missing)}")
        dimensions = [row[field] for field in SCORE_FIELDS]
        if any(not isinstance(value, int) or not 0 <= value <= 2 for value in dimensions):
            raise ValueError(f"score dimensions must be integers from 0 to 2: {row['case_id']}")
        if row["total"] != sum(dimensions):
            raise ValueError(f"score total does not match dimensions: {row['case_id']}")
        tags = row["critical_failure_tags"]
        if not isinstance(tags, list):
            raise ValueError(f"critical_failure_tags must be a list: {row['case_id']}")
        if any(not isinstance(tag, str) or not tag.strip() for tag in tags) or len(set(tags)) != len(tags):
            raise ValueError(
                "critical_failure_tags entries must be unique non-empty strings: "
                f"{row['case_id']}"
            )
        key = result_key(row)
        if key in scores:
            raise ValueError(f"duplicate score row: {key}")
        scores[key] = row
    return scores


def result_key(row):
    return (
        row.get("case_id"),
        row.get("model_requested"),
        row.get("prompt_version"),
        row.get("prompt_sha256"),
        row.get("context_sha256"),
    )


def final_model_rows(run_rows):
    grouped = {}
    for row in run_rows:
        key = result_key(row)
        if row.get("model_done") is False:
            continue
        grouped[key] = row
    return list(grouped.values())


def aggregate(rows, scores, group_name):
    group_fields = {
        "model": ("model_requested", "prompt_version"),
        "product_language": ("model_requested", "prompt_version", "product", "language"),
        "category": ("model_requested", "prompt_version", "category"),
    }[group_name]
    output = defaultdict(lambda: {
        "completed_cases": 0,
        "answered": 0,
        "provider_errors": 0,
        "empty": 0,
        "truncated": 0,
        "other_statuses": 0,
        "scored_answers": 0,
        "unscored_answered": 0,
        "score_sum": 0,
        "critical_failures": 0,
        "critical_failure_tags": Counter(),
        "critical_failure_cases": [],
        "case_ids": [],
    })
    for row in rows:
        group = "|".join(str(row.get(field) or "unknown") for field in group_fields)
        data = output[group]
        data["completed_cases"] += 1
        data["case_ids"].append(row.get("case_id"))
        status = row.get("status")
        if status == "answered":
            data["answered"] += 1
        elif status == "provider_error":
            data["provider_errors"] += 1
        elif status == "empty":
            data["empty"] += 1
        elif status == "truncated":
            data["truncated"] += 1
        else:
            data["other_statuses"] += 1

        score = scores.get(result_key(row))
        if status == "answered" and score is None:
            data["unscored_answered"] += 1
        if score:
            data["scored_answers"] += 1
            data["score_sum"] += score["total"]
            tags = score["critical_failure_tags"]
            if tags:
                data["critical_failures"] += 1
                data["critical_failure_cases"].append(row.get("case_id"))
                data["critical_failure_tags"].update(tags)

    for data in output.values():
        data["mean_score"] = round(data["score_sum"] / data["scored_answers"], 3) if data["scored_answers"] else None
        del data["score_sum"]
        data["critical_failure_tags"] = dict(sorted(data["critical_failure_tags"].items()))
        data["case_ids"] = sorted(set(data["case_ids"]))
        data["critical_failure_cases"] = sorted(set(data["critical_failure_cases"]))
    return dict(sorted(output.items()))


def build_report(run_rows, scores):
    final_rows = final_model_rows(run_rows)
    modes = {row.get("mode") for row in run_rows if row.get("mode")}
    if len(modes) > 1:
        raise ValueError("report cannot mix compare and fallback runs")
    prompt_contexts = defaultdict(set)
    for row in final_rows:
        prompt_contexts[(row.get("case_id"), row.get("prompt_version"))].add(
            (row.get("prompt_sha256"), row.get("context_sha256"))
        )
    if any(len(hashes) > 1 for hashes in prompt_contexts.values()):
        raise ValueError("report contains multiple prompt/context hashes for the same case")
    known = {
        result_key(row)
        for row in final_rows
        if row.get("status") == "answered"
    }
    orphan_scores = sorted(set(scores) - known)
    if orphan_scores:
        raise ValueError(f"score row has no answered result: {orphan_scores[0]}")
    report = {
        "api_attempts": len(run_rows),
        "final_model_results": len(final_rows),
        "scored_answers": len(scores),
        "by_model": aggregate(final_rows, scores, "model"),
        "by_product_language": aggregate(final_rows, scores, "product_language"),
        "by_category": aggregate(final_rows, scores, "category"),
    }
    fallback = [row for row in run_rows if row.get("mode") == "fallback"]
    if fallback:
        latest_case_results = {}
        for row in fallback:
            if row.get("case_done"):
                latest_case_results[row.get("case_id")] = row
        answered_by_model = Counter(
            row.get("model_requested")
            for row in latest_case_results.values()
            if row.get("status") == "answered"
        )
        failures_by_status = Counter(
            row.get("status")
            for row in latest_case_results.values()
            if row.get("status") != "answered"
        )
        report["fallback"] = {
            "completed_cases": len(latest_case_results),
            "answered": sum(row.get("status") == "answered" for row in latest_case_results.values()),
            "unanswered": sum(row.get("status") != "answered" for row in latest_case_results.values()),
            "answered_by_model": dict(sorted(answered_by_model.items())),
            "unanswered_by_status": dict(sorted(failures_by_status.items())),
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--scores", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = build_report(read_jsonl(args.runs), load_scores(args.scores))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
