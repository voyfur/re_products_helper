# Race Expert QA — Wiki

Проект: отдельное приложение Q&A и переносимый backend API для будущего подключения к Race Expert.

## Сначала прочитать

- [Передача контекста](session-handoff.md) — активный статус и следующий шаг.
- [Q&A-проект](sources/race-expert-qa-project.md) — назначение, поток данных и ограничения.
- [Web Search и API](syntheses/race-expert-qa-web-search.md) — текущая реализация backend, границы источников и открытые решения.
- [Production readiness](syntheses/race-expert-qa-production-readiness.md) — проверенные результаты и блокеры перед production; содержит копируемое сообщение следующему чату.
- [Production blueprint](../docs/deployment/product-qa-production-blueprint.md) — предложенные VPS, reverse proxy, MySQL TLS, storage и acceptance gates.
- [VPS install runbook](../docs/deployment/product-qa-vps-runbook.md) — пошаговый handoff для установки сервиса и подключения endpoint через HTTPS сайта без отдельной DNS-записи.
- [MySQL-доступ и схема Q&A](sources/qa-mysql-readonly-access-and-product-query.md) — пять таблиц, права, SSH-маршрут и локальные настройки.
- [Оценка Q&A](syntheses/race-expert-qa-evaluation.md) — текущая версия prompt и результаты проверок.

## Исходники и спецификации

- [История вопросов и ответов](../docs/test-harness/intent.md)
- [Спецификация потока пользователя](../docs/test-harness/2026-11-11-user-flow-spec.md)
- [План реализации стенда](../docs/test-harness/implementation-plan.md)
- [Краткая инструкция](../docs/test-harness/qa-quick-guide.md)
- [История архитектуры Q&A](../docs/test-harness/qa-architecture-history.md)
- [План оценки качества](../docs/superpowers/plans/2026-11-10-product-qa-evaluation.md)
- [План GPT-6 Luna](../docs/superpowers/plans/2026-11-11-gpt-6-luna-product-assistant-v8.md)
- [Историческая live-проверка Q&A v11](../docs/test-harness/qa-live-run-report-2026-11-13.md) — локальный запуск до перехода на украинский-only prompt v12.
- [Локальное подключение Q&A](../docs/test-harness/local-session-runbook.md) — SSH-туннель через VPS-61125 и обязательный MySQL TLS в локальной сессии.
- [Правила защиты контекста](../docs/superpowers/specs/2026-11-10-product-assistant-guardrails-design.md)
- [Дизайн GPT-6 Luna](../docs/superpowers/specs/2026-11-11-gpt-6-luna-product-assistant-v8-design.md)
- [Спецификация Web Search](../docs/superpowers/specs/2026-11-19-product-qa-web-search-design.md)
- [Спортивная пригодность и память диалога](../docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md) — проект сбалансированного ответа и контекста из 10 сообщений.
- [План обновления спортивного ответа и памяти](../docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md) — реализованы prompt v18, необязательная временная history и локальный UI; внешняя интеграция сайта и VPS acceptance остаются отдельными шагами.
- [Спецификация streaming и typing](../docs/superpowers/specs/2026-11-23-product-qa-streaming-and-typing-design.md) — POST SSE endpoint, скрытая typing-индикация в локальном UI и server-side handoff.
- [План streaming и typing](../docs/superpowers/plans/2026-11-23-product-qa-streaming-and-typing.md) — реализация и offline/container проверки; подключение backend сайта и deployment не входят в выполненную локальную работу.
- [План реализации Web Search](../docs/superpowers/plans/2026-11-19-product-qa-web-search.md)
- [План надёжности после live E2E](../docs/superpowers/plans/2026-11-20-product-qa-reliability-follow-up.md)
- [Live E2E: 50 товаров × 10 вопросов](../docs/test-harness/qa-live-50-products-500-questions-2026-11-20.md)
- [Планирование production handoff](syntheses/race-expert-qa-production-readiness.md#сообщение-для-следующего-чата)
- [Реестр доменов Web Search](../docs/superpowers/research/2026-11-19-raceexpert-web-search-domain-research.md) — сводная рекомендация по категориям Race Expert, производителям, дистрибьюторам и площадкам отзывов.
- Подробные исследования: [производители и дистрибьюторы](../docs/superpowers/research/2026-11-19-raceexpert-manufacturer-source-research.md), [площадки отзывов](../docs/superpowers/research/2026-11-19-raceexpert-product-review-platform-research.md)
- Оценочные фикстуры и отчёты: [evals/](../evals/)
- Активный prompt: [v18](../prompts/product-assistant-system-v18.md); v17 и v12–v16 сохранены без изменений как исторические версии.

## Структура Wiki

- wiki/sources/ — карточки источников и контекст проекта.
- wiki/source-manifest.md — карта сырьевых источников QA и указание, какие исторические записи являются только locator-файлами.
- wiki/syntheses/ — объединённые выводы.
- wiki/log.md — журнал изменений Wiki.
- wiki/session-index.jsonl — индекс сессий.
- wiki/content-index.jsonl — индекс карточек знаний.
