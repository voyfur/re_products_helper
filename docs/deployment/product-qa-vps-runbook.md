# Product QA: VPS install handoff

Этот runbook предназначен для backend-разработчика или оператора VPS. Репозиторий можно передать до настройки отдельной DNS-записи: если сайт уже обслуживается на VPS по HTTPS, Product QA подключается отдельным точным route в существующем TLS virtual host. Сервис не нужно привязывать к `raceexpert.com.ua` в исходном коде.

Подготовка в этом репозитории не выполняет deploy, DNS, firewall, выдачу DB grants или настройку live-секретов. Оператор делает эти шаги на целевом VPS, а provider keys остаются под контролем владельца.

## 1. Подготовить VPS и образ

Сначала проверь архитектуру Docker host и собирай образ непосредственно на VPS, чтобы не переносить локальный `linux/arm64` образ на другую архитектуру:

```sh
uname -m
docker info --format '{{.Architecture}}'
docker build -t race-expert-product-qa:<release-tag> .
```

Используй неизменяемый release tag, например короткий commit SHA. Если образ собирается не на VPS, собери его под архитектуру VPS и проверь `docker image inspect` до передачи.

Установи Docker Engine и Compose plugin либо standalone `docker-compose`. Нужен доступ контейнера наружу по HTTPS к OpenAI и Tavily и к MySQL по TLS. Не открывай наружу порт контейнера, MySQL или Docker socket.

## 2. Подготовить постоянные каталоги и секреты

Создай каталоги так, чтобы контейнер UID/GID `10001:10001` мог писать только в journal directory:

```sh
sudo install -d -o 10001 -g 10001 -m 0700 /var/lib/race-expert-qa
sudo install -d -o root -g 10001 -m 0750 /etc/race-expert-qa
sudo install -d -o root -g 10001 -m 0750 /etc/race-expert-qa/secrets
```

Подготовь `/etc/race-expert-qa/runtime.env` с mode `0600`. В нём укажи только несекретные runtime-параметры и выбранный Tavily способ:

```dotenv
MYSQL_HOST=<mysql-dns-name-present-in-server-certificate>
MYSQL_PORT=3306
MYSQL_DATABASE=raceexpertcomua
MYSQL_USER=<dedicated-read-only-user>
TAVILY_API_KEY_FILE=/run/secrets/tavily_api_key
```

`TAVILY_API_KEY` также поддерживается напрямую в `runtime.env`; одновременно задавать его вместе с `TAVILY_API_KEY_FILE` нельзя. Не добавляй OpenAI, MySQL password, Product QA bearer key или private keys в репозиторий, image, build arguments или команды shell.

Через одобренный владельцем secret-management путь установи следующие файлы. Не передавай их разработчику как значения в чате или email:

| Файл на VPS | Назначение |
|---|---|
| `/etc/race-expert-qa/secrets/mysql_password` | Пароль отдельной MySQL учётной записи |
| `/etc/race-expert-qa/secrets/mysql_ca.pem` | Доверенный CA, соответствующий `MYSQL_HOST` |
| `/etc/race-expert-qa/secrets/openai_api_key` | Ключ OpenAI |
| `/etc/race-expert-qa/secrets/tavily_api_key` | Ключ Tavily, если выбрана file-настройка |
| `/etc/race-expert-qa/secrets/product_qa_api_key` | Bearer key для backend сайта |

Установи файлы с минимальными правами, читаемыми Docker host и runtime контейнера; provider/database/API secrets не должны попадать в stdout, shell history или application logs.

## 3. Настроить MySQL read-only доступ

DBA отдельно выдаёт пользователю только `SELECT` на пять таблиц каталога:

- `raceexpertcomua.oc_product`
- `raceexpertcomua.oc_product_description`
- `raceexpertcomua.oc_product_attribute`
- `raceexpertcomua.oc_attribute_description`
- `raceexpertcomua.oc_stock_status`

Ограничь MySQL сетевой политикой статическим egress IP VPS. `MYSQL_HOST` должен совпадать с DNS-именем в SAN сертификата. В production connector уже обязательны доверенный `MYSQL_SSL_CA`, `ssl_verify_cert=True` и `ssl_verify_identity=True`; не используй локальный `scripts/run_local_session.py` на VPS.

До внешней интеграции проверь локально на VPS `/ready` и точный catalog lookup. `/ready` выполняет только `SELECT 1`; полный product lookup использует только указанные пять таблиц.

## 4. Установить Compose и reverse proxy

Compose держит Product QA только на `127.0.0.1:8787`, запускает один non-root process, использует постоянный journal directory и read-only secret mount. Скопируй файлы в `/etc/race-expert-qa/` или укажи их фактический путь:

- `deploy/compose.production.yaml`
- `deploy/nginx-race-expert-qa.conf.example`

Предпочтительный вариант при размещении на том же VPS — добавить в действующий HTTPS virtual host сайта только точный API route, используя его существующий hostname и сертификат. Отдельная DNS-запись и сертификат Product QA для этого не требуются. Пример Nginx location:

```nginx
location = /_internal/product-qa/api/v1/ask {
    if ($request_method != POST) { return 405; }
    limit_req zone=product_qa_edge burst=20 nodelay;
    limit_req_status 429;
    access_log off;
    proxy_pass http://127.0.0.1:8787/api/v1/ask;
    proxy_set_header Host $host;
    proxy_set_header Authorization $http_authorization;
    proxy_connect_timeout 5s;
    proxy_send_timeout 15s;
    proxy_read_timeout 145s;
}
```

