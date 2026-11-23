# Wiki log

## 2026-11-18 — отделён проект Race Expert QA

- Создан отдельный Q&A-проект в папке QA.
- Перенесены Q&A-промпты, спецификации, оценочные фикстуры и результаты.
- Создано самостоятельное приложение с Q&A-only API и журналом попыток.
- Сформирована Wiki проекта; исходный стенд оставлен без изменений.
- Перенос выполнен без подключения к базе, вызовов модели и развертывания.

## [2026-11-18] session | Separate Race Expert question-answer project

- Raw: `raw/sessions/2026-11-18-separate-race-expert-question-answer-project.md`
- Tags: `activity:implementation`, `project:race-expert`, `file:app/main.py`, `file:wiki/index.md`
- Status: `completed`

## [2026-11-18] session | Complete Q&A-only transfer into QA

- Raw: `raw/sessions/2026-11-18-complete-q-a-only-transfer-into-qa.md`
- Tags: `activity:documentation`, `status:completed`, `task:separate-race-expert-qa`, `project:race-expert`, `file:raw/sessions`, `file:wiki/session-index.jsonl`, `file:docs/test-harness/qa-live-run-report-2026-11-13.md`, `file:scripts/backup_journal.py`, `file:README.md`, `file:wiki/index.md`, `file:wiki/sources/race-expert-qa-project.md`, `file:wiki/content-index.jsonl`, `file:wiki/log.md`, `file:wiki/session-handoff.md`
- Status: `completed`

## [2026-11-18] session | Document the standalone Q&A project

- Raw: `raw/sessions/2026-11-18-document-the-standalone-q-a-project.md`
- Tags: `activity:documentation`, `status:completed`, `task:separate-race-expert-qa`, `project:race-expert`, `file:docs/test-harness/qa-quick-guide.md`, `file:docs/test-harness/qa-architecture-history.md`, `file:README.md`, `file:wiki/index.md`, `file:wiki/sources/race-expert-qa-project.md`, `file:wiki/content-index.jsonl`, `file:raw/sessions`, `file:wiki/session-index.jsonl`, `file:wiki/log.md`, `file:wiki/session-handoff.md`
- Status: `completed`

## [2026-11-18] session | Prepare isolated QA runtime configuration

- Raw: `raw/sessions/2026-11-18-prepare-isolated-qa-runtime-configuration.md`
- Tags: `activity:configuration`, `status:partial`, `task:qa-runtime-configuration`, `project:race-expert`, `file:.env`, `file:secrets`, `file:.gitignore`, `file:.dockerignore`, `file:README.md`, `file:wiki/sources/race-expert-qa-project.md`, `file:wiki/content-index.jsonl`, `file:raw/sessions`, `file:wiki/session-index.jsonl`, `file:wiki/log.md`, `file:wiki/session-handoff.md`
- Status: `partial`

## [2026-11-18] session | Document QA database access boundaries

- Raw: `raw/sessions/2026-11-18-document-qa-database-access-boundaries.md`
- Tags: `activity:documentation`, `status:partial`, `task:qa-runtime-configuration`, `project:race-expert`, `file:README.md`, `file:wiki/sources/race-expert-qa-project.md`, `file:wiki/content-index.jsonl`, `file:raw/sessions`, `file:wiki/session-index.jsonl`, `file:wiki/log.md`, `file:wiki/session-handoff.md`
- Status: `partial`

## [2026-11-18] session | Apply the approved local SSH tunnel procedure to standalone Q&A

- Raw: `raw/sessions/2026-11-18-apply-the-approved-local-ssh-tunnel-procedure-to.md`
- Tags: `activity:implementation`, `task:qa-local-tunnel`, `project:race-expert`, `topic:database-access`, `file:scripts/run_local_session.py`, `file:docs/test-harness/local-session-runbook.md`, `file:AGENTS.md`, `file:README.md`, `file:wiki/sources/race-expert-qa-project.md`, `file:wiki/index.md`, `file:wiki/content-index.jsonl`, `file:raw/sources/qa-local-ssh-tunnel-instruction-2026-11-18.md`
- Status: `completed`

