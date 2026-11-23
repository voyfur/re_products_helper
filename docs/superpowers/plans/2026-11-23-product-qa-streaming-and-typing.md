# Product QA streaming and typing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a backward-compatible Product QA SSE endpoint, real upstream Responses API streaming, a local typing reference UI, and deployment-ready integration documentation.

**Architecture:** Keep `/api/v1/ask` synchronous and add `/api/v1/ask/stream` using `text/event-stream`. Stream only strict structured answer text after product/safety flags, preserve assistant journaling and evidence filtering, and use the same local stream path for the internal reference UI. The site programmer proxies the server-to-server stream through their own backend; no storefront or production server code is changed here.

**Tech Stack:** Python 3.12, FastAPI 0.162.2, urllib Responses API SSE, Pydantic, vanilla JavaScript, OpenAPI 3.1, pytest, Docker container smoke.

---

### Task 1: Lock the SSE framing and provider stream parser with offline tests

**Files:**
- Modify: `tests/test_web_search.py`
- Create: `tests/test_streaming.py`
- Modify: `app/openai_client.py`

- [x] Write tests for parsing Responses SSE frames split across lines, ignored keepalive comments, malformed event JSON, missing completion, provider error events, and exact request fields including `stream: true`.
- [x] Write failing tests for streaming structured JSON with flags ordered before `answer`; assert no text is emitted before `product_related=true` and `health_related` is parsed, JSON escapes decode correctly, and provider completion matches the parsed answer.
- [x] Run `python -m pytest tests/test_streaming.py -q` and verify the new tests fail because no stream parser or stream methods exist.
- [x] Implement the minimal `OpenAIResponsesClient` stream request/parser and incremental structured-answer decoder, preserving the existing non-stream request path when no stream method is used.
- [x] Re-run `python -m pytest tests/test_streaming.py -q` and confirm the mocked stream tests pass without network access.

### Task 2: Stream the existing assistant decision/search/safety flow

**Files:**
- Modify: `app/assistant.py`
- Modify: `tests/test_web_search.py`
- Modify: `tests/test_streaming.py`

- [x] Add assistant stream tests for the direct-answer path, search decision followed by evidence answer, out-of-scope fixed answer, personal-health fixed refusal using prior user context, missing model classification, provider failure after partial output, and URL/domain replacement.
- [ ] Run the focused streaming and search tests to confirm the new cases fail.
- [x] Implement a streaming submission path that reuses the existing exact-product context, search allowlist, provenance filtering, journal metadata, fixed redirects/refusals, and disclaimer rules.
- [x] Ensure provider tool arguments, URLs, provenance, and unsafe domain tokens never become `delta` events; emit a final `replace` only when the completed safety check changes streamed text.
- [x] Run the focused tests and confirm successful attempts are journaled, errors remain sanitized, and the existing non-stream assistant path is unchanged.

### Task 3: Add authenticated public and local SSE routes

**Files:**
- Modify: `app/main.py`
- Modify: `tests/test_qa_app.py`
- Modify: `tests/conftest.py`

- [x] Add failing tests for `/api/v1/ask/stream` authentication, rate limiting, request/body limits, optional history forwarding, exact catalog revalidation, SSE content type/headers/events, pre-stream JSON errors, and post-start sanitized error events.
- [x] Add failing tests for the loopback-only `/api/ask/stream` reference route, including product revalidation and omission of internal journal metadata.
- [ ] Run the focused API tests and verify they fail because the stream routes do not exist.
- [x] Implement both routes using the same request schemas, auth/rate limiter, body cap, product lookup, and response/error codes as the existing JSON API. Use FastAPI's pinned SSE response support and disable proxy buffering through response headers.
- [x] Confirm generated OpenAPI lists `/api/v1/ask`, `/api/v1/ask/stream`, and `/health`, and that `/api/v1/ask` still returns the same JSON schema.
- [x] Re-run focused API tests and confirm both streaming and backwards compatibility pass.