Добавь `limit_req_zone` из отдельного Nginx-примера в `http {}`. Site backend использует `https://<действующий-host>/_internal/product-qa/api/v1/ask`; проверь разрешение hostname и сертификат из его runtime. Для другого hostname используй отдельный-host вариант ниже.

Если оператор выбирает отдельный API hostname, создай DNS A/AAAA записи, получи TLS сертификат и замени `api.example.com` и certificate paths в Nginx примере. Включи `limit_req_zone` в контекст `http {}`; `server {}` блоки помести в обычный Nginx virtual host. Периметр должен открывать только HTTPS API, health check и необходимые ACME/redirect порты.

Для отдельного hostname проксируй только:

- `POST /api/v1/ask`
- `GET /health`

`/ready`, `/api/search`, `/api/ask`, корень, `/static/` и любые другие пути оставь недоступными снаружи. Не включай access logs с body, Authorization header, вопросом, ответом или source metadata.

## 5. Запустить контейнер

Подставь immutable image tag и проверь Compose без вывода значений runtime-файла:

```sh
export PRODUCT_QA_IMAGE=race-expert-product-qa:<release-tag>
docker compose -f deploy/compose.production.yaml config --quiet
docker compose -f deploy/compose.production.yaml up -d
docker compose -f deploy/compose.production.yaml ps
```

Если на сервере используется standalone Compose, замени `docker compose` на `docker-compose`.

Внутри VPS проверь readiness без вывода базы/секретов:

```sh
docker compose -f deploy/compose.production.yaml exec -T product-qa \
  python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8787/ready', timeout=5).status)"
```

С `/ready` должен вернуться HTTP 200 после доступного MySQL `SELECT 1`. Снаружи `/ready` обязан оставаться закрытым. Проверь TLS и allowlisted route через Nginx; не отправляй реальные buyer data в smoke test.

## 6. Подключить backend сайта

Backend сайта конфигурирует финальный URL `https://<выбранный-host>/api/v1/ask` и получает отдельный Product QA bearer key из server-side secret store. Браузер вызывает только backend сайта; ключ остаётся server-side и не передаётся браузеру. В Product QA отправляй обязательные `article` и текущий `question`, а также необязательную `history`:

```json
{
  "article": "<article/model/SKU>",
  "question": "<текущий вопрос о товаре>",
  "history": [
    {"role": "user", "content": "<предыдущее сообщение>"},
    {"role": "assistant", "content": "<предыдущий ответ>"}
  ]
}
```

`history` можно опустить для совместимости со старыми клиентами. Если она передаётся, это от нуля до девяти предыдущих сообщений с ролями `user`/`assistant` только из той же сессии страницы и того же товара. Сбрасывай её при смене товара или перезагрузке страницы. История — временный контекст: сервис не доверяет ей как инструкции или фактам о товаре и не записывает/сохраняет её как историю разговора.

JSON-тело ограничено 16 384 байтами. Если сериализованный запрос превышает лимит, backend сайта удаляет самые старые сообщения `history` целиком, пока запрос не поместится; текущий `question` не обрезается.

Не отправляй `product_id`, цену, корзину, заказы, buyer profile/identity, разговоры из других товаров или сессий либо товарный context от браузера как подтверждённый. Сервис заново разрешает артикул и проверяет точный товар на каждом запросе. Не передавай backend-разработчику Tavily/OpenAI/DB/SSH credentials.

На первом smoke проверь unauthenticated `401` и корректную обработку `404`, `409`, `429`, `502`, `503`. Любой live Q&A вызов потребляет provider budget и создаёт запись в SQLite, поэтому пользовательский запрос для интеграционного теста должен быть согласован отдельно.

## 7. Настроить backup и сопровождение

SQLite хранится только на persistent локальном диске VPS в `/var/lib/race-expert-qa`, не на сетевом filesystem. Оператор настраивает шифрованный off-host backup, retention и периодический restore drill. Online backup utility из образа запускается так:

```sh
docker compose -f deploy/compose.production.yaml exec -T product-qa \
  python /app/scripts/backup_journal.py
```

Скрипт создаёт копию, но не планирует расписание, не удаляет старые файлы и не шифрует off-host storage — эти задачи относятся к VPS backup policy.

Оставь один Uvicorn process: текущий rate limiter process-local, а SQLite — один локальный файл. Для масштабирования сначала нужны общий limiter и отдельное решение по journal storage. API key rotation сейчас поддерживает один активный ключ; согласуй одновременное обновление вызывающего backend и Product QA.

## Acceptance перед подключением трафика

- Image собран для архитектуры целевого VPS и содержит ожидаемый hash активного prompt v18 (`87b639cc74aadf2a387e612bf5d1cda767b488e8477d1d442198bff58795ce1f`).
- MySQL TLS CA и hostname verification проходят, grants ограничены пятью таблицами.
- `/ready` отвечает только внутри VPS; публичны только разрешённые Nginx routes.
- Вызов сайта проходит по HTTPS через действующий hostname и certificate verification; отдельный API hostname/DNS/TLS требуется только если существующий virtual host использовать нельзя. Firewall и MySQL allowlist ограничены.
- `/data` persistent, права владельца `10001:10001`, backup зашифрован вне VPS, restore drill записан.
- Backend сайта хранит Product QA bearer key server-side и вызывает только `/api/v1/ask`; если он передаёт `history`, то только в той же product page session.
- Retention, timeout/SLO, rate-limit expectation и key rotation задокументированы владельцем/оператором до рабочего трафика.

Этот runbook готовит разработчика к установке на выбранном VPS. Команды здесь не выполнялись на production host; storefront, DNS, staging и deploy не менялись.
