from app.product_context import Attribute, LanguageCard, Product
from app.search_evidence import (
    SearchTopic,
    SourceRule,
    approved_domains_for_topic,
    build_search_query,
    filter_search_results,
)
from app.search_provider import SearchResult


def test_recurring_review_theme_does_not_include_single_name_author_prefix():
    product = Product(
        product_id=586,
        article="RE0731",
        model="RE0731",
        sku="RE0731",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Sponser Classic Shaker 500 ml",
                description=None,
                attributes=(
                    Attribute("Brand", "Sponser"),
                    Attribute("Volume", "500 ml"),
                ),
                stock_label=None,
            )
        },
    )
    registry = {
        "reviews-a.example": SourceRule("review_platform", independence_group="a"),
        "reviews-b.example": SourceRule("review_platform", independence_group="b"),
    }
    results = [
        SearchResult(
            title="Sponser Classic Shaker 500 ml",
            url="https://reviews-a.example/product/sponser-classic-shaker-500-ml",
            content=(
                "Олена: Смак приємний. Email reviewer@example.com, phone "
                "+380 50 123 45 67, @reviewer."
            ),
        ),
        SearchResult(
            title="Sponser Classic Shaker 500 ml",
            url="https://reviews-b.example/product/sponser-classic-shaker-500-ml",
            content="Смак хороший.",
        ),
    ]

    bundle = filter_search_results(
        product,
        results,
        registry=registry,
        source_types={"review_platform"},
    )

    assert len(bundle.model_evidence) == 2
    assert all("Олена" not in item.excerpt for item in bundle.model_evidence)
    assert all("reviewer@example.com" not in item.excerpt for item in bundle.model_evidence)
    assert all("380 50 123 45 67" not in item.excerpt for item in bundle.model_evidence)
    assert all("@reviewer" not in item.excerpt for item in bundle.model_evidence)


def test_internet_search_query_uses_name_without_catalog_identifiers():
    product = Product(
        product_id=587,
        article="RE0732",
        model="RE0732",
        sku="20004101",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Шейкер 500 мл",
                description=None,
                attributes=(),
                stock_label=None,
            )
        },
    )

    query = build_search_query(product, SearchTopic.PRODUCT_FACTS)

    assert query.startswith("Шейкер 500 мл ")
    assert "20004101" not in query
    assert "RE0732" not in query


def test_product_name_match_is_accepted_without_catalog_identifiers_in_url():
    product = Product(
        product_id=587,
        article="RE0732",
        model="RE0732",
        sku="20004101",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Шейкер 500 мл",
                description=None,
                attributes=(),
                stock_label=None,
            )
        },
    )

    bundle = filter_search_results(
        product,
        [
            SearchResult(
                title="Шейкер 500 мл",
                url="https://manufacturer.example/products/item-42",
                content="Місткість — 500 мл.",
            )
        ],
        registry={"manufacturer.example": SourceRule("manufacturer")},
        source_types={"manufacturer"},
    )

    assert len(bundle.model_evidence) == 1
    assert bundle.provenance[0].url == "https://manufacturer.example/products/item-42"
    assert bundle.provenance[0].match_basis == "product_name"
    assert bundle.model_payload() == [
        {
            "source_type": "manufacturer",
            "verified_product_name": "Шейкер 500 мл",
            "excerpt": "Місткість — 500 мл.",
        }
    ]
    assert not {"title", "url", "domain", "provenance"}.intersection(
        bundle.model_payload()[0]
    )


def test_review_health_claims_are_removed_from_recurring_subjective_theme():
    product = Product(
        product_id=586,
        article="RE0731",
        model="RE0731",
        sku="RE0731",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Sponser Classic Shaker 500 ml",
                description=None,
                attributes=(
                    Attribute("Brand", "Sponser"),
                    Attribute("Volume", "500 ml"),
                ),
                stock_label=None,
            )
        },
    )
    registry = {
        "reviews-a.example": SourceRule("review_platform", independence_group="a"),
        "reviews-b.example": SourceRule("review_platform", independence_group="b"),
    }
    results = [
        SearchResult(
            title="Sponser Classic Shaker 500 ml",
            url="https://reviews-a.example/product/sponser-classic-shaker-500-ml",
            content="Смак приємний. Допомогло від болю у суглобах.",
        ),
        SearchResult(
            title="Sponser Classic Shaker 500 ml",
            url="https://reviews-b.example/product/sponser-classic-shaker-500-ml",
            content="Смак хороший. Лечит воспаление суставов.",
        ),
    ]

    bundle = filter_search_results(
        product,
        results,
        registry=registry,
        source_types={"review_platform"},
    )

    assert len(bundle.model_evidence) == 2
    assert all("болю" not in item.excerpt.lower() for item in bundle.model_evidence)
    assert all("воспаление" not in item.excerpt.lower() for item in bundle.model_evidence)
    assert all("смак" in item.excerpt.lower() for item in bundle.model_evidence)


def test_review_aliases_on_the_same_platform_do_not_count_as_independent():
    product = Product(
        product_id=586,
        article="RE0731",
        model="RE0731",
        sku="RE0731",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Sponser Classic Shaker 500 ml",
                description=None,
                attributes=(
                    Attribute("Brand", "Sponser"),
                    Attribute("Volume", "500 ml"),
                ),
                stock_label=None,
            )
        },
    )
    registry = {
        "reviews-a.example": SourceRule("review_platform", independence_group="same-platform"),
        "reviews-b.example": SourceRule("review_platform", independence_group="same-platform"),
    }
    results = [
        SearchResult(
            title="Sponser Classic Shaker 500 ml",
            url="https://reviews-a.example/product/sponser-classic-shaker-500-ml",
            content="Смак приємний.",
        ),
        SearchResult(
            title="Sponser Classic Shaker 500 ml",
            url="https://reviews-b.example/product/sponser-classic-shaker-500-ml",
            content="Смак хороший.",
        ),
    ]

    bundle = filter_search_results(
        product,
        results,
        registry=registry,
        source_types={"review_platform"},
    )

    assert bundle.model_evidence == ()
    assert bundle.provenance == ()


