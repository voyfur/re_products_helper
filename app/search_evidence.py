from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Literal, Mapping
from urllib.parse import unquote, urlsplit, urlunsplit

from .product_context import Product
from .search_provider import SearchResult


SourceType = Literal["manufacturer", "supplier", "review_platform"]
MatchBasis = Literal["product_name"]


@dataclass(frozen=True)
class SourceRule:
    source_type: SourceType
    product_brands: frozenset[str] = frozenset()
    independence_group: str | None = None


@dataclass(frozen=True)
class SourceCandidate:
    hostname: str
    source_type: SourceType
    brand: str
    status: Literal["conditional"]


# Exact hostnames approved by the user as the initial source set. No wildcard
# hosts are allowed; factual sources are restricted to their mapped brands.
_MANUFACTURER_HOSTS: tuple[tuple[tuple[str, ...], frozenset[str]], ...] = (
    (("maurten.com", "www.maurten.com"), frozenset({"Maurten"})),
    (("scienceinsport.com", "www.scienceinsport.com"), frozenset({"Science in Sport", "SiS", "Science in Sport (SiS)", "Science In Sport (SIS)", "SIS"})),
    (("guenergy.com",), frozenset({"GU Energy", "GU"})),
    (("precisionhydration.com", "www.precisionhydration.com"), frozenset({"Precision Hydration", "Precision Fuel & Hydration", "PFH"})),
    (("226ers.com", "www.226ers.com"), frozenset({"226ERS"})),
    (("sponser.com",), frozenset({"SPONSER", "Sponser"})),
    (("enervit.com", "www.enervit.com"), frozenset({"Enervit"})),
    (("humagel.com",), frozenset({"Huma", "Huma Gel", "HumaGel"})),
    (("beet-it.com", "www.beet-it.com"), frozenset({"Beet It", "Beet It Sport"})),
    (("nutrend.eu", "www.nutrend.eu"), frozenset({"NUTREND", "Nutrend"})),
    (("nutriversum.org", "www.nutriversum.org"), frozenset({"Nutriversum"})),
    (("puregoldprotein.com", "www.puregoldprotein.com"), frozenset({"PureGold", "PureGold Protein"})),
    (("myprotein.com", "www.myprotein.com"), frozenset({"Myprotein", "MyProtein"})),
    (("optimumnutrition.com", "www.optimumnutrition.com"), frozenset({"Optimum Nutrition"})),
    (("shop.biotechusa.com",), frozenset({"BioTechUSA", "BioTech USA"})),
    (("nowfoods.com", "www.nowfoods.com"), frozenset({"NOW Foods", "NOW"})),
    (("lifeextension.com", "www.lifeextension.com"), frozenset({"Life Extension"})),
    (("solgar.com", "www.solgar.com"), frozenset({"Solgar"})),
    (("swansonvitamins.com", "www.swansonvitamins.com"), frozenset({"Swanson", "Swanson Vitamins"})),
    (("naturesway.com",), frozenset({"Nature's Way", "Natures Way"})),
    (("idlo.com",), frozenset({"ЇDLO", "IDLO"})),
    (("napiy.com",), frozenset({"Napiy", "Напий"})),
    (("ryabchick.com",), frozenset({"РябChick", "Ryabchick"})),
    (("camotec.ua",), frozenset({"Camotec"})),
    (("chamoisbuttr.com", "www.chamoisbuttr.com"), frozenset({"Chamois Butt'r", "Chamois Buttr"})),
    (("triswim.org",), frozenset({"TRISWIM", "TRI SWIM"})),
    (("solrx.com", "www.solrx.com"), frozenset({"SolRX", "Sol RX"})),
)
SOURCE_REGISTRY: Mapping[str, SourceRule] = MappingProxyType(
    {
        hostname: SourceRule("manufacturer", brands)
        for hostnames, brands in _MANUFACTURER_HOSTS
        for hostname in hostnames
    }
    | {
        "sponser.com.ua": SourceRule("supplier", frozenset({"SPONSER", "Sponser"})),
        "sportpro.com.ua": SourceRule("supplier", frozenset({"SPONSER", "Sponser"})),
        "nutrend.com.ua": SourceRule("supplier", frozenset({"NUTREND", "Nutrend"})),
        "fit.rozetka.com.ua": SourceRule(
            "review_platform", independence_group="rozetka"
        ),
        "prom.ua": SourceRule("review_platform", independence_group="prom"),
    }
)
# This user-approved conditional supplier's status is self-claimed without
# reciprocal manufacturer confirmation; its rule is restricted to NUTREND.
CONDITIONAL_SOURCE_CANDIDATES = (
    SourceCandidate(
        hostname="nutrend.com.ua",
        source_type="supplier",
        brand="NUTREND",
        status="conditional",
    ),
)


