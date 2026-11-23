from __future__ import annotations

import hashlib
import hmac
import json
import logging
import threading
import time
from collections import deque
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.sse import EventSourceResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from app.assistant import AssistantService, QuestionRejected, load_system_prompt
from app.catalog import (
    OpenCartCatalog,
    create_mysql_connection,
    create_mysql_connection_factory,
)
from app.config import Settings
from app.conversation import ConversationMessage, MAX_PRIOR_MESSAGES
from app.journal import Journal, JournalAttempt
from app.openai_client import OpenAIResponsesClient
from app.product_context import LanguageCard, Product, html_to_safe_text
from app.security import AskBodySizeLimit, security_headers
from app.search_provider import TavilySearchClient
from app.suggested_questions import get_suggested_questions


BASE_PATH = Path(__file__).parent
TEMPLATE_PATH = BASE_PATH / "templates" / "index.html"
STATIC_PATH = BASE_PATH / "static"
LOGGER = logging.getLogger(__name__)


def _log_catalog_unavailable(error: Exception) -> None:
    error_code = getattr(error, "errno", None)
    safe_code = error_code if isinstance(error_code, int) else "unknown"
    LOGGER.warning(
        "catalog_unavailable error_type=%s error_code=%s",
        type(error).__name__,
        safe_code,
    )


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    article: str = Field(min_length=1, max_length=128)
    product_id: int
    question: str = Field(min_length=1, max_length=2000)
    history: list[ConversationMessage] = Field(
        default_factory=list, max_length=MAX_PRIOR_MESSAGES
    )


class VersionedAskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    article: str = Field(min_length=1, max_length=128)
    question: str = Field(min_length=1, max_length=2000)
    history: list[ConversationMessage] = Field(
        default_factory=list, max_length=MAX_PRIOR_MESSAGES
    )


class AskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["succeeded"]
    answer: str


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: Literal[
        "unauthorized",
        "product_not_found",
        "product_selection_required",
        "request_too_large",
        "invalid_request",
        "rate_limited",
        "answer_unavailable",
        "catalog_unavailable",
        "service_not_configured",
    ]


class HealthResponse(BaseModel):
    status: Literal["ok"]


_PRODUCT_QA_BEARER = HTTPBearer(
    scheme_name="productQaBearer",
    bearerFormat="opaque API key",
    description="Server-side only. Storefront browser code must never receive this key.",
    auto_error=False,
)
_VERSIONED_ASK_RESPONSES = {
    401: {
        "model": ApiErrorResponse,
        "description": "Missing or invalid bearer credential.",
        "headers": {"WWW-Authenticate": {"schema": {"type": "string", "const": "Bearer"}}},
    },
    404: {"model": ApiErrorResponse, "description": "No product matches the article."},
    409: {"model": ApiErrorResponse, "description": "The article matches multiple products."},
    413: {"model": ApiErrorResponse, "description": "Request body exceeds 16 KiB."},
    422: {"model": ApiErrorResponse, "description": "Request fields are invalid."},
    429: {
        "model": ApiErrorResponse,
        "description": "The credential exceeded its request limit.",
        "headers": {"Retry-After": {"schema": {"type": "integer", "const": 60}}},
    },
    502: {"model": ApiErrorResponse, "description": "A safe answer could not be generated."},
    503: {"model": ApiErrorResponse, "description": "The catalog or service is unavailable."},
}
_VERSIONED_STREAM_RESPONSES = {
    **{
        status: response
        for status, response in _VERSIONED_ASK_RESPONSES.items()
        if status != 502
    },
    200: {
        "description": (
            "SSE events: start, delta, replace, done, or error. Event data is JSON."
        ),
        "content": {"text/event-stream": {"schema": {"type": "string"}}},
    },
}


class _MinuteRateLimiter:
    def __init__(self, limit: int = 60):
        self.limit = limit
        self._lock = threading.Lock()
        self._requests: dict[str, deque[float]] = {}

    def allow(self, credential: str, now: float | None = None) -> bool:
        timestamp = time.monotonic() if now is None else now
        key = hashlib.sha256(credential.encode("utf-8")).hexdigest()
        with self._lock:
            requests = self._requests.setdefault(key, deque())
            while requests and requests[0] <= timestamp - 60:
                requests.popleft()
            if len(requests) >= self.limit:
                return False
            requests.append(timestamp)
            return True


