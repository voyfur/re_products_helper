---
schema_version: 2
id: "synthesis.race-expert-qa-production-readiness"
type: "synthesis"
title: "Подготовка Product QA Race Expert к production"
description: "Проверенное состояние Product QA v18 после offline/mock verification и отдельные незакрытые требования site-backend и VPS acceptance."
tags: ["project:race-expert", "capability:product-qa", "workflow:deployment", "topic:production-readiness", "platform:raceexpert.com.ua"]
source: {"raw_path": "docs/test-harness/qa-live-50-products-500-questions-2026-11-20.md"}
dates: {"added_at": "2026-11-21T17:24:20+02:00", "updated_at": "2026-11-22T16:38:38+02:00"}
relations: [{"type": "references", "target": "synthesis.race-expert-qa-evaluation"}, {"type": "references", "target": "synthesis.race-expert-qa-web-search"}, {"type": "references", "target": "project.race-expert-qa"}]
aliases: ["Product QA production readiness", "Продакшн-готовность Q&A"]
status: "active"
---

# Product QA: production-readiness handoff

## Текущий вывод

Backend прошёл локальный 500-сценарный E2E после восстановления SSH-туннеля и offline-набор после адаптации. Live UI E2E на v16 подтвердил запуск Tavily, но ответ был слишком осторожным. После изменения prompt выполнен успешный live UI E2E на v17: каталог повторно подтвердил товар, Tavily вызвался, источник прошёл точный фильтр, OpenAI завершил ответ HTTP 200. Ответ дал прямой общий вывод о спортивном применении без упоминания внутренней карточки или наличия и без заявления о специальной формуле для плавцов. Время полного ответа — 10,759 ms. Локальный интерфейс оставлен открытым на `http://127.0.0.1:8787/`; база доступна через одобренный локальный SSH-туннель. Storefront Raceexpert.com.ua не подключался; staging и production deploy не выполнялись.

Утверждённые [спецификация спортивной пригодности и памяти диалога](../../docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md) и [план обновления проекта](../../docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md) реализованы в локальном Git checkout. Активен prompt v18; изменения прошли offline и mock verification. Следующий отдельный этап — server-side интеграция сайта и VPS acceptance по runbook; этот статус не означает, что эти работы выполнены или storefront подключён.

## Проверенные результаты

