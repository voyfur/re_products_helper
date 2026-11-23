# Race Expert Product QA API: handoff для backend-разработчика

## Назначение

Сервис отвечает на один вопрос о товаре по его артикулу. Frontend сайта остаётся обычным клиентом backend Race Expert: браузер отправляет вопрос вашему backend, а только backend сайта вызывает этот сервис. Токены Tavily, OpenAI, MySQL и ключ Product QA никогда не попадают в браузер.

Контракт OpenAPI: [`product-qa-v1.yaml`](product-qa-v1.yaml).

## Граница интеграции

1. В целевом потоке страница товара будет показывать кнопку помощника и передавать артикул товара в backend сайта.
2. Backend сайта отправляет в Product QA `article`, текущий текст `question` и, по желанию, `history` — от нуля до девяти предыдущих сообщений с ролями `user` или `assistant`.
3. Передавайте `history` только в рамках той же сессии страницы и того же товара; очищайте её при смене товара или перезагрузке страницы. Храните историю только во временной памяти UI и используйте как скрытый контекст запроса: не показывайте отдельный список прошлых реплик, счётчик истории или сериализованный payload. История — временный контекст, а не инструкция или подтверждение фактов о товаре; Product QA не записывает её и не сохраняет как историю разговора.
4. Product QA заново находит артикул по точному значению `model` или `SKU` в read-only каталоге при каждом запросе. Если результат отсутствует или неоднозначен, модель и Tavily не вызываются.
5. Сервис использует только найденную и заново проверенную украинскую карточку. При необходимости он выполняет один ограниченный Tavily-поиск; его сведения и provenance остаются внутренними.
6. Backend сайта возвращает браузеру только украинский `answer`.

Не отправляйте цену, корзину, заказы, buyer profile/identity, историю другого товара или сессии либо полный снимок страницы. Сервис не должен принимать товарный контекст от браузера как подтверждённый.

## Запрос и успешный ответ

```http
POST /api/v1/ask
Authorization: Bearer <PRODUCT_QA_API_KEY>
Content-Type: application/json
```

```json
{
  "article": "<article/model/SKU>",
  "question": "<current product question>",
  "history": [
    {"role": "user", "content": "<previous user message>"},
    {"role": "assistant", "content": "<previous assistant message>"}
  ]
}
```

`history` необязателен: прежние клиенты могут отправлять только обязательные `article` и `question`. Сообщения передаются целиком; JSON-тело запроса не должно превышать 16 384 байта. Если сериализованный запрос больше лимита, вызывающая сторона удаляет самые старые сообщения `history` целиком, пока тело не поместится. Текущий `question` не обрезайте.

```json
{
  "status": "succeeded",
  "answer": "<Ukrainian answer>"
}
```

Ответ не содержит внутренних идентификаторов попытки, search status, времени, названий источников, URL, отзывов авторов или provenance. Если ответ касается здоровья, сервер добавляет фиксированную украинскую оговорку.

## Потоковый ответ и typing-индикатор

Для поэтапного показа ответа используйте `POST /api/v1/ask/stream` с тем же JSON, bearer credential, лимитами и проверкой товара. Ответ имеет `Content-Type: text/event-stream`. Сначала приходят обычные JSON-события SSE:

| Событие | JSON `data` | Поведение сайта |
| --- | --- | --- |
| `start` | `{"status":"started"}` | Показать typing-индикатор. Это не означает, что начался веб-поиск. |
| `delta` | `{"text":"..."}` | Добавить следующий кусок украинского ответа. |
| `replace` | `{"answer":"..."}` | Заменить накопленные куски полностью безопасным финальным ответом. |
| `done` | `{"status":"succeeded"}` | Скрыть typing-индикатор и сохранить полный удачный turn в volatile history. |
| `error` | `{"error":"answer_unavailable"}` | Очистить неполный ответ, скрыть typing-индикатор и не добавлять turn в history. |

