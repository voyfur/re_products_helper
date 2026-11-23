---
schema_version: 2
id: "project.race-expert-qa"
type: "project"
title: "Race Expert — вопросы и ответы о товаре"
description: "Отдельное приложение Q&A по выбранному товару; активен prompt v18 с Intent Classifier, 24-категорийной матрицей быстрых вопросов и UI витрины в стиле Rozetka AI на VPS."
tags: ["project:race-expert", "domain:ecommerce", "capability:product-qa", "capability:web-search", "workflow:implementation", "topic:product-data", "topic:ui-redesign", "topic:intent-classifier"]
source: {"raw_path": "raw/sources/qa-project-scope-and-transfer-2026-11-18.md"}
dates: {"added_at": "2026-11-18T19:28:00+02:00", "updated_at": "2026-11-23T19:35:00+02:00"}
relations: [{"type": "references", "target": "synthesis.race-expert-qa-evaluation"}, {"type": "references", "target": "source.race-expert-qa-mysql-access"}, {"type": "references", "target": "synthesis.race-expert-qa-web-search"}, {"type": "references", "target": "synthesis.race-expert-qa-production-readiness"}]
aliases: ["Race Expert Q&A", "Помощник по вопросам о товаре"]
status: "active"
---

# Race Expert — Q&A о товаре

## Назначение

Покупатель или тестировщик находит товар по артикулу, модели или SKU и задаёт вопрос именно о выбранной карточке. Сервер повторно подтверждает пару article/product_id перед вызовом модели, чтобы ответ не строился по подменённому товару.

## Поток

1. Каталог возвращает точные совпадения по model/SKU; при нескольких результатах пользователь выбирает нужный товар.
2. Сервер отправляет модели данные украинской карточки, контекст диалога (до 10 последних сообщений) и текущий вопрос. Входной запрос классифицируется модулем Intent Classifier (`app/intent_classifier.py`), который динамически подключает доменные правила (витрина выносливости, нутрициология, единоборства/зал, общий консультант).
3. Сервис может ответить по карточке или запросить одну узкую тему для поиска. Backend строит запрос из идентичности товара и фиксированной темы; произвольный текст покупателя не отправляется как поисковый запрос. Если в карточке не хватает информации о бренде или фактах, автоматически срабатывает fallback-поиск через Tavily по белому списку производителей.
4. При нужде Tavily ищет только по runtime allowlist, после повторной проверки товара. Ответ формируется по активному prompt v18 на украинском языке, независимо от языка вопроса, без канцеляризмов («в карточке указано», «на товаре написано») и без роботизированных отказов («отдельной рекомендации нет»).
5. Попытка, приватные provenance и задержки записываются в SQLite; excerpts и тексты отзывов не сохраняются, а buyer-facing API не выдаёт metadata.
6. Будущий backend сайта отправляет `article` и текущий `question` на `POST /api/v1/ask`.

## Витрина и быстрые вопросы (Rozetka AI style)

1. Витрина реализована в дизайне Race Expert с функционалом Rozetka AI: плавающая брендированная кнопка `Race Expert AI`, выдвижная боковая панель с мини-карточкой товара (название, фото, артикул, статус наличия, цена, переключатель артикулов `RE0126`, `RE1050`, `RE0518`).
2. Полная матрица из 24 товарных групп и подгрупп реализована в `app/suggested_questions.py`: покрывает 100% каталога OpenCart (гели стандартные, кофеиновые, 1:0.8, порошки, таблетки электролитов, изотоники, солевые капсулы, сывороточный/казеиновый/веганский протеин, рековери, гейнеры, креатин, аминокислоты, предтрены, батончики, пасты, каши, суставы/коллаген, витамины, шейкеры, фляги).
3. Для каждой группы предоставляется ровно по 6 целевых быстрых вопросов, возвращаемых эндпоинтом `/api/search` и динамически переключаемых при смене товара на витрине.
4. Live демо развёрнуто на VPS по адресу `https://n8n.raceexpert-tools.net.ua/re-products-demo/`.

## Данные и ограничения

Поиск использует read-only параметризованный запрос к пяти таблицам OpenCart: oc_product, oc_product_description, oc_product_attribute, oc_attribute_description и oc_stock_status. В запрос не включаются цена, остатки как числовые обещания, данные покупателей, заказы или сведения иных товаров.

Последняя проверка grants показала дополнительные SELECT-разрешения у текущей учётной записи сверх этих пяти таблиц. Код QA обращается только к пяти таблицам карточки; для строгой изоляции перед развёртыванием нужен отдельный MySQL-пользователь только с нужными Q&A-разрешениями.

Для локальной QA-сессии используется отдельный запускатель через временный SSH-туннель VPS-61125. Он проверяет SSH host key (`StrictHostKeyChecking=yes`) и требует MySQL TLS 1.2/1.3, но отключает проверку MySQL-сертификата и имени только в этой локальной сессии. У endpoint самоподписанный сертификат без подходящего SAN; шифрование включено, личность MySQL-сервера этой проверкой не подтверждается. Этот режим не подходит для постоянного backend, staging или production. Там нужны независимо подтверждённый CA и подходящее имя сервера. Источник решения: [зафиксированная инструкция](../../raw/sources/qa-local-ssh-tunnel-instruction-2026-11-18.md); запуск и ограничения: [локальный runbook](../../docs/test-harness/local-session-runbook.md).