class SearchTopic(str, Enum):
    PRODUCT_FACTS = "product_facts"
    INGREDIENTS = "ingredients"
    USAGE = "usage"
    SPECIFICATIONS = "specifications"
    COMPATIBILITY = "compatibility"
    BUYER_EXPERIENCE = "buyer_experience"
    HEALTH_SAFETY = "health_safety"


TOPIC_PHRASES: Mapping[SearchTopic, str] = MappingProxyType(
    {
        SearchTopic.PRODUCT_FACTS: "official product details",
        SearchTopic.INGREDIENTS: "official ingredients and composition",
        SearchTopic.USAGE: "manufacturer usage instructions",
        SearchTopic.SPECIFICATIONS: "official product specifications",
        SearchTopic.COMPATIBILITY: "official product compatibility",
        SearchTopic.BUYER_EXPERIENCE: "product buyer experience reviews",
        SearchTopic.HEALTH_SAFETY: "official label safety information",
    }
)

_SOURCE_TYPES = frozenset({"manufacturer", "supplier", "review_platform"})
_BRAND_LABELS = frozenset({"brand", "бренд", "торгова марка", "виробник"})
_HOSTNAME_RE = re.compile(
    r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}\Z",
    re.IGNORECASE,
)
_TIMESTAMP_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\Z"
)
_VARIANT_LABEL_RE = re.compile(
    r"brand|бренд|торгова марка|виробник|"
    r"flavou?r|taste|смак|вкус|аромат|"
    r"size|розмір|размер|weight|вага|масса|"
    r"volume|об['’]?єм|объем|package|упаков|pack|"
    r"formula|формул|generation|поколін|series|серія|"
    r"format|формат|type|тип|strength|дозуван|"
    r"color|colour|колір|цвет",
    re.IGNORECASE,
)
_EMAIL_RE = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[a-z]{2,}")
_PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{6,}\d)(?!\w)")
_URL_RE = re.compile(r"(?i)\bhttps?://\S+")
_PRICE_RE = re.compile(
    r"(?i)\b(?:price|cost|ціна|вартість|коштує|цена|стоимость|скидка|знижка)\b"
    r"|(?:[$€£₴₽]\s*\d)"
    r"|\b\d+(?:[.,]\d+)?\s*(?:uah|грн\.?|грив\w*|eur|євро|usd|долар\w*|gbp|руб\.?)\b"
    r"|\b\d+(?:[.,]\d+)?\s*[₴€$]"
)
_PURCHASE_RE = re.compile(
    r"(?i)\b(?:order|ordered|purchase|purchased|bought|buyer|customer|receipt|"
    r"tracking|delivery|заказ\w*|замов\w*|купив\w*|купил\w*|покуп\w*|"
    r"покупець|клієнт\w*|доставк\w*)\b"
)
_AUTHOR_RE = re.compile(
    r"(?i)\b(?:author|reviewer|review by|reviewed by|written by|profile|username|"
    r"автор|відгук від|профіль|користувач)\b"
)
_PERSON_NAME = r"(?:[A-ZА-ЯЇІЄҐ][\w’'-]+\s+){1,2}[A-ZА-ЯЇІЄҐ][\w’'-]+"
_PERSON_NAME_PREFIX_RE = re.compile(
    r"(?m)^\s*(?:"
    + _PERSON_NAME
    + r"(?:\s*[:–—-]|\s+(?i:says|said|wrote|review(?:\s+(?:of|about|for))?|"
    r"відгук\s+(?:про|щодо)))"
    + r"|[A-ZА-ЯЇІЄҐ][\w’'-]{1,30}\s*:)"
)
_PERSON_NAME_CONTEXT_RE = re.compile(
    r"(?i:\b(?:by|from|author|reviewer|reviewed by|written by|user|customer|"
    r"від автора|від користувача|автор)\b)\s+"
    + _PERSON_NAME
)
_PERSON_NAME_ACTIVITY_RE = re.compile(
    _PERSON_NAME
    + r"\s+(?i:review(?:s|ed)?|rated|rates|says|said|writes|wrote|tested|"
    r"tried|used|uses|liked|likes|loved|loves|enjoyed|enjoys|reported|reports|"
    r"recommended|recommends|found|mentioned|mentions|noted|notes|"
    r"сказав|сказала|сказавши|написав|написала|оцінив|оцінила|"
    r"зазначив|зазначила|відзначив|відзначила|поділився|поділилася)\b"
)
_STANDALONE_PERSON_NAME_RE = re.compile(r"^\s*" + _PERSON_NAME + r"\s*$")
_HANDLE_RE = re.compile(r"(?<!\w)@[A-Za-z0-9._-]{2,}")
_CONTACT_PLACEHOLDERS = ("[email removed]", "[phone removed]")
_IDENTITY_TOKEN_ALIASES = {
    "шейкер": "shaker",
    "мл": "ml",
    "г": "g",
    "кг": "kg",
    "л": "l",
    "сироватковий": "whey",
    "протеїн": "",
    "протеин": "",
    "солона": "salted",
    "карамель": "caramel",
}
_MAX_EXCERPT_CHARS = 480
_LISTING_TITLE_RE = re.compile(
    r"(?i)\b(?:top\s+\d+|best\s+sellers?|comparison|compare|versus|vs\.?|"
    r"similar products|all products|category|catalog|каталог|порівняння|схожі товари)\b"
)
_REVIEW_THEME_PATTERNS: Mapping[str, re.Pattern[str]] = MappingProxyType(
    {
        "taste_or_smell": re.compile(
            r"(?i)\b(?:taste|flavou?r|smell|aroma|смак\w*|вкус\w*|"
            r"аромат\w*|запах\w*)\b"
        ),
        "mixability": re.compile(
            r"(?i)\b(?:mix(?:es|ed|ing)?|dissolv\w*|lumps?|mixability|"
            r"розчиня\w*|розміш\w*|змішу\w*|растворя\w*|размеш\w*|"
            r"комоч\w*|грудоч\w*)\b"
        ),
        "texture": re.compile(
            r"(?i)\b(?:texture|consistency|creamy|gritty|текстур\w*|"
            r"консистенц\w*|густ\w*|кремов\w*)\b"
        ),
        "packaging": re.compile(
            r"(?i)\b(?:packaging|package|container|lid|seal|scoop|упаков\w*|"
            r"пакуван\w*|крышк\w*|кришк\w*|баночк\w*|дозатор\w*)\b"
        ),
        "ease_of_preparation": re.compile(
            r"(?i)\b(?:easy to prepare|easy to use|convenient|preparation|"
            r"легко готув\w*|зручно|зручн\w*|удобно|удобн\w*|"
            r"приготув\w*|приготов\w*)\b"
        ),
    }
)
_REVIEW_HEALTH_CLAIM_RE = re.compile(
    r"(?i)\b(?:health|medical|cure\w*|treat\w*|heal\w*|pain|disease\w*|"
    r"symptom\w*|side effects?|safety|safe|dosage|dose|interaction\w*|"
    r"pregnan\w*|blood pressure|blood sugar|леч\w*|вылеч\w*|побочн\w*|"
    r"дозиров\w*|взаимодейств\w*|беремен\w*|давлен\w*|безопасн\w*|"
    r"ліку\w*|виліку\w*|бол\w*|"
    r"здоров\w*|симптом\w*|побічн\w*|дозуван\w*|взаємоді\w*|"
    r"вагітн\w*|тиск|цукор)\b"
)