### Task 4: Implement typing and incremental rendering in the internal QA UI

**Files:**
- Modify: `app/templates/index.html`
- Modify: `app/static/app.js`
- Modify: `app/static/app.css`
- Modify: `tests/test_qa_app.py`

- [x] Add UI assertions that the page contains an accessible typing indicator and no visible prior-history transcript/counter.
- [x] Implement POST `fetch` stream reading for the local QA route; render `delta`, overwrite on `replace`, clear partial text and skip history append on `error`, and hide typing on completion.
- [x] Keep `conversationHistory` in memory only, add turns only after successful `done`, send up to nine prior messages, and reset on product search or reload.
- [x] Bump static asset query versions and verify with `node --check app/static/app.js` plus a browser run using a synthetic local catalog/provider response; do not call OpenAI or Tavily live.

### Task 5: Publish a complete handoff contract and proxy requirements

**Files:**
- Modify: `README.md`
- Modify: `docs/api/product-qa-v1.yaml`
- Modify: `docs/api/product-qa-integration.md`
- Modify: `docs/ui/product-qa-widget-brief.md`
- Modify: `docs/deployment/product-qa-production-blueprint.md`
- Modify: `deploy/nginx-race-expert-qa.conf.example`

- [x] Document the exact POST request, SSE response headers/events, same-request limits, pre-stream HTTP errors, post-start SSE errors, and client handling rules.
- [x] Document that the site backend calls Product QA with the bearer key and proxies the stream to its own browser-facing endpoint; show fetch-based browser stream parsing because the site request is a POST.
- [x] Document the typing indicator and the hidden, volatile same-product history behavior; do not describe any site endpoint as already deployed.
- [x] Add an exact Nginx stream location with `proxy_buffering off`, the existing bearer-forwarding and rate limit, and a sufficient read timeout; leave `/ready` private.
- [x] Review all docs for unsupported claims about production deployment, DNS, TLS, provider progress, or storefront changes.

### Task 6: Extend offline container smoke and run the final verification suite

**Files:**
- Modify: `scripts/container_smoke.py`
- Modify: `README.md`

- [x] Extend the synthetic container smoke assistant to yield stream events and assert `/api/v1/ask/stream` returns `start`, `delta`, and `done` while `/api/v1/ask` remains JSON.
- [x] Run focused tests: `python -m pytest tests/test_streaming.py tests/test_qa_app.py tests/test_web_search.py -q`.
- [x] Run full offline tests: `python -m pytest -q`.
- [x] Run `node --check app/static/app.js`, `git diff --check`, and Docker container smoke using `--network none`; do not use OpenAI or Tavily live.
- [x] Inspect the final diff for accidental changes to storefront/backend-site code, secrets, source URLs/provenance, or prompt v12–v18 hashes.

### Task 7: Prepare the GitHub handoff

**Files:**
- Modify: `docs/superpowers/specs/2026-11-23-product-qa-streaming-and-typing-design.md`
- Modify: `docs/superpowers/plans/2026-11-23-product-qa-streaming-and-typing.md`

- [x] Commit the verified feature on the dedicated Product QA branch.
- [x] Publish the verified handoff only to the Product QA repository `voyfur/re_qa`; do not publish to the unrelated `raceexpert-summary-service` repository.
- [x] Keep the branch local while no target was available; after the user provided `voyfur/re_qa`, publish the curated handoff snapshot there.
- [x] Leave VPS/staging/production deployment to the site programmer and report the complete endpoint handoff.

### Execution notes

- The Task 2 and Task 3 implementation groups were verified by their final focused tests, but the pre-implementation red runs were not performed. The corresponding red-run checklist items remain unchecked.
- The verified handoff snapshot was published to private repository `voyfur/re_qa` on `main`. The snapshot includes the backend, active/history prompts, tests, deployment files, and programmer-facing docs; it excludes Wiki, raw session/source records, and eval archives. No storefront, VPS, staging, or production code was changed or deployed.
