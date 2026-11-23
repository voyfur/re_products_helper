# Session Handoff

## Active Context

- Last session: `raw/sessions/2026-11-23-add-product-qa-streaming-and-typing.md`
- Current objective: Add Product QA streaming and typing

## Current Decisions

- Keep POST /api/v1/ask as JSON and add POST /api/v1/ask/stream for SSE.
- Typing and streamed answer are available in the local QA UI; conversation history stays hidden and volatile.
- The site backend must proxy the stream server-side with buffering disabled and keep credentials server-side.

## Open Tasks

- Connect the website backend to the versioned JSON or SSE endpoint; no storefront code is connected by this implementation.
- Complete target VPS configuration and acceptance separately; no deployment was performed.
- Provide the target Product QA repository if this local branch should be published.

## Blockers

- No blockers recorded.

## Next Action

- Use docs/api/product-qa-integration.md for the site-backend handoff and docs/deployment/product-qa-vps-runbook.md for VPS acceptance.
- Keep this branch local until a Product QA repository target is supplied.

## Relevant Pages

- wiki/index.md
- wiki/sources/race-expert-qa-project.md
- wiki/syntheses/race-expert-qa-evaluation.md
- wiki/syntheses/race-expert-qa-web-search.md
- wiki/syntheses/race-expert-qa-production-readiness.md
- docs/api/product-qa-integration.md
- docs/api/product-qa-v1.yaml
- docs/deployment/product-qa-vps-runbook.md
