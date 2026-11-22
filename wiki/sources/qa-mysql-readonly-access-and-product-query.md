---
schema_version: 2
id: "source.race-expert-qa-mysql-access"
type: "source"
title: "Q&A: read-only MySQL context and access"
description: "Self-contained Q&A scope for the five OpenCart tables, grants, local SSH tunnel, MySQL TLS, and credential prerequisites."
tags: ["project:race-expert", "topic:database-access", "topic:database-schema", "topic:product-data", "capability:product-qa"]
source: {"raw_path": "raw/sources/qa-mysql-schema-and-access-context-2026-11-18.md"}
dates: {"added_at": "2026-11-18T22:37:55+02:00", "updated_at": "2026-11-18T22:37:55+02:00"}
relations: [{"type": "supports", "target": "project.race-expert-qa"}]
aliases: ["QA MySQL guide", "Контекст доступа QA к MySQL"]
status: "active"
---

# MySQL и контекст данных для Race Expert QA

## Подключение

Локальный запуск выполняется через scripts/run_local_session.py: он проверяет SSH host key, создаёт временный туннель через VPS-61125 и требует MySQL TLS 1.2 или 1.3. Проверка сертификата и имени MySQL-сервера отключена только в этой локальной сессии. TLS остаётся включён; личность MySQL endpoint этим способом не подтверждается. Подробные шаги — в [локальном runbook](../../docs/test-harness/local-session-runbook.md).

QA-конфигурация и нужные секреты находятся в игнорируемых .env и secrets/. На момент последней локальной проверки файлы присутствовали с ограниченными правами, запускатель прочитал их без вывода значений, а VPS host key нашёлся в системном known_hosts. Сами SSH/MySQL учётные данные и OpenAI ключ внешне не проверялись. Локального файла CA для прямого подключения нет; прямой коннектор требует CA и hostname verification.

## Доступ и границы запросов

Проверенный учётный аккаунт исторически имел только read-only права, но SELECT предоставлен на семь таблиц. QA читает только пять таблиц карточки товара: oc_product, oc_product_description, oc_product_attribute, oc_attribute_description и oc_stock_status. Ещё две таблицы в grants не нужны приложению; код Q&A их не запрашивает. До постоянного развёртывания выдай отдельному пользователю SELECT только на пять таблиц Q&A.

Схема и права проверялись 2026-11-10. Текущий endpoint был взят из локальной конфигурации, но его соответствие актуальной базе сайта не подтверждено администратором. Повторная проверка в этой QA-папке не выполнялась.

## Схема, которую использует Q&A

| Таблица | Столбцы по аудиту | Связь и используемые поля |
|---|---:|---|
| oc_product | 35 | product_id — PK; model индексирован, но не уникален; sku |
| oc_product_description | 10 | product_id + language_id; name, description |
| oc_product_attribute | 4 | product_id, attribute_id, language_id, text |
| oc_attribute_description | 3 | attribute_id + language_id; имя характеристики |
| oc_stock_status | 3 | stock_status_id + language_id; подпись наличия |

Языки 1 и 6 соответствуют русской и украинской локали. Точные столбцы и SQL смотри в текущем коде [app/catalog.py](../../app/catalog.py); он остаётся источником истины, если схема изменится.

## Что получает модель

Q&A повторно подтверждает товар по паре article/product_id. Для ответа используется только украинское название, очищенное описание, характеристики и локальная подпись наличия выбранной карточки вместе с текущим вопросом. Цены, количественные остатки, отзывы, заказы, данные покупателей, другие товары и история вопросов в контекст модели не включаются. Активный системный prompt — [v12](../../prompts/product-assistant-system-v12.md); ответ всегда по-украински.

Полный срез доступа, источники и ограничения сохранены в [raw capture](../../raw/sources/qa-mysql-schema-and-access-context-2026-11-18.md).