def create_app(
    *,
    catalog: Any | None = None,
    journal: Journal | None = None,
    assistant: AssistantService | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    rate_limiter = _MinuteRateLimiter()
    runtime_settings: Settings | None = settings
    services: dict[str, Any] = {
        "catalog": catalog,
        "journal": journal,
        "assistant": assistant,
    }
    services_lock = threading.Lock()

    def get_runtime_settings() -> Settings:
        nonlocal runtime_settings
        if runtime_settings is None:
            runtime_settings = Settings.from_env()
        return runtime_settings

    def get_services() -> dict[str, Any]:
        if all(services[name] is not None for name in ("catalog", "journal", "assistant")):
            return services
        with services_lock:
            if all(services[name] is not None for name in ("catalog", "journal", "assistant")):
                return services
            active_settings = get_runtime_settings()
            active_journal = services["journal"] or Journal(active_settings.journal_path)
            active_catalog = services["catalog"] or OpenCartCatalog(
                create_mysql_connection_factory(active_settings.mysql)
            )
            active_assistant = services["assistant"] or AssistantService(
                active_journal,
                OpenAIResponsesClient(active_settings.openai_api_key),
                system_prompt=load_system_prompt(),
                search_client=TavilySearchClient(active_settings.tavily_api_key),
            )
            services.update(
                catalog=active_catalog,
                journal=active_journal,
                assistant=active_assistant,
            )
            return services

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(AskBodySizeLimit)
    app.middleware("http")(security_headers)
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

    @app.exception_handler(RequestValidationError)
    async def request_validation_error(
        _request: Request, _error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse({"error": "invalid_request"}, status_code=422)

    @app.get("/health", response_model=HealthResponse)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", include_in_schema=False)
    def ready():
        cursor = None
        try:
            active = get_services()
            with active["catalog"].connection_scope() as connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("SELECT 1")
                    row = cursor.fetchone()
                    if not row or row[0] != 1:
                        raise RuntimeError("catalog_readiness_check_failed")
                finally:
                    if cursor is not None:
                        cursor.close()
            return {"status": "ready"}
        except Exception as error:
            _log_catalog_unavailable(error)
            return JSONResponse({"status": "unavailable"}, status_code=503)

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(TEMPLATE_PATH)

    @app.get("/api/search", include_in_schema=False)
    def search(article: str = Query(min_length=1)) -> JSONResponse:
        submitted_article = article.strip()
        if not submitted_article:
            return JSONResponse({"error": "article_required"}, status_code=400)
        try:
            active = get_services()
            with active["catalog"].connection_scope() as connection:
                products = active["catalog"].search_products(
                    submitted_article, connection=connection
                )
                if not products:
                    return JSONResponse({"status": "not_found"})
        except Exception as error:
            _log_catalog_unavailable(error)
            return JSONResponse({"error": "catalog_unavailable"}, status_code=503)
        if len(products) == 1:
            return JSONResponse({"status": "single", "product": _product_payload(products[0])})
        return JSONResponse(
            {
                "status": "ambiguous",
                "candidates": [_product_payload(product) for product in products],
            }
        )

    @app.post("/api/ask", include_in_schema=False)
    def ask(payload: AskRequest) -> JSONResponse:
        request_started_at = time.monotonic()
        article = payload.article.strip()
        if not article:
            return JSONResponse({"error": "article_required"}, status_code=400)
        try:
            active = get_services()
            with active["catalog"].connection_scope() as connection:
                products = active["catalog"].search_products(
                    article, connection=connection
                )
                product = next(
                    (item for item in products if item.product_id == payload.product_id),
                    None,
                )
                if product is None:
                    error = "product_not_found" if not products else "product_selection_required"
                    return JSONResponse({"error": error}, status_code=409)
        except Exception as error:
            _log_catalog_unavailable(error)
            return JSONResponse({"error": "catalog_unavailable"}, status_code=503)
        try:
            attempt = active["assistant"].submit(
                product,
                payload.question,
                history=payload.history,
                request_started_at=request_started_at,
            )
        except QuestionRejected as error:
            return JSONResponse({"error": error.code}, status_code=422)
        except Exception:
            return JSONResponse({"error": "question_unavailable"}, status_code=503)
        return JSONResponse({"attempt": _attempt_payload(attempt)})

    @app.post("/api/ask/stream", include_in_schema=False, response_model=None)
    def ask_local_stream(payload: AskRequest) -> EventSourceResponse | JSONResponse:
        request_started_at = time.monotonic()
        article = payload.article.strip()
        question = payload.question.strip()
        if not article or not question:
            return JSONResponse({"error": "invalid_request"}, status_code=422)
        try:
            active = get_services()
            with active["catalog"].connection_scope() as connection:
                products = active["catalog"].search_products(
                    article, connection=connection
                )
                product = next(
                    (item for item in products if item.product_id == payload.product_id),
                    None,
                )
                if product is None:
                    error = "product_not_found" if not products else "product_selection_required"
                    return JSONResponse({"error": error}, status_code=409)
        except Exception as error:
            _log_catalog_unavailable(error)
            return JSONResponse({"error": "catalog_unavailable"}, status_code=503)
        events = active["assistant"].stream(
            product,
            question,
            history=payload.history,
            request_started_at=request_started_at,
        )
        return _sse_response(events)

    @app.post(
        "/api/v1/ask",
        response_model=AskResponse,
        responses=_VERSIONED_ASK_RESPONSES,
    )
    def ask_v1(
        payload: VersionedAskRequest,
        credentials: HTTPAuthorizationCredentials | None = Depends(_PRODUCT_QA_BEARER),
    ) -> JSONResponse:
        request_started_at = time.monotonic()
        configured_key = get_runtime_settings().integration_api_key
        if not configured_key:
            return JSONResponse({"error": "service_not_configured"}, status_code=503)
        if (
            credentials is None
            or credentials.scheme.casefold() != "bearer"
            or not credentials.credentials
        ):
            return JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not hmac.compare_digest(credentials.credentials, configured_key):
            return JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not rate_limiter.allow(credentials.credentials):
            return JSONResponse(
                {"error": "rate_limited"},
                status_code=429,
                headers={"Retry-After": "60"},
            )

        article = payload.article.strip()
        question = payload.question.strip()
        if not article or not question:
            return JSONResponse({"error": "invalid_request"}, status_code=422)
        try:
            active = get_services()
            with active["catalog"].connection_scope() as connection:
                products = active["catalog"].search_products(article, connection=connection)
        except Exception as error:
            _log_catalog_unavailable(error)
            return JSONResponse({"error": "catalog_unavailable"}, status_code=503)
        if not products:
            return JSONResponse({"error": "product_not_found"}, status_code=404)
        if len(products) != 1:
            return JSONResponse({"error": "product_selection_required"}, status_code=409)
        try:
            attempt = active["assistant"].submit(
                products[0],
                question,
                history=payload.history,
                request_started_at=request_started_at,
            )
        except QuestionRejected as error:
            return JSONResponse({"error": error.code}, status_code=422)
        except Exception:
            return JSONResponse({"error": "answer_unavailable"}, status_code=502)
        if attempt.status != "succeeded" or not attempt.answer:
            return JSONResponse({"error": "answer_unavailable"}, status_code=502)
        return JSONResponse({"status": "succeeded", "answer": attempt.answer})

    @app.post(
        "/api/v1/ask/stream",
        responses=_VERSIONED_STREAM_RESPONSES,
        response_model=None,
    )
    def ask_v1_stream(
        payload: VersionedAskRequest,
        credentials: HTTPAuthorizationCredentials | None = Depends(_PRODUCT_QA_BEARER),
    ) -> EventSourceResponse | JSONResponse:
        request_started_at = time.monotonic()
        configured_key = get_runtime_settings().integration_api_key
        if not configured_key:
            return JSONResponse({"error": "service_not_configured"}, status_code=503)
        if (
            credentials is None
            or credentials.scheme.casefold() != "bearer"
            or not credentials.credentials
        ):
            return JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not hmac.compare_digest(credentials.credentials, configured_key):
            return JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not rate_limiter.allow(credentials.credentials):
            return JSONResponse(
                {"error": "rate_limited"},
                status_code=429,
                headers={"Retry-After": "60"},
            )

        article = payload.article.strip()
        question = payload.question.strip()
        if not article or not question:
            return JSONResponse({"error": "invalid_request"}, status_code=422)
        try:
            active = get_services()
            with active["catalog"].connection_scope() as connection:
                products = active["catalog"].search_products(
                    article, connection=connection
                )
        except Exception as error:
            _log_catalog_unavailable(error)
            return JSONResponse({"error": "catalog_unavailable"}, status_code=503)
        if not products:
            return JSONResponse({"error": "product_not_found"}, status_code=404)
        if len(products) != 1:
            return JSONResponse({"error": "product_selection_required"}, status_code=409)
        events = active["assistant"].stream(
            products[0],
            question,
            history=payload.history,
            request_started_at=request_started_at,
        )
        return _sse_response(events)

    @app.get(
        "/api/v1/products/{article}/suggested-questions",
        include_in_schema=False,
    )
    def get_suggested_questions_v1(
        article: str,
        credentials: HTTPAuthorizationCredentials | None = Depends(_PRODUCT_QA_BEARER),
    ) -> JSONResponse:
        configured_key = get_runtime_settings().integration_api_key
        if configured_key:
            if (
                credentials is None
                or credentials.scheme.casefold() != "bearer"
                or not credentials.credentials
                or not hmac.compare_digest(credentials.credentials, configured_key)
            ):
                return JSONResponse(
                    {"error": "unauthorized"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
        clean_article = article.strip()
        if not clean_article:
            return JSONResponse({"error": "invalid_request"}, status_code=422)
        try:
            active = get_services()
            with active["catalog"].connection_scope() as connection:
                products = active["catalog"].search_products(
                    clean_article, connection=connection
                )
        except Exception as error:
            _log_catalog_unavailable(error)
            return JSONResponse({"error": "catalog_unavailable"}, status_code=503)
        if not products:
            return JSONResponse({"error": "product_not_found"}, status_code=404)
        if len(products) != 1:
            return JSONResponse({"error": "product_selection_required"}, status_code=409)

        product = products[0]
        uk_card = product.languages.get("uk") or product.languages.get("ru")
        name = uk_card.name if uk_card else (product.model or product.article)
        return JSONResponse(
            {
                "status": "succeeded",
                "article": product.article,
                "product_name": name,
                "suggested_questions": get_suggested_questions(product),
            }
        )

    return app


def _sse_response(events) -> EventSourceResponse:
    def frames():
        yield _sse_frame("start", {"status": "started"})
        try:
            for event in events:
                event_type = event.get("type")
                if event_type == "delta":
                    payload = {"text": event.get("text", "")}
                elif event_type == "replace":
                    payload = {"answer": event.get("answer", "")}
                elif event_type == "error":
                    payload = {"error": "answer_unavailable"}
                elif event_type == "done":
                    payload = {"status": "succeeded"}
                else:
                    continue
                yield _sse_frame(event_type, payload)
        except Exception:
            yield _sse_frame("error", {"error": "answer_unavailable"})

    return EventSourceResponse(
        frames(),
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


def _sse_frame(event: str, payload: dict[str, str]) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}\n\n"
    )


def _product_payload(product: Product) -> dict[str, Any]:
    return {
        "product_id": product.product_id,
        "article": product.article,
        "model": product.model,
        "sku": product.sku,
        "languages": {
            language: _language_payload(card)
            for language, card in product.languages.items()
        },
        "suggested_questions": get_suggested_questions(product),
    }


def _language_payload(card: LanguageCard) -> dict[str, Any]:
    return {
        "language": card.language,
        "name": card.name,
        "description": html_to_safe_text(card.description) if card.description else None,
        "attributes": [asdict(attribute) for attribute in card.attributes],
        "stock_label": card.stock_label,
    }


def _attempt_payload(attempt: JournalAttempt) -> dict[str, Any]:
    return {
        "attempt_id": attempt.attempt_id,
        "submitted_at": attempt.submitted_at,
        "article": attempt.article,
        "product_model": attempt.product_model,
        "product_sku": attempt.product_sku,
        "product_name": attempt.product_name,
        "question": attempt.question,
        "status": attempt.status,
        "answer": attempt.answer,
        "error_code": attempt.error_code,
        "model_name": attempt.model_name,
        "prompt_version": attempt.prompt_version,
    }


app = create_app()
