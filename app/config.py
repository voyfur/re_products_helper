from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from app.catalog import CatalogSettings


def _secret(value_name: str, file_name: str) -> str | None:
    file_path = os.environ.get(file_name)
    if file_path:
        try:
            value = Path(file_path).read_text(encoding="utf-8").strip()
            return value or None
        except OSError:
            return None
    value = os.environ.get(value_name, "").strip()
    return value or None


@dataclass(frozen=True)
class Settings:
    journal_path: Path
    mysql: CatalogSettings = field(repr=False)
    openai_api_key: str | None = field(repr=False)
    tavily_api_key: str | None = field(repr=False)
    integration_api_key: str | None = field(repr=False)

    @classmethod
    def from_env(cls) -> "Settings":
        if os.environ.get("TAVILY_API_KEY") and os.environ.get("TAVILY_API_KEY_FILE"):
            raise ValueError("tavily_configuration_invalid")
        if os.environ.get("PRODUCT_QA_API_KEY") and os.environ.get("PRODUCT_QA_API_KEY_FILE"):
            raise ValueError("product_qa_api_key_configuration_invalid")
        try:
            port = int(os.environ.get("MYSQL_PORT", "3306"))
        except ValueError:
            raise ValueError("mysql_configuration_invalid") from None
        return cls(
            journal_path=Path(os.environ.get("JOURNAL_PATH", "var/qa-journal.sqlite3")),
            mysql=CatalogSettings(
                host=os.environ.get("MYSQL_HOST", "").strip(),
                port=port,
                database=os.environ.get("MYSQL_DATABASE", "").strip(),
                user=os.environ.get("MYSQL_USER", "").strip(),
                password=_secret("MYSQL_PASSWORD", "MYSQL_PASSWORD_FILE") or "",
                ssl_ca=Path(os.environ.get("MYSQL_SSL_CA", "")),
            ),
            openai_api_key=_secret("OPENAI_API_KEY", "OPENAI_API_KEY_FILE"),
            tavily_api_key=_secret("TAVILY_API_KEY", "TAVILY_API_KEY_FILE"),
            integration_api_key=_secret("PRODUCT_QA_API_KEY", "PRODUCT_QA_API_KEY_FILE"),
        )
