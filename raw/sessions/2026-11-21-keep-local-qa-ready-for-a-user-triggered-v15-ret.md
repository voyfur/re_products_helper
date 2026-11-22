---
id: "session-2026-11-21T19-23-30plus-02-00-keep-local-qa-ready-for-a-user-triggered-v15-ret"
started_at: "2026-11-21T19:18:02+02:00"
ended_at: "2026-11-21T19:23:30+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Keep local QA ready for a user-triggered v15 retest"
status: "partial"
transcript_source: "faithful-summary"
summary: "Restarted the approved local QA launcher with active prompt v15 after offline verification. Read-only MySQL preflight passed and negotiated TLS 1.3. Restored the selected product in the local UI and left the question field empty for a user-triggered retest. No OpenAI or Tavily call was made after v15."
files_changed: [{"path": "wiki/session-handoff.md", "action": "updated"}, {"path": "wiki/log.md", "action": "updated"}, {"path": "wiki/session-index.jsonl", "action": "updated"}]
tags: ["activity:testing", "status:partial", "project:race-expert", "task:local-v15-retest", "component:assistant", "topic:local-qa", "file:scripts/run_local_session.py", "file:wiki/session-handoff.md", "file:wiki/syntheses/race-expert-qa-production-readiness.md"]
verification: [{"command": ".venv/bin/python scripts/run_local_session.py --env-file .env", "result": "passed through approved launcher; MySQL read-only preflight passed, TLSv1.3 active, local app running on 127.0.0.1:8787"}, {"command": "Local QA UI exact product lookup", "result": "passed; product selected and question field left empty for user-controlled submission"}]
decisions: ["Prompt v15 is active; sports activity alone does not trigger the personal-health refusal, and stock is reported only when asked.", "Do not repeat paid provider requests without a separate user request.", "No DNS record or fixed public hostname is required to hand off the repository; the VPS operator selects the endpoint during installation."]
open_tasks: ["The owner can submit a live v15 question in the open local QA tab; the assistant has not submitted one.", "The VPS operator must build for the target architecture and configure the public hostname, TLS, database access, secrets, storage, backups, retention, and integration acceptance gates.", "A positive buyer-facing answer with a new exact external fact remains unverified."]
blockers: ["No live v15 answer has been observed; paid model validation awaits a user-triggered submission or new explicit request."]
next_actions: ["Use the open local QA UI to submit the test question when ready; inspect the resulting buyer-facing answer.", "Provide the repository, API contract, production blueprint, and VPS runbook to the developer; configure DNS and TLS only on the target VPS."]
relevant_pages: ["wiki/index.md", "wiki/syntheses/race-expert-qa-production-readiness.md", "wiki/session-handoff.md", "docs/api/product-qa-integration.md", "docs/deployment/product-qa-production-blueprint.md", "docs/deployment/product-qa-vps-runbook.md"]
---

# Session

## Outcome

Restarted the approved local QA launcher with active prompt v15 after offline verification. Read-only MySQL preflight passed and negotiated TLS 1.3. Restored the selected product in the local UI and left the question field empty for a user-triggered retest. No OpenAI or Tavily call was made after v15.

## Changed Files

- `wiki/session-handoff.md` — updated
- `wiki/log.md` — updated
- `wiki/session-index.jsonl` — updated

## Tags

- `activity:testing`
- `status:partial`
- `project:race-expert`
- `task:local-v15-retest`
- `component:assistant`
- `topic:local-qa`
- `file:scripts/run_local_session.py`
- `file:wiki/session-handoff.md`
- `file:wiki/syntheses/race-expert-qa-production-readiness.md`

## Verification

- `.venv/bin/python scripts/run_local_session.py --env-file .env` — passed through approved launcher; MySQL read-only preflight passed, TLSv1.3 active, local app running on 127.0.0.1:8787
- `Local QA UI exact product lookup` — passed; product selected and question field left empty for user-controlled submission