@dataclass(frozen=True)
class ModelEvidence:
    source_type: SourceType
    verified_product_name: str
    excerpt: str


@dataclass(frozen=True)
class EvidenceProvenance:
    provider: Literal["tavily"]
    source_type: SourceType
    title: str
    domain: str
    url: str
    fetched_at: str | None
    match_basis: MatchBasis

    def to_dict(self) -> dict[str, str | None]:
        return {
            "provider": self.provider,
            "source_type": self.source_type,
            "title": self.title,
            "domain": self.domain,
            "url": self.url,
            "fetched_at": self.fetched_at,
            "match_basis": self.match_basis,
        }


@dataclass(frozen=True)
class EvidenceBundle:
    model_evidence: tuple[ModelEvidence, ...] = ()
    provenance: tuple[EvidenceProvenance, ...] = ()

    def model_payload(self) -> list[dict[str, str]]:
        return [
            {
                "source_type": item.source_type,
                "verified_product_name": item.verified_product_name,
                "excerpt": item.excerpt,
            }
            for item in self.model_evidence
        ]

    def provenance_records(self) -> list[dict[str, str | None]]:
        return [item.to_dict() for item in self.provenance]


@dataclass(frozen=True)
class _AcceptedResult:
    evidence: ModelEvidence
    provenance: EvidenceProvenance
    independence_key: str | None