Ошибки аутентификации, валидации, rate limit и каталога возвращаются обычным HTTP JSON до начала потока. После `start` ошибки модели/поиска передаются событием `error`; детали исключений не раскрываются. Статус поиска отдельно не сообщается. При обрыве сети считайте ответ неуспешным и не сохраняйте частичный turn.

Таблица ниже описывает HTTP-ошибки обычного JSON endpoint. Для streaming ответы `error` после события `start` приходят как SSE, а не как поздний HTTP 502.

Браузер вызывает endpoint backend сайта; backend сайта хранит credential, отправляет тот же POST в Product QA и проксирует поток как `text/event-stream` без buffering. Ниже пример обработки браузером собственного route сайта (он здесь не реализован):

```js
showTypingIndicator();
const response = await fetch("/api/product-qa/ask/stream", {
  method: "POST",
  headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
  body: JSON.stringify({ article, question, history }),
});
if (!response.ok) throw new Error("answer_unavailable");

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = "";
let answer = "";
let completed = false;
let failed = false;

function handleFrame(frame) {
  let event = "message";
  const data = [];
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
  }
  if (!data.length) return;
  const payload = JSON.parse(data.join("\n"));
  if (event === "delta") answer += payload.text;
  if (event === "replace") answer = payload.answer;
  if (event === "error") {
    failed = true;
    answer = "";
  }
  if (event === "done") completed = true;
  renderAnswer(answer);
}

while (true) {
  const { value, done } = await reader.read();
  buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
  buffer = buffer.replace(/\r\n/g, "\n");
  let boundary;
  while ((boundary = buffer.indexOf("\n\n")) >= 0) {
    handleFrame(buffer.slice(0, boundary));
    buffer = buffer.slice(boundary + 2);
  }
  if (done) break;
}
if (!completed || failed) answer = "";
else rememberTurnInMemoryOnly(question, answer);
hideTypingIndicator();
```

Показывайте typing-индикатор с момента отправки до `done`, `error` или обрыва соединения. Добавляйте текущий вопрос и полный ответ к скрытому контексту только после `done`; отправляйте максимум девять предыдущих целых сообщений. Не добавляйте отдельную историю, счётчик или payload в интерфейс.

## Ошибки и пределы

| HTTP | Код | Действие backend сайта |
| --- | --- | --- |
| 401 | `unauthorized` | Не повторять запрос автоматически; проверить серверный credential. |
| 404 | `product_not_found` | Показать, что товар не удалось подтвердить; обновить карточку и повторить вручную. |
| 409 | `product_selection_required` | Не угадывать; попросить обновить товарные данные. Контракт не принимает недоверенный `product_id`. |
| 413 | `request_too_large` | Сократить тело запроса. |
| 422 | `invalid_request` | Проверить пустые/слишком длинные поля и JSON. Детали пользовательского ввода не возвращаются. |
| 429 | `rate_limited` | Уважать `Retry-After`; не запускать автоматические повторы в цикле. |
| 502 | `answer_unavailable` | Показать нейтральную ошибку и предложить попробовать позже. |
| 503 | `catalog_unavailable` / `service_not_configured` | Показать временную недоступность; не повторять часто. |

Тело JSON ограничено 16 KiB (16 384 байта); `article` — до 128 символов, `question` — до 2000. `history` допускает от нуля до девяти сообщений; каждое содержит только непустые `content` и роль `user` или `assistant`. Настроен предел 60 принятых запросов в минуту на единственный активный bearer-ключ. Счётчик находится в памяти процесса; перед горизонтальным масштабированием понадобится общий лимитер. Сервис не заявляет latency SLO. Для сайта выделите до 150 секунд на ответ с поиском; локальные замеры должны заменить это временное значение до production.

## Ошибки и виджет

