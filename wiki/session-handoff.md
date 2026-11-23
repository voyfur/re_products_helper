# Session Handoff

## Active Context

- Last session: `raw/sessions/2026-11-23-publish-product-qa-streaming-handoff.md`
- Current objective: Publish Product QA streaming handoff
- Preserved local checkout: `/Users/anatoly/Workspace/03_Business/WORK/Race Expert/QA/.codex-checkouts/product-qa-v18` (branch `codex/product-qa-v18`)

## Current Decisions

- Keep website credentials server-side and proxy JSON or SSE POST from the site backend.
- Do not deploy to VPS, staging, or production as part of this handoff.

## Open Tasks

- Website programmer must connect the site backend to the versioned JSON/SSE API.
- Operator must configure the target VPS, database TLS/read-only access, reverse proxy, persistence, and acceptance checks.

## Blockers

- No blockers recorded.

## Next Action

- Use docs/api/product-qa-integration.md for website backend integration.
- Use docs/deployment/product-qa-vps-runbook.md for operator VPS installation and acceptance.

## Relevant Pages

- wiki/index.md
- wiki/sources/race-expert-qa-project.md
- wiki/syntheses/race-expert-qa-production-readiness.md
- docs/api/product-qa-integration.md
- docs/deployment/product-qa-vps-runbook.md
- docs/superpowers/plans/2026-11-23-product-qa-streaming-and-typing.md
