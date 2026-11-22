---
id: "session-2026-11-12T13-03-53plus-02-00-update-race-expert-test-harness-wiki"
started_at: "2026-11-12T12:48:53+02:00"
ended_at: "2026-11-12T13:03:53+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Update Race Expert test harness Wiki"
status: "completed"
transcript_source: "faithful-summary"
summary: "Сохранена рабочая история утверждения intent/spec и плана, foundation-решений, выбора MySQL-маршрута из локального .env через SSH-туннель VPS-61125, запуска стенда и двух наблюдавшихся ошибок. Пользователь выбрал Python/FastAPI, loopback/SSH-only, отдельный SQLite и только локальные изменения в публичном voyfur/re_products_helper; deployment и push не разрешены. После обсуждения CA финально выбран SSH-туннель через 185.25.119.96 к MySQL endpoint из MySQL-блока .env; дублирующиеся HOST/PASSWORD разбираются отдельно, секреты в Wiki не сохраняются. Для текущей тестовой сессии по явному разрешению пользователя MySQL TLS обязателен, но проверка самоподписанного сертификата отключена только на срок сессии; production bypass не допускается.\n\nВ worktree добавлены scripts/run_local_session.py, русскоязычный runbook и handoff в AGENTS.md; README ссылается на runbook. Украинский индикатор коли добавлен в app/assistant.py после того, как «коли приймати?» было ошибочно помечено как неподдерживаемый язык. Ранее UI выдавал ошибку поиска RE0126 до подключения, отдельно отображался provider_unavailable; после подключения в предыдущем запуске карточка RE0126 открывалась, но provider-ошибка остаётся нерешённой.\n\nНовый launcher прошёл read-only preflight: SELECT DATABASE() вернул raceexpertcomua, SELECT 1 успешен, TLS 1.3 активен, настройка OpenAI key присутствовала. Uvicorn не запустился, потому что порт 127.0.0.1:8787 уже занят существующим сервером. Health текущего сервиса с разрешённым доступом вернул {\"status\":\"ok\"}; существующий процесс не трогали. OpenAI-запрос, повтор украинского вопроса и проектные тесты в этой сессии не выполнялись."
files_changed: [{"path": "/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/app/assistant.py", "action": "updated Ukrainian language detection with коли"}, {"path": "/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/scripts/run_local_session.py", "action": "created session-only launcher"}, {"path": "/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/AGENTS.md", "action": "created next-chat launch instructions"}, {"path": "/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/README.md", "action": "updated with runbook pointer and session distinction"}, {"path": "/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/docs/test-harness/local-session-runbook.md", "action": "created Russian operating guide"}, {"path": "wiki/sources/race-expert-test-harness-runtime.md", "action": "created"}, {"path": "wiki/sources/race-expert-ai-product-assistant.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/index.md", "action": "updated"}, {"path": "raw/sessions/2026-11-12-update-race-expert-test-harness-wiki.md", "action": "created by save_memory.py"}, {"path": "wiki/session-handoff.md", "action": "rewritten by save_memory.py"}, {"path": "wiki/log.md", "action": "appended by save_memory.py"}, {"path": "wiki/session-index.jsonl", "action": "appended by save_memory.py"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt"}]
tags: ["activity:documentation", "status:completed", "task:test-harness-wiki-update", "project:race-expert", "topic:test-harness", "topic:database-access", "topic:openai-api", "topic:security", "file:wiki/sources/race-expert-test-harness-runtime.md", "file:wiki/sources/race-expert-ai-product-assistant.md", "file:wiki/syntheses/race-expert-product-qa-evaluation.md", "file:wiki/index.md", "file:wiki/session-handoff.md", "file:wiki/log.md", "file:wiki/session-index.jsonl", "file:wiki/content-index.jsonl", "file:scripts/run_local_session.py", "file:docs/test-harness/local-session-runbook.md"]
verification: [{"command": "run scripts/run_local_session.py with the local workspace .env path", "result": "read-only DB preflight passed: schema raceexpertcomua, SELECT 1, TLSv1.3; Uvicorn bind was blocked because 127.0.0.1:8787 was already occupied"}, {"command": "curl --fail --silent --show-error http://127.0.0.1:8787/health with allowed loopback access", "result": "{\"status\":\"ok\"}; existing server left running"}, {"command": "OpenAI question submission and project test suite", "result": "not run; no provider request was sent and no project tests were requested in this Wiki task"}]
decisions: ["The approved standalone tester flow remains separate from the storefront; Python/FastAPI and SQLite form the local implementation, with VPS-61125 only a future deployment candidate.", "The user's final MySQL choice is the existing .env route over SSH forwarding through VPS-61125; never source the mixed .env file or copy secrets.", "For the explicitly approved local test session, require MySQL TLS but disable certificate verification only for the active local session; never use plaintext or carry this bypass into production.", "The application catalog is read-only and limited to the five product-context tables; journal storage remains separate SQLite.", "The OpenAI key is server-side; startup and health must not submit a model request."]
open_tasks: ["Investigate the previously observed provider_unavailable only after the tester explicitly submits a question; startup confirms key presence, not validity.", "Verify the Ukrainian language change for коли without auto-sending a model question; the code change has not been regression-tested.", "Confirm exact live product search in the active session if requested; current launcher preflight verifies schema and SELECT, not the full product flow.", "For production, independently confirm the live-site database identity, narrow grants, verified CA/hostname or an approved persistent protected tunnel, and access controls; deployment and push remain unapproved."]
blockers: ["The configured schema is raceexpertcomua, but administrator confirmation that it is the current live website database is not recorded; MySQL certificate identity remains unverified.", "The current provider_unavailable symptom has not been reproduced after the key-presence check.", "The active Uvicorn server already occupies 127.0.0.1:8787; the new launcher must reuse it or wait until it is stopped before starting a second instance."]
next_actions: ["At the next chat, read this handoff and the runtime Wiki page, then check /health with permitted loopback access before launching anything.", "If health is OK, use the existing UI. If it is down, run the exact command in the worktree AGENTS.md or runtime runbook; do not expose .env values.", "Let the tester manually submit any question; do not call OpenAI automatically.", "Keep production deployment, public push, and any persistent TLS-verification bypass out of scope without new approval."]
relevant_pages: ["wiki/index.md", "wiki/sources/race-expert-test-harness-runtime.md", "wiki/sources/race-expert-ai-product-assistant.md", "wiki/sources/mysql-readonly-access-and-product-query-guide.md", "wiki/syntheses/race-expert-product-qa-evaluation.md", "wiki/session-handoff.md", "docs/test-harness/intent.md", "docs/test-harness/2026-11-11-user-flow-spec.md", "docs/test-harness/implementation-plan.md", "docs/test-harness/implementation-decisions.md", "/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/AGENTS.md", "/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/docs/test-harness/local-session-runbook.md"]
---

# Session

## Outcome

Сохранена рабочая история утверждения intent/spec и плана, foundation-решений, выбора MySQL-маршрута из локального .env через SSH-туннель VPS-61125, запуска стенда и двух наблюдавшихся ошибок. Пользователь выбрал Python/FastAPI, loopback/SSH-only, отдельный SQLite и только локальные изменения в публичном voyfur/re_products_helper; deployment и push не разрешены. После обсуждения CA финально выбран SSH-туннель через 185.25.119.96 к MySQL endpoint из MySQL-блока .env; дублирующиеся HOST/PASSWORD разбираются отдельно, секреты в Wiki не сохраняются. Для текущей тестовой сессии по явному разрешению пользователя MySQL TLS обязателен, но проверка самоподписанного сертификата отключена только на срок сессии; production bypass не допускается.

В worktree добавлены scripts/run_local_session.py, русскоязычный runbook и handoff в AGENTS.md; README ссылается на runbook. Украинский индикатор коли добавлен в app/assistant.py после того, как «коли приймати?» было ошибочно помечено как неподдерживаемый язык. Ранее UI выдавал ошибку поиска RE0126 до подключения, отдельно отображался provider_unavailable; после подключения в предыдущем запуске карточка RE0126 открывалась, но provider-ошибка остаётся нерешённой.

Новый launcher прошёл read-only preflight: SELECT DATABASE() вернул raceexpertcomua, SELECT 1 успешен, TLS 1.3 активен, настройка OpenAI key присутствовала. Uvicorn не запустился, потому что порт 127.0.0.1:8787 уже занят существующим сервером. Health текущего сервиса с разрешённым доступом вернул {"status":"ok"}; существующий процесс не трогали. OpenAI-запрос, повтор украинского вопроса и проектные тесты в этой сессии не выполнялись.

## Changed Files

- `/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/app/assistant.py` — updated Ukrainian language detection with коли
- `/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/scripts/run_local_session.py` — created session-only launcher
- `/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/AGENTS.md` — created next-chat launch instructions
- `/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/README.md` — updated with runbook pointer and session distinction
- `/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/docs/test-harness/local-session-runbook.md` — created Russian operating guide
- `wiki/sources/race-expert-test-harness-runtime.md` — created
- `wiki/sources/race-expert-ai-product-assistant.md` — updated
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated
- `wiki/index.md` — updated
- `raw/sessions/2026-11-12-update-race-expert-test-harness-wiki.md` — created by save_memory.py
- `wiki/session-handoff.md` — rewritten by save_memory.py
- `wiki/log.md` — appended by save_memory.py
- `wiki/session-index.jsonl` — appended by save_memory.py
- `wiki/content-index.jsonl` — rebuilt

## Tags

- `activity:documentation`
- `status:completed`
- `task:test-harness-wiki-update`
- `project:race-expert`
- `topic:test-harness`
- `topic:database-access`
- `topic:openai-api`
- `topic:security`
- `file:wiki/sources/race-expert-test-harness-runtime.md`
- `file:wiki/sources/race-expert-ai-product-assistant.md`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`
- `file:wiki/index.md`
- `file:wiki/session-handoff.md`
- `file:wiki/log.md`
- `file:wiki/session-index.jsonl`
- `file:wiki/content-index.jsonl`
- `file:scripts/run_local_session.py`
- `file:docs/test-harness/local-session-runbook.md`

## Verification

- `run scripts/run_local_session.py with the local workspace .env path` — read-only DB preflight passed: schema raceexpertcomua, SELECT 1, TLSv1.3; Uvicorn bind was blocked because 127.0.0.1:8787 was already occupied
- `curl --fail --silent --show-error http://127.0.0.1:8787/health with allowed loopback access` — {"status":"ok"}; existing server left running
- `OpenAI question submission and project test suite` — not run; no provider request was sent and no project tests were requested in this Wiki task