## [2026-11-18] session | Audit standalone QA context and access completeness

- Raw: `raw/sessions/2026-11-18-audit-standalone-qa-context-and-access-completen.md`
- Tags: `activity:documentation`, `task:qa-context-completeness`, `project:race-expert`, `topic:database-access`, `topic:project-memory`, `file:raw/sources/qa-mysql-schema-and-access-context-2026-11-18.md`, `file:wiki/sources/qa-mysql-readonly-access-and-product-query.md`, `file:wiki/source-manifest.md`, `file:wiki/index.md`, `file:docs/test-harness/local-session-runbook.md`, `file:README.md`, `file:AGENTS.md`
- Status: `completed`

## [2026-11-18] session | Record the shared staging boundary in standalone QA

- Raw: `raw/sessions/2026-11-18-record-the-shared-staging-boundary-in-standalone.md`
- Tags: `activity:documentation`, `task:qa-context-completeness`, `project:race-expert`, `topic:staging`, `topic:database-access`, `file:raw/sources/qa-staging-boundary-2026-11-18.md`, `file:README.md`, `file:wiki/sources/race-expert-qa-project.md`, `file:wiki/source-manifest.md`, `file:wiki/content-index.jsonl`
- Status: `completed`

## [2026-11-19] session | Update Wiki for Web Search design and next-step handoff

- Raw: `raw/sessions/2026-11-19-update-wiki-for-web-search-design-and-next-step-.md`
- Tags: `activity:documentation`, `status:completed`, `task:web-search-design-handoff`, `project:race-expert`, `topic:web-search`, `topic:project-memory`, `file:wiki/index.md`, `file:wiki/source-manifest.md`, `file:wiki/sources/race-expert-qa-project.md`, `file:wiki/syntheses/race-expert-qa-web-search.md`, `file:wiki/syntheses/race-expert-qa-evaluation.md`, `file:wiki/session-handoff.md`, `file:wiki/log.md`, `file:wiki/content-index.jsonl`, `file:wiki/session-index.jsonl`
- Status: `completed`
- Source/evidence: `docs/superpowers/specs/2026-11-19-product-qa-web-search-design.md`; current `app/config.py` and local runner allowlist were inspected without opening `.env`.
- Wiki updated: project summary, Web Search synthesis, evaluation status, navigation, source manifest, session handoff and session index.
- Verification: `rebuild_content_index.py` indexed 4 cards; `lint_content.py` and `lint_memory.py` passed.
- User reports a Tavily token in `.env`; the value was neither read nor logged. Current loader does not yet consume Tavily configuration.
- Next: in a new chat, prepare the implementation plan from the Web Search specification; do not implement or deploy in that planning step.

## [2026-11-19] session | Complete Race Expert Web Search source research

- Raw: `raw/sessions/2026-11-19-complete-race-expert-web-search-source-research.md`
- Tags: `activity:research`, `status:completed`, `task:web-search-source-research`, `project:race-expert`, `topic:web-search`, `file:docs/superpowers/research/2026-11-19-raceexpert-web-search-domain-research.md`, `file:docs/superpowers/research/2026-11-19-raceexpert-manufacturer-source-research.md`, `file:docs/superpowers/research/2026-11-19-raceexpert-product-review-platform-research.md`, `file:docs/superpowers/plans/2026-11-19-product-qa-web-search.md`, `file:wiki/syntheses/race-expert-qa-web-search.md`, `file:wiki/source-manifest.md`
- Status: `completed`

## [2026-11-19] session | Record conditional NUTREND Ukraine domain decision