def test_generic_product_name_and_catalog_article_do_not_match_external_source():
    product = Product(
        product_id=586,
        article="RE0731",
        model="RE0731",
        sku=None,
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Шейкер",
                description=None,
                attributes=(),
                stock_label=None,
            )
        },
    )
    result = SearchResult(
        title="Шейкер RE0731",
        url="https://manufacturer.example/products/RE0731",
        content="Місткість 500 мл.",
    )

    bundle = filter_search_results(
        product,
        [result],
        registry={"manufacturer.example": SourceRule("manufacturer")},
        source_types={"manufacturer"},
    )

    assert bundle.model_evidence == ()
    assert bundle.provenance == ()


def test_factual_excerpt_removes_price_and_purchase_fragments():
    product = Product(
        product_id=587,
        article="RE0732",
        model="RE0732",
        sku="RE0732",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Шейкер 500 мл",
                description=None,
                attributes=(),
                stock_label=None,
            )
        },
    )
    result = SearchResult(
        title="Шейкер 500 мл",
        url="https://manufacturer.example/products/item-73",
        content="Ціна 500 грн. Об’єм дорівнює 500 мл. Замовив учора.",
    )

    bundle = filter_search_results(
        product,
        [result],
        registry={"manufacturer.example": SourceRule("manufacturer")},
        source_types={"manufacturer"},
    )

    assert len(bundle.model_evidence) == 1
    assert "500 грн" not in bundle.model_evidence[0].excerpt
    assert "Замовив" not in bundle.model_evidence[0].excerpt
    assert "500 мл" in bundle.model_evidence[0].excerpt


def test_factual_domains_are_inferred_from_a_known_brand_in_product_name():
    product = Product(
        product_id=588,
        article="RE0732",
        model="RE0732",
        sku="20004101",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Шейкер Sponser Original Shaker, 600 мл",
                description=None,
                attributes=(),
                stock_label=None,
            )
        },
    )

    domains = approved_domains_for_topic(product, SearchTopic.PRODUCT_FACTS)

    assert "sponser.com" in domains
    assert "sponser.com.ua" in domains
    assert "nutrend.com.ua" not in domains


def test_product_name_tokens_match_reordered_title_and_reject_wrong_capacity():
    product = Product(
        product_id=588,
        article="RE0732",
        model="RE0732",
        sku="20004101",
        languages={
            "uk": LanguageCard(
                language="uk",
                name="Шейкер Sponser Original Shaker, 600 мл",
                description=None,
                attributes=(),
                stock_label=None,
            )
        },
    )
    registry = {
        "manufacturer.example": SourceRule(
            "manufacturer", frozenset({"Sponser"})
        )
    }
    results = [
        SearchResult(
            title="SPONSER Original Shaker 600 ml",
            url="https://manufacturer.example/products/original-shaker-600-ml",
            content="Виготовлений із харчового пластику.",
        ),
        SearchResult(
            title="SPONSER Original Shaker 750 ml",
            url="https://manufacturer.example/products/original-shaker-750-ml",
            content="Виготовлений із харчового пластику.",
        ),
    ]

    bundle = filter_search_results(
        product,
        results,
        registry=registry,
        source_types={"manufacturer"},
    )

    assert len(bundle.model_evidence) == 1
    assert bundle.model_evidence[0].excerpt == "Виготовлений із харчового пластику."
    assert bundle.model_payload()[0]["verified_product_name"] == (
        "Шейкер Sponser Original Shaker, 600 мл"
    )
    assert bundle.provenance[0].url.endswith("original-shaker-600-ml")
    assert bundle.provenance[0].match_basis == "product_name"


def test_official_brand_host_matches_translated_exact_flavor_and_package():
    product = Product(
        product_id=589,
        article="RE89157",
        model="RE89157",
        sku=None,
        languages={
            "uk": LanguageCard(
                language="uk",
                name=(
                    "Сироватковий протеїн PureGold Compact Whey Gold "
                    "(солона карамель) 500 г"
                ),
                description=None,
                attributes=(),
                stock_label=None,
            )
        },
    )
    registry = {
        "puregold.example": SourceRule(
            "manufacturer", frozenset({"PureGold"})
        )
    }
    results = [
        SearchResult(
            title="Compact Whey Gold Salted Caramel 500 g",
            url="https://puregold.example/products/compact-whey-gold-salted-caramel-500g",
            content="Ingredients: whey protein and cocoa-free flavoring.",
        ),
        SearchResult(
            title="Compact Whey Gold Chocolate 500 g",
            url="https://puregold.example/products/compact-whey-gold-chocolate-500g",
            content="Ingredients: whey protein and chocolate flavoring.",
        ),
    ]

    bundle = filter_search_results(
        product,
        results,
        registry=registry,
        source_types={"manufacturer"},
    )

    assert len(bundle.model_evidence) == 1
    assert bundle.provenance[0].url.endswith(
        "compact-whey-gold-salted-caramel-500g"
    )
    assert bundle.provenance[0].match_basis == "product_name"