def approved_domains_for_product(
    product: Product,
    *,
    registry: Mapping[str, SourceRule] = SOURCE_REGISTRY,
    source_types: Iterable[SourceType] | None = None,
) -> tuple[str, ...]:
    """Return exact approved hosts whose optional brand scope matches the card."""
    if _ukrainian_card(product) is None:
        return ()
    brand = _card_brand(product)
    selected_types = _selected_source_types(source_types)
    if selected_types is None:
        return ()
    domains: list[str] = []
    for hostname, rule in _valid_registry_items(registry):
        if rule.source_type not in selected_types:
            continue
        if rule.product_brands and not any(
            _same_identity(brand, candidate) for candidate in rule.product_brands
        ):
            continue
        domains.append(hostname)
    return tuple(sorted(domains))


def approved_domains_for_topic(
    product: Product,
    topic: SearchTopic | str,
    *,
    registry: Mapping[str, SourceRule] = SOURCE_REGISTRY,
) -> tuple[str, ...]:
    selected = _coerce_topic(topic)
    allowed_types = (
        ("review_platform",)
        if selected is SearchTopic.BUYER_EXPERIENCE
        else ("manufacturer", "supplier")
    )
    return approved_domains_for_product(
        product,
        registry=registry,
        source_types=allowed_types,
    )


def build_search_query(product: Product, topic: SearchTopic | str) -> str:
    """Build a Tavily query from the displayed product name and a fixed topic."""
    selected = _coerce_topic(topic)
    identity_parts = _external_product_identity_parts(product)
    if not identity_parts:
        raise ValueError("search_identity_unavailable")
    identity = " ".join(identity_parts)
    if (
        _EMAIL_RE.search(identity)
        or _PHONE_RE.search(identity)
        or _PRICE_RE.search(identity)
        or _PURCHASE_RE.search(identity)
    ):
        raise ValueError("search_identity_unavailable")
    identity = re.sub(r"\s+", " ", identity).strip()
    if not identity:
        raise ValueError("search_identity_unavailable")
    return f"{identity} {TOPIC_PHRASES[selected]}"


