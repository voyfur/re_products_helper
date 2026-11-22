---
id: "session-2026-11-18T21-42-37plus-02-00-prepare-isolated-qa-runtime-configuration"
started_at: "2026-11-18T21:30:00+02:00"
ended_at: "2026-11-18T21:42:37+02:00"
timezone: "Europe/Kyiv"
agent: "Codex"
task: "Prepare isolated QA runtime configuration"
status: "partial"
transcript_source: "Codex conversation on 2026-11-18"
summary: "Prepared a QA-only .env and protected local secret files using only MySQL, SSH-route, and OpenAI settings needed by Q&A. The source .env was not changed, and no secret values were written to Wiki or logs. The trusted MySQL CA is not available locally and the current certificate has no SAN for the endpoint, so the app remains fail-closed; no live database or model calls were made."
files_changed: [{"path": ".env", "action": "created QA-only runtime configuration with mode 600"}, {"path": "secrets/", "action": "stored protected local access material with mode 600 files and mode 700 directory"}, {"path": ".gitignore", "action": "excluded local secret files"}, {"path": ".dockerignore", "action": "excluded local secret files from container build context"}, {"path": "README.md", "action": "documented QA environment loading and connection prerequisites"}, {"path": "wiki/sources/race-expert-qa-project.md", "action": "recorded non-secret environment status and database blockers"}, {"path": "wiki/content-index.jsonl", "action": "rebuild from updated knowledge cards"}, {"path": "raw/sessions", "action": "recorded this environment-setup session without credential values"}, {"path": "wiki/session-index.jsonl", "action": "rebuild from all session records"}, {"path": "wiki/log.md", "action": "recorded this setup and its blocker"}, {"path": "wiki/session-handoff.md", "action": "updated active context and open connection requirements"}]
tags: ["activity:configuration", "status:partial", "task:qa-runtime-configuration", "project:race-expert", "file:.env", "file:secrets", "file:.gitignore", "file:.dockerignore", "file:README.md", "file:wiki/sources/race-expert-qa-project.md", "file:wiki/content-index.jsonl", "file:raw/sessions", "file:wiki/session-index.jsonl", "file:wiki/log.md", "file:wiki/session-handoff.md"]
verification: [{"command": "file permission check", "result": "QA .env and secret files are mode 600; secrets directory is mode 700"}, {"command": "secret exclusion check", "result": ".env ignored by Git/Docker; secrets directory ignored by Git/Docker"}, {"command": "MySQL CA check", "result": "CA file absent; app remains fail-closed"}, {"command": "database/model calls and tests", "result": "not run"}]
decisions: ["The QA environment includes only settings needed by the Q&A app; unrelated provider settings were excluded.", "The MySQL CA and endpoint identity remain unresolved; no TLS bypass is allowed.", "The original project environment file and Review project remain unchanged."]
open_tasks: ["Obtain an independently confirmed MySQL CA and a hostname that passes certificate identity verification.", "Provide a reachable MySQL route for the standalone QA app; the app does not create an SSH tunnel.", "Before deployment, set access controls and request limits."]
blockers: ["The local QA copy cannot connect to MySQL until a confirmed CA and matching endpoint identity are available."]
next_actions: ["Keep live database and model operations stopped until the certificate and route are confirmed."]
relevant_pages: ["README.md", "wiki/session-handoff.md", "wiki/sources/race-expert-qa-project.md"]
---

# Session

## Outcome

Prepared a QA-only .env and protected local secret files using only MySQL, SSH-route, and OpenAI settings needed by Q&A. The source .env was not changed, and no secret values were written to Wiki or logs. The trusted MySQL CA is not available locally and the current certificate has no SAN for the endpoint, so the app remains fail-closed; no live database or model calls were made.

## Changed Files

- `.env` — created QA-only runtime configuration with mode 600
- `secrets/` — stored protected local access material with mode 600 files and mode 700 directory
- `.gitignore` — excluded local secret files
- `.dockerignore` — excluded local secret files from container build context
- `README.md` — documented QA environment loading and connection prerequisites
- `wiki/sources/race-expert-qa-project.md` — recorded non-secret environment status and database blockers
- `wiki/content-index.jsonl` — rebuild from updated knowledge cards
- `raw/sessions` — recorded this environment-setup session without credential values
- `wiki/session-index.jsonl` — rebuild from all session records
- `wiki/log.md` — recorded this setup and its blocker
- `wiki/session-handoff.md` — updated active context and open connection requirements

## Tags

- `activity:configuration`
- `status:partial`
- `task:qa-runtime-configuration`
- `project:race-expert`
- `file:.env`
- `file:secrets`
- `file:.gitignore`
- `file:.dockerignore`
- `file:README.md`
- `file:wiki/sources/race-expert-qa-project.md`
- `file:wiki/content-index.jsonl`
- `file:raw/sessions`
- `file:wiki/session-index.jsonl`
- `file:wiki/log.md`
- `file:wiki/session-handoff.md`

## Verification

- `file permission check` — QA .env and secret files are mode 600; secrets directory is mode 700
- `secret exclusion check` — .env ignored by Git/Docker; secrets directory ignored by Git/Docker
- `MySQL CA check` — CA file absent; app remains fail-closed
- `database/model calls and tests` — not run
