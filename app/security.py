import json
from typing import Any, Awaitable, Callable

from fastapi import Request, Response


class AskBodySizeLimit:
    def __init__(self, app: Callable[..., Awaitable[Any]], max_bytes: int = 16_384):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send) -> None:
        if not (
            scope.get("type") == "http"
            and scope.get("method") == "POST"
            and scope.get("path") in {"/api/ask", "/api/v1/ask"}
        ):
            await self.app(scope, receive, send)
            return

        messages = []
        total = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                messages.append(message)
                continue
            total += len(message.get("body", b""))
            if total > self.max_bytes:
                body = json.dumps({"error": "request_too_large"}).encode("utf-8")
                await send(
                    {
                        "type": "http.response.start",
                        "status": 413,
                        "headers": [(b"content-type", b"application/json")],
                    }
                )
                await send({"type": "http.response.body", "body": body})
                return
            messages.append(message)
            if not message.get("more_body", False):
                break

        index = 0

        async def replay_receive():
            nonlocal index
            if index < len(messages):
                message = messages[index]
                index += 1
                return message
            return await receive()

        await self.app(scope, replay_receive, send)


async def security_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    )
    return response
