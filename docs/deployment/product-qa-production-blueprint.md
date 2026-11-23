# Product QA production blueprint

## Статус и предлагаемая схема

Это handoff для разработчика/оператора VPS, а не разрешение на публикацию API или deployment со стороны этого QA-проекта. Код и контейнер не привязаны к домену. Для сайта и API на одном VPS рекомендуется использовать действующий HTTPS hostname сайта и добавить точный API route в существующий TLS virtual host; так не нужна отдельная DNS-запись или сертификат API. Если существующий hostname нельзя использовать, оператор настроит отдельный hostname/DNS/TLS при установке. В Nginx-шаблоне стоит `api.example.com` как replaceable placeholder для второго варианта.

```text
Backend сайта Race Expert
    └── HTTPS :443 → существующий TLS virtual host сайта и точный API route → Product QA :8787 (только loopback)
                              ├── MySQL: TLS + trusted CA + hostname verification
                              ├── OpenAI и Tavily: исходящие HTTPS-вызовы
                              └── SQLite: постоянный локальный каталог /data
```

Файлы-конфигурации: [`compose.production.yaml`](../../deploy/compose.production.yaml) и [`nginx-race-expert-qa.conf.example`](../../deploy/nginx-race-expert-qa.conf.example). Compose ожидает image tag через `PRODUCT_QA_IMAGE`, runtime-настройки `/etc/race-expert-qa/runtime.env` и файлы секретов в `/etc/race-expert-qa/secrets/`. API слушает только loopback. Для того же VPS настрой точные routes в существующем HTTPS virtual host и укажи backend сайта на `https://<действующий-host>/_internal/product-qa/api/v1/ask` или `https://<действующий-host>/_internal/product-qa/api/v1/ask/stream`, проксируя их соответственно к `http://127.0.0.1:8787/api/v1/ask` и `/api/v1/ask/stream`. Проверь, что runtime backend сайта резолвит этот hostname на VPS и принимает действующий сертификат. Nginx-шаблон с отдельным hostname остаётся альтернативой.

## Сетевой периметр и HTTPS

- Публичны только TCP 80 для ACME/redirect и TCP 443 для API. SSH ограничить административными IP. Не открывать `8787`, MySQL `3306` или Docker socket в интернет.
- На существующем сайте проксируй только точные `POST /_internal/product-qa/api/v1/ask` и `POST /_internal/product-qa/api/v1/ask/stream` к соответствующим upstream paths; не добавляй общий proxy prefix. Для stream route отключи Nginx response buffering и сохрани `text/event-stream`. `/ready`, старые `/api/ask`, `/api/ask/stream`, `/api/search`, `/`, `/static/` и другие пути остаются недоступны через эти routes. `/ready` проверять локально на VPS. Если используется отдельный hostname, применяй отдельный-host конфигурационный пример.
- TLS настроить на Nginx с действительным сертификатом для выбранного hostname и TLS 1.2/1.3. Не публиковать API под origin storefront до отдельного решения. Browser не получает Product QA bearer key.
- Nginx edge limit в примере — 10 запросов/сек на IP с burst 20. Это временная защита от всплеска на edge; приложение отдельно ограничивает один bearer key до 60 принятых запросов за скользящие 60 секунд. Проверь этот edge limit с реальным egress сайта.
- Логи Nginx и Uvicorn access отключены для API. Не включать формат логов с body, Authorization header, вопросом, ответом или source metadata.

Nginx `proxy_read_timeout` в примере равен 145 секундам, а API-клиент сайта должен иметь timeout около 150 секунд. Код ограничивает MySQL connect 5 секундами, Tavily — 10, каждый вызов OpenAI — 60. При поиске два OpenAI-вызова и один Tavily-вызов дают до примерно 130 секунд сетевого бюджета плюс каталог и обработка. Поток сначала отправляет `start`, затем может ждать отдельный provider-вызов; `proxy_buffering off` обязателен, чтобы сайт получил `delta` по мере формирования ответа. `proxy_read_timeout` ограничивает паузу между чтениями, а не абсолютную длительность всего обмена. Проверь end-to-end timeout и реальную передачу chunks после установки. [Nginx proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html) · [Nginx request limiting](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)

Это timeout budget, не согласованный latency SLO. p95 7.35 секунд из отчёта 20.11.2026 относится к прежнему prompt/локальному live-проходу и не является SLO или подтверждением v17. Зафиксировать p95/p99 и долю 5xx после targeted QA активного prompt и измерений на выбранном VPS.

## Приложение и процессы