- Raw: `raw/sessions/2026-11-19-record-conditional-nutrend-ukraine-domain-decisi.md`
- Tags: `activity:documentation`, `status:completed`, `task:nutrend-domain-decision`, `project:race-expert`, `topic:web-search`, `file:docs/superpowers/research/2026-11-19-raceexpert-web-search-domain-research.md`, `file:docs/superpowers/plans/2026-11-19-product-qa-web-search.md`, `file:wiki/syntheses/race-expert-qa-web-search.md`, `file:wiki/sources/race-expert-qa-project.md`
- Status: `completed`

## [2026-11-19] session | Continue Race Expert Web Search backend preparation

- Raw: `raw/sessions/2026-11-19-continue-race-expert-web-search-backend-preparat.md`
- Tags: `activity:implementation`, `status:partial`, `project:race-expert`, `topic:web-search`, `topic:backend-api`, `file:app/search_evidence.py`, `file:app/assistant.py`, `file:README.md`, `file:docs/superpowers/plans/2026-11-19-product-qa-web-search.md`, `file:wiki/index.md`, `file:wiki/session-handoff.md`
- Status: `partial`

## [2026-11-19] session | Configure the approved Race Expert Web Search source set

- Raw: `raw/sessions/2026-11-19-configure-the-approved-race-expert-web-search-so.md`
- Tags: `activity:implementation`, `status:partial`, `project:race-expert`, `topic:web-search`, `topic:domain-allowlist`, `file:app/search_evidence.py`, `file:docs/superpowers/plans/2026-11-19-product-qa-web-search.md`, `file:docs/superpowers/research/2026-11-19-raceexpert-web-search-domain-research.md`, `file:docs/api/product-qa-integration.md`, `file:wiki/session-handoff.md`
- Status: `partial`

## [2026-11-19] session | Verify and harden the approved Race Expert Web Search backend with offline mocks

- Raw: `raw/sessions/2026-11-19-verify-and-harden-the-approved-race-expert-web-s.md`
- Tags: `status:partial`, `project:race-expert`, `topic:web-search`, `topic:domain-allowlist`, `file:app/search_evidence.py`, `file:docs/superpowers/plans/2026-11-19-product-qa-web-search.md`, `file:docs/superpowers/research/2026-11-19-raceexpert-web-search-domain-research.md`, `file:docs/api/product-qa-integration.md`, `file:wiki/session-handoff.md`, `topic:mock-tests`, `file:tests/test_web_search.py`, `file:tests/test_config.py`, `file:tests/test_web_search_metrics.py`, `activity:testing`
- Status: `partial`

## [2026-11-20] session | Run live end-to-end QA for Product QA Web Search

- Raw: `raw/sessions/2026-11-20-run-live-end-to-end-qa-for-product-qa-web-search.md`
- Tags: `activity:testing`, `status:completed`, `task:web-search-e2e`, `component:product-qa`, `file:docs/test-harness/web-search-local-qa-report.md`, `file:docs/superpowers/plans/2026-11-19-product-qa-web-search.md`, `file:wiki/session-handoff.md`
- Status: `completed`

## [2026-11-20] session | Complete browser UI E2E for Product QA Web Search

- Raw: `raw/sessions/2026-11-20-complete-browser-ui-e2e-for-product-qa-web-searc.md`
- Tags: `activity:testing`, `status:completed`, `task:web-search-browser-e2e`, `component:product-qa`, `file:docs/test-harness/web-search-local-qa-report.md`, `file:docs/superpowers/plans/2026-11-19-product-qa-web-search.md`, `file:wiki/session-handoff.md`
- Status: `completed`

## [2026-11-20] session | Implement Product QA reliability follow-up

- Raw: `raw/sessions/2026-11-20-implement-product-qa-reliability-follow-up.md`
- Tags: `activity:implementation`, `status:completed`, `project:race-expert`, `task:reliability-follow-up`, `component:assistant`, `component:web-search`, `file:app/assistant.py`, `file:app/openai_client.py`, `file:app/search_evidence.py`, `file:app/main.py`, `file:app/journal.py`, `file:prompts/product-assistant-system-v14.md`, `file:tests/test_web_search.py`, `file:tests/test_search_evidence.py`, `file:tests/test_qa_app.py`, `file:tests/test_journal.py`, `file:docs/test-harness/local-session-runbook.md`, `file:wiki/syntheses/race-expert-qa-evaluation.md`
- Status: `completed`

