---
id: "session-2026-11-21T19-57-32plus-02-00-run-the-local-connected-product-qa-ui-end-to-end"
started_at: "2026-11-21T19:49:00+02:00"
ended_at: "2026-11-21T19:57:32+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Run the local connected Product QA UI end-to-end"
status: "completed"
transcript_source: "faithful-summary"
summary: "Started the local QA UI on 127.0.0.1:8787 with the approved SSH tunnel to MySQL. A live v17 UI request completed end-to-end: the catalog returned the product, Tavily search ran and passed one exact-source match, and gpt-6-luna returned a successful buyer-facing answer. The result is visibly displayed in the open browser; only non-content attempt metadata was inspected. The service and UI were left running for the user to continue testing."
files_changed: [{"path": "README.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-qa-evaluation.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-qa-web-search.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-qa-production-readiness.md", "action": "updated"}]
tags: ["activity:testing", "status:completed", "project:race-expert", "task:local-product-qa-demo", "topic:database", "topic:web-search", "topic:openai", "file:README.md", "file:wiki/syntheses/race-expert-qa-evaluation.md", "file:wiki/syntheses/race-expert-qa-web-search.md", "file:wiki/syntheses/race-expert-qa-production-readiness.md"]
decisions: ["Keep the demo bound to loopback at 127.0.0.1:8787; no public VPS deployment or internet exposure was performed.", "Use scripts/run_local_session.py for the approved local MySQL tunnel; the local-only MySQL certificate-verification exception is not a production setting.", "Leave the visible UI and QA server running so the user can enter more product articles and questions."]
open_tasks: []
blockers: []
next_actions: ["Use the open local page to enter another article/SKU and a question; the real v17 flow has been confirmed end-to-end."]
relevant_pages: ["README.md", "wiki/syntheses/race-expert-qa-production-readiness.md", "docs/test-harness/local-session-runbook.md", "docs/api/product-qa-integration.md"]
verification: [{"command": "scripts/run_local_session.py --env-file .env", "result": "startup preflight passed: MySQL catalog and table permissions verified; MySQL TLSv1.3; UI served on loopback"}, {"command": "live local UI request", "result": "passed: model gpt-6-luna, prompt v17, attempt succeeded, Tavily used, exact source match accepted; search 488 ms, total 10,759 ms"}, {"command": "read-only SQLite attempt metadata check", "result": "passed; emitted only status, model/prompt version, search provider/status, timings, and accepted-source count; no question, answer, or source provenance printed"}]
---

# Session

## Outcome

Started the local QA UI on 127.0.0.1:8787 with the approved SSH tunnel to MySQL. A live v17 UI request completed end-to-end: the catalog returned the product, Tavily search ran and passed one exact-source match, and gpt-6-luna returned a successful buyer-facing answer. The result is visibly displayed in the open browser; only non-content attempt metadata was inspected. The service and UI were left running for the user to continue testing.

## Changed Files

- `README.md` — updated
- `wiki/syntheses/race-expert-qa-evaluation.md` — updated
- `wiki/syntheses/race-expert-qa-web-search.md` — updated
- `wiki/syntheses/race-expert-qa-production-readiness.md` — updated

## Tags

- `activity:testing`
- `status:completed`
- `project:race-expert`
- `task:local-product-qa-demo`
- `topic:database`
- `topic:web-search`
- `topic:openai`
- `file:README.md`
- `file:wiki/syntheses/race-expert-qa-evaluation.md`
- `file:wiki/syntheses/race-expert-qa-web-search.md`
- `file:wiki/syntheses/race-expert-qa-production-readiness.md`

## Verification

- `scripts/run_local_session.py --env-file .env` — startup preflight passed: MySQL catalog and table permissions verified; MySQL TLSv1.3; UI served on loopback
- `live local UI request` — passed: model gpt-6-luna, prompt v17, attempt succeeded, Tavily used, exact source match accepted; search 488 ms, total 10,759 ms
- `read-only SQLite attempt metadata check` — passed; emitted only status, model/prompt version, search provider/status, timings, and accepted-source count; no question, answer, or source provenance printed
