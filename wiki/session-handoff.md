# Session Handoff

## Active Context

- Last session: `raw/sessions/2026-11-23-record-product-qa-implementation-and-github-hand.md`
- Current objective: Record Product QA implementation and GitHub handoff in Wiki

## Current Decisions

- Keep POST /api/v1/ask JSON-compatible and expose SSE through POST /api/v1/ask/stream with start/delta/replace/done/error events.
- The site backend must keep the bearer key server-side and proxy SSE without buffering; the site UI owns its typing indicator.
- Temporary history is optional, hidden, same-product, untrusted, in-memory only, max nine prior messages plus the current question, with the 16 KiB body cap preserved.
- No storefront, VPS, staging, or production changes and no paid live OpenAI/Tavily calls were made.

## Open Tasks

- Website programmer: connect the site backend to the versioned JSON/SSE API, proxy the stream without buffering, and implement the browser typing/stream UI.
- Operator: deploy for the target VPS architecture; configure server-side keys, MySQL read-only grants and TLS verification, reverse proxy, persistent SQLite storage, backups, and acceptance.

## Blockers

- No blockers recorded.

## Next Action

- Start the programmer handoff from the private repository https://github.com/voyfur/re_qa and integration guide docs/api/product-qa-integration.md.
- Use docs/deployment/product-qa-vps-runbook.md for VPS installation and acceptance after site-backend integration.

## Relevant Pages

- wiki/index.md
- wiki/session-handoff.md
- wiki/sources/race-expert-qa-project.md
- wiki/syntheses/race-expert-qa-production-readiness.md
- docs/api/product-qa-integration.md
- docs/api/product-qa-v1.yaml
- docs/deployment/product-qa-vps-runbook.md
- docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md
- docs/superpowers/plans/2026-11-23-product-qa-streaming-and-typing.md
