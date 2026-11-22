from contextlib import contextmanager

import pytest

from app.journal import JournalAttempt
from app.product_context import Attribute, LanguageCard, Product
from app.main import create_app


def sample_product():
    return Product(
        product_id=586,
        article="RE0731",
        model="RE0731",
        sku="20004101",
        languages={
            "ru": LanguageCard(
                language="ru",
                name="Шейкер",
                description="<p>500 мл</p>",
                attributes=(Attribute("Объём", "500 мл"),),
                stock_label="Нет в наличии",
            ),
            "uk": LanguageCard(
                language="uk",
                name="Шейкер",
                description="<p>500 мл</p>",
                attributes=(Attribute("Об’єм", "500 мл"),),
                stock_label="Немає в наявності",
            ),
        },
    )


class FakeCatalog:
    def __init__(self, products=None):
        self.products = products or [sample_product()]
        self.searches = []
        self.readiness_queries = []
        self.readiness_error = None
        self.readiness_cursor_closed = False

    @contextmanager
    def connection_scope(self):
        yield self

    def cursor(self):
        if self.readiness_error is not None:
            raise self.readiness_error
        return FakeReadinessCursor(self.readiness_queries, self)

    def search_products(self, article, *, connection=None):
        self.searches.append((article, connection))
        key = article.casefold()
        return [
            product for product in self.products
            if key in {
                (product.model or "").casefold(),
                (product.sku or "").casefold(),
                product.article.casefold(),
            }
        ]


class FakeReadinessCursor:
    def __init__(self, queries, catalog):
        self.queries = queries
        self.catalog = catalog

    def execute(self, query):
        self.queries.append(query)

    def fetchone(self):
        return (1,)

    def close(self):
        self.catalog.readiness_cursor_closed = True


class FakeJournal:
    pass


class FakeAssistant:
    def __init__(self):
        self.calls = []
        self.call_kwargs = []
        self.request_started_at = None

    def submit(self, product, question, **kwargs):
        self.calls.append((product, question))
        self.call_kwargs.append(kwargs)
        self.request_started_at = kwargs.get("request_started_at")
        return JournalAttempt(
            attempt_id=1,
            submitted_at="2026-11-18T12:00:00+00:00",
            product_id=product.product_id,
            article=product.article,
            product_model=product.model,
            product_sku=product.sku,
            product_name=product.languages["uk"].name,
            question=question,
            status="succeeded",
            answer="Відповідь за даними картки.",
            error_code=None,
            model_name="gpt-6-luna",
            prompt_version="v18",
        )


@pytest.fixture
def harness():
    from fastapi.testclient import TestClient

    catalog = FakeCatalog()
    assistant = FakeAssistant()
    app = create_app(catalog=catalog, journal=FakeJournal(), assistant=assistant)
    return type("Harness", (), {
        "app": app,
        "client": TestClient(app),
        "catalog": catalog,
        "assistant": assistant,
    })()
