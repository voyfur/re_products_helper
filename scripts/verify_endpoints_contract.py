#!/usr/bin/env python3
"""
Скрипт повної верифікації HTTP-ендпоінтів згідно з офіційною документацією
(docs/api/product-qa-integration.md та docs/api/product-qa-v1.yaml).
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

# Додаємо корінь проєкту в sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.catalog import CatalogSettings
from app.config import Settings
from app.journal import Journal
from app.main import create_app
from app.product_context import Attribute, LanguageCard, Product


# Створюємо тестові товари
SINGLE_PRODUCT = Product(
    product_id=586,
    article="RE0731",
    model="RE0731",
    sku="20004101",
    languages={
        "uk": LanguageCard(
            language="uk",
            name="Шейкер 500 мл",
            description="Зручний шейкер для спортивного харчування.",
            attributes=(Attribute("Об’єм", "500 мл"),),
            stock_label="Є в наявності",
        )
    },
)

AMBIGUOUS_PRODUCT_1 = Product(
    product_id=101,
    article="AMBIGUOUS-01",
    model="AMBIGUOUS-01",
    sku="1001",
    languages={"uk": LanguageCard("uk", "Товар Варіант 1", None, (), None)},
)

AMBIGUOUS_PRODUCT_2 = Product(
    product_id=102,
    article="AMBIGUOUS-01",
    model="AMBIGUOUS-01",
    sku="1002",
    languages={"uk": LanguageCard("uk", "Товар Варіант 2", None, (), None)},
)


class MockCatalog:
    def __init__(self):
        self.catalog_error: Exception | None = None

    @contextmanager
    def connection_scope(self):
        if self.catalog_error:
            raise self.catalog_error
        yield self

    def cursor(self):
        if self.catalog_error:
            raise self.catalog_error
        return MockCursor()

    def search_products(self, article: str, *, connection: Any | None = None) -> list[Product]:
        if self.catalog_error:
            raise self.catalog_error
        if article == "RE0731":
            return [SINGLE_PRODUCT]
        elif article == "AMBIGUOUS-01":
            return [AMBIGUOUS_PRODUCT_1, AMBIGUOUS_PRODUCT_2]
        return []


class MockCursor:
    def execute(self, query: str):
        if query != "SELECT 1":
            raise ValueError(f"Unexpected query: {query}")

    def fetchone(self):
        return (1,)

    def close(self):
        pass


class MockAssistant:
    def __init__(self):
        self.fail_mode = False

    def submit(self, product: Product, question: str, *, history=None, request_started_at: float | None = None, **kwargs):
        if self.fail_mode:
            raise RuntimeError("Model provider temporarily unavailable")
        return SimpleNamespace(
            attempt_id=123,
            status="succeeded",
            answer=f"Об’єм шейкера {product.article} становить 500 мл.",
        )


def verify_all_endpoints():
    print("=" * 70)
    print("ПОЧАТОК ВЕРИФІКАЦІЇ ЕНДПОІНТІВ ЗГІДНО З ДОКУМЕНТАЦІЄЮ")
    print("=" * 70)

    tmp_journal = PROJECT_ROOT / "var" / "test-verify-journal.sqlite3"
    tmp_journal.parent.mkdir(parents=True, exist_ok=True)
    if tmp_journal.exists():
        tmp_journal.unlink()

    catalog = MockCatalog()
    journal = Journal(tmp_journal)
    assistant = MockAssistant()

    API_KEY = "test-integration-secret-key"

    settings = Settings(
        journal_path=tmp_journal,
        mysql=CatalogSettings(
            host="127.0.0.1",
            port=3306,
            database="testdb",
            user="testuser",
            password="testpassword",
        ),
        openai_api_key="synthetic-openai-key",
        tavily_api_key="synthetic-tavily-key",
        integration_api_key=API_KEY,
    )

    app = create_app(catalog=catalog, journal=journal, assistant=assistant, settings=settings)
    client = TestClient(app)

    # 1. GET /health
    print("\n[1/12] Перевірка GET /health (Liveness)...")
    res = client.get("/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert res.json() == {"status": "ok"}, f"Unexpected body: {res.json()}"
    print("  -> HTTP 200 OK, body: {'status': 'ok'} [ПРОЙДЕНО]")

    # 2. GET /ready (Readiness - успіх)
    print("\n[2/12] Перевірка GET /ready (Readiness успіх)...")
    res = client.get("/ready")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert res.json() == {"status": "ready"}, f"Unexpected body: {res.json()}"
    print("  -> HTTP 200 OK, body: {'status': 'ready'} [ПРОЙДЕНО]")

    # 3. GET /ready (Readiness - недоступність каталогу)
    print("\n[3/12] Перевірка GET /ready (Readiness відмова БД)...")
    catalog.catalog_error = RuntimeError("Database connection timed out")
    res = client.get("/ready")
    assert res.status_code == 503, f"Expected 503, got {res.status_code}"
    assert res.json() == {"status": "unavailable"}, f"Unexpected body: {res.json()}"
    catalog.catalog_error = None
    print("  -> HTTP 503 Service Unavailable, body: {'status': 'unavailable'} [ПРОЙДЕНО]")

    # 4. POST /api/v1/ask - Успішний запит (HTTP 200)
    print("\n[4/12] Перевірка POST /api/v1/ask (Успішна відповідь)...")
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"article": "RE0731", "question": "Який об’єм цього шейкера?"}
    res = client.post("/api/v1/ask", headers=headers, json=payload)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    body = res.json()
    assert body.get("status") == "succeeded", f"Expected status succeeded: {body}"
    assert "Об’єм шейкера" in body.get("answer", ""), f"Unexpected answer: {body}"
    print(f"  -> HTTP 200 OK, answer: '{body['answer']}' [ПРОЙДЕНО]")

    # 5. POST /api/v1/ask - 401 Unauthorized (відсутній або хибний токен)
    print("\n[5/12] Перевірка POST /api/v1/ask (401 Unauthorized)...")
    res_no_auth = client.post("/api/v1/ask", json=payload)
    assert res_no_auth.status_code == 401, f"Expected 401, got {res_no_auth.status_code}"
    assert res_no_auth.json() == {"error": "unauthorized"}
    assert res_no_auth.headers.get("www-authenticate") == "Bearer"

    res_bad_auth = client.post(
        "/api/v1/ask",
        headers={"Authorization": "Bearer wrong-key"},
        json=payload,
    )
    assert res_bad_auth.status_code == 401, f"Expected 401, got {res_bad_auth.status_code}"
    assert res_bad_auth.json() == {"error": "unauthorized"}
    assert res_bad_auth.headers.get("www-authenticate") == "Bearer"
    print("  -> HTTP 401 Unauthorized, header WWW-Authenticate: Bearer, error: 'unauthorized' [ПРОЙДЕНО]")

    # 6. POST /api/v1/ask - 404 Product Not Found
    print("\n[6/12] Перевірка POST /api/v1/ask (404 product_not_found)...")
    res = client.post(
        "/api/v1/ask",
        headers=headers,
        json={"article": "NONEXISTENT", "question": "Який об’єм?"},
    )
    assert res.status_code == 404, f"Expected 404, got {res.status_code}"
    assert res.json() == {"error": "product_not_found"}
    print("  -> HTTP 404 Not Found, error: 'product_not_found' [ПРОЙДЕНО]")

    # 7. POST /api/v1/ask - 409 Product Selection Required (неоднозначний артикул)
    print("\n[7/12] Перевірка POST /api/v1/ask (409 product_selection_required)...")
    res = client.post(
        "/api/v1/ask",
        headers=headers,
        json={"article": "AMBIGUOUS-01", "question": "Який склад?"},
    )
    assert res.status_code == 409, f"Expected 409, got {res.status_code}"
    assert res.json() == {"error": "product_selection_required"}
    print("  -> HTTP 409 Conflict, error: 'product_selection_required' [ПРОЙДЕНО]")

    # 8. POST /api/v1/ask - 413 Request Too Large (тіло > 16 KiB)
    print("\n[8/12] Перевірка POST /api/v1/ask (413 request_too_large)...")
    oversized_data = b"x" * 16385
    res = client.post(
        "/api/v1/ask",
        headers=headers,
        content=oversized_data,
    )
    assert res.status_code == 413, f"Expected 413, got {res.status_code}"
    assert res.json() == {"error": "request_too_large"}
    print("  -> HTTP 413 Payload Too Large, error: 'request_too_large' [ПРОЙДЕНО]")

    # 9. POST /api/v1/ask - 422 Invalid Request (зайві поля, порожні поля, надто довге питання)
    print("\n[9/12] Перевірка POST /api/v1/ask (422 invalid_request)...")
    # Додаткове поле (заборонено)
    res_extra = client.post(
        "/api/v1/ask",
        headers=headers,
        json={"article": "RE0731", "question": "Питання", "extra_field": "val"},
    )
    assert res_extra.status_code == 422
    assert res_extra.json() == {"error": "invalid_request"}

    # Питання більше 2000 символів
    res_long = client.post(
        "/api/v1/ask",
        headers=headers,
        json={"article": "RE0731", "question": "а" * 2001},
    )
    assert res_long.status_code == 422
    assert res_long.json() == {"error": "invalid_request"}
    print("  -> HTTP 422 Unprocessable Entity, error: 'invalid_request' [ПРОЙДЕНО]")

    # 10. POST /api/v1/ask - 429 Rate Limited (перевищення 60 запитів/хв)
    print("\n[10/12] Перевірка POST /api/v1/ask (429 rate_limited)...")
    rate_limit_settings = Settings(
        journal_path=tmp_journal,
        mysql=settings.mysql,
        openai_api_key=settings.openai_api_key,
        tavily_api_key=settings.tavily_api_key,
        integration_api_key="dedicated-rate-limit-key",
    )
    rate_limit_client = TestClient(create_app(catalog=catalog, journal=journal, assistant=assistant, settings=rate_limit_settings))
    rl_headers = {"Authorization": "Bearer dedicated-rate-limit-key", "Content-Type": "application/json"}

    # Робимо рівно 60 запитів з цим ключем
    for i in range(60):
        r = rate_limit_client.post("/api/v1/ask", headers=rl_headers, json=payload)
        assert r.status_code == 200, f"Request {i+1} failed with {r.status_code}"
    # 61-й запит має отримати 429
    res_limited = rate_limit_client.post("/api/v1/ask", headers=rl_headers, json=payload)
    assert res_limited.status_code == 429, f"Expected 429, got {res_limited.status_code}"
    assert res_limited.json() == {"error": "rate_limited"}
    assert res_limited.headers.get("retry-after") == "60"
    print("  -> HTTP 429 Too Many Requests, Retry-After: 60, error: 'rate_limited' [ПРОЙДЕНО]")

    # 11. POST /api/v1/ask - 502 Answer Unavailable (збій моделі)
    print("\n[11/12] Перевірка POST /api/v1/ask (502 answer_unavailable)...")
    assistant.fail_mode = True
    # Використовуємо інший ключ для обходу рейтобмеження в тесті
    fresh_settings = Settings(
        journal_path=tmp_journal,
        mysql=settings.mysql,
        openai_api_key=settings.openai_api_key,
        tavily_api_key=settings.tavily_api_key,
        integration_api_key="fresh-key-for-502",
    )
    client_502 = TestClient(create_app(catalog=catalog, journal=journal, assistant=assistant, settings=fresh_settings))
    res_502 = client_502.post(
        "/api/v1/ask",
        headers={"Authorization": "Bearer fresh-key-for-502"},
        json=payload,
    )
    assert res_502.status_code == 502, f"Expected 502, got {res_502.status_code}"
    assert res_502.json() == {"error": "answer_unavailable"}
    assistant.fail_mode = False
    print("  -> HTTP 502 Bad Gateway, error: 'answer_unavailable' [ПРОЙДЕНО]")

    # 12. POST /api/v1/ask - 503 Catalog Unavailable (збій БД)
    print("\n[12/12] Перевірка POST /api/v1/ask (503 catalog_unavailable)...")
    catalog.catalog_error = RuntimeError("MySQL lost connection")
    fresh_settings_503 = Settings(
        journal_path=tmp_journal,
        mysql=settings.mysql,
        openai_api_key=settings.openai_api_key,
        tavily_api_key=settings.tavily_api_key,
        integration_api_key="fresh-key-for-503",
    )
    client_503 = TestClient(create_app(catalog=catalog, journal=journal, assistant=assistant, settings=fresh_settings_503))
    res_503 = client_503.post(
        "/api/v1/ask",
        headers={"Authorization": "Bearer fresh-key-for-503"},
        json=payload,
    )
    assert res_503.status_code == 503, f"Expected 503, got {res_503.status_code}"
    assert res_503.json() == {"error": "catalog_unavailable"}
    catalog.catalog_error = None
    print("  -> HTTP 503 Service Unavailable, error: 'catalog_unavailable' [ПРОЙДЕНО]")

    # Очистка тимчасового журналу
    if tmp_journal.exists():
        tmp_journal.unlink()

    print("\n" + "=" * 70)
    print("УСІ 12 СЦЕНАРІЇВ ПОВНІСТЮ ВІДПОВІДАЮТЬ ДОКУМЕНТАЦІЇ ТА УСПІШНО ПРОЙДЕНІ!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(verify_all_endpoints())