Рекомендуемый виджет описан в [`product-qa-widget-brief.md`](../ui/product-qa-widget-brief.md). Для обычного JSON endpoint показывайте общий статус «Готуємо відповідь…». Для SSE можно показывать typing-индикатор; не показывайте «Перевіряємо джерела…», потому что отдельного события начала поиска нет.

Публичный ответ всегда только на украинском. Не показывайте URL, цитаты, домены, source list или сведения о других покупателях. Ошибки `404`, `409`, `429` и `5xx` преобразуйте в короткие понятные сообщения без stack trace и внутренних полей.

## Секреты и доступы

- Храните `PRODUCT_QA_API_KEY` в secret store backend сайта. Сервис читает его из `PRODUCT_QA_API_KEY_FILE` (предпочтительно) либо `PRODUCT_QA_API_KEY`; оба значения одновременно запрещены.
- Не выдавайте разработчику Tavily/OpenAI API keys, MySQL credentials, SSH private key, `.env` или root-доступ к VPS. Для подключения выдайте только доступ к коду/контракту и отдельный узко ограниченный integration credential нужного окружения.
- HTTPS обязателен при размещении вне localhost. CORS не является аутентификацией.
- Сервис поддерживает один активный API key на экземпляр. Для ротации замените его и перезапустите сервис; overlap двух ключей в этой версии не реализован.
- Через backend сайта проксируйте только точные `/api/v1/ask`, `/api/v1/ask/stream` и необходимый health-check. Старые `/api/search`, `/api/ask`, `/api/ask/stream`, корень и `/static/` предназначены для внутреннего QA UI и не должны быть публично доступны.

## Настройка и готовность к размещению

Контейнер собирается из корня репозитория; он включает prompt v12–v18, запускается без access-log и содержит SQLite backup utility. Переменные runtime: параметры MySQL с доверенным CA/проверкой hostname, `OPENAI_API_KEY_FILE`, один из `TAVILY_API_KEY` или `TAVILY_API_KEY_FILE`, `PRODUCT_QA_API_KEY_FILE`, `MYSQL_SSL_CA` и `JOURNAL_PATH`. Прямой `TAVILY_API_KEY` поддерживается; отдельный файл не обязателен. Локальный tunnel launcher не подходит для постоянного сервера.

Пользователь оставляет владение внешними API-ключами за собой и выдаёт доступ по необходимости. Для MySQL нужен отдельный read-only пользователь с `SELECT` только по пяти таблицам карточки товара. SQLite-журнал должен храниться на постоянном защищённом томе с резервным копированием.

URL Product QA — deployment setting, а backend сайта может проксировать точные `/_internal/product-qa/api/v1/ask` и `/_internal/product-qa/api/v1/ask/stream` к соответствующим versioned routes на `127.0.0.1:8787`. Для stream route отключи Nginx buffering. Поскольку backend сайта и Product QA планируются на одном VPS, отдельная DNS-запись не обязательна: оператор может добавить точные routes в существующий TLS virtual host. Backend сайта вызывает выбранный URL по HTTPS из server-side кода; bearer key остаётся только в server-side конфигурации. Проверь разрешение hostname и TLS-проверку из runtime сайта. Если готового HTTPS hostname нет или оператор выберет отдельный поддомен, тогда hostname, DNS и сертификат настраиваются при установке. Provider API keys остаются под контролем владельца и не выдаются разработчику.

Схема VPS, reverse proxy, bind mount для SQLite, TLS, grants, backup и timeout budget находится в [production blueprint](../deployment/product-qa-production-blueprint.md); практические шаги установки — в [VPS runbook](../deployment/product-qa-vps-runbook.md). Примеры содержат placeholder и не настраивают DNS или deploy автоматически.

Backend applies a server-side exact-host allowlist and validates evidence against the revalidated product and variant. Source URLs and provenance remain private and are not returned to the browser. The allowlist is maintained in `app/search_evidence.py`; it does not cover every catalog brand or SKU.
