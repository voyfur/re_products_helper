from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


MODEL_NAME = "gpt-6-luna"
PROMPT_VERSION = "v18"
MIGRATION_PATH = Path(__file__).parent / "migrations" / "001_create_qa_attempts.sql"
SEARCH_MIGRATION_PATH = Path(__file__).parent / "migrations" / "002_add_search_provenance.sql"


@dataclass(frozen=True)
class JournalAttempt:
    attempt_id: int
    submitted_at: str
    product_id: int
    article: str
    product_model: str | None
    product_sku: str | None
    product_name: str | None
    question: str
    status: str
    answer: str | None
    error_code: str | None
    model_name: str
    prompt_version: str
    search_status: str = "skipped"
    search_provider: str | None = None
    search_latency_ms: int | None = None
    total_latency_ms: int | None = None
    source_metadata_json: str = "[]"


class Journal:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path.parent.chmod(0o700)
        with self._connection() as connection:
            connection.executescript(MIGRATION_PATH.read_text(encoding="utf-8"))
            columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(attempts)")
            }
            if "search_status" not in columns:
                connection.executescript(SEARCH_MIGRATION_PATH.read_text(encoding="utf-8"))
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = FULL")
        self.path.chmod(0o600)

    def create_attempt(
        self,
        *,
        product_id: int,
        article: str,
        model: str | None,
        sku: str | None,
        product_name: str | None,
        question: str,
    ) -> JournalAttempt:
        if not question.strip():
            raise ValueError("question_required")
        if not article.strip():
            raise ValueError("article_required")
        submitted_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO attempts (
                    submitted_at, product_id, article, product_model, product_sku,
                    product_name, question, status, answer, error_code,
                    model_name, prompt_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', NULL, NULL, ?, ?)
                """,
                (
                    submitted_at,
                    product_id,
                    article,
                    model,
                    sku,
                    product_name,
                    question,
                    MODEL_NAME,
                    PROMPT_VERSION,
                ),
            )
            attempt_id = cursor.lastrowid
        return self.get_attempt(attempt_id)

    def complete_attempt(self, attempt_id: int, answer: str) -> None:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE attempts
                SET status = 'succeeded', answer = ?, error_code = NULL
                WHERE attempt_id = ? AND status = 'pending'
                """,
                (answer, attempt_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("attempt_not_pending")

    def fail_attempt(self, attempt_id: int, error_code: str) -> None:
        if not error_code or any(
            char not in "abcdefghijklmnopqrstuvwxyz0123456789_" for char in error_code
        ):
            raise ValueError("invalid_error_code")
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE attempts
                SET status = 'error', answer = NULL, error_code = ?
                WHERE attempt_id = ? AND status = 'pending'
                """,
                (error_code, attempt_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("attempt_not_pending")

    def update_search_metadata(
        self,
        attempt_id: int,
        *,
        status: str,
        provider: str | None,
        search_latency_ms: int | None,
        total_latency_ms: int | None,
        sources: list[dict[str, str]],
    ) -> None:
        import json

        if status not in {"skipped", "used", "failed"}:
            raise ValueError("search_status_invalid")
        for latency in (search_latency_ms, total_latency_ms):
            if latency is not None and latency < 0:
                raise ValueError("latency_invalid")
        allowed = {"source_type", "title", "domain", "url", "fetched_at", "match_basis"}
        safe_sources = [
            {key: value for key, value in source.items() if key in allowed and isinstance(value, str)}
            for source in sources
        ]
        source_json = json.dumps(safe_sources, ensure_ascii=False, separators=(",", ":"))
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE attempts
                SET search_status = ?, search_provider = ?, search_latency_ms = ?,
                    total_latency_ms = ?, source_metadata_json = ?
                WHERE attempt_id = ?
                """,
                (status, provider, search_latency_ms, total_latency_ms, source_json, attempt_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("attempt_not_found")

    def get_attempt(self, attempt_id: int) -> JournalAttempt | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM attempts WHERE attempt_id = ?", (attempt_id,)
            ).fetchone()
        return self._to_attempt(row) if row else None

    def list_attempts(self) -> list[JournalAttempt]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM attempts ORDER BY submitted_at DESC, attempt_id DESC"
            ).fetchall()
        return [self._to_attempt(row) for row in rows]

    @staticmethod
    def _to_attempt(row: sqlite3.Row) -> JournalAttempt:
        return JournalAttempt(**dict(row))