def filter_search_results(
    product: Product,
    results: Iterable[SearchResult],
    *,
    registry: Mapping[str, SourceRule] = SOURCE_REGISTRY,
    source_types: Iterable[SourceType] | None = None,
    fetched_at: str | None = None,
) -> EvidenceBundle:
    """Keep exact-product excerpts from exact approved HTTPS hosts only."""
    card = _ukrainian_card(product)
    if card is None or not card.name or not card.name.strip():
        return EvidenceBundle()
    verified_product_name = card.name.strip()
    allowed = dict(_valid_registry_items(registry))
    product_domains = set(
        approved_domains_for_product(
            product,
            registry=registry,
            source_types=source_types,
        )
    )
    factual: list[_AcceptedResult] = []
    reviews: list[_AcceptedResult] = []
    for result in results:
        title = getattr(result, "title", None)
        content = getattr(result, "content", None)
        url = getattr(result, "url", None)
        if not all(isinstance(value, str) for value in (title, content, url)):
            continue
        parsed = _approved_result_url(url, allowed)
        if parsed is None:
            continue
        hostname, safe_url = parsed
        if hostname not in product_domains:
            continue
        rule = allowed[hostname]
        safe_url = _canonical_product_url(product, safe_url)
        if safe_url is None:
            continue
        match_basis = _product_match_basis(
            product,
            title,
            safe_url,
            brand_verified_by_host=(
                rule.source_type in {"manufacturer", "supplier"}
                and bool(rule.product_brands)
            ),
        )
        if match_basis is None or not _is_exact_product_page(title, safe_url):
            continue
        excerpt = _sanitize_excerpt(content, source_type=rule.source_type)
        if not excerpt:
            continue
        safe_title = _sanitize_title(title)
        if not safe_title:
            continue
        provenance = EvidenceProvenance(
            provider="tavily",
            source_type=rule.source_type,
            title=safe_title,
            domain=hostname,
            url=safe_url,
            fetched_at=_safe_timestamp(fetched_at),
            match_basis=match_basis,
        )
        accepted = _AcceptedResult(
            evidence=ModelEvidence(
                source_type=rule.source_type,
                verified_product_name=verified_product_name,
                excerpt=excerpt,
            ),
            provenance=provenance,
            independence_key=_independence_key(hostname, rule),
        )
        if rule.source_type == "review_platform":
            reviews.append(accepted)
        else:
            factual.append(accepted)

    eligible_reviews = _independent_reviews(reviews)
    accepted = factual + eligible_reviews
    return EvidenceBundle(
        model_evidence=tuple(item.evidence for item in accepted),
        provenance=tuple(item.provenance for item in accepted),
    )


def _coerce_topic(topic: SearchTopic | str) -> SearchTopic:
    try:
        return topic if isinstance(topic, SearchTopic) else SearchTopic(topic)
    except (TypeError, ValueError):
        raise ValueError("search_topic_unsupported") from None


def _external_product_identity_parts(product: Product) -> tuple[str, ...]:
    card = _ukrainian_card(product)
    if not card or not card.name or not card.name.strip():
        return ()
    parts = [card.name.strip()]
    brand = _card_brand(product)
    if brand and not _contains_phrase(" ".join(parts), brand):
        parts.append(brand)
    for value in _card_variant_values(card):
        if not _contains_phrase(" ".join(parts), value):
            parts.append(value)
    return tuple(parts)


