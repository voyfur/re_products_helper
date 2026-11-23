from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if not (PROJECT_ROOT / "app" / "assistant.py").is_file():
    PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))

from app.assistant import DEFAULT_PROMPT_VERSION, EXPECTED_PROMPT_HASHES, PROMPT_PATHS, load_system_prompt
from app.config import Settings
from app.main import create_app
from app.product_context import LanguageCard, Product


PRODUCT = Product(
    product_id=1,
    article="SMOKE-001",
    model="SMOKE-001",
    sku="SMOKE-001",
    languages={
        "uk": LanguageCard(
            language="uk",
            name="Тестовий товар",
            description=None,
            attributes=(),
            stock_label=None,
        )
    },
)


class _Cursor:
    def execute(self, query: str) -> None:
        if query != "SELECT 1":
            raise AssertionError("unexpected_readiness_query")

    @staticmethod
    def fetchone() -> tuple[int]:
        return (1,)

    @staticmethod
    def close() -> None:
        return None


class _Connection:
    @staticmethod
    def cursor() -> _Cursor:
        return _Cursor()


class _Catalog:
    @contextmanager
    def connection_scope(self):
        yield _Connection()

    @staticmethod
    def search_products(article: str, *, connection: Any | None = None) -> list[Product]:
        return [PRODUCT] if article == PRODUCT.article else []


class _Assistant:
    @staticmethod
    def submit(
        product: Product,
        question: str,
        *,
        request_started_at: float,
        history: Any = (),
    ) -> Any:
        return SimpleNamespace(status="succeeded", answer="Контейнер smoke-проверен.")

    @staticmethod
    def stream(
        product: Product,
        question: str,
        *,
        request_started_at: float,
        history: Any = (),
    ):
        yield {"type": "delta", "text": "Контейнер smoke-проверен."}
        yield {"type": "done"}


async def _request(app: Any, method: str, path: str, body: bytes = b"", headers=()) -> tuple[int, bytes]:
    incoming = [{"type": "http.request", "body": body, "more_body": False}]
    sent = []

    async def receive():
        if incoming:
            return incoming.pop(0)
        await asyncio.Event().wait()

    async def send(message):
        sent.append(message)

    raw_path = path.encode("ascii")
    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": raw_path,
            "query_string": b"",
            "root_path": "",
            "headers": list(headers) + [(b"host", b"127.0.0.1")],
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 8787),
        },
        receive,
        send,
    )
    start = next(item for item in sent if item["type"] == "http.response.start")
    response_body = b"".join(
        item.get("body", b"") for item in sent if item["type"] == "http.response.body"
    )
    return start["status"], response_body


def main() -> None:
    if DEFAULT_PROMPT_VERSION != "v18":
        raise AssertionError("default_prompt_version_mismatch")
    for version, expected_hash in EXPECTED_PROMPT_HASHES.items():
        prompt = load_system_prompt(version)
        actual_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if actual_hash != expected_hash or version not in PROMPT_PATHS:
            raise AssertionError("prompt_hash_mismatch")

    key_name = "PRODUCT_QA_API_KEY"
    original_key = os.environ.get(key_name)
    os.environ[key_name] = "synthetic-container-smoke-key"
    try:
        settings = Settings.from_env()
    finally:
        if original_key is None:
            os.environ.pop(key_name, None)
        else:
            os.environ[key_name] = original_key

    app = create_app(
        catalog=_Catalog(),
        journal=object(),
        assistant=_Assistant(),
        settings=settings,
    )
    health_status, _ = asyncio.run(_request(app, "GET", "/health"))
    ready_status, _ = asyncio.run(_request(app, "GET", "/ready"))
    payload = json.dumps(
        {"article": PRODUCT.article, "question": "Який це товар?"},
        ensure_ascii=False,
    ).encode("utf-8")
    headers = [
        (b"authorization", b"Bearer synthetic-container-smoke-key"),
        (b"content-type", b"application/json"),
    ]
    ask_status, ask_body = asyncio.run(
        _request(
            app,
            "POST",
            "/api/v1/ask",
            payload,
            headers=headers,
        )
    )
    stream_status, stream_body = asyncio.run(
        _request(
            app,
            "POST",
            "/api/v1/ask/stream",
            payload,
            headers=headers,
        )
    )
    stream_text = stream_body.decode("utf-8")
    if (health_status, ready_status, ask_status, stream_status) != (200, 200, 200, 200):
        raise AssertionError("container_route_smoke_failed")
    if json.loads(ask_body) != {
        "status": "succeeded",
        "answer": "Контейнер smoke-проверен.",
    }:
        raise AssertionError("container_json_contract_failed")
    if not all(f"event: {event}\n" in stream_text for event in ("start", "delta", "done")):
        raise AssertionError("container_stream_contract_failed")
    if "attempt_id" in stream_text or "source_metadata" in stream_text:
        raise AssertionError("container_stream_private_data_leaked")
    print(
        "container_smoke=passed prompts=v12,v13,v14,v15,v16,v17,v18 "
        "health=200 ready=200 ask_json=200 ask_stream=200"
    )


if __name__ == "__main__":
    main()
