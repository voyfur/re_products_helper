---
id: "session-2026-11-18T21-46-00plus-02-00-document-qa-database-access-boundaries"
started_at: "2026-11-18T21:43:00+02:00"
ended_at: "2026-11-18T21:46:00+02:00"
timezone: "Europe/Kyiv"
agent: "Codex"
task: "Document QA database access boundaries"
status: "partial"
transcript_source: "Codex conversation on 2026-11-18"
summary: "Recorded that the copied MySQL account is read-only but has additional grants beyond the five product-card tables used by QA. The app SQL is limited to those five tables; database-level separation requires a dedicated least-privilege account. No database query was made."
files_changed: [{"path": "README.md", "action": "documented inherited account scope and least-privilege requirement"}, {"path": "wiki/sources/race-expert-qa-project.md", "action": "documented Q&A query boundary and inherited grants"}, {"path": "wiki/content-index.jsonl", "action": "rebuild from updated knowledge cards"}, {"path": "raw/sessions", "action": "recorded this non-secret database-scope note"}, {"path": "wiki/session-index.jsonl", "action": "rebuild from all session records"}, {"path": "wiki/log.md", "action": "recorded the scope and outstanding database prerequisites"}, {"path": "wiki/session-handoff.md", "action": "updated open tasks and blockers"}]
tags: ["activity:documentation", "status:partial", "task:qa-runtime-configuration", "project:race-expert", "file:README.md", "file:wiki/sources/race-expert-qa-project.md", "file:wiki/content-index.jsonl", "file:raw/sessions", "file:wiki/session-index.jsonl", "file:wiki/log.md", "file:wiki/session-handoff.md"]
verification: [{"command": "scope comparison", "result": "QA source query references only five product-card tables; prior grants record additional read-only permissions"}, {"command": "live database", "result": "not queried"}]
decisions: ["Keep the current application query scoped to five product-card tables.", "A separate database user limited to those five tables is required for strict database-level separation before deployment.", "Certificate and hostname verification remain mandatory."]
open_tasks: ["Obtain an independently confirmed MySQL CA and a hostname that passes certificate identity verification.", "Provide a reachable MySQL route for the standalone QA app; it does not create an SSH tunnel.", "Have the database owner issue a dedicated read-only user with SELECT only on the five Q&A tables before deployment."]
blockers: ["The local CA file is absent and the previously observed certificate lacks a SAN for the endpoint.", "The inherited read-only account has broader grants than the application needs."]
next_actions: ["Do not attempt live database access until the CA, hostname, route, and least-privilege account are confirmed."]
relevant_pages: ["README.md", "wiki/session-handoff.md", "wiki/sources/race-expert-qa-project.md"]
---

# Session

## Outcome

Recorded that the copied MySQL account is read-only but has additional grants beyond the five product-card tables used by QA. The app SQL is limited to those five tables; database-level separation requires a dedicated least-privilege account. No database query was made.

## Changed Files

- `README.md` — documented inherited account scope and least-privilege requirement
- `wiki/sources/race-expert-qa-project.md` — documented Q&A query boundary and inherited grants
- `wiki/content-index.jsonl` — rebuild from updated knowledge cards
- `raw/sessions` — recorded this non-secret database-scope note
- `wiki/session-index.jsonl` — rebuild from all session records
- `wiki/log.md` — recorded the scope and outstanding database prerequisites
- `wiki/session-handoff.md` — updated open tasks and blockers

## Tags

- `activity:documentation`
- `status:partial`
- `task:qa-runtime-configuration`
- `project:race-expert`
- `file:README.md`
- `file:wiki/sources/race-expert-qa-project.md`
- `file:wiki/content-index.jsonl`
- `file:raw/sessions`
- `file:wiki/session-index.jsonl`
- `file:wiki/log.md`
- `file:wiki/session-handoff.md`

## Verification

- `scope comparison` — QA source query references only five product-card tables; prior grants record additional read-only permissions
- `live database` — not queried