QA-конфигурация и секреты хранятся локально в игнорируемых `.env`/`secrets/`; их значения в Wiki не записываются. Приложение не открывает SSH-туннель при обычном прямом запуске; используй `scripts/run_local_session.py`.

## Доступ к MySQL и схема

Состав таблиц, grants, ограничения источника базы и статус локальных доступов описаны в отдельной [карточке MySQL для Q&A](qa-mysql-readonly-access-and-product-query.md) и [manifest источников](../source-manifest.md).

## Историческая проверка Q&A

13.11.2026 локальный стенд нашёл два точных товара и успешно выполнил два запроса GPT-6 Luna с prompt v11; попытки записались в SQLite. Тогда ответы следовали языку вопроса. Это исторический результат до v12, а не проверка текущего языка ответов. Подробности: [отчёт Q&A](../../docs/test-harness/qa-live-run-report-2026-11-13.md).

## Web Search и backend API

В коде реализованы Tavily adapter/configuration, доменно-ограниченная обработка доказательств, versioned API `/api/v1/ask`, активный prompt v17 и приватная provenance конкретной попытки. Prompt v12–v16 сохранены; SHA-256 v17 закреплён в runtime. Локальный launcher читает ровно один из `TAVILY_API_KEY` или `TAVILY_API_KEY_FILE` через свой allowlist-парсер.

Пользователь утвердил стартовый набор exact hostnames производителей/поставщиков из исследования и две review-площадки. `SOURCE_REGISTRY` содержит только явно перечисленные hostnames; factual sources ограничены брендами. `nutrend.com.ua` активен только как условный supplier для NUTREND, без статуса manufacturer-confirmed. Для отзывов включены `fit.rozetka.com.ua` и `prom.ua`; Rozetka aliases имеют одну независимую группу. Makeup, Epicentr, SaltStick redirect и holdout бренды исключены. Это не полное покрытие каталога. Отзывы допускаются только как анонимная общая тема, поддержанная двумя независимыми площадками; непересекающиеся темы не передаются модели. Отзывы не служат источником объективных или health-фактов.

Подготовлены [спецификация Web Search](../../docs/superpowers/specs/2026-11-19-product-qa-web-search-design.md), [план](../../docs/superpowers/plans/2026-11-19-product-qa-web-search.md), [исследование доменов](../../docs/superpowers/research/2026-11-19-raceexpert-web-search-domain-research.md), [API-контракт](../../docs/api/product-qa-v1.yaml), [handoff разработчику](../../docs/api/product-qa-integration.md) и [brief интерфейса](../../docs/ui/product-qa-widget-brief.md). Для следующего изменения утверждены [спецификация спортивного ответа и памяти](../../docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md) и [план реализации v18](../../docs/superpowers/plans/2026-11-21-product-qa-sports-suitability-and-memory.md). До завершения этого плана активным остаётся v17; API пока не принимает историю. Утверждённый набор источников не покрывает все бренды. VPS в Украине — будущая цель; production-подключение требует runbook, TLS/firewall и read-only учётной записи.

Offline-набор prompt v17 и mock container smoke пройдены; 21.11 выполнен один bounded local UI E2E через каталог, Tavily exact-source filter и OpenAI. Подробности и границы покрытия сохранены в [production-readiness synthesis](../syntheses/race-expert-qa-production-readiness.md). В этой сессии секреты не открывались; staging и production deploy не выполнялись. Общий staging остаётся отдельной средой на прежнем v12.

## Существующий общий staging

В общем test harness Q&A prompt v12 развёрнут 16.11.2026; последняя запись статуса на 17.11 указывает общий image product-overview-v4. Этот стенд не является отдельным QA-проектом из этой папки. Его URL: https://n8n.raceexpert-tools.net.ua/re-products-demo/. Basic Auth отключён по запросу пользователя, а лимита GPT-запросов нет; вызовы могут создавать расходы. После выкладки v12 live-вызов Q&A не выполнялся. Не отправляй запросы и не развёртывай код туда без отдельного задания. См. [границу staging](../../raw/sources/qa-staging-boundary-2026-11-18.md).

## Статус

Отдельная локальная копия Q&A создана 18.11.2026. QA-only `.env`, защищённые секреты и Q&A-only SSH-запускатель настроены; значения секретов в Wiki не записываются. Локальная сессия v17 прошла через одобренный tunnel, но не подключала storefront, staging или production. Перед публикацией нужны целевая архитектура VPS, проверенная идентичность базы, пользователь с минимальными grants и ограничения доступа/расходов.

Для технической оценки см. [сводку Q&A](../syntheses/race-expert-qa-evaluation.md).