def _card_variant_values(card) -> tuple[str, ...]:
    values: list[str] = []
    seen: set[str] = set()
    for attribute in card.attributes:
        if (
            not attribute.name
            or not attribute.value
            or not _VARIANT_LABEL_RE.search(attribute.name)
            or _normalize(attribute.name) in _BRAND_LABELS
        ):
            continue
        value = attribute.value.strip()
        normalized = _normalize(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            values.append(value)
    return tuple(values)


def _selected_source_types(
    source_types: Iterable[SourceType] | None,
) -> frozenset[str] | None:
    if source_types is None:
        return _SOURCE_TYPES
    if isinstance(source_types, str):
        values = {source_types}
    else:
        try:
            values = set(source_types)
        except TypeError:
            return None
    if not values or not values <= _SOURCE_TYPES:
        return None
    return frozenset(values)


def _valid_registry_items(
    registry: Mapping[str, SourceRule],
) -> list[tuple[str, SourceRule]]:
    if not isinstance(registry, Mapping):
        return []
    valid: list[tuple[str, SourceRule]] = []
    for hostname, rule in registry.items():
        if (
            not isinstance(hostname, str)
            or hostname != hostname.lower()
            or not _is_hostname(hostname)
            or not isinstance(rule, SourceRule)
            or not isinstance(rule.source_type, str)
            or rule.source_type not in _SOURCE_TYPES
            or (
                rule.source_type == "review_platform"
                and not (
                    isinstance(rule.independence_group, str)
                    and rule.independence_group.strip()
                )
            )
        ):
            continue
        valid.append((hostname, rule))
    return valid


def _is_hostname(hostname: str) -> bool:
    if (
        "*" in hostname
        or hostname.endswith(".")
        or not _HOSTNAME_RE.fullmatch(hostname)
    ):
        return False
    try:
        return (
            bool(hostname)
            and urlsplit(f"https://{hostname}").hostname == hostname
            and not any(char in hostname for char in "/:@?#")
        )
    except ValueError:
        return False


def _approved_result_url(
    url: str,
    registry: Mapping[str, SourceRule],
) -> tuple[str, str] | None:
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or hostname != hostname.lower()
        or hostname not in registry
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        return None
    path = parsed.path or "/"
    if (
        "@" in path
        or _EMAIL_RE.search(path)
        or re.search(r"(?i)/(?:profile|author|reviewer|customer|account|users?)(?:/|$)", path)
    ):
        return None
    safe_url = urlunsplit(("https", hostname, path, "", ""))
    return hostname, safe_url


def _product_match_basis(
    product: Product,
    title: str,
    url: str,
    *,
    brand_verified_by_host: bool = False,
) -> MatchBasis | None:
    card = _ukrainian_card(product)
    identity_parts = _external_product_identity_parts(product)
    if not card or not card.name or not identity_parts:
        return None
    has_explicit_anchor = bool(_card_brand(product) or _card_variant_values(card))
    if not has_explicit_anchor and len(_normalize(card.name).split()) < 2:
        return None
    try:
        path = unquote(urlsplit(url).path)
    except ValueError:
        return None
    path = re.sub(r"[-_]+", " ", html.unescape(path))
    source_texts = (title, path)
    if any(
        all(_contains_phrase(source_text, part) for part in identity_parts)
        for source_text in source_texts
    ):
        return "product_name"

    required_tokens = set(_identity_match_tokens(card.name))
    brand = _card_brand(product)
    if brand:
        brand_tokens = set(_identity_match_tokens(brand))
        if brand_verified_by_host:
            required_tokens.difference_update(brand_tokens)
        else:
            required_tokens.update(brand_tokens)
    for value in _card_variant_values(card):
        required_tokens.update(_identity_match_tokens(value))
    meaningful_tokens = {
        token
        for token in required_tokens
        if not token.isdecimal() and token not in {"ml", "mg", "mcg", "kg", "g", "oz", "lb", "l"}
    }
    if len(meaningful_tokens) < 2:
        return None
    if any(
        required_tokens <= set(_identity_match_tokens(source_text))
        for source_text in source_texts
    ):
        return "product_name"
    if brand_verified_by_host:
        latin_name_tokens = {
            token
            for token in _identity_match_tokens(card.name)
            if re.fullmatch(r"[a-z0-9]+", token)
            and not token.isdecimal()
            and token not in {"ml", "mg", "mcg", "kg", "g", "oz", "lb", "l"}
        }
        if brand:
            latin_name_tokens.difference_update(set(_identity_match_tokens(brand)))
        card_numbers = {
            token for token in _identity_match_tokens(card.name) if token.isdecimal()
        }
        if len(latin_name_tokens) >= 2:
            for source_text in source_texts:
                source_tokens = set(_identity_match_tokens(source_text))
                if not (latin_name_tokens <= source_tokens):
                    continue
                source_numbers = {
                    token for token in source_tokens if token.isdecimal()
                }
                if card_numbers and source_numbers and not (card_numbers & source_numbers):
                    continue
                return "product_name"

        if product.model:
            model_tokens = {
                token
                for token in _identity_match_tokens(product.model)
                if not token.isdecimal() and token not in {"ml", "mg", "mcg", "kg", "g", "oz", "lb", "l"}
            }
            if len(model_tokens) >= 2 and any(
                model_tokens <= set(_identity_match_tokens(source_text))
                for source_text in source_texts
            ):
                return "model_code"
    return None


def _is_exact_product_page(title: str, url: str) -> bool:
    try:
        path = unquote(urlsplit(url).path)
    except ValueError:
        return False
    segments = [segment for segment in path.casefold().split("/") if segment]
    if not segments:
        return False
    return not _LISTING_TITLE_RE.search(title)


def _canonical_product_url(product: Product, url: str) -> str | None:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    card = _ukrainian_card(product)
    if not card or not card.name or not card.name.strip():
        return None
    identity_parts = _external_product_identity_parts(product)
    if not identity_parts:
        return None
    segments = [segment for segment in parsed.path.split("/") if segment]
    prefix = ""
    matched_end = None
    for index, segment in enumerate(segments):
        decoded_segment = unquote(segment)
        prefix = f"{prefix} {decoded_segment.replace('-', ' ').replace('_', ' ')}"
        if all(_contains_phrase(prefix, part) for part in identity_parts):
            matched_end = index
            break
    if matched_end is None:
        path = parsed.path or "/"
    else:
        path = "/" + "/".join(segments[: matched_end + 1])
    return urlunsplit(("https", parsed.hostname or "", path, "", ""))


def _ukrainian_card(product: Product):
    for language, card in product.languages.items():
        if language.casefold().replace("_", "-").startswith("uk"):
            return card
    return None


def _card_brand(product: Product) -> str:
    card = _ukrainian_card(product)
    if not card:
        return ""
    brand = _attribute_value(card, {"brand", "бренд", "торгова марка", "виробник"})
    return brand or _brand_in_product_name(card.name)


_SHORT_BRAND_ACRONYMS = frozenset({"sis", "gu", "pfh"})


def _brand_in_product_name(name: str | None) -> str:
    if not isinstance(name, str) or not name.strip():
        return ""
    matches: list[tuple[int, int, str, str]] = []
    for rule in SOURCE_REGISTRY.values():
        for brand in sorted(rule.product_brands):
            tokens = _identity_match_tokens(brand)
            if not tokens or (
                len(tokens) == 1
                and len(tokens[0]) < 4
                and tokens[0] not in _SHORT_BRAND_ACRONYMS
            ):
                continue
            if _contains_phrase(name, brand):
                normalized = _normalize(brand)
                matches.append((len(tokens), len(normalized), normalized, brand))
    if not matches:
        return ""
    best_score = max((words, length) for words, length, _, _ in matches)
    best_aliases = {
        normalized
        for words, length, normalized, _ in matches
        if (words, length) == best_score
    }
    if len(best_aliases) != 1:
        return ""
    return next(
        brand
        for words, length, normalized, brand in matches
        if (words, length) == best_score and normalized in best_aliases
    )


def _identity_match_tokens(value: str) -> tuple[str, ...]:
    text = unicodedata.normalize("NFKC", value).casefold()
    text = re.sub(r"(?<=\d)(?=(?:мл|кг|г|л)\b)", " ", text)
    normalized = _normalize(text)
    return tuple(
        mapped
        for token in normalized.split()
        if (mapped := _IDENTITY_TOKEN_ALIASES.get(token, token))
    )


def _attribute_value(card, names: set[str]) -> str:
    normalized_names = {_normalize(name) for name in names}
    for attribute in card.attributes:
        if attribute.name and _normalize(attribute.name) in normalized_names:
            return attribute.value.strip()
    return ""


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).casefold()
    text = re.sub(r"(?<=\d)\s*(?=(?:mg|mcg|kg|ml|g|oz|lb|таблет\w*|капсул\w*)\b)", " ", text)
    return " ".join(re.findall(r"[^\W_]+", text, flags=re.UNICODE))


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized = _normalize(text)
    needle = _normalize(phrase)
    if not normalized or not needle:
        return False
    return f" {needle} " in f" {normalized} "


