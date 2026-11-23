# Product QA streaming and typing design

## Goal

Prepare the Product QA backend for a site programmer to deploy and connect to the Race Expert site. Keep the existing complete JSON answer API, add a real server-to-server answer stream, and provide a reference typing indicator in the local QA UI.

## Integration boundary

- Product QA owns catalog revalidation, answer policy, provider calls, stream framing, and API documentation.
- The site backend owns its browser-facing proxy route and keeps the Product QA bearer credential in server-side configuration.
- The storefront browser never calls Product QA directly and never receives OpenAI, Tavily, database, SSH, or Product QA credentials.
- This work does not change storefront code, configure a production hostname, deploy to VPS, or send paid live provider requests.

## Endpoints

- `POST /api/v1/ask` remains unchanged and returns one complete JSON answer.
- `POST /api/v1/ask/stream` accepts the same bearer authentication, request body, limits, catalog resolution, and request rate limit as the JSON endpoint.
- Before the stream begins, authentication, request validation, rate limiting, and exact product resolution return the existing normal JSON error statuses.
- Successful streaming responses use `text/event-stream` and these JSON data events:
  - `start`: `{ "status": "started" }`
  - `delta`: `{ "text": "..." }`, incremental Ukrainian answer text
  - `replace`: `{ "answer": "..." }`, replaces accumulated deltas if final buyer-safe sanitization changes them
  - `done`: `{ "status": "succeeded" }`
  - `error`: `{ "error": "answer_unavailable" }`; the client clears partial answer text and does not add a failed turn to history
- No event includes source URLs, domains, provenance, internal attempt identifiers, buyer data, or prior conversation history.

## Safety and stream behavior

- Revalidate the exact article against the read-only catalog before returning a stream.
- Run out-of-scope and personal-health checks, including relevant same-product prior user context, before exposing answer text. The fixed health refusal remains dose-free.
- Keep the Responses API strict structured output and place `product_related` and `health_related` flags before `answer` in the schema. Stream only after the product-related flag is confirmed true; redirect with the fixed answer when false.
- A search decision and Tavily search complete before final answer deltas are exposed. Never stream tool arguments, raw provider events, evidence excerpts, URLs, or provenance.
- Apply the backend buyer-safe answer check to the completed response. If it changes streamed text, send `replace` with the final safe response. Append the fixed health disclaimer after generated deltas when required.
- On provider failure after the SSE response starts, send the sanitized `error` event and let the site discard partial output. Do not include exception text.
- Continue to cap request bodies at 16 KiB, keep history optional and limited to nine prior messages, and remove oldest whole history messages in the caller rather than truncate the current question.

## Browser/UI behavior

- The local QA UI is a reference for the site programmer: after submit it shows an animated typing state, renders `delta` events incrementally, handles `replace`, and hides the typing state on `done` or `error`.
- The UI keeps at most ten transcript messages in volatile page memory, sends up to nine prior messages plus the current question, and never displays the prior-message context as a separate transcript or counter.
- It clears that context on product change or page reload and does not add partial/failed turns.
- The site programmer implements an equivalent browser-facing route on the site backend and forwards the SSE stream. Use `fetch` streaming for a POST request; do not expose the Product QA bearer key to browser JavaScript.

## Deployment/handoff

- Update OpenAPI, README, integration guide, widget brief, production blueprint, reverse-proxy example, and container smoke coverage.
- The reverse proxy must forward the stream without buffering and allow the existing provider timeout budget.
- Production deployment and GitHub publication are separate operational steps. Do not configure DNS or alter the live storefront as part of this feature.
