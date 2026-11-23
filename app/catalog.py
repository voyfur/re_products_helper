from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

from app.product_context import Attribute, LanguageCard, Product


LANGUAGE_IDS = {"ru": 1, "uk": 6}

SEARCH_PRODUCTS_SQL = """
SELECT
    p.product_id,
    p.model,
    p.sku,
    languages.language_id,
    pd.name,
    pd.description,
    ss.name AS stock_label,
    pa.attribute_id,
    ad.name AS attribute_name,
    pa.text AS attribute_value
FROM (
    SELECT product_id
    FROM oc_product
    WHERE model = %s OR sku = %s
    ORDER BY product_id
    LIMIT 2
) AS candidates
JOIN oc_product AS p ON p.product_id = candidates.product_id
CROSS JOIN (
    SELECT %s AS language_id
    UNION ALL
    SELECT %s AS language_id
) AS languages
LEFT JOIN oc_product_description AS pd
    ON pd.product_id = p.product_id AND pd.language_id = languages.language_id
LEFT JOIN oc_stock_status AS ss
    ON ss.stock_status_id = p.stock_status_id AND ss.language_id = languages.language_id
LEFT JOIN oc_product_attribute AS pa
    ON pa.product_id = p.product_id
   AND pa.language_id = languages.language_id
   AND TRIM(pa.text) <> ''
LEFT JOIN oc_attribute_description AS ad
    ON ad.attribute_id = pa.attribute_id AND ad.language_id = languages.language_id
ORDER BY p.product_id, languages.language_id, pa.attribute_id
"""


@dataclass(frozen=True)
class CatalogSettings:
    host: str
    port: int
    database: str
    user: str
    password: str = field(repr=False)
    ssl_ca: Path = Path("")


def create_mysql_connection(
    settings: CatalogSettings,
    *,
    connector: Callable[..., Any] | None = None,
) -> Any:
    if not settings.host or not settings.database or not settings.user or not settings.password:
        raise ValueError("mysql_configuration_incomplete")
    if not settings.ssl_ca.is_file():
        raise ValueError("mysql_ca_unavailable")
    if connector is None:
        import mysql.connector

        connector = mysql.connector.connect
    return connector(
        host=settings.host,
        port=settings.port,
        database=settings.database,
        user=settings.user,
        password=settings.password,
        ssl_ca=str(settings.ssl_ca),
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        allow_local_infile=False,
        connection_timeout=5,
    )


def create_mysql_connection_factory(
    settings: CatalogSettings,
    *,
    pool_size: int = 5,
    connector: Callable[..., Any] | None = None,
) -> Callable[[], Any]:
    if not settings.host or not settings.database or not settings.user or not settings.password:
        raise ValueError("mysql_configuration_incomplete")
    if not settings.ssl_ca.is_file():
        raise ValueError("mysql_ca_unavailable")

    if connector is not None or pool_size <= 1:
        return lambda: create_mysql_connection(settings, connector=connector)

    try:
        from mysql.connector.pooling import MySQLConnectionPool

        pool = MySQLConnectionPool(
            pool_name="product_qa_catalog",
            pool_size=pool_size,
            pool_reset_session=True,
            host=settings.host,
            port=settings.port,
            database=settings.database,
            user=settings.user,
            password=settings.password,
            ssl_ca=str(settings.ssl_ca),
            ssl_verify_cert=True,
            ssl_verify_identity=True,
            allow_local_infile=False,
            connection_timeout=5,
        )
        return pool.get_connection
    except Exception:
        return lambda: create_mysql_connection(settings, connector=connector)


class OpenCartCatalog:
    def __init__(self, connection_factory: Callable[[], Any]):
        self.connection_factory = connection_factory

    @contextmanager
    def connection_scope(self) -> Iterator[Any]:
        connection = self.connection_factory()
        try:
            yield connection
        finally:
            connection.close()

    def search_products(
        self, article: str, *, connection: Any | None = None
    ) -> list[Product]:
        article = article.strip()
        if not article:
            return []
        if connection is None:
            with self.connection_scope() as active:
                return self.search_products(article, connection=active)

        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                SEARCH_PRODUCTS_SQL,
                (article, article, *LANGUAGE_IDS.values()),
            )
            rows = cursor.fetchall()
            grouped: dict[int, dict[str, list[dict[str, Any]]]] = {}
            first_rows: dict[int, dict[str, Any]] = {}
            language_by_id = {
                language_id: language for language, language_id in LANGUAGE_IDS.items()
            }
            for row in rows:
                product_id = int(row["product_id"])
                language = language_by_id.get(row.get("language_id"))
                if language is None:
                    continue
                first_rows.setdefault(product_id, row)
                grouped.setdefault(product_id, {}).setdefault(language, []).append(row)

            products: list[Product] = []
            for product_id, language_rows in grouped.items():
                first = first_rows[product_id]
                languages = {
                    language: card
                    for language in LANGUAGE_IDS
                    if (
                        card := self._language_card(
                            language, language_rows.get(language, [])
                        )
                    ) is not None
                }
                products.append(
                    Product(
                        product_id=product_id,
                        article=article,
                        model=first.get("model"),
                        sku=first.get("sku"),
                        languages=languages,
                    )
                )
            return products
        finally:
            if cursor is not None:
                cursor.close()

    @staticmethod
    def _language_card(
        language: str, rows: list[dict[str, Any]]
    ) -> LanguageCard | None:
        if not rows:
            return None
        first = rows[0]
        attributes = tuple(
            Attribute(name=row["attribute_name"], value=row["attribute_value"])
            for row in rows
            if row.get("attribute_id") is not None
            and row.get("attribute_name")
            and row.get("attribute_value")
        )
        name = first.get("name")
        description = first.get("description")
        stock_label = first.get("stock_label")
        if not (name or description or stock_label or attributes):
            return None
        return LanguageCard(
            language=language,
            name=name,
            description=description,
            attributes=attributes,
            stock_label=stock_label,
        )
