---
id: "session-2026-11-21T18-53-26plus-02-00-run-one-bounded-product-qa-e2e-and-prepare-vps-d"
started_at: "2026-11-21T18:15:00+02:00"
ended_at: "2026-11-21T18:53:26+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Run one bounded Product QA E2E and prepare VPS developer handoff"
status: "partial"
transcript_source: "faithful-summary"
summary: "Ran one local live E2E request for RE89157 through the approved SSH-tunnel launcher. Catalog resolution, Tavily invocation, and exact official source filtering succeeded; v14 returned a safe abstention instead of the requested new serving-count fact. Reworked deployment docs so the VPS operator chooses hostname/DNS at installation, added a practical VPS runbook, and disabled local Uvicorn access logs. No additional live call, staging, storefront change, or deployment occurred."
decisions: ["Do not require a DNS record or fixed hostname to hand off the repository; the VPS operator sets the hostname, DNS, TLS certificate, and reverse proxy during installation.", "Record the live check as a technical source-path pass and a positive-answer failure; the exact official record was accepted but the answer did not confirm the asked fact.", "Do not repeat paid live requests without a separate user request.", "Keep provider/API credentials owner-controlled and server-side; do not give them to the developer as chat or repository values."]
open_tasks: ["Developer/operator builds the image for the target VPS architecture and follows docs/deployment/product-qa-vps-runbook.md.", "On the VPS, configure hostname/DNS/TLS/firewall, production MySQL CA/hostname and five table-level SELECT grants, secrets, persistent SQLite storage, backup/restore, retention, and operational limits.", "Versioned /api/v1/ask live authentication and website-backend integration remain to be checked in the agreed deployment environment; container verification used mocks.", "A positive buyer-facing answer containing a new external fact was not demonstrated; run more live QA only when separately requested."]
blockers: ["No VPS credentials or deployment authorization were provided, and no VPS deployment was attempted.", "The local target remains linux/arm64; VPS architecture is unknown.", "No live query fact was returned despite an accepted exact source."]
next_actions: ["Give the developer the repository, API contract, production blueprint, and VPS install runbook; the operator selects the final public endpoint during VPS setup.", "Use the developer's VPS acceptance report to close TLS, database grants, backup, and endpoint integration gates."]
relevant_pages: ["wiki/index.md", "wiki/syntheses/race-expert-qa-production-readiness.md", "wiki/session-handoff.md", "docs/api/product-qa-integration.md", "docs/deployment/product-qa-production-blueprint.md", "docs/deployment/product-qa-vps-runbook.md"]
files_changed: [{"path": "scripts/run_local_session.py", "action": "modified"}, {"path": "deploy/nginx-race-expert-qa.conf.example", "action": "modified"}, {"path": "docs/deployment/product-qa-production-blueprint.md", "action": "modified"}, {"path": "docs/deployment/product-qa-vps-runbook.md", "action": "created"}, {"path": "docs/api/product-qa-integration.md", "action": "modified"}, {"path": "README.md", "action": "modified"}, {"path": "wiki/syntheses/race-expert-qa-production-readiness.md", "action": "modified"}, {"path": "wiki/index.md", "action": "modified"}, {"path": "wiki/source-manifest.md", "action": "modified"}, {"path": "wiki/content-index.jsonl", "action": "generated"}, {"path": "wiki/session-handoff.md", "action": "modified"}, {"path": "wiki/session-index.jsonl", "action": "generated"}, {"path": "wiki/log.md", "action": "appended"}]
tags: ["activity:testing", "status:partial", "task:bounded-e2e-vps-handoff", "project:race-expert", "topic:web-search", "topic:deployment", "topic:production-readiness", "file:scripts/run_local_session.py", "file:docs/deployment/product-qa-vps-runbook.md", "file:wiki/syntheses/race-expert-qa-production-readiness.md"]
verification: [{"command": "one approved local run via scripts/run_local_session.py; one catalog lookup and one /api/ask POST", "result": "HTTP 200, succeeded, search_status=used, exact official source accepted, requested fact absent from final answer; 849 ms search and 11811 ms total"}, {"command": ".venv/bin/pytest -q", "result": "passed: 168 tests and 4009 subtests"}, {"command": ".venv/bin/python scripts/container_smoke.py", "result": "passed: v12/v13/v14 hashes and mock-backed /health, /ready, /api/v1/ask"}, {"command": "rebuild_content_index.py . and lint_content.py .", "result": "passed: indexed 5 content cards"}, {"command": "lint_memory.py .", "result": "passed"}]
---

# Session

## Outcome

Ran one local live E2E request for RE89157 through the approved SSH-tunnel launcher. Catalog resolution, Tavily invocation, and exact official source filtering succeeded; v14 returned a safe abstention instead of the requested new serving-count fact. Reworked deployment docs so the VPS operator chooses hostname/DNS at installation, added a practical VPS runbook, and disabled local Uvicorn access logs. No additional live call, staging, storefront change, or deployment occurred.

## Changed Files

- `scripts/run_local_session.py` — modified
- `deploy/nginx-race-expert-qa.conf.example` — modified
- `docs/deployment/product-qa-production-blueprint.md` — modified
- `docs/deployment/product-qa-vps-runbook.md` — created
- `docs/api/product-qa-integration.md` — modified
- `README.md` — modified
- `wiki/syntheses/race-expert-qa-production-readiness.md` — modified
- `wiki/index.md` — modified
- `wiki/source-manifest.md` — modified
- `wiki/content-index.jsonl` — generated
- `wiki/session-handoff.md` — modified
- `wiki/session-index.jsonl` — generated
- `wiki/log.md` — appended

## Tags

- `activity:testing`
- `status:partial`
- `task:bounded-e2e-vps-handoff`
- `project:race-expert`
- `topic:web-search`
- `topic:deployment`
- `topic:production-readiness`
- `file:scripts/run_local_session.py`
- `file:docs/deployment/product-qa-vps-runbook.md`
- `file:wiki/syntheses/race-expert-qa-production-readiness.md`

## Verification

- `one approved local run via scripts/run_local_session.py; one catalog lookup and one /api/ask POST` — HTTP 200, succeeded, search_status=used, exact official source accepted, requested fact absent from final answer; 849 ms search and 11811 ms total
- `.venv/bin/pytest -q` — passed: 168 tests and 4009 subtests
- `.venv/bin/python scripts/container_smoke.py` — passed: v12/v13/v14 hashes and mock-backed /health, /ready, /api/v1/ask
- `rebuild_content_index.py . and lint_content.py .` — passed: indexed 5 content cards
- `lint_memory.py .` — passed
