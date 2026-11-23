---
schema_version: 2
id: "synthesis.race-expert-qa-production-readiness"
type: "synthesis"
title: "Подготовка Product QA Race Expert к production"
description: "Проверенное текущее состояние backend после live E2E; утверждённый кодовый handoff v18/памяти и отдельные VPS production-блокеры."
tags: ["project:race-expert", "capability:product-qa", "workflow:deployment", "topic:production-readiness", "platform:raceexpert.com.ua"]
source: {"raw_path": "docs/test-harness/qa-live-50-products-500-questions-2026-11-20.md"}
dates: {"added_at": "2026-11-21T17:24:20+02:00", "updated_at": "2026-11-23T19:35:00+02:00"}
relations: [{"type": "references", "target": "synthesis.race-expert-qa-evaluation"}, {"type": "references", "target": "synthesis.race-expert-qa-web-search"}, {"type": "references", "target": "project.race-expert-qa"}]
aliases: ["Product QA production readiness", "Продакшн-готовность Q&A"]
status: "active"
---

# Product QA: production-readiness handoff

## Текущий вывод

23 ноября 2026 развёрнут и подтверждён live-демостенд на VPS (`https://n8n.raceexpert-tools.net.ua/re-products-demo/`). Витрина выполнена в дизайне Race Expert с функционалом Rozetka AI (плавающая кнопка, боковая панель с мини-карточкой товара, переключатель артикулов, динамические быстрые подсказки). Активирован prompt v18 с модулем Intent Classifier (`app/intent_classifier.py`), устраняющим сухой педантизм и роботизированные отказы («отдельной рекомендации пить после забега нет») в пользу реалистичной практики спортивной нутрициологии (протокол ISSN / Adaptive Endurance Coach: питье небольшими глотками по 100–150 мл каждые 15–20 мин на дистанции и прием на финише для быстрого восстановления гликогена).

Реализована полная матрица из 24 товарных категорий и подгрупп (`app/suggested_questions.py`), возвращающая ровно по 6 целевых вопросов через `/api/search` для любого товара из 5000+ позиций каталога OpenCart. Docker-образ собран нативно на VPS, контейнер переведён в статус `ready`, E2E-тесты проверены через браузерный агент и живой API. Все 219 тестов в pytest пройдены успешно.

Ранее backend прошёл локальный 500-сценарный E2E после восстановления SSH-туннеля и offline-набор после адаптации. Live UI E2E на v16 подтвердил запуск Tavily, но ответ был слишком осторожным. После изменения prompt выполнен успешный live UI E2E на v17: каталог повторно подтвердил товар, Tavily вызвался, источник прошёл точный фильтр, OpenAI завершил ответ HTTP 200. Ответ дал прямой общий вывод о спортивном применении без упоминания внутренней карточки или наличия и без заявления о специальной формуле для плавцов. Время полного ответа — 10,759 ms. Локальный интерфейс оставлен открытым на `http://127.0.0.1:8787/`; база доступна через одобренный локальный SSH-туннель. Storefront Raceexpert.com.ua не подключался; staging и production deploy не выполнялись.

Утверждены [спецификация спортивной пригодности и памяти диалога](../../docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md) и [план обновления проекта](../../docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md). Следующий рабочий шаг — реализация v18 и временного контекста в коде и API-контракте. Этот handoff не просит выполнять VPS deployment или менять storefront.

## Проверенные результаты

