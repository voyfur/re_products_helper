# Session Handoff

## Active Context

- Last session: `raw/sessions/2026-11-22-race-expert-qa-v18-update.md`
- Current objective: Race Expert QA v18 update

## Current Decisions

- Prompt v18 is active with the approved balanced general-sports conclusion and sport-specific limitation; v17 and its pinned hash remain unchanged.
- The API accepts optional history with up to nine prior user/assistant messages; the current question is separate. Context is same-product/session, untrusted, non-persistent, and excluded from history logging.
- The local UI keeps up to ten messages in page memory, clears on new product search or reload, and removes oldest whole history messages to fit 16 KiB without shortening the current question.
- Clear dependent personal-health safety/dose follow-ups use the fixed refusal before provider calls; prior user health context includes common condition terms such as asthma.
- Active checkout: /Users/anatoly/Workspace/03_Business/WORK/Race Expert/QA/.codex-checkouts/product-qa-v18; this is a local snapshot repository on branch codex/product-qa-v18 with no remote/upstream.

## Open Tasks

- Integrate the versioned Product QA API with the website backend server-to-server, keeping credentials server-side and scoping history to the same product/page session.
- Complete target-VPS image/platform selection, MySQL TLS and read-only grants, HTTPS reverse-proxy routing, persistent journal storage, backup/restore, and operational acceptance.

## Blockers

- No blockers recorded.

## Next Action

- Continue work only in /Users/anatoly/Workspace/03_Business/WORK/Race Expert/QA/.codex-checkouts/product-qa-v18 and inspect git status before making further edits.
- Use docs/deployment/product-qa-vps-runbook.md for the separate site-backend/VPS handoff; this implementation did not deploy or connect the storefront.

## Relevant Pages

- wiki/index.md
- wiki/session-handoff.md
- wiki/syntheses/race-expert-qa-evaluation.md
- wiki/syntheses/race-expert-qa-web-search.md
- wiki/syntheses/race-expert-qa-production-readiness.md
- docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md
- docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md
- docs/api/product-qa-v1.yaml
- docs/api/product-qa-integration.md
- docs/deployment/product-qa-vps-runbook.md
