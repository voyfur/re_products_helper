#!/usr/bin/env python3
"""Validate product QA fixtures, bilingual pairs, holdout separation, and source links."""

import argparse
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


PRODUCTS = ("RE89157", "RE1687", "RE0731")
LANGUAGES = ("ru", "uk")
BASE_REQUIRED_CATEGORIES = {
    "RE89157": {"fact_retrieval", "conflict", "availability", "scope_injection", "instruction", "abstention", "missing_data"},
    "RE1687": {"fact_retrieval", "historical_fact", "conflict", "availability", "scope_injection", "missing_data"},
    "RE0731": {"fact_retrieval", "availability", "scope_injection", "abstention", "missing_data"},
}
HOLDOUT_REQUIRED_CATEGORIES = {
    "RE89157": {"fact_retrieval", "conflict", "availability", "scope_injection"},
    "RE1687": {"historical_fact", "conflict", "missing_data", "availability", "scope_injection"},
    "RE0731": {"fact_retrieval", "partial_answer", "availability", "missing_data", "scope_injection"},
}
GUARDRAIL_REQUIRED_CATEGORIES = {
    product: {
        "abusive_product_query",
        "abuse_only_redirect",
        "off_topic_nonsense",
        "prompt_extraction_with_product_query",
        "customer_data_request",
    }
    for product in PRODUCTS
}
GUARDRAIL_CANARY_TAG = "synthetic_canary_disclosure"
NUMBER_TOKEN = re.compile(r"(?<![A-Za-zА-Яа-я0-9])\d+(?:[.,]\d+)?")
NUMBER_UNIT_TOKEN = re.compile(
    r"(?<![A-Za-zА-Яа-я0-9])(?P<number>\d+(?:[.,]\d+)?)\s*"
    r"(?P<unit>(?:мг|mg)(?:\s+(?:натрия|натрію|sodium))?\s+(?:на|per)\s+(?:литр|літр|liter)|"
    r"(?:мг|mg)\s*/\s*(?:л|l)|ккал|kcal|мг|mg|мл|ml|г|g|"
    r"таблеток|таблетк(?:а|и|у|ой|ах))"
    r"(?![A-Za-zА-Яа-я0-9])",
    re.IGNORECASE,
)
REQUIRED_CASE_FIELDS = (
    "id",
    "pair_id",
    "product",
    "context_id",
    "language",
    "category",
    "question",
    "expected_behavior",
    "must_cover",
    "must_not_claim",
    "critical_fail_tags",
    "source_ref",
)


def normalized_number(value):
    try:
        return format(Decimal(value.replace(",", ".")).normalize(), "f")
    except InvalidOperation:
        return value


def numeric_tokens(value):
    return {normalized_number(match.group(0)) for match in NUMBER_TOKEN.finditer(value)}


def number_unit_pairs(value):
    pairs = set()
    for match in NUMBER_UNIT_TOKEN.finditer(value):
        unit = re.sub(r"\s+", "", match.group("unit")).lower()
        if unit in {"мг/л", "mg/l"} or "литр" in unit or "літр" in unit or "liter" in unit:
            canonical_unit = "mg_per_liter"
        elif unit in {"ккал", "kcal"}:
            canonical_unit = "kcal"
        elif unit in {"мг", "mg"}:
            canonical_unit = "mg"
        elif unit in {"мл", "ml"}:
            canonical_unit = "ml"
        elif unit in {"г", "g"}:
            canonical_unit = "g"
        else:
            canonical_unit = "tablet_count"
        pairs.add((normalized_number(match.group("number")), canonical_unit))
    return pairs


def read_jsonl(path):
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: invalid JSON: {exc.msg}") from exc
    return rows


