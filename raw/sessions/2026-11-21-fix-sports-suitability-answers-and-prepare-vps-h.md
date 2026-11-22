---
id: "session-2026-11-21T19-18-02plus-02-00-fix-sports-suitability-answers-and-prepare-vps-h"
started_at: "2026-11-21T19:08:00+02:00"
ended_at: "2026-11-21T19:18:02+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Fix sports-suitability answers and prepare VPS handoff"
status: "partial"
transcript_source: "faithful-summary"
summary: "Adjusted the active Product QA prompt after a local UI check exposed an overly cautious sports-suitability answer with an unsolicited availability mention. Prompt v15 answers with supported card facts, avoids unsupported sport-specific suitability claims, and mentions stock only when asked. Versions v12-v14 remain unchanged."
files_changed: [{"path": "prompts/product-assistant-system-v15.md", "action": "created"}, {"path": "app/assistant.py", "action": "updated"}, {"path": "app/journal.py", "action": "updated"}, {"path": "Dockerfile", "action": "updated"}, {"path": "scripts/container_smoke.py", "action": "updated"}, {"path": "tests/test_web_search.py", "action": "updated"}, {"path": "tests/test_qa_app.py", "action": "updated"}, {"path": "tests/test_journal.py", "action": "updated"}, {"path": "tests/conftest.py", "action": "updated"}, {"path": "README.md", "action": "updated"}, {"path": "AGENTS.md", "action": "updated"}, {"path": "docs/api/product-qa-integration.md", "action": "updated"}, {"path": "docs/deployment/product-qa-production-blueprint.md", "action": "updated"}, {"path": "docs/deployment/product-qa-vps-runbook.md", "action": "updated"}, {"path": "wiki/index.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-qa-evaluation.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-qa-web-search.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-qa-production-readiness.md", "action": "updated"}, {"path": "wiki/session-handoff.md", "action": "updated"}, {"path": "wiki/log.md", "action": "updated"}, {"path": "wiki/session-index.jsonl", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt"}]
tags: ["activity:implementation", "status:partial", "project:race-expert", "task:qa-sports-suitability", "component:assistant", "topic:prompt-quality", "topic:vps-handoff", "file:prompts/product-assistant-system-v15.md", "file:app/assistant.py", "file:app/journal.py", "file:tests/test_web_search.py", "file:Dockerfile", "file:scripts/container_smoke.py", "file:wiki/syntheses/race-expert-qa-production-readiness.md", "file:docs/deployment/product-qa-vps-runbook.md"]
verification: [{"command": ".venv/bin/pytest -q", "result": "passed: 169 tests and 4009 subtests"}, {"command": ".venv/bin/python scripts/container_smoke.py", "result": "passed: prompts v12-v15, /health, /ready and /api/v1/ask"}, {"command": "docker build --platform linux/arm64 --tag race-expert-product-qa:v15-check .", "result": "passed"}, {"command": "docker run --rm -v scripts/container_smoke.py:/tmp/container_smoke.py:ro race-expert-product-qa:v15-check python /tmp/container_smoke.py", "result": "passed inside local container; prompts v12-v15 and all smoke routes returned HTTP 200"}]
decisions: ["Sports activity alone does not trigger the personal-health refusal; answer only with product-card facts and do not claim sport-specific suitability without exact support.", "Mention product availability only when the buyer asks about availability, access, or ordering.", "Do not issue another paid provider request after prompt v15 without a separate user request.", "DNS and a fixed hostname are not prerequisites for source-code handoff; the VPS operator selects the endpoint during installation."]
open_tasks: ["The owner may resubmit the question in the local QA UI to observe a live v15 response; no v15 provider response has been observed yet.", "The VPS operator must build for the actual host architecture and complete TLS, database grants, secrets, storage, backup, retention, and endpoint acceptance gates.", "A positive buyer-facing answer containing a new exact external fact remains unverified."]
blockers: ["The local UI must be restarted on prompt v15 before the owner can retest; do not invoke paid providers automatically."]
next_actions: ["Restart the local QA launcher so the active UI uses prompt v15, then leave it ready for a user-triggered live check.", "Hand the repository, API contract, production blueprint, and VPS runbook to the developer; select DNS and TLS hostname on the VPS."]
relevant_pages: ["wiki/index.md", "wiki/syntheses/race-expert-qa-production-readiness.md", "wiki/session-handoff.md", "docs/api/product-qa-integration.md", "docs/deployment/product-qa-production-blueprint.md", "docs/deployment/product-qa-vps-runbook.md"]
---

# Session

## Outcome

Adjusted the active Product QA prompt after a local UI check exposed an overly cautious sports-suitability answer with an unsolicited availability mention. Prompt v15 answers with supported card facts, avoids unsupported sport-specific suitability claims, and mentions stock only when asked. Versions v12-v14 remain unchanged.

## Changed Files

- `prompts/product-assistant-system-v15.md` — created
- `app/assistant.py` — updated
- `app/journal.py` — updated
- `Dockerfile` — updated
- `scripts/container_smoke.py` — updated
- `tests/test_web_search.py` — updated
- `tests/test_qa_app.py` — updated
- `tests/test_journal.py` — updated
- `tests/conftest.py` — updated
- `README.md` — updated
- `AGENTS.md` — updated
- `docs/api/product-qa-integration.md` — updated
- `docs/deployment/product-qa-production-blueprint.md` — updated
- `docs/deployment/product-qa-vps-runbook.md` — updated
- `wiki/index.md` — updated
- `wiki/syntheses/race-expert-qa-evaluation.md` — updated
- `wiki/syntheses/race-expert-qa-web-search.md` — updated
- `wiki/syntheses/race-expert-qa-production-readiness.md` — updated
- `wiki/session-handoff.md` — updated
- `wiki/log.md` — updated
- `wiki/session-index.jsonl` — updated
- `wiki/content-index.jsonl` — rebuilt

## Tags

- `activity:implementation`
- `status:partial`
- `project:race-expert`
- `task:qa-sports-suitability`
- `component:assistant`
- `topic:prompt-quality`
- `topic:vps-handoff`
- `file:prompts/product-assistant-system-v15.md`
- `file:app/assistant.py`
- `file:app/journal.py`
- `file:tests/test_web_search.py`
- `file:Dockerfile`
- `file:scripts/container_smoke.py`
- `file:wiki/syntheses/race-expert-qa-production-readiness.md`
- `file:docs/deployment/product-qa-vps-runbook.md`

## Verification

- `.venv/bin/pytest -q` — passed: 169 tests and 4009 subtests
- `.venv/bin/python scripts/container_smoke.py` — passed: prompts v12-v15, /health, /ready and /api/v1/ask
- `docker build --platform linux/arm64 --tag race-expert-product-qa:v15-check .` — passed
- `docker run --rm -v scripts/container_smoke.py:/tmp/container_smoke.py:ro race-expert-product-qa:v15-check python /tmp/container_smoke.py` — passed inside local container; prompts v12-v15 and all smoke routes returned HTTP 200
