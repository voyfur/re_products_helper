from __future__ import annotations

import json
import re
import socket
from dataclasses import dataclass
from typing import Callable, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SEARCH_TIMEOUT_SECONDS = 10
MAX_RESULTS = 5
_MAX_RESPONSE_BYTES = 1_000_000
_MAX_FIELD_CHARS = 4_000
_TAVILY_SEARCH_URL = "https://api.tavily.com/search"
_DOMAIN_RE = re.compile(
    r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}\Z",
    re.IGNORECASE,
)


class SearchProviderError(RuntimeError):
    """A provider failure with a stable, sanitized error code."""

    CODES = frozenset(
        {
            "search_key_unavailable",
            "search_timeout",
            "search_provider_error",
            "search_invalid_response",
        }
    )

    def __init__(self, code: str) -> None:
        if code not in self.CODES:
            code = "search_provider_error"
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    content: str


class TavilySearchClient:
    """Make one bounded Tavily Search API request and keep only excerpts."""

    def __init__(
        self,
        api_key: str | None,
        *,
        opener: Callable[..., object] = urlopen,
    ) -> None:
        self._api_key = api_key.strip() if isinstance(api_key, str) else ""
        self._opener = opener

    def search(self, query: str, include_domains: Sequence[str]) -> list[SearchResult]:
        if not self._api_key:
            raise SearchProviderError("search_key_unavailable")
        if not isinstance(query, str) or not query.strip():
            raise SearchProviderError("search_provider_error")
        domains = _validated_domains(include_domains)
        if not domains:
            raise SearchProviderError("search_provider_error")

        body = json.dumps(
            {
                "query": query.strip(),
                "search_depth": "fast",
                "max_results": MAX_RESULTS,
                "chunks_per_source": 1,
                "include_domains": domains,
                "include_domains_mode": "restrict",
                "include_raw_content": False,
                "include_answer": False,
            },
            separators=(",", ":"),
        ).encode("utf-8")
        request = Request(
            _TAVILY_SEARCH_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            response = self._opener(request, timeout=SEARCH_TIMEOUT_SECONDS)
            try:
                payload = response.read(_MAX_RESPONSE_BYTES + 1)
            finally:
                close = getattr(response, "close", None)
                if callable(close):
                    close()
        except (TimeoutError, socket.timeout):
            raise SearchProviderError("search_timeout") from None
        except HTTPError:
            raise SearchProviderError("search_provider_error") from None
        except URLError as error:
            if isinstance(error.reason, (TimeoutError, socket.timeout)):
                raise SearchProviderError("search_timeout") from None
            raise SearchProviderError("search_provider_error") from None
        except OSError:
            raise SearchProviderError("search_provider_error") from None
        except Exception:
            raise SearchProviderError("search_provider_error") from None

        if not isinstance(payload, bytes) or len(payload) > _MAX_RESPONSE_BYTES:
            raise SearchProviderError("search_invalid_response")
        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise SearchProviderError("search_invalid_response") from None
        if not isinstance(decoded, dict) or not isinstance(decoded.get("results"), list):
            raise SearchProviderError("search_invalid_response")

        results: list[SearchResult] = []
        for item in decoded["results"][:MAX_RESULTS]:
            if not isinstance(item, dict):
                raise SearchProviderError("search_invalid_response")
            title, url, content = item.get("title"), item.get("url"), item.get("content")
            if not all(isinstance(value, str) for value in (title, url, content)):
                raise SearchProviderError("search_invalid_response")
            if not title.strip() or not url.strip():
                raise SearchProviderError("search_invalid_response")
            results.append(
                SearchResult(
                    title=title[:_MAX_FIELD_CHARS],
                    url=url[:_MAX_FIELD_CHARS],
                    content=content[:_MAX_FIELD_CHARS],
                )
            )
        return results


def _validated_domains(include_domains: Sequence[str]) -> list[str]:
    if isinstance(include_domains, (str, bytes)):
        return []
    try:
        values = list(include_domains)
    except TypeError:
        return []
    domains: list[str] = []
    for value in values:
        if not isinstance(value, str):
            return []
        hostname = value.strip()
        if (
            hostname != hostname.lower()
            or not _DOMAIN_RE.fullmatch(hostname)
            or "*" in hostname
            or hostname in domains
        ):
            if hostname in domains:
                continue
            return []
        domains.append(hostname)
    return domains
