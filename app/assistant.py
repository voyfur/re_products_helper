from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from app.journal import Journal, JournalAttempt
from app.openai_client import (
    AssistantDecision,
    OpenAIResponsesClient,
    ProviderError,
    StructuredAnswer,
)
from app.product_context import Product, build_model_context
from app.search_evidence import (
    SearchTopic,
    approved_domains_for_topic,
    build_search_query,
    filter_search_results,
)
from app.search_provider import SearchProviderError, TavilySearchClient


EXPECTED_PROMPT_SHA256_V12 = "d5d7f11bdc65abe95d6549f8d438153fc6e46b35ef5d16ca69a2d0b4468a41b2"
EXPECTED_PROMPT_SHA256_V13 = "d845e2278a11c3cf62f7ceb48d70fca808f026454d2d3a52729f0d6ea354e7c7"
EXPECTED_PROMPT_SHA256_V14 = "c78822fcec4d4148099dbce6a8fce54c447750594f65f3d3ef9506ca46d772a6"
EXPECTED_PROMPT_SHA256_V15 = "d9260562fd9bf5998c93aebbaaa2bd6ba13e93c3f716d82b1c3d8aad3106058f"
EXPECTED_PROMPT_SHA256_V16 = "2789348950c64432833f678cd1b83db06fc46f5363e40a7356d83f43bf35c876"
EXPECTED_PROMPT_SHA256_V17 = "f26e6eabf5d2867adf5608843abb1da277c362759cd3606d892c3c101e9fcdea"
DEFAULT_PROMPT_VERSION = "v17"
PROMPT_PATHS = {
    "v12": Path(__file__).parents[1] / "prompts" / "product-assistant-system-v12.md",
    "v13": Path(__file__).parents[1] / "prompts" / "product-assistant-system-v13.md",
    "v14": Path(__file__).parents[1] / "prompts" / "product-assistant-system-v14.md",
    "v15": Path(__file__).parents[1] / "prompts" / "product-assistant-system-v15.md",
    "v16": Path(__file__).parents[1] / "prompts" / "product-assistant-system-v16.md",
    "v17": Path(__file__).parents[1] / "prompts" / "product-assistant-system-v17.md",
}
EXPECTED_PROMPT_HASHES = {
    "v12": EXPECTED_PROMPT_SHA256_V12,
    "v13": EXPECTED_PROMPT_SHA256_V13,
    "v14": EXPECTED_PROMPT_SHA256_V14,
    "v15": EXPECTED_PROMPT_SHA256_V15,
    "v16": EXPECTED_PROMPT_SHA256_V16,
    "v17": EXPECTED_PROMPT_SHA256_V17,
}
HEALTH_DISCLAIMER = (
    "Це відповідь штучного інтелекту; інформацію щодо здоров’я потрібно перевірити з фахівцем."
)
SAFE_UNSUPPORTED_ANSWER = (
    "Не вдалося підтвердити відповідь за даними картки й доступними перевіреними джерелами."
)
OUT_OF_SCOPE_ANSWER = (
    "Я можу допомогти з питаннями про цей товар, його характеристики або застосування."
)
PERSONAL_HEALTH_REFUSAL = (
    "Не можу визначати особисту безпеку продукту або дозу з урахуванням стану "
    "здоров’я, віку чи ліків. Обговоріть це з лікарем або фармацевтом."
)
_EXPLICIT_OUT_OF_SCOPE_RE = re.compile(
    r"(?ix)\b(?:"
    r"не\s+(?:про|стосується|відноситься)\s+"
    r"(?:(?:цей|цього|ця|этот|этого|эта)\s+)?(?:товар\w*|продукт\w*|добавк\w*)|"
    r"(?:питання|вопрос)\s+не\s+(?:про|стосується|относится\s+к)\s+"
    r"(?:(?:цей|этот|этого)\s+)?(?:товар\w*|продукт\w*)|"
    r"відволічен\w*\s+питан\w*|"
    r"not\s+(?:about|related\s+to)\s+(?:(?:this|the)\s+)?(?:product|item|supplements?)|"
    r"unrelated\s+to\s+(?:(?:this|the)\s+)?(?:product|item|supplements?)|"
    r"off[-\s]?topic"
    r")\b"
)
_PERSONAL_HEALTH_CONTEXT_RE = re.compile(
    r"(?ix)\b(?:"
    r"вагітн\w*|беремен\w*|pregnan\w*|"
    r"алергі\w*|аллерги\w*|allerg(?:y|ies|ic)|"
    r"висок\w*\s+(?:тиск|давлен\w*)|high\s+blood\s+pressure|"
    r"діабет\w*|диабет\w*|diabet(?:es|ic)|"
    r"нирк\w*\s+(?:недостат|хвороб|захворюван)|kidney\s+(?:disease|condition|failure)|"
    r"хвороб\w*|захворюван\w*|заболеван\w*|condition|disease|illness|"
    r"лікарськ\w*\s+препарат\w*|ліки|медикамент\w*|лекарств\w*|medication|prescription|drug\s+interaction\w*|"
    r"стан\w*\s+здоров|health\s+(?:condition|issue)|"
    r"дитин\w*|ребен\w*|підлітк\w*|подрост\w*|child(?:ren)?|teen(?:ager)?|minor|under\s+18"
    r")\b"
)
_PERSONALIZED_DOSE_RE = re.compile(
    r"(?ix)(?:"
    r"\b(?:яку|яка|скільки|какую|сколько)\b.{0,70}\b(?:доз\w*|приймат\w*|вживат\w*)\b|"
    r"\b(?:what|which|how\s+much)\b.{0,50}\b(?:dose|dosage)\b.{0,50}\b(?:should|can|may|i|my|take|use)\b|"
    r"\b(?:my|for\s+me|should\s+i|can\s+i|do\s+i)\b.{0,50}\b(?:dose|dosage|take|use)\b|"
    r"\b(?:індивідуальн\w*|особист\w*)\s+доз\w*\b"
    r")"
)
URL_OR_DOMAIN_RE = re.compile(
    r"(?:https?://|www\.)\S+|\b(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/\S*)?",
    re.IGNORECASE,
)