## [2026-11-21] session | Prepare Product QA production-readiness handoff

- Raw: `raw/sessions/2026-11-21-prepare-product-qa-production-readiness-handoff.md`
- Tags: `activity:documentation`, `status:completed`, `project:race-expert`, `task:production-readiness-handoff`, `component:web-search`, `component:wiki`, `file:wiki/index.md`, `file:wiki/syntheses/race-expert-qa-web-search.md`, `file:wiki/syntheses/race-expert-qa-production-readiness.md`, `file:wiki/session-handoff.md`
- Status: `completed`

## [2026-11-21] session | Prepare Product QA production container and readiness handoff

- Raw: `raw/sessions/2026-11-21-prepare-product-qa-production-container-and-read.md`
- Tags: `activity:documentation`, `status:partial`, `task:production-readiness-handoff`, `project:race-expert`, `topic:container`, `topic:production-readiness`, `topic:web-search`, `file:Dockerfile`, `file:scripts/container_smoke.py`, `file:docs/deployment/product-qa-production-blueprint.md`, `file:wiki/syntheses/race-expert-qa-production-readiness.md`, `file:wiki/session-handoff.md`
- Status: `partial`

## [2026-11-21] session | Run one bounded Product QA E2E and prepare VPS developer handoff

- Raw: `raw/sessions/2026-11-21-run-one-bounded-product-qa-e2e-and-prepare-vps-d.md`
- Tags: `activity:testing`, `status:partial`, `task:bounded-e2e-vps-handoff`, `project:race-expert`, `topic:web-search`, `topic:deployment`, `topic:production-readiness`, `file:scripts/run_local_session.py`, `file:docs/deployment/product-qa-vps-runbook.md`, `file:wiki/syntheses/race-expert-qa-production-readiness.md`
- Status: `partial`

## [2026-11-21] session | Fix sports-suitability answers and prepare VPS handoff

- Raw: `raw/sessions/2026-11-21-fix-sports-suitability-answers-and-prepare-vps-h.md`
- Tags: `activity:implementation`, `status:partial`, `project:race-expert`, `task:qa-sports-suitability`, `component:assistant`, `topic:prompt-quality`, `topic:vps-handoff`, `file:prompts/product-assistant-system-v15.md`, `file:app/assistant.py`, `file:app/journal.py`, `file:tests/test_web_search.py`, `file:Dockerfile`, `file:scripts/container_smoke.py`, `file:wiki/syntheses/race-expert-qa-production-readiness.md`, `file:docs/deployment/product-qa-vps-runbook.md`
- Status: `partial`

## [2026-11-21] session | Keep local QA ready for a user-triggered v15 retest

- Raw: `raw/sessions/2026-11-21-keep-local-qa-ready-for-a-user-triggered-v15-ret.md`
- Tags: `activity:testing`, `status:partial`, `project:race-expert`, `task:local-v15-retest`, `component:assistant`, `topic:local-qa`, `file:scripts/run_local_session.py`, `file:wiki/session-handoff.md`, `file:wiki/syntheses/race-expert-qa-production-readiness.md`
- Status: `partial`

## [2026-11-21] session | Tighten sports-suitability answer behavior and finalize VPS handoff

- Raw: `raw/sessions/2026-11-21-tighten-sports-suitability-answer-behavior-and-f.md`
- Tags: `activity:implementation`, `status:partial`, `project:race-expert`, `task:qa-sports-suitability`, `topic:backend-api`, `topic:production-readiness`, `file:README.md`, `file:app/templates/index.html`, `file:docs/api/product-qa-integration.md`, `file:docs/deployment/product-qa-production-blueprint.md`, `file:docs/deployment/product-qa-vps-runbook.md`, `file:wiki/index.md`, `file:wiki/syntheses/race-expert-qa-evaluation.md`, `file:wiki/syntheses/race-expert-qa-web-search.md`, `file:wiki/syntheses/race-expert-qa-production-readiness.md`
- Status: `partial`