- Live E2E от 20 ноября: 50 товаров × 10 вопросов, итог 500/500 успешных ответов после повторения 286 неуспешных/недоставленных запросов после перезапуска локального launcher.
- Tavily вызван 217 раз, 0 ошибок провайдера; в 5 финальных попытках были приняты записи по имени товара, только для RE89157. Ни одна запись не подтвердила запрошенный exact-вкус/объём/фасовку. Остальные поиски не дали положительного exact-variant факта.
- 283 финальных попытки имели `search_status=skipped`, то есть Tavily не вызывался. Не считать эти пропуски автоматом корректными: при дальнейшем аудите классифицировать каждый важный сценарий по решению маршрутизации и вопросу. Поиск по одобренному источнику должен запускаться только когда карточки недостаточно или запрошены допустимые темы отзывов.
- Отчёт выявил 21/50 общих ответов на явно нерелевантные вопросы и 41/50 ответов с количеством/инструкцией из карточки в personal-health сценариях.
- План адаптации v14 остаётся в силе: fail-closed `product_related`; фиксированный отказ на личные health/dose вопросы без повторения порций; `verified_product_name` передаётся модели только после точной серверной фильтрации; `/ready` делает read-only `SELECT 1`, а `/health` остаётся liveness. Prompt v18 добавляет совместный общий спортивный вывод и ограничение по названному спорту, сохраняя эти guardrails.
- Исторический offline-набор v17: 171 тест и 4009 subtests passed. Для v18 выполнен новый offline-набор (результат выше); текущая browser/container smoke использовала локальные mock данные, а не live providers.
- Один live UI E2E на v17: последняя попытка имеет `status=succeeded`, модель `gpt-6-luna`, `prompt_version=v17`, `search_status=used`, `search_provider=tavily`; источник прошёл exact-match фильтр. Поиск занял 488 ms, полный ответ — 10,759 ms. Buyer-facing результат показан в интерфейсе; вопрос, ответ и source provenance в Wiki не копировались.
- Один live local E2E запрос после v14: article `RE89157` разрешился по каталогу; `/api/ask` вернул HTTP 200 и `succeeded`; `search_status=used`; точная запись производителя принята; поиск занял 849 ms, полный запрос 11,811 ms. Финальный ответ не содержал запрошенное число порций и сообщил, что факт не подтверждён доступным evidence. Ответ/запрос и source metadata не скопированы в логи или Wiki; сохранён только штатный SQLite журнал.
- Prompt v18 активен с SHA-256 `87b639cc74aadf2a387e612bf5d1cda767b488e8477d1d442198bff58795ce1f`; prompt v17 по-прежнему имеет SHA-256 `f26e6eabf5d2867adf5608843abb1da277c362759cd3606d892c3c101e9fcdea` и не изменён.
- API принимает необязательные 0–9 предыдущих `user`/`assistant` реплик; история не является источником фактов или инструкций, не логируется и не сохраняется. UI держит до 10 сообщений в памяти текущей страницы, сбрасывает историю при новом поиске и reload, сокращает только самые старые целые реплики при 16 KiB, сохраняя текущий вопрос.
- Offline проверки 22 ноября: focused pytest — 88 passed; полный suite — 195 passed и 4009 subtests. Prompt pins v12–v18 проверены. Локальный image `race-expert-product-qa:v18-check` собран; in-container smoke с `--network none` прошёл на synthetic dependencies, `/health`, `/ready`, `/api/v1/ask` ответили 200.
- Browser acceptance для локального UI выполнена на временном localhost mock без OpenAI/Tavily: проверены передача 9 prior messages, 10-сообщный transcript, сброс при смене товара/reload, отсутствие добавления failed-ответа, UTF-8 pruning целых старых реплик и отображение HTML-похожего текста как текста.
- Во время этого обновления не выполнялись live OpenAI/Tavily запросы, storefront/backend сайта не менялись, VPS/staging/production deployment не проводились.
- Использовался local QA `/api/search` → `/api/ask` flow через `scripts/run_local_session.py`; это не live auth-check `/api/v1/ask`. Versioned endpoint ранее прошёл контейнерный mock smoke. Uvicorn access logging local launcher выключен для сессии.
- Prompt v12–v17 сохранены без изменений; active v18 hash приведён выше.
- Production Dockerfile копирует v12–v18 и `scripts/backup_journal.py`; Uvicorn access log выключен. Локальный `race-expert-product-qa:v18-check` прошёл mock smoke без сети. Архитектура целевого VPS неизвестна, поэтому оператор/разработчик должен собрать образ для нужной platform.
- Добавлены черновые production-конфигурации и handoff: [`compose.production.yaml`](../../deploy/compose.production.yaml), [`nginx-race-expert-qa.conf.example`](../../deploy/nginx-race-expert-qa.conf.example), [production blueprint](../../docs/deployment/product-qa-production-blueprint.md). Compose config прошёл YAML/compose parsing; Nginx binary в окружении отсутствует, поэтому пример Nginx не прошёл `nginx -t`.
- Backup utility проверен на disposable Linux tmpfs: создаёт SQLite online backup с mode `0600`, содержимое таблиц совпало. Restore drill и тест на постоянном VPS volume не проводились.
- В live-запросе v16 точная страница производителя прошла matcher, но buyer-facing ответ остался слишком осторожным. Внешние данные поддерживают общий вывод о применении продукта в спортивном контексте, но не о специальной разработке для плавцов и не о персональной медицинской безопасности. Из-за противоречия числовых данных между источником и карточкой количество белка и другие такие числа в ответ не включаются.
- Для разработчика добавлен [VPS install runbook](../../docs/deployment/product-qa-vps-runbook.md). В конфигурации hostname изменён на placeholder `api.example.com`; выбранный hostname/DNS не нужен для передачи исходников и настраивается оператором VPS при установке.
- `.env` обрабатывался только allowlist-parser внутри одобренного local launcher; значения не выводились. После неудачного по качеству ответа v16 выполнен один bounded live E2E на v17. Staging, storefront и production deploy не подключались.

Источники: [Live E2E report](../../docs/test-harness/qa-live-50-products-500-questions-2026-11-20.md), [план адаптации](../../docs/superpowers/plans/2026-11-20-product-qa-reliability-follow-up.md), [API integration handoff](../../docs/api/product-qa-integration.md), [API OpenAPI contract](../../docs/api/product-qa-v1.yaml), [текущий Web Search synthesis](race-expert-qa-web-search.md).

## Аудит 283 пропусков Tavily

В отчёте сохраняется только `search_status`; он не содержит `search_topic` или `skip_reason`. Поэтому по прошлым попыткам можно распределить сценарии, но нельзя доказать точное решение маршрутизатора для каждого запроса.

| Слоты | Пропуски | Оценка |
|---|---:|---|
| Q1: карточка уже подтверждена | 50 | Ожидаемо без поиска: вопрос только повторно проверяет идентичность/вариант из карточки. |
| Q8: явно не о товаре | 50 | Ожидаемо перенаправлять до модели и поиска. В baseline 21/50 ответов всё же были общими ответами не по теме. |
| Q9: личное здоровье/доза | 50 | Ожидаемо фиксированное безопасное перенаправление без поиска. В baseline 41/50 ответов повторяли порцию/инструкцию из карточки; v14 исправление подтверждено offline, не новым live-тестом. |
| Q10: просьба раскрыть секрет/данные покупателя и выдумать отзыв | 50 | Ожидаемо без поиска; запрос содержит только негативную privacy/injection проверку. |
| Q2–Q7: fact/review | 83 | Смешанная группа: 65 слотов у брендов без активного allowlist источника; 18 слотов у брендов/карточек с подходящим контекстом источника. |

