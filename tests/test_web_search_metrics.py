from scripts import report_web_search_latency
from app.journal import Journal


def test_latency_report_prints_aggregates_without_attempt_details(tmp_path, monkeypatch, capsys):
    journal_path = tmp_path / "journal.sqlite3"
    journal = Journal(journal_path)
    for index, status, search_latency, total_latency in (
        (1, "skipped", None, 100),
        (2, "used", 40, 200),
        (3, "failed", 10, 300),
    ):
        attempt = journal.create_attempt(
            product_id=index,
            article=f"private-article-{index}",
            model=f"private-model-{index}",
            sku=f"private-sku-{index}",
            product_name=f"private-name-{index}",
            question=f"private-question-{index}",
        )
        journal.update_search_metadata(
            attempt.attempt_id,
            status=status,
            provider="tavily" if status != "skipped" else None,
            search_latency_ms=search_latency,
            total_latency_ms=total_latency,
            sources=[
                {
                    "source_type": "manufacturer",
                    "title": f"private-title-{index}",
                    "domain": "private-domain.example",
                    "url": f"https://private-domain.example/{index}",
                    "fetched_at": "2026-11-19T12:00:00Z",
                    "match_basis": "exact_sku",
                }
            ],
        )
        journal.complete_attempt(attempt.attempt_id, f"private-answer-{index}")

    monkeypatch.setattr(
        "sys.argv",
        ["report_web_search_latency.py", "--journal", str(journal_path)],
    )

    assert report_web_search_latency.main() == 0
    output = capsys.readouterr().out

    assert "attempts=3" in output
    assert "search_use_share_percent=66.7" in output
    assert "end_to_end_p50_ms=200" in output
    assert "end_to_end_p95_ms=300" in output
    assert "search_p50_ms=10" in output
    assert "search_p95_ms=40" in output
    assert "private-article" not in output
    assert "private-question" not in output
    assert "private-answer" not in output
    assert "private-domain.example" not in output