## [2026-11-21] session | Run the local connected Product QA UI end-to-end

- Raw: `raw/sessions/2026-11-21-run-the-local-connected-product-qa-ui-end-to-end.md`
- Tags: `activity:testing`, `status:completed`, `project:race-expert`, `task:local-product-qa-demo`, `topic:database`, `topic:web-search`, `topic:openai`, `file:README.md`, `file:wiki/syntheses/race-expert-qa-evaluation.md`, `file:wiki/syntheses/race-expert-qa-web-search.md`, `file:wiki/syntheses/race-expert-qa-production-readiness.md`
- Status: `completed`

## [2026-11-21] session | Design balanced sports-suitability answer wording

- Raw: `raw/sessions/2026-11-21-design-balanced-sports-suitability-answer-wordin.md`
- Tags: `activity:planning`, `status:needs-review`, `project:race-expert`, `task:prompt-sports-suitability-tone`, `topic:prompt-design`, `file:docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md`, `file:wiki/index.md`
- Status: `needs-review`

## [2026-11-21] session | Expand the sports-suitability prompt design with short-term conversation memory

- Raw: `raw/sessions/2026-11-21-expand-the-sports-suitability-prompt-design-with.md`
- Tags: `activity:planning`, `status:needs-review`, `project:race-expert`, `task:prompt-and-conversation-memory-design`, `topic:prompt-design`, `topic:conversation-context`, `file:docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md`, `file:wiki/index.md`
- Status: `needs-review`

## [2026-11-23] session | Deploy Race Expert AI Rozetka-style demo, Tavily brand search & meta-phrase cleanup

- Tags: `activity:implementation`, `status:completed`, `project:race-expert`, `task:vps-demo-rozetka-ai-style`, `topic:ui-design`, `topic:web-search`, `topic:tavily`, `topic:clean-answers`, `file:app/templates/index.html`, `file:app/static/app.js`, `file:app/assistant.py`, `file:app/search_evidence.py`, `file:app/openai_client.py`, `file:tests/test_web_search.py`
- Status: `completed`
- Description: Реализован и развернут на VPS live demo интерфейс в фирменном стиле Race Expert (логотип, навигация, палитра #253237 и #3960FF, боковое модальное окно консультанта «Race Expert AI» в стиле Rozetka AI, чипы предзаготовленных вопросов, поле ввода артикула и поиск товара в реальной базе OpenCart). Устранено дублирование индикатора печати. Добавлена локальная отдача картинок товаров. Реализован контекст предыдущих реплик диалога (до 3 последних ходов). Устранена мета-фразировка («На товарі зазначено...», «В картці вказано...») во всех ответах модели. Настроено автоматическое обращение к Tavily Search по белому списку доменов производителей (включая scienceinsport.com для бренда SiS) при вопросах о бренде или нехватке данных в карточке. Все 180 тестов пройдены успешно, деплой на VPS протестирован в live-режиме.


## [2026-11-23] session | Deploy Rozetka-AI style demo with sports skills, intent classifier, and 24-category questions matrix

- Raw: `raw/sessions/2026-11-23-deploy-rozetka-ai-style-demo-with-sports-skills-.md`
- Tags: `activity:implementation`, `status:completed`, `project:race-expert`, `task:rozetka-ai-demo-and-sports-skills`, `topic:ui-redesign`, `topic:intent-classifier`, `topic:sports-nutrition`, `topic:suggested-questions`, `topic:vps-deployment`, `file:app/intent_classifier.py`, `file:app/suggested_questions.py`, `file:app/main.py`, `file:app/static/app.js`, `file:app/templates/index.html`
- Status: `completed`