Из последних 18: 15 SiS слотов (RE0126, RE0667, RE1163 по Q2/Q3/Q4/Q6/Q7) и RE2466 Q3 выглядят как вероятно пропущенные допустимые поиски. Для RE11838 Q2 и RE2199 Q3 ответ, вероятно, уже покрывался карточкой. Эти 16/18 — гипотезы по вопросу, бренду, карточке и ответу из отчёта, а не доказанные route decisions: следующий targeted run должен записывать внутренние `search_topic`/`skip_reason` без вопроса, ответа, URL или provenance в логи. Точный разброс приведён в [production blueprint](../../docs/deployment/product-qa-production-blueprint.md).

## Подтверждённые решения пользователя

- Сайт: Raceexpert.com.ua; целевая VPS находится в Украине. Сам сайт и его виджет в этом приложении не реализуются.
- Backend сайта позже должен передавать `article` товара и текущий вопрос в versioned server-to-server API. Каталог разрешает товар по артикулу/model/SKU; Tavily строит запрос по названию выбранной карточки, не по штрихкоду.
- API-ключи Tavily/OpenAI и тестовые/production integration credentials остаются под контролем владельца проекта; доступы выдаются программисту по мере необходимости. Не передавать программисту Tavily/OpenAI/DB/SSH секреты.
- Пользователь сообщил, что в `.env` задан `TAVILY_API_KEY`; отдельный key-файл не нужен. Код runtime и локальный launcher принимают прямой `TAVILY_API_KEY` или file-вариант, но не оба. Значения `.env` не открывать и не сохранять в Wiki.
- Начальный allowlist утверждён: exact hostnames без wildcard; `nutrend.com.ua` — условный поставщик только NUTREND; отзывные платформы — `fit.rozetka.com.ua` и `prom.ua`, Rozetka считается одной независимой площадкой. Полный состав и ограничения — в [domain research](../../docs/superpowers/research/2026-11-19-raceexpert-web-search-domain-research.md).

## Что блокирует production-приёмку

1. **Нужна сборка для target VPS.** Локальный image — `linux/arm64`, VPS architecture неизвестна. Runbook предписывает разработчику собрать image на VPS или под target platform.
2. **Live-проверка пока узкая.** Один v17 E2E подтвердил общий спортивный вывод для exact-продукта; прочие товары, варианты и типы вопросов этим одиночным запуском не покрыты. Числовые данные, противоречащие карточке, по-прежнему не следует выдавать без дополнительного подтверждения.
3. **VPS runtime setup ещё не выполнен.** Отдельная DNS-запись не требуется, если Product QA проксируется по точному route через действующий HTTPS hostname сайта. Backend сайта и API подключит разработчик/оператор по runbook; отдельный hostname/certificate нужен только если существующий virtual host использовать нельзя.
4. **Production MySQL/TLS должны быть настроены на VPS.** Нужен выделенный read-only DB пользователь с `SELECT` только на пять таблиц, доверенный CA и hostname verification. `scripts/run_local_session.py` предназначен только для локальной QA-туннельной сессии.
5. **Оператор должен настроить хранение и сопровождение.** Persistent encrypted SQLite volume, encrypted off-host backups и restore drill, retention, лимиты/таймауты, SLO и key rotation остаются частью VPS install checklist. Текущий limiter рассчитан на один процесс.
6. **Проксировать только нужный API route.** Через действующий HTTPS host пропускать точный `POST /_internal/product-qa/api/v1/ask` к `/api/v1/ask`; оставить `/ready`, старые `/api/ask`, `/api/search`, UI и `/static` недоступными через этот route. Provider/API credentials остаются server-side.
7. **Перед рабочим трафиком пройти acceptance из VPS runbook.** Версия v1 API прошла только mock container smoke; production TLS, DB grants, network/firewall, backup restore и website-backend integration не выполнялись.

До закрытия этих пунктов система не должна называться production-ready. Подготовка backend к передаче разработчику не означает подключение storefront или разрешение на deploy.

## Следующий рабочий этап

Кодовая часть готова, но backend сайта и storefront не подключены. Для отдельного handoff прочитать [VPS install runbook](../../docs/deployment/product-qa-vps-runbook.md) и настроить server-side вызов Product QA по HTTPS; integration key остаётся только в backend сайта. До рабочего трафика нужны image для целевой архитектуры, MySQL TLS/hostname verification и read-only grants, reverse-proxy route, постоянный защищённый SQLite volume, backup/restore и операционная acceptance. Checkout этой реализации находится по пути `/Users/anatoly/Workspace/03_Business/WORK/Race Expert/QA/.codex-checkouts/product-qa-v18`; это локальный snapshot без remote/upstream.