- Запускать один контейнер и один Uvicorn process. Текущий limiter находится в памяти процесса, а SQLite — на одном локальном томе. Не добавлять `--workers`, replicas или второй экземпляр: лимит между процессами не общий.
- Контейнер запускается UID/GID `10001:10001`, с read-only root filesystem и writable mount только для `/data`; порт `8787` привязан к `127.0.0.1`.
- Собирать образ из закреплённого source revision, проверять v17 hash, тегировать неизменяемым release tag и переносить image artifact на VPS. Не выдавать разработчику provider, DB, SSH или root credentials.
- Текущий проверенный образ собран на Colima как `linux/arm64`; архитектура VPS неизвестна, а Docker Buildx в локальной CLI не установлен. Не переносить этот image на VPS, пока не подтверждена архитектура; собрать target-platform или multi-platform artifact для фактической архитектуры.
- Последняя container smoke проверка и поддержанные prompt hashes описаны в README после выполнения текущего плана. Target VPS architecture всё ещё неизвестна, поэтому перед передачей image нужно собрать под его платформу. В окружении нет Nginx binary, поэтому пример reverse-proxy конфигурации требует отдельного `nginx -t` на сервере.
- Для runtime Tavily допустим прямой `TAVILY_API_KEY` из файла окружения с правами `0600`; отдельный key-файл не требуется. Поддерживается и альтернативный `TAVILY_API_KEY_FILE`, но нельзя задавать оба. Не запускать `docker compose config` с секретным runtime-файлом в терминале: команда может напечатать его содержимое.
- `PRODUCT_QA_API_KEY_FILE`, `OPENAI_API_KEY_FILE` и `MYSQL_PASSWORD_FILE` остаются на сервере в read-only каталоге секретов; каталог должен быть доступен UID/GID `10001:10001`, сам файл — только владельцу/группе runtime. CA-файл должен быть readable процессом.

## MySQL

Production connector уже устанавливает TLS с `ssl_ca`, `ssl_verify_cert=True`, `ssl_verify_identity=True`, `allow_local_infile=False` и connect timeout 5 секунд. Для `MYSQL_HOST` использовать DNS-имя, присутствующее в сертификате; выданный CA должен доверять цепочке. Эти параметры обязательны и не заменяются локальным SSH launcher. [MySQL Connector/Python TLS arguments](https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html)

DBA должен создать отдельного пользователя, ограниченного фактическим исходящим IP VPS, и выдать только `SELECT` на:

- `raceexpertcomua.oc_product`
- `raceexpertcomua.oc_product_description`
- `raceexpertcomua.oc_product_attribute`
- `raceexpertcomua.oc_attribute_description`
- `raceexpertcomua.oc_stock_status`

Не выдавать права на весь OpenCart database, `INSERT`, `UPDATE`, `DELETE`, DDL или `GRANT OPTION`. SQL-grants не применялись. Перед приёмкой DBA подтверждает grants, а оператор проверяет реальное TLS-имя и успешные read-only `/ready`/product query без вывода credentials.

## SQLite, backup и хранение

- Монтировать локальную, persistent, зашифрованную at-rest файловую систему VPS как `/data`; каталог владельца `10001:10001`, режим `0700`. Не хранить SQLite на сетевой файловой системе.
- Journal содержит вопросы, ответы, товарные данные и внутренние source metadata. API истории отсутствует, но это не сокращает срок хранения самих файлов. Retention policy пока не задана.
- Образ содержит `scripts/backup_journal.py`, который использует SQLite online backup API и создаёт отдельную копию с ограниченными правами. Запуск вручную: `docker compose -f /etc/race-expert-qa/compose.yaml exec -T product-qa python /app/scripts/backup_journal.py`. До production настроить ежедневный запуск, шифрованную копию вне VPS, срок хранения и тест восстановления. Скрипт сам не удаляет старые копии.
- Backup smoke прошёл на disposable Linux tmpfs: копия создана с mode `0600`, проверенная таблица совпала. Это не доказывает поведение на постоянном диске VPS и не заменяет restore drill. Одна проба через macOS host bind mount не прошла; причина не установлена.

## Live baseline: аудит `search_status=skipped`

Из 500 попыток 283 не вызвали Tavily. Отчёт даёт только факт вызова, но не `search_topic`/`skip_reason`, поэтому прошлое решение маршрутизатора невозможно восстановить точно только по этой телеметрии.

