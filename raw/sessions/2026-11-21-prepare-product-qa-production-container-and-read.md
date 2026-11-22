---
id: "session-2026-11-21T18-13-56plus-02-00-prepare-product-qa-production-container-and-read"
started_at: "2026-11-21T17:24:20+02:00"
ended_at: "2026-11-21T18:13:56+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Prepare Product QA production container and readiness handoff"
status: "partial"
transcript_source: "faithful-summary"
summary: "Added v14 and journal backup utility to the Docker image, prepared production compose/Nginx blueprint, audited the 283 baseline Tavily skips, and verified offline tests and container smoke. Exact SPONSER source page is identified but current title/path matching rejects its localized product card; infrastructure choices and bounded live-provider authorization remain open."
decisions: ["Keep the API hostname qa-api.raceexpert.com.ua as a proposal pending owner confirmation.", "Keep one Uvicorn process until rate limiting and SQLite storage are shared safely.", "Do not weaken exact-product matching to force the SPONSER candidate through; first define safe localized identity matching.", "Treat 16 of 18 supported-brand skipped fact/review slots as likely missed searches, not proven routing decisions, because the baseline report has no search_topic or skip_reason."]
open_tasks: ["Confirm API hostname/DNS, VPS architecture and operator, egress IP, and allowed website-backend source IPs.", "Confirm production MySQL CA/hostname and table-level SELECT grants with the DBA.", "Choose SQLite retention, encrypted off-host backup, and restore schedule; run a restore drill on the target filesystem.", "Set latency/error SLO and bearer-key rotation policy.", "Design safe localized exact-product matching for RE1372, then run one bounded Tavily positive only after authorization is confirmed.", "Repeat targeted v14 QA with internal search_topic/skip_reason diagnostics that do not log question, answer, URL, or provenance."]
blockers: ["Production infrastructure values and DBA setup are not confirmed.", "No current authorization was established for new paid Tavily/OpenAI calls; no live provider call was made.", "Local Docker image is linux/arm64; VPS architecture is unknown. Docker Buildx and an Nginx binary were unavailable locally."]
next_actions: ["Use the copyable task in wiki/syntheses/race-expert-qa-production-readiness.md after the owner supplies infrastructure decisions and live-QA authorization.", "Keep storefront, staging, and deployment outside this preparation task."]
relevant_pages: ["wiki/index.md", "wiki/syntheses/race-expert-qa-production-readiness.md", "wiki/syntheses/race-expert-qa-web-search.md", "wiki/session-handoff.md", "docs/deployment/product-qa-production-blueprint.md", "docs/test-harness/qa-live-50-products-500-questions-2026-11-20.md"]
files_changed: [{"path": "Dockerfile", "action": "modified"}, {"path": ".dockerignore", "action": "modified"}, {"path": ".env.example", "action": "modified"}, {"path": "README.md", "action": "modified"}, {"path": "docs/api/product-qa-integration.md", "action": "modified"}, {"path": "scripts/container_smoke.py", "action": "created"}, {"path": "deploy/compose.production.yaml", "action": "created"}, {"path": "deploy/nginx-race-expert-qa.conf.example", "action": "created"}, {"path": "docs/deployment/product-qa-production-blueprint.md", "action": "created"}, {"path": "wiki/syntheses/race-expert-qa-production-readiness.md", "action": "modified"}, {"path": "wiki/index.md", "action": "modified"}, {"path": "wiki/session-handoff.md", "action": "modified"}, {"path": "wiki/source-manifest.md", "action": "modified"}, {"path": "wiki/content-index.jsonl", "action": "generated"}, {"path": "wiki/session-index.jsonl", "action": "generated"}, {"path": "wiki/log.md", "action": "appended"}]
tags: ["activity:documentation", "status:partial", "task:production-readiness-handoff", "project:race-expert", "topic:container", "topic:production-readiness", "topic:web-search", "file:Dockerfile", "file:scripts/container_smoke.py", "file:docs/deployment/product-qa-production-blueprint.md", "file:wiki/syntheses/race-expert-qa-production-readiness.md", "file:wiki/session-handoff.md"]
verification: [{"command": ".venv/bin/pytest -q", "result": "passed: 168 tests and 4009 subtests"}, {"command": ".venv/bin/python scripts/container_smoke.py", "result": "passed: v12/v13/v14 hashes and mock-backed /health, /ready, /api/v1/ask"}, {"command": "docker build --pull=false -t race-expert-product-qa:handoff .", "result": "passed; built linux/arm64 image with v14 and backup utility"}, {"command": "docker-compose config --quiet", "result": "passed using a sanitized temporary env file"}, {"command": "scripts/backup_journal.py against disposable Linux tmpfs", "result": "passed: backup exists, mode 0600, table copy matched; target VPS restore drill remains open"}, {"command": "scripts/rebuild_content_index.py . and scripts/lint_content.py .", "result": "passed: indexed 5 content cards and content lint passed"}]
---

# Session

## Outcome

Added v14 and journal backup utility to the Docker image, prepared production compose/Nginx blueprint, audited the 283 baseline Tavily skips, and verified offline tests and container smoke. Exact SPONSER source page is identified but current title/path matching rejects its localized product card; infrastructure choices and bounded live-provider authorization remain open.

## Changed Files

- `Dockerfile` — modified
- `.dockerignore` — modified
- `.env.example` — modified
- `README.md` — modified
- `docs/api/product-qa-integration.md` — modified
- `scripts/container_smoke.py` — created
- `deploy/compose.production.yaml` — created
- `deploy/nginx-race-expert-qa.conf.example` — created
- `docs/deployment/product-qa-production-blueprint.md` — created
- `wiki/syntheses/race-expert-qa-production-readiness.md` — modified
- `wiki/index.md` — modified
- `wiki/session-handoff.md` — modified
- `wiki/source-manifest.md` — modified
- `wiki/content-index.jsonl` — generated
- `wiki/session-index.jsonl` — generated
- `wiki/log.md` — appended

## Tags

- `activity:documentation`
- `status:partial`
- `task:production-readiness-handoff`
- `project:race-expert`
- `topic:container`
- `topic:production-readiness`
- `topic:web-search`
- `file:Dockerfile`
- `file:scripts/container_smoke.py`
- `file:docs/deployment/product-qa-production-blueprint.md`
- `file:wiki/syntheses/race-expert-qa-production-readiness.md`
- `file:wiki/session-handoff.md`

## Verification

- `.venv/bin/pytest -q` — passed: 168 tests and 4009 subtests
- `.venv/bin/python scripts/container_smoke.py` — passed: v12/v13/v14 hashes and mock-backed /health, /ready, /api/v1/ask
- `docker build --pull=false -t race-expert-product-qa:handoff .` — passed; built linux/arm64 image with v14 and backup utility
- `docker-compose config --quiet` — passed using a sanitized temporary env file
- `scripts/backup_journal.py against disposable Linux tmpfs` — passed: backup exists, mode 0600, table copy matched; target VPS restore drill remains open
- `scripts/rebuild_content_index.py . and scripts/lint_content.py .` — passed: indexed 5 content cards and content lint passed
