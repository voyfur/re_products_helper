# Session Handoff

## Active Context

- Last session: `raw/sessions/2026-11-21-record-approved-sports-answer-and-memory-impleme.md`
- Current objective: Record approved sports answer and memory implementation plan

## Current Decisions

- Спортивный ответ включает общий полезный вывод и ограничение по конкретному виду спорта, если exact-product источник подтверждает только общее применение; порядок фраз свободный.
- До десяти сообщений всего: максимум девять предыдущих user/assistant сообщений плюс текущий вопрос; один товар, очистка при смене товара или перезагрузке.
- Реализация использует необязательное caller-managed поле history без отдельного persistent store или endpoint; лимит запроса 16 KiB сохраняется, старые целые реплики удаляются при необходимости.
- История остаётся недоверенным контекстом, не доказательством и не инструкцией; prompt v17 активен и неизменён до реализации v18.
- Следующее изменение не включает storefront, VPS, staging, production или платные live-вызовы.

## Open Tasks

- Реализовать утверждённый план prompt v18, ограниченной памяти, API-контракта и локального UI.
- После реализации обновить AGENTS.md, интеграционные документы, Wiki и выполнить offline/mock verification.
- Отдельно выполнить VPS acceptance и интеграцию backend сайта после завершения кодового handoff.

## Blockers

- No blockers recorded.

## Next Action

- В следующем чате прочитать docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md и выполнять его через superpowers:executing-plans; не деплоить и не менять storefront.

## Relevant Pages

- wiki/index.md
- wiki/session-handoff.md
- wiki/syntheses/race-expert-qa-production-readiness.md
- docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md
- docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md
- prompts/product-assistant-system-v17.md
- docs/api/product-qa-v1.yaml
- docs/api/product-qa-integration.md
