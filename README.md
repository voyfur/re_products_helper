# Race Expert Product QA backend

Standalone product question-and-answer API with a local reference UI. The storefront and the website backend are separate systems and are not included here. The active assistant prompt is v18; v17 and earlier prompt files remain preserved and pinned.

## API for the website backend

Use the versioned server-to-server endpoints:

- `POST /api/v1/ask` returns a complete JSON answer.
- `POST /api/v1/ask/stream` returns an SSE stream for incremental display and a typing indicator.

Both accept the same `article` and current `question`; optional `history` carries up to nine earlier user/assistant messages for the same product page. Requests without history remain compatible. The body limit is 16 KiB: remove oldest whole history messages to fit and never shorten the current question. History is hidden, temporary, untrusted context and is not persisted or logged as conversation history.

The browser should call the website's own backend. That backend stores the Product QA bearer key and calls these endpoints server-side. For SSE, proxy `text/event-stream` without buffering; the site UI handles `start`, `delta`, `replace`, `done`, and `error` events. The local reference UI demonstrates streaming and typing behavior.

See the [OpenAPI contract](docs/api/product-qa-v1.yaml), [integration handoff](docs/api/product-qa-integration.md), and [widget brief](docs/ui/product-qa-widget-brief.md).

## Service behavior

Product QA resolves and revalidates the exact product against the read-only catalog for every request. It uses prompt v18 and approved exact-product evidence; customer-specific health questions follow the fixed refusal rules. The API does not return source provenance. The attempt journal is separate from the temporary conversation context.

## Configuration and deployment

The Docker image runs as a non-root user and exposes the service on port 8787. Configure MySQL TLS with trusted CA and hostname verification, read-only access to the five product-card tables, server-side provider credentials, and a separate Product QA integration key. Never put credentials in this repository or browser code.

Deployment artifacts are in [`deploy/`](deploy/). Follow the [production blueprint](docs/deployment/product-qa-production-blueprint.md) and [VPS install runbook](docs/deployment/product-qa-vps-runbook.md). The Nginx example disables buffering for the stream route. These files are handoff templates; this repository does not deploy them or modify the storefront.

## Verification

The tests use offline fixtures and mocks; they do not require live OpenAI or Tavily calls:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The synthetic container smoke is in `scripts/container_smoke.py`. Production acceptance, target-VPS architecture, TLS, database grants, backups, and website-backend integration must be verified by the operator before serving traffic.