- Live E2E от 20 ноября: 50 товаров × 10 вопросов, итог 500/500 успешных ответов после повторения 286 неуспешных/недоставленных запросов после перезапуска локального launcher.
- Tavily вызван 217 раз, 0 ошибок провайдера; в 5 финальных попытках были приняты записи по имени товара, только для RE89157. Ни одна запись не подтвердила запрошенный exact-вкус/объём/фасовку. Остальные поиски не дали положительного exact-variant факта.
- 283 финальных попытки имели `search_status=skipped`, то есть Tavily не вызывался. Не считать эти пропуски автоматом корректными: при дальнейшем аудите классифицировать каждый важный сценарий по решению маршрутизации и вопросу. Поиск по одобренному источнику должен запускаться только когда карточки недостаточно или запрошены допустимые темы отзывов.
- Отчёт выявил 21/50 общих ответов на явно нерелевантные вопросы и 41/50 ответов с количеством/инструкцией из карточки в personal-health сценариях.
- План адаптации v14 остаётся в силе: fail-closed `product_related`; фиксированный отказ на личные health/dose вопросы без повторения порций; `verified_product_name` передаётся модели только после точной серверной фильтрации; `/ready` делает read-only `SELECT 1`, а `/health` остаётся liveness. Активный prompt v17 отделяет вопрос о спортивном применении от персональной медицинской рекомендации, запускает точный поиск по производителю при нехватке данных, позволяет ответить на уровне общего спортивного использования и убирает ссылки на внутреннюю карточку и незапрошенное наличие.
- Полный offline-набор v17: 171 тест и 4009 subtests passed. Отдельный mock container smoke на `linux/arm64` проверил hashes v12–v17 и `/health`, `/ready`, `/api/v1/ask`.
- Один live UI E2E на v17: последняя попытка имеет `status=succeeded`, модель `gpt-6-luna`, `prompt_version=v17`, `search_status=used`, `search_provider=tavily`; источник прошёл exact-match фильтр. Поиск занял 488 ms, полный ответ — 10,759 ms. Buyer-facing результат показан в интерфейсе; вопрос, ответ и source provenance в Wiki не копировались.
- Один live local E2E запрос после v14: article `RE89157` разрешился по каталогу; `/api/ask` вернул HTTP 200 и `succeeded`; `search_status=used`; точная запись производителя принята; поиск занял 849 ms, полный запрос 11,811 ms. Финальный ответ не содержал запрошенное число порций и сообщил, что факт не подтверждён доступным evidence. Ответ/запрос и source metadata не скопированы в логи или Wiki; сохранён только штатный SQLite журнал.
- Использовался local QA `/api/search` → `/api/ask` flow через `scripts/run_local_session.py`; это не live auth-check `/api/v1/ask`. Versioned endpoint ранее прошёл контейнерный mock smoke. Uvicorn access logging local launcher выключен для сессии.
- Prompt v12–v16 сохранены без изменений. Активный v17 SHA-256: `f26e6eabf5d2867adf5608843abb1da277c362759cd3606d892c3c101e9fcdea`.
- Production Dockerfile копирует v12–v17 и `scripts/backup_journal.py`; Uvicorn access log выключен. Локальный `race-expert-product-qa:v17-check` собран для `linux/arm64`, in-container mock smoke прошёл для prompt hashes и `/health`, `/ready`, `/api/v1/ask`. Архитектура VPS неизвестна, поэтому разработчик должен собрать образ для целевой архитектуры.
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

## Сообщение для следующего чата

Скопируй этот блок в следующий чат для реализации утверждённой спецификации:

```text
Обнови Race Expert Product QA по утверждённой спецификации и плану реализации:
- docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md
- docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md

Перед работой прочитай AGENTS.md, wiki/index.md, wiki/session-handoff.md, эту production-readiness страницу, prompt v17 и связанные API/assistant файлы. Используй superpowers:executing-plans и выполняй план по задачам; актуальный код сверяй с каждым указанным путём.

Работай в Git checkout, предоставленном пользователем. Если текущая папка не содержит `.git`, сначала используй данный GitHub checkout и сверь в нём hash v17; не выдумывай remote и не перезаписывай пользовательские изменения.

Сейчас активен prompt v17 с SHA-256 f26e6eabf5d2867adf5608843abb1da277c362759cd3606d892c3c101e9fcdea. Сохрани v17 и прежние версии без изменений; добавь новый v18 и активируй его только после обновления pin, журнала, Dockerfile и container smoke.

Обязательное поведение v18: если точный источник производителя или одобренного поставщика подтверждает общее применение для активных спортсменов/после тренировки, но не подтверждает специальную формулу для конкретного спорта, дай обе части в одном коротком ответе: полезный общий вывод и аккуратное ограничение по виду спорта. Не отвечай только «не заявлено»; не утверждай личную безопасность, дозу, лечебный эффект или улучшение результата. Сохрани существующий поиск Tavily по точному товару и все прежние guardrails.

Добавь временную память максимум из 10 последних сообщений всего: до 9 предыдущих user/assistant реплик плюс текущий вопрос. API получает предыдущие сообщения в необязательном поле history, старые клиенты без него продолжают работать. Не принимай system/developer роли. Тело запроса остаётся максимум 16 KiB: удаляй самые старые целые предыдущие сообщения до вхождения в лимит, текущий вопрос не сокращай. История относится только к одному выбранному товару; local UI сбрасывает её при смене товара и перезагрузке. Не добавляй persistent storage, endpoint чтения истории, отдельные логи истории или доверие к прежним ответам как к доказательствам. Product QA заново проверяет товар на каждом запросе. Учитывай релевантный prior health-контекст в зависимых follow-up и сохраняй фиксированный отказ без дозировки.

Обнови API OpenAPI/integration docs, VPS runbook, AGENTS.md, README, локальный UI, offline regression tests, prompt hash loader, журнал версии, Dockerfile и smoke. После завершения обнови Wiki и session-handoff через штатный save_memory workflow. Не копируй покупательские вопросы/ответы, source URLs/provenance или секреты в Wiki.

Граница этой задачи: код, API-контракт, локальный UI, документация и offline/mock verification. Не меняй отдельный storefront/backend сайта, не делай VPS/staging/production deployment и не запускай платные live OpenAI/Tavily запросы. Реальная интеграция endpoint сайта и установка на VPS остаются отдельным следующим шагом по docs/deployment/product-qa-vps-runbook.md. Не передавай разработчику provider, database, SSH или integration credentials.

Проверь focused tests и полный pytest suite, hash неизменённого v17, новый v18 pin, API backward compatibility, memory reset/size behavior и container smoke без сети. В конце перечисли изменения, фактические результаты проверок и оставшуюся границу интеграции/production.
```
