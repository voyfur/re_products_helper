---
id: "session-2026-11-18T22-01-24plus-02-00-apply-the-approved-local-ssh-tunnel-procedure-to"
started_at: "2026-11-18T21:47:00+02:00"
ended_at: "2026-11-18T22:01:24+02:00"
timezone: "Europe/Kyiv"
agent: "Codex"
task: "Apply the approved local SSH tunnel procedure to standalone Q&A"
status: "completed"
transcript_source: "Codex conversation on 2026-11-18"
summary: "Found the existing local-session instruction in the source AGENTS.md and runbook. Added a Q&A-only launcher that tunnels through VPS-61125, verifies the SSH host key, requires MySQL TLS 1.2 or 1.3, and disables MySQL certificate checks only for this local session. No database, OpenAI, or deployment operation was performed."
files_changed: [{"path": "scripts/run_local_session.py", "action": "created Q&A-only local SSH tunnel launcher"}, {"path": "docs/test-harness/local-session-runbook.md", "action": "documented the tunnel and local-only TLS policy"}, {"path": "raw/sources/qa-local-ssh-tunnel-instruction-2026-11-18.md", "action": "captured the non-secret source instruction"}, {"path": "AGENTS.md", "action": "distinguished local tunnel mode from strict direct backend mode"}, {"path": "README.md", "action": "replaced direct local launch instructions with the tunnel runner"}, {"path": ".env.example", "action": "clarified that it describes persistent backend configuration"}, {"path": "docs/test-harness/qa-architecture-history.md", "action": "recorded the local-only connection exception"}, {"path": "wiki/index.md", "action": "linked the local connection runbook"}, {"path": "wiki/sources/race-expert-qa-project.md", "action": "updated connection facts and current status"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt from updated knowledge cards"}]
tags: ["activity:implementation", "task:qa-local-tunnel", "project:race-expert", "topic:database-access", "file:scripts/run_local_session.py", "file:docs/test-harness/local-session-runbook.md", "file:AGENTS.md", "file:README.md", "file:wiki/sources/race-expert-qa-project.md", "file:wiki/index.md", "file:wiki/content-index.jsonl", "file:raw/sources/qa-local-ssh-tunnel-instruction-2026-11-18.md"]
verification: [{"command": "Python 3.12 py_compile on scripts/run_local_session.py", "result": "passed"}, {"command": "Wiki content index rebuild", "result": "passed: indexed 2 content cards"}, {"command": "database, OpenAI, tests, deployment", "result": "not run"}]
decisions: ["Use the local Q&A launcher for access through the SSH tunnel; it checks the VPS host key and requires MySQL TLS 1.2 or 1.3.", "Disable MySQL certificate and hostname verification only inside this explicitly approved local tunnel session; keep the direct backend connector strict.", "Keep QA secrets in ignored local files and parse only an allowlist of .env keys without executing or printing the file."]
open_tasks: ["The first local database connection through the new QA-only launcher has not been run.", "Before any persistent deployment, confirm MySQL CA and hostname, issue a dedicated least-privilege account, and set access and request limits."]
blockers: []
next_actions: ["Use docs/test-harness/local-session-runbook.md when starting a local Q&A session.", "Do not deploy this local certificate-verification bypass."]
relevant_pages: ["README.md", "docs/test-harness/local-session-runbook.md", "wiki/session-handoff.md", "wiki/sources/race-expert-qa-project.md"]
---

# Session

## Outcome

Found the existing local-session instruction in the source AGENTS.md and runbook. Added a Q&A-only launcher that tunnels through VPS-61125, verifies the SSH host key, requires MySQL TLS 1.2 or 1.3, and disables MySQL certificate checks only for this local session. No database, OpenAI, or deployment operation was performed.

## Changed Files

- `scripts/run_local_session.py` — created Q&A-only local SSH tunnel launcher
- `docs/test-harness/local-session-runbook.md` — documented the tunnel and local-only TLS policy
- `raw/sources/qa-local-ssh-tunnel-instruction-2026-11-18.md` — captured the non-secret source instruction
- `AGENTS.md` — distinguished local tunnel mode from strict direct backend mode
- `README.md` — replaced direct local launch instructions with the tunnel runner
- `.env.example` — clarified that it describes persistent backend configuration
- `docs/test-harness/qa-architecture-history.md` — recorded the local-only connection exception
- `wiki/index.md` — linked the local connection runbook
- `wiki/sources/race-expert-qa-project.md` — updated connection facts and current status
- `wiki/content-index.jsonl` — rebuilt from updated knowledge cards

## Tags

- `activity:implementation`
- `task:qa-local-tunnel`
- `project:race-expert`
- `topic:database-access`
- `file:scripts/run_local_session.py`
- `file:docs/test-harness/local-session-runbook.md`
- `file:AGENTS.md`
- `file:README.md`
- `file:wiki/sources/race-expert-qa-project.md`
- `file:wiki/index.md`
- `file:wiki/content-index.jsonl`
- `file:raw/sources/qa-local-ssh-tunnel-instruction-2026-11-18.md`

## Verification

- `Python 3.12 py_compile on scripts/run_local_session.py` — passed
- `Wiki content index rebuild` — passed: indexed 2 content cards
- `database, OpenAI, tests, deployment` — not run