def validate_rows(rows, label, expected_per_product, expected_per_language):
    errors = []
    seen_ids = set()
    pairs = defaultdict(list)
    for index, row in enumerate(rows, 1):
        missing = [field for field in REQUIRED_CASE_FIELDS if field not in row]
        if missing:
            errors.append(f"{label} row {index}: missing fields {', '.join(missing)}")
            continue
        case_id = row["id"]
        if case_id in seen_ids:
            errors.append(f"{label}: duplicate case id {case_id}")
        seen_ids.add(case_id)
        if row["product"] not in PRODUCTS:
            errors.append(f"{label} {case_id}: unknown product {row['product']}")
        if row["language"] not in LANGUAGES:
            errors.append(f"{label} {case_id}: unknown language {row['language']}")
        if row["context_id"] != f"{row['product']}_{row['language']}":
            errors.append(f"{label} {case_id}: context_id does not match product/language")
        for field in ("id", "pair_id", "category", "question", "expected_behavior", "source_ref"):
            if not isinstance(row[field], str) or not row[field].strip():
                errors.append(f"{label} {case_id}: {field} must be a non-empty string")
        for field in ("must_cover", "must_not_claim", "critical_fail_tags"):
            if not isinstance(row[field], list):
                errors.append(f"{label} {case_id}: {field} must be a list")
            elif any(not isinstance(value, str) or not value.strip() for value in row[field]):
                errors.append(f"{label} {case_id}: {field} entries must be non-empty strings")
        pairs[row["pair_id"]].append(row)

    products = Counter(row.get("product") for row in rows)
    if products != Counter({product: expected_per_product for product in PRODUCTS}):
        errors.append(f"{label}: expected {expected_per_product} cases per product, got {dict(products)}")

    product_languages = Counter((row.get("product"), row.get("language")) for row in rows)
    for product in PRODUCTS:
        for language in LANGUAGES:
            count = product_languages[(product, language)]
            if count != expected_per_language:
                errors.append(
                    f"{label}: expected {expected_per_language} {language} cases for {product}, got {count}"
                )

    for pair_id, group in pairs.items():
        if len(group) != 2 or {row.get("language") for row in group} != set(LANGUAGES):
            errors.append(f"{label}: pair {pair_id} must contain exactly one ru and one uk case")
            continue
        if len({row.get("product") for row in group}) != 1:
            errors.append(f"{label}: pair {pair_id} spans multiple products")
        if len({row.get("category") for row in group}) != 1:
            errors.append(f"{label}: pair {pair_id} has mismatched categories")
        tag_lists = [row.get("critical_fail_tags") for row in group]
        if all(
            isinstance(tags, list) and all(isinstance(tag, str) for tag in tags)
            for tags in tag_lists
        ) and len({tuple(sorted(set(tags))) for tags in tag_lists}) != 1:
            errors.append(f"{label}: pair {pair_id} has mismatched critical_fail_tags")
    return errors, pairs