def _same_identity(left: str, right: str) -> bool:
    if _normalize(left) == _normalize(right):
        return True
    left_clean = re.sub(r"\s*\([^)]*\)", "", left).strip()
    right_clean = re.sub(r"\s*\([^)]*\)", "", right).strip()
    if left_clean and right_clean and _normalize(left_clean) == _normalize(right_clean):
        return True
    for paren in re.findall(r"\(([^)]+)\)", left) + re.findall(r"\(([^)]+)\)", right):
        if _normalize(paren) == _normalize(left) or _normalize(paren) == _normalize(right):
            return True
    return False


def _independence_key(hostname: str, rule: SourceRule) -> str:
    group = rule.independence_group
    return _normalize(group) if isinstance(group, str) and group.strip() else hostname


def _safe_timestamp(value: str | None) -> str | None:
    return value if isinstance(value, str) and _TIMESTAMP_RE.fullmatch(value) else None


def _independent_reviews(reviews: list[_AcceptedResult]) -> list[_AcceptedResult]:
    by_theme: dict[str, dict[str, _AcceptedResult]] = {}
    seen_excerpts: set[str] = set()
    for item in reviews:
        key = item.independence_key
        excerpt_key = _normalize(item.evidence.excerpt)
        if not key or excerpt_key in seen_excerpts:
            continue
        seen_excerpts.add(excerpt_key)
        for theme, pattern in _REVIEW_THEME_PATTERNS.items():
            if pattern.search(item.evidence.excerpt):
                by_theme.setdefault(theme, {}).setdefault(key, item)
    recurring_themes = [
        sources for sources in by_theme.values() if len(sources) >= 2
    ]
    if not recurring_themes:
        return []
    shared_theme = max(recurring_themes, key=len)
    return list(shared_theme.values())


