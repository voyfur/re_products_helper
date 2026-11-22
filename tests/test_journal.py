import json
import sqlite3

import pytest

from app.journal import Journal, MIGRATION_PATH


def test_failed_attempt_can_be_retried_as_a_new_record(tmp_path):
    journal = Journal(tmp_path / "journal.sqlite3")
    first = journal.create_attempt(
        product_id=586, article="RE0731", model="RE0731",
        sku="20004101", product_name="Шейкер", question="Какой объём?"
    )
    journal.fail_attempt(first.attempt_id, "provider_unavailable")
    second = journal.create_attempt(
        product_id=586, article="RE0731", model="RE0731",
        sku="20004101", product_name="Шейкер", question="Какой объём?"
    )
    journal.complete_attempt(second.attempt_id, "500 мл")

    assert journal.get_attempt(first.attempt_id).status == "error"
    assert journal.get_attempt(second.attempt_id).status == "succeeded"
    assert first.attempt_id != second.attempt_id


def test_invalid_error_code_is_rejected(tmp_path):
    journal = Journal(tmp_path / "journal.sqlite3")
    attempt = journal.create_attempt(
        product_id=586, article="RE0731", model="RE0731",
        sku="20004101", product_name="Шейкер", question="Что это?"
    )
    with pytest.raises(ValueError, match="invalid_error_code"):
        journal.fail_attempt(attempt.attempt_id, "bad-code")


def test_old_attempts_migrate_and_search_metadata_excludes_evidence_text(tmp_path):
    path = tmp_path / "journal.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.executescript(MIGRATION_PATH.read_text(encoding="utf-8"))
        connection.execute(
            """
            INSERT INTO attempts (
                submitted_at, product_id, article, product_model, product_sku,
                product_name, question, status, answer, error_code, model_name,
                prompt_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'succeeded', ?, NULL, ?, 'v12')
            """,
            (
                "2026-11-18T12:00:00+00:00",
                586,
                "RE0731",
                "RE0731",
                "20004101",
                "Шейкер",
                "Який об’єм?",
                "500 мл",
                "gpt-6-luna",
            ),
        )

    journal = Journal(path)
    old_attempt = journal.get_attempt(1)
    new_attempt = journal.create_attempt(
        product_id=586,
        article="RE0731",
        model="RE0731",
        sku="20004101",
        product_name="Шейкер",
        question="Чи зручний він?",
    )
    journal.update_search_metadata(
        new_attempt.attempt_id,
        status="used",
        provider="tavily",
        search_latency_ms=125,
        total_latency_ms=840,
        sources=[
            {
                "source_type": "review_platform",
                "title": "Шейкер 20004101",
                "domain": "fit.rozetka.com.ua",
                "url": "https://fit.rozetka.com.ua/product/20004101",
                "fetched_at": "2026-11-19T12:00:00Z",
                "match_basis": "exact_sku",
                "excerpt": "Смак хороший.",
                "author": "Synthetic Reviewer",
                "profile_url": "https://fit.rozetka.com.ua/profile/secret",
            }
        ],
    )
    saved = journal.get_attempt(new_attempt.attempt_id)

    assert old_attempt.prompt_version == "v12"
    assert old_attempt.search_status == "skipped"
    assert json.loads(old_attempt.source_metadata_json) == []
    assert saved.prompt_version == "v18"
    assert saved.search_provider == "tavily"
    assert saved.search_latency_ms == 125
    assert saved.total_latency_ms == 840
    assert json.loads(saved.source_metadata_json) == [
        {
            "source_type": "review_platform",
            "title": "Шейкер 20004101",
            "domain": "fit.rozetka.com.ua",
            "url": "https://fit.rozetka.com.ua/product/20004101",
            "fetched_at": "2026-11-19T12:00:00Z",
            "match_basis": "exact_sku",
        }
    ]