def validate_pack(
    base_rows,
    holdout_rows,
    product_facts,
    model_contexts,
    root,
    guardrail_rows=None,
    guardrail_contexts=None,
):
    errors = []
    base_errors, base_pairs = validate_rows(base_rows, "base", 20, 10)
    holdout_errors, holdout_pairs = validate_rows(holdout_rows, "holdout", 10, 5)
    errors.extend(base_errors)
    errors.extend(holdout_errors)
    base_categories = defaultdict(set)
    for row in base_rows:
        base_categories[row.get("product")].add(row.get("category"))
    for product, required_categories in BASE_REQUIRED_CATEGORIES.items():
        missing_categories = required_categories - base_categories[product]
        if missing_categories:
            errors.append(f"base: missing required category {sorted(missing_categories)[0]} for {product}")
    named_datasets = [("base", base_rows), ("holdout", holdout_rows)]
    guardrail_pairs = {}
    if guardrail_rows is not None:
        guardrail_errors, guardrail_pairs = validate_rows(guardrail_rows, "guardrail", 10, 5)
        errors.extend(guardrail_errors)
        named_datasets.append(("guardrail", guardrail_rows))
    holdout_categories = defaultdict(set)
    for row in holdout_rows:
        holdout_categories[row.get("product")].add(row.get("category"))
    for product, required_categories in HOLDOUT_REQUIRED_CATEGORIES.items():
        missing_categories = required_categories - holdout_categories[product]
        if missing_categories:
            errors.append(
                f"holdout: missing required category {sorted(missing_categories)[0]} for {product}"
            )

    if guardrail_rows is not None:
        guardrail_categories = defaultdict(set)
        for row in guardrail_rows:
            guardrail_categories[row.get("product")].add(row.get("category"))
            critical_tags = row.get("critical_fail_tags")
            if not isinstance(critical_tags, list) or GUARDRAIL_CANARY_TAG not in critical_tags:
                errors.append(f"guardrail {row.get('id')}: missing required critical tag {GUARDRAIL_CANARY_TAG}")
        for product, required_categories in GUARDRAIL_REQUIRED_CATEGORIES.items():
            missing_categories = required_categories - guardrail_categories[product]
            if missing_categories:
                errors.append(
                    f"guardrail: missing required category {sorted(missing_categories)[0]} for {product}"
                )

    for index, (left_name, left_rows) in enumerate(named_datasets):
        left_ids = {row.get("id") for row in left_rows}
        left_pair_ids = {row.get("pair_id") for row in left_rows}
        for right_name, right_rows in named_datasets[index + 1:]:
            for duplicate in sorted(left_ids & {row.get("id") for row in right_rows}):
                errors.append(f"{left_name} and {right_name} share case id {duplicate}")
            for duplicate in sorted(left_pair_ids & {row.get("pair_id") for row in right_rows}):
                errors.append(f"{left_name} and {right_name} share pair id {duplicate}")

    facts_products = product_facts.get("products", {})
    contexts = model_contexts.get("contexts", {})
    guardrail_context_map = (guardrail_contexts or {}).get("contexts", {})
    if guardrail_rows is not None and set(guardrail_context_map) != set(contexts):
        errors.append("guardrail contexts must contain exactly the six base product-language contexts")
    for product in PRODUCTS:
        if product not in facts_products:
            errors.append(f"product facts missing {product}")
        for language in LANGUAGES:
            context_id = f"{product}_{language}"
            if context_id not in contexts or not isinstance(contexts.get(context_id), str):
                errors.append(f"model contexts missing text for {context_id}")
            elif product in facts_products:
                product_data = facts_products[product]
                model = product_data.get("model")
                sku = product_data.get("sku")
                if model and sku and f"Модель — {model}; SKU — {sku}." not in contexts[context_id]:
                    errors.append(f"model context missing verified model/SKU identity for {context_id}")
            if guardrail_rows is not None:
                guardrail_context = guardrail_context_map.get(context_id)
                base_context = contexts.get(context_id)
                if not isinstance(guardrail_context, str):
                    errors.append(f"guardrail contexts missing text for {context_id}")
                elif not isinstance(base_context, str) or not guardrail_context.startswith(
                    base_context.rstrip() + "\n\n"
                ):
                    errors.append(f"guardrail context does not preserve the base product context for {context_id}")
                elif not all(
                    marker in guardrail_context
                    for marker in (
                        "TEST_ONLY_API_KEY_DO_NOT_ECHO_",
                        "TEST_ONLY_BUYER_NAME_DO_NOT_ECHO_",
                        "TEST_ONLY_BUYER_PHONE_DO_NOT_ECHO_",
                        "@example.invalid",
                        "TEST_ONLY_ORDER_DO_NOT_ECHO_",
                    )
                ):
                    errors.append(f"guardrail context missing synthetic canary fields for {context_id}")

    all_rows = base_rows + holdout_rows + (guardrail_rows or [])
    for row in all_rows:
        source_ref = row.get("source_ref")
        if isinstance(source_ref, str) and source_ref and not (root / source_ref).is_file():
            errors.append(f"{row.get('id')}: source_ref does not exist: {source_ref}")
        product = row.get("product")
        language = row.get("language")
        if product in facts_products and language in LANGUAGES:
            facts = facts_products[product].get(language)
            if not isinstance(facts, dict):
                errors.append(f"product facts missing {product}_{language}")

    for label, rows, context_map in (
        ("base", base_rows, contexts),
        ("holdout", holdout_rows, contexts),
        ("guardrail", guardrail_rows or [], guardrail_context_map),
    ):
        for row in rows:
            context_id = row.get("context_id")
            context = context_map.get(context_id)
            if not isinstance(context, str):
                continue
            context_numbers = numeric_tokens(context)
            context_number_units = number_unit_pairs(context)
            for item in row.get("must_cover", []):
                if not isinstance(item, str):
                    continue
                for required_number in numeric_tokens(item) - context_numbers:
                    errors.append(
                        f"{label} {row.get('id')}: must_cover number {required_number} is missing from {context_id}"
                    )
                for required_pair in number_unit_pairs(item) - context_number_units:
                    errors.append(
                        f"{label} {row.get('id')}: must_cover number-unit pair "
                        f"{required_pair[0]} {required_pair[1]} is missing from {context_id}"
                    )

    if errors:
        raise ValueError("\n".join(errors))
    result = {
        "base_cases": len(base_rows),
        "base_pairs": len(base_pairs),
        "holdout_cases": len(holdout_rows),
        "holdout_pairs": len(holdout_pairs),
    }
    if guardrail_rows is not None:
        result["guardrail_cases"] = len(guardrail_rows)
        result["guardrail_pairs"] = len(guardrail_pairs)
        result["guardrail_contexts"] = len(guardrail_context_map)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path("evals/product-qa-cases.jsonl"))
    parser.add_argument("--holdout", type=Path, default=Path("evals/holdout-cases.jsonl"))
    parser.add_argument("--guardrail", type=Path, default=Path("evals/guardrail-cases.jsonl"))
    parser.add_argument("--product-facts", type=Path, default=Path("evals/product-contexts.json"))
    parser.add_argument("--model-contexts", type=Path, default=Path("evals/model-contexts.json"))
    parser.add_argument(
        "--guardrail-model-contexts",
        type=Path,
        default=Path("evals/guardrail-model-contexts.json"),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        result = validate_pack(
            read_jsonl(args.base),
            read_jsonl(args.holdout),
            json.loads(args.product_facts.read_text(encoding="utf-8")),
            json.loads(args.model_contexts.read_text(encoding="utf-8")),
            args.root.resolve(),
            read_jsonl(args.guardrail),
            json.loads(args.guardrail_model_contexts.read_text(encoding="utf-8")),
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    summary = (
        f"PASS base: {result['base_cases']} cases / {result['base_pairs']} bilingual pairs; "
        f"holdout: {result['holdout_cases']} cases / {result['holdout_pairs']} bilingual pairs"
    )
    if "guardrail_cases" in result:
        summary += (
            f"; guardrail: {result['guardrail_cases']} cases / {result['guardrail_pairs']} bilingual pairs"
            f" / {result['guardrail_contexts']} synthetic-canary contexts"
        )
    print(summary + "; sources and contexts resolve.")


if __name__ == "__main__":
    main()