class QuestionRejected(Exception):
    def __init__(self, code: str, attempt: JournalAttempt | None = None):
        self.code = code
        self.attempt = attempt
        super().__init__(code)


def load_system_prompt(version: str = DEFAULT_PROMPT_VERSION) -> str:
    path = PROMPT_PATHS.get(version)
    if path is None:
        raise ValueError("prompt_version_unsupported")
    prompt = path.read_text(encoding="utf-8")
    expected = EXPECTED_PROMPT_HASHES.get(version)
    if not expected or hashlib.sha256(prompt.encode("utf-8")).hexdigest() != expected:
        raise ValueError("prompt_hash_mismatch")
    return prompt


class AssistantService:
    def __init__(
        self,
        journal: Journal,
        provider: OpenAIResponsesClient,
        *,
        system_prompt: str,
        search_client: TavilySearchClient | None = None,
        progress_callback: Callable[[], None] | None = None,
    ):
        self.journal = journal
        self.provider = provider
        self.system_prompt = system_prompt
        self.search_client = search_client
        self.progress_callback = progress_callback

    def submit(
        self,
        product: Product | None,
        question: str,
        *,
        request_started_at: float | None = None,
    ) -> JournalAttempt:
        if product is None:
            raise QuestionRejected("product_required")
        if not question.strip():
            raise QuestionRejected("question_required")

        localized = product.languages.get("uk")
        product_context = build_model_context(product, "uk")
        attempt = self.journal.create_attempt(
            product_id=product.product_id,
            article=product.article,
            model=product.model,
            sku=product.sku,
            product_name=localized.name if localized else None,
            question=question,
        )
        request_started = (
            request_started_at
            if request_started_at is not None
            else time.monotonic()
        )
        search_status = "skipped"
        search_provider = None
        search_latency_ms = None
        provenance: list[dict[str, str]] = []

        try:
            if _EXPLICIT_OUT_OF_SCOPE_RE.search(question):
                self.journal.update_search_metadata(
                    attempt.attempt_id,
                    status="skipped",
                    provider=None,
                    search_latency_ms=None,
                    total_latency_ms=max(
                        0, round((time.monotonic() - request_started) * 1000)
                    ),
                    sources=[],
                )
                self.journal.complete_attempt(attempt.attempt_id, OUT_OF_SCOPE_ANSWER)
                return self.journal.get_attempt(attempt.attempt_id)

            if _is_personal_health_request(question):
                self.journal.update_search_metadata(
                    attempt.attempt_id,
                    status="skipped",
                    provider=None,
                    search_latency_ms=None,
                    total_latency_ms=max(
                        0, round((time.monotonic() - request_started) * 1000)
                    ),
                    sources=[],
                )
                self.journal.complete_attempt(
                    attempt.attempt_id,
                    f"{PERSONAL_HEALTH_REFUSAL}\n\n{HEALTH_DISCLAIMER}",
                )
                return self.journal.get_attempt(attempt.attempt_id)

            decision = self.provider.decide(
                instructions=self.system_prompt,
                product_context=product_context,
                question=question,
            )
            if not isinstance(decision, AssistantDecision):
                raise ProviderError("provider_invalid_response")
            if decision.product_related is not True:
                self.journal.update_search_metadata(
                    attempt.attempt_id,
                    status="skipped",
                    provider=None,
                    search_latency_ms=None,
                    total_latency_ms=max(
                        0, round((time.monotonic() - request_started) * 1000)
                    ),
                    sources=[],
                )
                self.journal.complete_attempt(attempt.attempt_id, OUT_OF_SCOPE_ANSWER)
                return self.journal.get_attempt(attempt.attempt_id)
            if decision.search_topic is None:
                answer = decision.answer or SAFE_UNSUPPORTED_ANSWER
                health_related = decision.health_related
            else:
                if not isinstance(decision.search_topic, SearchTopic):
                    raise ProviderError("provider_invalid_response")
                evidence_text = ""
                if self._search_is_allowed(decision.search_topic):
                    domains = self._domains_for_topic(product, decision.search_topic)
                    try:
                        query = build_search_query(product, decision.search_topic)
                    except ValueError:
                        query = ""
                    if not query:
                        domains = []
                    if domains and self.search_client is not None:
                        search_started = time.monotonic()
                        search_status = "failed"
                        search_provider = "tavily"
                        try:
                            if self.progress_callback is not None:
                                self.progress_callback()
                            results = self.search_client.search(
                                query,
                                include_domains=domains,
                            )
                            search_status = "used"
                            bundle = filter_search_results(
                                product,
                                results,
                                source_types=self._source_types(decision.search_topic),
                                fetched_at=datetime.now(timezone.utc).isoformat(
                                    timespec="seconds"
                                ),
                            )
                            evidence_text = json.dumps(
                                bundle.model_payload(), ensure_ascii=False
                            )
                            provenance = [
                                record
                                for record in bundle.provenance_records()
                                if all(isinstance(value, str) for value in record.values())
                            ]
                        except SearchProviderError:
                            search_status = "failed"
                        finally:
                            search_latency_ms = max(
                                0, round((time.monotonic() - search_started) * 1000)
                            )
                final = self.provider.answer_with_evidence(
                    instructions=self.system_prompt,
                    product_context=product_context,
                    question=question,
                    evidence=evidence_text,
                )
                if not isinstance(final, StructuredAnswer):
                    raise ProviderError("provider_invalid_response")
                if final.product_related is not True:
                    answer = OUT_OF_SCOPE_ANSWER
                    health_related = False
                else:
                    answer = final.answer
                    health_related = final.health_related

            answer = self._buyer_safe_answer(answer, provenance)
            if health_related:
                answer = f"{answer}\n\n{HEALTH_DISCLAIMER}"
            self.journal.update_search_metadata(
                attempt.attempt_id,
                status=search_status,
                provider=search_provider,
                search_latency_ms=search_latency_ms,
                total_latency_ms=max(0, round((time.monotonic() - request_started) * 1000)),
                sources=provenance,
            )
            self.journal.complete_attempt(attempt.attempt_id, answer)
        except ProviderError as error:
            self._update_metadata(
                attempt.attempt_id,
                search_status,
                search_provider,
                search_latency_ms,
                request_started,
                provenance,
            )
            self.journal.fail_attempt(attempt.attempt_id, error.code)
        except Exception:
            self._update_metadata(
                attempt.attempt_id,
                search_status,
                search_provider,
                search_latency_ms,
                request_started,
                provenance,
            )
            self.journal.fail_attempt(attempt.attempt_id, "provider_error")
        return self.journal.get_attempt(attempt.attempt_id)

    @staticmethod
    def _source_types(topic: SearchTopic) -> set[str]:
        if topic is SearchTopic.BUYER_EXPERIENCE:
            return {"review_platform"}
        return {"manufacturer", "supplier"}

    @classmethod
    def _domains_for_topic(cls, product: Product, topic: SearchTopic) -> list[str]:
        return list(approved_domains_for_topic(product, topic))

    @classmethod
    def _search_is_allowed(cls, topic: SearchTopic) -> bool:
        return isinstance(topic, SearchTopic)

    @staticmethod
    def _buyer_safe_answer(answer: str, provenance: list[dict[str, str]]) -> str:
        text = answer.strip()
        if URL_OR_DOMAIN_RE.search(text):
            return SAFE_UNSUPPORTED_ANSWER
        lower = text.casefold()
        if any(
            source.get("domain", "").casefold() in lower
            for source in provenance
            if source.get("domain")
        ):
            return SAFE_UNSUPPORTED_ANSWER
        return text or SAFE_UNSUPPORTED_ANSWER

    def _update_metadata(
        self,
        attempt_id: int,
        status: str,
        provider: str | None,
        search_latency_ms: int | None,
        request_started: float,
        provenance: list[dict[str, str]],
    ) -> None:
        self.journal.update_search_metadata(
            attempt_id,
            status=status,
            provider=provider,
            search_latency_ms=search_latency_ms,
            total_latency_ms=max(0, round((time.monotonic() - request_started) * 1000)),
            sources=provenance,
        )


def _is_personal_health_request(question: str) -> bool:
    return bool(
        _PERSONAL_HEALTH_CONTEXT_RE.search(question)
        or _PERSONALIZED_DOSE_RE.search(question)
    )