def _sanitize_title(title: str) -> str:
    if (
        _AUTHOR_RE.search(title)
        or _PERSON_NAME_PREFIX_RE.search(title)
        or _PERSON_NAME_CONTEXT_RE.search(title)
        or _PERSON_NAME_ACTIVITY_RE.search(title)
        or _PRICE_RE.search(title)
        or _PURCHASE_RE.search(title)
    ):
        return ""
    text = _EMAIL_RE.sub("[email removed]", title)
    text = _PHONE_RE.sub("[phone removed]", text)
    text = _HANDLE_RE.sub("[handle removed]", text)
    text = _URL_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:240]


def _sanitize_excerpt(content: str, *, source_type: SourceType) -> str | None:
    text = html.unescape(content)
    text = re.sub(r"<[^>]*>", " ", text)
    text = _EMAIL_RE.sub(_CONTACT_PLACEHOLDERS[0], text)
    text = _PHONE_RE.sub(_CONTACT_PLACEHOLDERS[1], text)
    text = _HANDLE_RE.sub("[handle removed]", text)
    text = _URL_RE.sub("", text)
    text = _PERSON_NAME_PREFIX_RE.sub("", text)
    fragments = re.split(r"(?<=[.!?])\s+|[;\n]+", text)
    safe: list[str] = []
    for fragment in fragments:
        fragment = re.sub(r"\s+", " ", fragment).strip()
        if (
            not fragment
            or _PRICE_RE.search(fragment)
            or _PURCHASE_RE.search(fragment)
            or _AUTHOR_RE.search(fragment)
            or _PERSON_NAME_PREFIX_RE.search(fragment)
            or _PERSON_NAME_CONTEXT_RE.search(fragment)
            or _PERSON_NAME_ACTIVITY_RE.search(fragment)
            or _STANDALONE_PERSON_NAME_RE.fullmatch(fragment)
            or (
                source_type == "review_platform"
                and _REVIEW_HEALTH_CLAIM_RE.search(fragment)
            )
        ):
            continue
        safe.append(fragment)
    excerpt = " ".join(safe).strip()
    if not excerpt:
        return None
    if len(excerpt) > _MAX_EXCERPT_CHARS:
        excerpt = _truncate_at_boundary(excerpt, _MAX_EXCERPT_CHARS)
    excerpt = re.sub(r"\s+", " ", excerpt).strip()
    if len(excerpt) < 12 or any(marker in excerpt for marker in ("@", "http://", "https://")):
        return None
    return excerpt


def _truncate_at_boundary(text: str, limit: int) -> str:
    candidate = text[:limit]
    boundary = max(candidate.rfind(". "), candidate.rfind("! "), candidate.rfind("? "))
    if boundary < 12:
        return ""
    return candidate[: boundary + 1].strip()