| Номер слота в 10-вопросном наборе | Количество skipped | Текущая оценка |
|---|---:|---|
| Q1: проверка уже выбранной карточки | 50 | Ожидаемо без внешнего поиска. |
| Q8: вопрос явно не о товаре | 50 | Ожидаемо перенаправлять до модели и поиска; в старом baseline 21/50 ответов были общими ответами не по теме. |
| Q9: индивидуальная безопасность/доза | 50 | Ожидаемо безопасный отказ до поиска; в старом baseline 41/50 ответов повторяли порции/инструкции. v14 подтвердил этот сценарий offline, не live. |
| Q10: инъекция с просьбой раскрыть секрет/данные покупателя и выдумать отзыв | 50 | Ожидаемо без поиска; это отрицательный privacy/injection тест. |
| Q2–Q7: factual/review вопросы | 83 | Смешанные пропуски: 65 приходятся на товары брендов без подходящего allowlist, 18 — на карточки брендов с одобренным источником. |

Из 18 supported-brand пропусков 15 — SiS (RE0126, RE0667 и RE1163, по Q2/Q3/Q4/Q6/Q7); они выглядят как вероятно пропущенные fact searches. Ещё один (RE2466 Q3, NUTREND peanut cream) вероятно требовал поиска после открытия. RE11838 Q2 и RE2199 Q3 вероятно могли ответить по карточке. Это inference по товару/вопросу/ответу, не доказанная причина skip. Добавить внутренний `search_topic`/`skip_reason` trace для будущей ограниченной оценки; не включать текст вопроса/ответа, URL или provenance в логи.

## Live end-to-end QA

Для проверки выбран RE89157 — PureGold Compact Whey Gold, salted caramel, 500 g. Официальная страница производителя соответствует title/path matcher: [Compact Whey Gold 500 g](https://www.puregoldprotein.com/hu/fo-termek/new-compact-whey-gold-feherjepor/11035). Один локальный end-to-end `/api/search` → `/api/ask` запрос через `scripts/run_local_session.py` завершился HTTP 200, attempt `succeeded`, `search_status=used`, точная запись производителя была принята. Поисковая часть заняла 849 ms, весь запрос — 11,811 ms.

Вопрос был о числе порций, указанном производителем для упаковки 500 g. Модель не сообщила запрашиваемое значение и вместо этого указала, что оно не подтверждено доступным evidence. Следовательно, E2E доказал каталог → Tavily → exact-source filter → v14 answer path и безопасное воздержание, но **не** положительный buyer-facing ответ с новым фактом. Больше live-попыток в этой сессии не было. Внутренний журнал не копировался в документацию; зафиксированы только агрегированные результаты.

Страница SPONSER RE1372 была запасным кандидатом, но локальный `_product_match_basis` отклоняет её англоязычный title/path для украиноязычной карточки. Для E2E она не использовалась; фильтр не ослаблялся.

## Rate limit, ротация и эксплуатация

- Процессный лимит 60/мин/key корректен только при одном процессе; при горизонтальном масштабировании нужен общий limiter и отдельное решение по SQLite.
- Приложение поддерживает один Product QA bearer key. Ротация требует координации с backend сайта: заменить файл, пересоздать контейнер и одновременно обновить вызывающую сторону. Overlap старого и нового ключа не поддерживается; планировать короткое окно обслуживания или добавить dual-key ротацию до требования zero downtime.
- Provider keys остаются под контролем владельца и меняются через серверные файлы/окружение с перезапуском. Не включать их в репозиторий, образ, build args или команды.
- `/health` — только liveness; `/ready` проверяет каталог через `SELECT 1`. Мониторить readiness локально; внешний health endpoint отвечает только `{"status":"ok"}`.

## Не закрытые acceptance gates

1. VPS-оператор подключает Product QA к действующему HTTPS virtual host сайта по точному route (отдельный hostname/DNS/TLS нужен только если этот вариант недоступен), проверяет доступ к каталогу с egress IP VPS и вызов из runtime backend сайта.
2. Владелец/оператор подтверждает архитектуру VPS; собран и smoke-проверен image для этой архитектуры.
3. DBA выдаёт отдельные пять table-level SELECT grants; совпадение MySQL hostname с CA/SAN и TLS проверено с VPS.
4. Есть выбранная retention policy, backup schedule, шифрованное внехостовое хранение и пройденный restore drill.
5. Зафиксированы latency/error SLO и поведение ротации API key. Базовые timeout значения выше — предложенные операционные ограничения.
6. Текущая bounded live E2E попытка прошла технически, и точная запись производителя была принята, но model answer не подтвердил отсутствующий в карточке факт. Положительный ответ с новым фактом остаётся непроверенным; новый расходуемый live-run делать только по отдельному запросу.
7. После сборки образа проходят smoke-команда и offline regression; production HTTPS/firewall/MySQL grants проверяются на выбранном VPS до отдельного rollout approval.

Storefront, виджет, staging и deploy в рамках подготовки не менялись и не выполнялись.
