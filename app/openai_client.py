from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

from app.search_evidence import SearchTopic


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
SEARCH_TOOL_NAME = "request_product_search"


class ProviderError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class AssistantDecision:
    answer: str | None = None
    search_topic: SearchTopic | None = None
    health_related: bool = True
    product_related: bool = True


@dataclass(frozen=True)
class StructuredAnswer:
    answer: str
    health_related: bool
    product_related: bool = True


_DIRECT_ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "health_related": {"type": "boolean"},
        "product_related": {"type": "boolean"},
    },
    "required": ["answer", "health_related", "product_related"],
    "additionalProperties": False,
}

_FINAL_ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "health_related": {"type": "boolean"},
        "product_related": {"type": "boolean"},
    },
    "required": ["answer", "health_related", "product_related"],
    "additionalProperties": False,
}


class OpenAIResponsesClient:
    def __init__(
        self,
        api_key: str | None,
        *,
        opener: Callable[..., Any] = urllib.request.urlopen,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.opener = opener
        self.timeout = timeout

    def decide(
        self,
        *,
        instructions: str,
        product_context: str,
        question: str,
    ) -> AssistantDecision:
        body = self._request(
            instructions=instructions,
            input_text=(
                f"Факти поточної картки товару:\n{product_context}\n\n"
                f"Поточне запитання покупця:\n{question}"
            ),
            tools=[
                {
                    "type": "function",
                    "name": SEARCH_TOOL_NAME,
                    "description": (
                        "Request one backend search for a fixed product topic when the "
                        "revalidated card cannot answer or the buyer asks about subjective reviews."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "enum": [topic.value for topic in SearchTopic],
                            },
                            "product_related": {"type": "boolean"},
                        },
                        "required": ["topic", "product_related"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            ],
            tool_choice="auto",
            parallel_tool_calls=False,
            text_format={
                "type": "json_schema",
                "name": "product_qa_direct_answer",
                "strict": True,
                "schema": _DIRECT_ANSWER_SCHEMA,
            },
        )
        calls = self._function_calls(body)
        if calls:
            if len(calls) != 1 or calls[0].get("name") != SEARCH_TOOL_NAME:
                raise ProviderError("provider_invalid_response")
            try:
                arguments = json.loads(calls[0].get("arguments", ""))
                product_related = arguments["product_related"]
                if not isinstance(product_related, bool):
                    raise ValueError
                if not product_related:
                    return AssistantDecision(product_related=False)
                topic = SearchTopic(arguments["topic"])
            except (TypeError, ValueError, KeyError, json.JSONDecodeError):
                raise ProviderError("provider_invalid_response") from None
            return AssistantDecision(search_topic=topic, product_related=True)

        payload = self._structured_payload(body)
        answer = payload.get("answer")
        if not isinstance(answer, str) or not answer.strip():
            raise ProviderError("provider_empty_response")
        health_related = payload.get("health_related")
        product_related = payload.get("product_related")
        return AssistantDecision(
            answer=answer.strip(),
            health_related=health_related if isinstance(health_related, bool) else True,
            product_related=product_related if isinstance(product_related, bool) else False,
        )

    def answer_with_evidence(
        self,
        *,
        instructions: str,
        product_context: str,
        question: str,
        evidence: str,
    ) -> StructuredAnswer:
        body = self._request(
            instructions=instructions,
            input_text=(
                f"Факти повторно перевіреної картки:\n{product_context}\n\n"
                f"Поточне запитання покупця:\n{question}\n\n"
                f"Компактні перевірені зовнішні дані для цього товару:\n"
                f"{evidence or 'Немає точних підтверджених веб-даних.'}"
            ),
            text_format={
                "type": "json_schema",
                "name": "product_qa_final_answer",
                "strict": True,
                "schema": _FINAL_ANSWER_SCHEMA,
            },
        )
        if self._function_calls(body):
            raise ProviderError("provider_invalid_response")
        try:
            payload = self._structured_payload(body)
        except ProviderError:
            return StructuredAnswer(
                answer="Не вдалося сформувати перевірену відповідь за наявними даними.",
                health_related=True,
                product_related=True,
            )
        answer = payload.get("answer")
        health_related = payload.get("health_related")
        product_related = payload.get("product_related")
        if not isinstance(answer, str) or not answer.strip():
            return StructuredAnswer(
                answer="Не вдалося сформувати перевірену відповідь за наявними даними.",
                health_related=True,
                product_related=True,
            )
        return StructuredAnswer(
            answer=answer.strip(),
            health_related=health_related if isinstance(health_related, bool) else True,
            product_related=product_related if isinstance(product_related, bool) else False,
        )

    def _request(
        self,
        *,
        instructions: str,
        input_text: str,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
        parallel_tool_calls: bool | None = None,
        text_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ProviderError("provider_unavailable")
        payload: dict[str, Any] = {
            "model": "gpt-6-luna",
            "instructions": instructions,
            "input": input_text,
            "reasoning": {"effort": "medium"},
            "max_output_tokens": 2048,
            "store": False,
        }
        if tools is not None:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice or "auto"
            payload["parallel_tool_calls"] = bool(parallel_tool_calls)
        if text_format is not None:
            payload["text"] = {"format": text_format}

        request = urllib.request.Request(
            OPENAI_RESPONSES_URL,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                body = json.loads(response.read())
        except urllib.error.HTTPError:
            raise ProviderError("provider_error") from None
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            raise ProviderError("provider_unavailable") from None
        if not isinstance(body, dict):
            raise ProviderError("provider_invalid_response")
        return body

    @staticmethod
    def _function_calls(body: dict[str, Any]) -> list[dict[str, Any]]:
        output = body.get("output", [])
        if not isinstance(output, list):
            raise ProviderError("provider_invalid_response")
        return [
            item
            for item in output
            if isinstance(item, dict) and item.get("type") == "function_call"
        ]

    @classmethod
    def _structured_payload(cls, body: dict[str, Any]) -> dict[str, Any]:
        answer = body.get("output_text")
        if not isinstance(answer, str):
            answer = cls._extract_output_text(body)
        if not isinstance(answer, str) or not answer.strip():
            raise ProviderError("provider_empty_response")
        try:
            payload = json.loads(answer)
        except json.JSONDecodeError:
            raise ProviderError("provider_invalid_response") from None
        if not isinstance(payload, dict):
            raise ProviderError("provider_invalid_response")
        return payload

    @staticmethod
    def _extract_output_text(body: dict[str, Any]) -> str:
        parts: list[str] = []
        output = body.get("output", [])
        if not isinstance(output, list):
            return ""
        for item in output:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "message" or item.get("role") != "assistant":
                continue
            for content in item.get("content", []):
                if (
                    isinstance(content, dict)
                    and content.get("type") == "output_text"
                    and isinstance(content.get("text"), str)
                ):
                    parts.append(content["text"])
        return "\n".join(parts)
