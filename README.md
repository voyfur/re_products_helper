# Race Expert AI — ШІ-Консультант у картці товару (Product QA Service)

> **Офіційний репозиторій мікросервісу штучного інтелекту для інтернет-магазину Race Expert ([raceexpert.com.ua](https://raceexpert.com.ua)).**  
> Версія ядра: **v18** (`87b639cc...`) | Спеціалізація: **Спортивна нутриціологія, біг, велоспорт, тренажерний зал** | Модель: **gpt-4o-mini / gpt-4o** (з підтримкою OpenAI Prompt Caching).

---

## ⚡ Швидкий старт для розробника

1. **Готова демо-сторінка для браузера:**  
   Відкрийте подвійним кліком файл [`docs/api/test-widget-demo.html`](docs/api/test-widget-demo.html) у будь-якому браузері (Safari, Chrome, Firefox). Він містить автономний інтерактивний стенд із повною версткою картки товару, виїзною шторкою (Rozetka AI style), живим typing-індикатором, чіпами швидких запитань та ефектом друку відповідей.

2. **Офіційна повна специфікація інтеграції:**  
   Повний технічний документ також дублюється у файлі [`docs/api/product-qa-integration.md`](docs/api/product-qa-integration.md).

3. **Запуск локальних тестів:**
   ```bash
   # Активація віртуального оточення
   source .venv/bin/activate

   # Запуск 178 unit-тестів
   pytest tests/

   # Перевірка контракту ендпоінтів згідно з документацією (12 сценаріїв)
   python scripts/verify_endpoints_contract.py
   ```

---

# Race Expert Product QA API: Повна інструкція з інтеграції для розробника

Цей документ є офіційним, вичерпним технічним посібником для backend- та frontend-розробників інтернет-магазину **Race Expert** ([raceexpert.com.ua](https://raceexpert.com.ua)) щодо підключення мікросервісу штучного інтелекту відповідей на питання про товари (**Race Expert Product QA**).

---

## Зміст
1. [Загальна архітектура та принцип Zero-Trust](#1-загальна-архітектура-та-принцип-zero-trust)
2. [Повна специфікація HTTP Ендпоінтів](#2-повна-специфікація-http-ендпоінтів)
   - [2.1. Streaming ендпоінт: POST /api/v1/ask/stream (SSE)](#21-streaming-ендпоінт-post-apiv1askstream-sse)
   - [2.2. Синхронний ендпоінт: POST /api/v1/ask (JSON)](#22-синхронний-ендпоінт-post-apiv1ask-json)
   - [2.3. Предготові запитання: GET /api/v1/products/{article}/suggested-questions](#23-предготові-запитання-get-apiv1productsarticlesuggested-questions)
   - [2.4. Системний Liveness: GET /health](#24-системний-liveness-get-health)
   - [2.5. Системний Readiness: GET /ready](#25-системний-readiness-get-ready)
3. [Typing-індикатор: механіка та візуальні стани](#3-typing-індикатор-механіка-та-візуальні-стани)
4. [Предготові швидкі запитання (Suggested Chips Matrix)](#4-предготові-швидкі-запитання-suggested-chips-matrix)
5. [Налаштування сервера, оточення та Nginx (Configuration)](#5-налаштування-сервера-оточення-та-nginx-configuration)
6. [Рекомендації по кнопці та модальній шторці (Drawer UI/UX)](#6-рекомендації-по-кнопці-та-модальній-шторці-drawer-uiux)
7. [Повний приклад реалізації на OpenCart (PHP Backend + JS Frontend + CSS)](#7-повний-приклад-реалізації-на-opencart-php-backend--js-frontend--css)
8. [Тестова автономна HTML-сторінка для тестування](#8-тестова-автономна-html-сторінка-для-тестування)

---

## 1. Загальна архітектура та принцип Zero-Trust

Сервіс **Race Expert Product QA** надає покупцям точні, безпечні та підтверджені консультації зі спортивного харчування та екіпірування безпосередньо в картці товару.

### Фундаментальні правила безпеки:
1. **Server-to-Server (Zero-Trust):** Браузер покупця **ніколи** не контактує з мікросервісом QA напряму. Усі запити проходять через контролер OpenCart магазину.
2. **Ізоляція секретів:** Ключі `OPENAI_API_KEY`, `TAVILY_API_KEY`, реквізити MySQL та `PRODUCT_QA_API_KEY` зберігаються виключно у захищеному середовищі сервера і не транслюються клієнту.
3. **Серверна верифікація:** Браузер передає лише артикул (`article`) та запитання (`question`). Сервіс самостійно знаходить товар у базі даних каталогу OpenCart, верифікує українську картку і генерує відповідь виключно за фактами.
4. **Мова виводу:** Усі відповіді формуються **виключно українською мовою**, незалежно від мови, якою покупець написав запитання.
5. **Prompt Caching:** Сервіс використовує оптимізацію OpenAI Prompt Caching. Передача історії діалогу (`history`) зберігає контекст розмови і знижує вартість запитів на 50%.

```
┌────────────────────────────────────────────────────────┐
│                   Браузер покупця                      │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS (AJAX / Fetch / SSE)
                            ▼
┌────────────────────────────────────────────────────────┐
│               Backend сайту Race Expert                │
│             (OpenCart / PHP Controller)                │
└───────────────────────────┬────────────────────────────┘
                            │ Внутрішній HTTP/HTTPS Loopback
                            │ Authorization: Bearer <PRODUCT_QA_API_KEY>
                            ▼
┌────────────────────────────────────────────────────────┐
│            Product QA Microservice (FastAPI)           │
│                                                        │
│  1. Перевірка Bearer токена та Rate-limit (60/хв)     │
│  2. Пошук товару в MySQL OpenCart (5 таблиць SELECT)   │
│  3. Intent Classifier (кардіо/біг, добавки, сила)      │
│  4. Fast-path Security (миттєвий відсів ліків/діагнозів)│
│  5. LLM Completion (gpt-4o-mini / gpt-4o + SSE)        │
│  6. Запис аудиту спроби в SQLite-журнал                │
└────────────────────────────────────────────────────────┘
```

---

## 2. Повна специфікація HTTP Ендпоінтів

| Метод | Шлях (URI) | Авторизація | Формат відповіді | Призначення |
|---|---|:---:|---|---|
| **POST** | `/api/v1/ask/stream` | `Bearer` | `text/event-stream` (SSE) | **Рекомендований:** потокова видача слів у реальному часі |
| **POST** | `/api/v1/ask` | `Bearer` | `application/json` | Класичний REST запит із повною відповіддю |
| **GET** | `/api/v1/products/{article}/suggested-questions` | `Bearer` | `application/json` | Отримання 6 релевантних швидких запитань для картки товару |
| **GET** | `/health` | Немає | `application/json` | Перевірка працездатності контейнера (Liveness probe) |
| **GET** | `/ready` | Немає (локально) | `application/json` | Перевірка з'єднання з базою OpenCart (Readiness probe) |

---

### 2.1. Streaming ендпоінт: `POST /api/v1/ask/stream` (SSE)

Головний ендпоінт для швидкого відгуку (Time-To-First-Token ~0.5–0.8 с). Відповідь передається через протокол **Server-Sent Events (SSE)**.

#### Заголовки запиту:
```http
POST /api/v1/ask/stream HTTP/1.1
Host: 127.0.0.1:8787
Authorization: Bearer YOUR_SECRET_PRODUCT_QA_API_KEY
Content-Type: application/json
Accept: text/event-stream
```

#### Тіло запиту (Request Body JSON):
```json
{
  "article": "RE0126",
  "question": "Чи можна пити цей напій на фініші після 60 хвилин бігу?",
  "history": [
    {
      "question": "Скільки калорій в одній порції?",
      "answer": "В одній порції (50 г) міститься 189 ккал і 47 г вуглеводів."
    }
  ]
}
```

* `article` *(string, обов'язкове)*: Артикул товару (відповідає `model` або `sku` в OpenCart, 1–128 символів).
* `question` *(string, обов'язкове)*: Запитання покупця (1–2000 символів).
* `history` *(array, опціональне)*: Масив попередніх реплік діалогу (до 9 реплік). Дозволяє вести природний діалог з пам'яттю контексту.

#### Потік подій SSE (Response Events):

1. **`event: start`** — початок генерації:
   ```text
   event: start
   data: {"status":"started"}
   ```

2. **`event: delta`** — шматочок згенерованого тексту (повторюється багато разів у процесі генерації):
   ```text
   event: delta
   data: {"text":"Так, "}

   event: delta
   data: {"text":"якщо 60-хвилинний біг "}

   event: delta
   data: {"text":"завершився, "}
   ```

3. **`event: replace`** *(опціонально)* — повна заміна тексту відповіді (надсилається лише якщо спрацював постпроцесинг безпеки або фільтр застережень):
   ```text
   event: replace
   data: {"answer":"Так, якщо 60-хвилинний біг завершився, можна випити напій на фініші..."}
   ```

4. **`event: done`** — успішне завершення генерації:
   ```text
   event: done
   data: {"status":"succeeded"}
   ```

5. **`event: error`** — помилка генерації відповіді:
   ```text
   event: error
   data: {"error":"answer_unavailable"}
   ```

---

### 2.2. Синхронний ендпоінт: `POST /api/v1/ask` (JSON)

Класичний REST ендпоінт, що очікує повної генерації відповіді та повертає єдиний JSON.

#### Тіло запиту:
Ідентичне до потокового ендпоінту (`article`, `question`, опціонально `history`).

#### Успішна відповідь (HTTP 200 OK):
```json
{
  "status": "succeeded",
  "answer": "Так, якщо 60-хвилинний біг завершився, можна випити напій на фініші. Інструкція радить пити 500 мл кожні 45–60 хвилин тренування або за потребою.

Це відповідь штучного інтелекту; інформацію щодо здоров’я потрібно перевірити з фахівцем."
}
```

#### Коди помилок (Error Codes):
* `401 Unauthorized`: відсутній або невірний Bearer токен (`{"error": "unauthorized"}`).
* `404 Not Found`: товар з таким артикулом відсутній у базі (`{"error": "product_not_found"}`).
* `409 Conflict`: знайдено кілька товарів з однаковим артикулом (`{"error": "product_selection_required"}`).
* `413 Payload Too Large`: тіло запиту більше 16 KiB (`{"error": "request_too_large"}`).
* `422 Unprocessable Entity`: порожнє питання чи артикул (`{"error": "invalid_request"}`).
* `429 Too Many Requests`: перевищено ліміт 60 запитів на хвилину (`{"error": "rate_limited"}`).
* `502 Bad Gateway`: помилка генерації відповіді (`{"error": "answer_unavailable"}`).
* `503 Service Unavailable`: база OpenCart недоступна (`{"error": "catalog_unavailable"}`).

---

### 2.3. Предготові запитання: `GET /api/v1/products/{article}/suggested-questions`

Повертає рівно 6 персоналізованих запитань, сформованих для конкретної категорії вибраного товару (наприклад, для енергетичних гелів із кофеїном питання стосуються дозування кофеїну та дистанції, для електролітів — судом та розведення водою).

#### Запит:
```http
GET /api/v1/products/RE0126/suggested-questions HTTP/1.1
Host: 127.0.0.1:8787
Authorization: Bearer YOUR_SECRET_PRODUCT_QA_API_KEY
```

#### Відповідь (HTTP 200 OK):
```json
{
  "status": "succeeded",
  "article": "RE0126",
  "product_name": "Напій енергетичний SiS Go Energy (чорна смородина) 1,6 кг",
  "suggested_questions": [
    "Як правильно приймати за інструкцією?",
    "Скільки калорій і вуглеводів у порції?",
    "Чи підходить для бігу та велоспорту?",
    "Чи можна вживати з кавою?",
    "Чи є протипоказання або алергени?",
    "Який смак і розчинність у воді?"
  ]
}
```

---

### 2.4. Системний Liveness: `GET /health`
* **Призначення:** Миттєва перевірка доступності веб-процесу (для Docker / Kubernetes / Nginx).
* **Відповідь:** `{"status": "ok"}` (HTTP 200). Не навантажує базу даних і не викликає зовнішні API.

### 2.5. Системний Readiness: `GET /ready`
* **Призначення:** Внутрішня перевірка підключення до бази даних MySQL (`SELECT 1`).
* **Відповідь:** `{"status": "ready"}` (HTTP 200) або `{"status": "unavailable"}` (HTTP 503).
* *Доступ до цього ендпоінту має бути закритий для зовнішніх користувачів у конфігурації Nginx.*

---

## 3. Typing-індикатор: механіка та візуальні стани

Typing-індикатор (анімація з трьома пульсуючими крапками) є обов'язковим елементом гарного UX. Він показує покупцеві, що система обробляє його запит і формує кваліфіковану відповідь.

### Життєвий цикл (Lifecycle) на стороні клієнта:
1. **Користувач надіслав запитання (клік по кнопці або Enter):**
   - Блокується інпут введення та кнопка відправки (щоб уникнути спаму).
   - Повідомлення користувача додається до вікна діалогу з вирівнюванням праворуч.
   - **МИТТЄВО вмикається typing-індикатор:** створюється або відображається плашка асистента з трьома анімованими крапками.
   - Вікно чату автоматично скролиться до низу (`scrollTop = scrollHeight`).
2. **Отримання першого шматочка відповіді (`event: delta` або прийом тіла JSON):**
   - **Typing-індикатор приховується (`display: none`).**
   - Створюється бульбашка відповіді асистента, куди починають потоково додаватися літери/слова.
3. **Завершення генерації або помилка:**
   - Інпут розблоковується, повертається фокус у поле вводу.
   - Typing-індикатор гарантовано вимкнено (у блоці `finally`).

### Приклад CSS анімації трьох крапок:
```css
/* Typing Indicator Container */
.typing-bubble {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f1f5f9;
  border-radius: 14px 14px 14px 2px;
  width: fit-content;
  margin-bottom: 12px;
}

/* Dots Animation */
.typing-dots {
  display: flex;
  align-items: center;
  gap: 4px;
}
.typing-dots span {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out both;
}
.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; background: #3960FF; }
}
```

---

## 4. Предготові швидкі запитання (Suggested Chips Matrix)

Для підвищення конверсії в консультацію та зручності на смартфонах у блоці діалогу відображається горизонтальний скрол або сітка швидких питань (чіпів).

### Логіка роботи:
1. При відкритті картки товару або завантаженні артикула фронтенд викликає:
   `GET /api/v1/products/{article}/suggested-questions`.
2. Сервер автоматично визначає категорію товару за внутрішнім класифікатором серед **24 груп** (енергетичні гелі, гелі з кофеїном, порошкові ізотоніки, електроліти в шипучих таблетках, сольові капсули, протеїни, креатин, батончики тощо).
3. Якщо категорія товару специфічна — повертаються 6 запитань саме для неї.
4. Якщо товар новий або нестандартний — спрацьовує `GENERAL_FALLBACK` (загальні перевірені питання про склад, застосування та сумісність).
5. **Поведінка при кліку:** Користувач клікає на чіп `button.prompt-chip` -> текст чіпа автоматично відправляється в чат так, ніби покупець сам його надрукував.

---

## 5. Налаштування сервера, оточення та Nginx (Configuration)

### 5.1. Змінні середовища (`.env` або Docker runtime.env)
```dotenv
# API Ключ для зв'язку між OpenCart та мікросервісом QA
PRODUCT_QA_API_KEY=re_sec_live_9f83b271d4a046c8e31298457

# Доступ до MySQL OpenCart (Read-Only)
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=raceexpertcomua
MYSQL_USER=qa_readonly
MYSQL_PASSWORD=STRONG_READONLY_PASSWORD
MYSQL_SSL_CA=/run/secrets/mysql_ca.pem

# Ключі моделей штучного інтелекту та пошуку
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx

# Локальний журнал спроб
JOURNAL_PATH=/var/lib/race-expert-qa/qa-journal.sqlite3
```

### 5.2. Налаштування Nginx (Критично для SSE Streaming)
При роботі через Server-Sent Events (SSE) вкрай важливо **вимкнути буферизацію Nginx**, інакше Nginx збиратиме всі байти в пам'ять і видасть їх користувачеві лише після повного завершення генерації.

Додайте в блок вашого сайту `server { ... }`:

```nginx
# Внутрішній проксі для зв'язку з мікросервісом
location /_internal/product-qa/ {
    # Дозволено тільки локальному серверу або через внутрішній роутинг
    proxy_pass http://127.0.0.1:8787/;
    proxy_http_version 1.1;

    # ОБОВ'ЯЗКОВО для роботи Streaming / SSE:
    proxy_set_header Connection '';
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header X-Accel-Buffering no;
    chunked_transfer_encoding on;

    # Заголовки авторизації та таймаути
    proxy_set_header Host $host;
    proxy_set_header Authorization $http_authorization;
    proxy_read_timeout 150s;
    proxy_connect_timeout 5s;
    
    # Вимкнення логування конфіденційних запитів покупців
    access_log off;
}

# Заборона прямого доступу ззовні до службових ендпоінтів
location ~ ^/(_internal/product-qa/)?(ready|api/search|api/ask)$ {
    return 404;
}
```

---

## 6. Рекомендації по кнопці та модальній шторці (Drawer UI/UX)

Для максимальної конверсії рекомендується реалізувати інтерфейс за паттерном **Rozetka AI / Apple-style Sliding Drawer** (бічна виїзна шторка).

### 6.1. Де розмістити кнопку відкриття:
1. **Основна CTA-кнопка під кнопкою «Купити»:**
   * Розміщується безпосередньо в картці товару праворуч біля ціни та кнопки замовлення.
   * Текст кнопки: `🤖 Запитати Race Expert AI про цей товар` або `Поставити питання штучному інтелекту`.
   * Стиль: нейтральний світлий або акцентний синій контур (`border: 1.5px solid #3960FF; color: #3960FF; background: #f0f4ff; border-radius: 10px; font-weight: 600;`).
2. **Плаваюча кругла кнопка (Floating Action Button - FAB):**
   * Фіксується в нижньому правому кутку екрану (`position: fixed; bottom: 24px; right: 24px; z-index: 999;`).
   * Має круглу форму (56x56 px), фірмовий синій градієнт, іконку іскорок/бота та маленький бейдж «AI».
   * При першому візиті картки може показати спливаючу підказку (bubble): *"Підказати, як правильно приймати цей товар?"*.
3. **Вкладка у блоці характеристик:**
   * Додатковий таб «Консультація AI» поряд із табами «Опис товару», «Склад та характеристики», «Відгуки».

### 6.2. Як шторка повинна виїжджати (Drawer Behavior):
* **Анімація виїзду:** Шторка розташована біля правого краю (`right: 0`) і спочатку прихована за межами екрану через `transform: translateX(100%)`.
* **Плавний вхід:** При натисканні на кнопку додається клас `.is-open`, що встановлює `transform: translateX(0)`. Для анімації використовується плавна крива `transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1)`.
* **Затемнення фону (Backdrop):** З'являється напівпрозорий шар з ефектом блюру (`backdrop-filter: blur(4px); background: rgba(15, 23, 42, 0.45); opacity: 1; transition: opacity 0.25s ease;`).
* **Блокування прокрутки:** При відкритій шторці для тега `<body>` задається `overflow: hidden;`, щоб прокрутка сторінки магазину не конфліктувала зі скролом діалогу.
* **Закриття шторки:** Закривається при натисканні на хрестик `X`, при кліку на затемнену область бекдропу або при натисканні клавіші `Escape`.
* **Мобільна адаптивність:** На екранах шириною менше 768px шторка повинна займати **100% ширини екрану** або виїжджати знизу (Bottom Sheet).

---

## 7. Повний приклад реалізації на OpenCart (PHP Backend + JS Frontend + CSS)

### 7.1. PHP-контролер OpenCart (`catalog/controller/extension/module/race_expert_ai.php`)

```php
<?php
declare(strict_types=1);

class ControllerExtensionModuleRaceExpertAi extends Controller
{
    private const QA_INTERNAL_URL = 'http://127.0.0.1:8787/api/v1';

    /**
     * Отримання 6 швидких запитань про товар
     */
    public function getQuestions(): void
    {
        $this->response->addHeader('Content-Type: application/json; charset=utf-8');
        $article = trim((string)($this->request->get['article'] ?? ''));

        if ($article === '') {
            $this->response->setOutput(json_encode(['error' => 'article_required'], JSON_UNESCAPED_UNICODE));
            return;
        }

        $apiKey = $this->getApiKey();
        $ch = curl_init(self::QA_INTERNAL_URL . '/products/' . rawurlencode($article) . '/suggested-questions');
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $apiKey,
                'Accept: application/json'
            ],
            CURLOPT_TIMEOUT => 5
        ]);

        $body = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($code === 200 && $body) {
            $this->response->setOutput($body);
        } else {
            $this->response->setOutput(json_encode([
                'status' => 'fallback',
                'suggested_questions' => [
                    'Як правильно приймати за інструкцією?',
                    'Скільки калорій і вуглеводів у порції?',
                    'Чи підходить для бігу та велоспорту?',
                    'Чи можна вживати з кавою?',
                    'Чи є протипоказання або алергени?',
                    'Який смак і розчинність у воді?'
                ]
            ], JSON_UNESCAPED_UNICODE));
        }
    }

    /**
     * Відправка запитання (Проксі-метод до потокового або синхронного QA API)
     */
    public function ask(): void
    {
        $this->response->addHeader('Content-Type: application/json; charset=utf-8');

        $input = json_decode(file_get_contents('php://input'), true);
        $article = trim((string)($input['article'] ?? ''));
        $question = trim((string)($input['question'] ?? ''));
        $history = (array)($input['history'] ?? []);

        if ($article === '' || $question === '') {
            $this->response->setOutput(json_encode(['error' => 'invalid_input'], JSON_UNESCAPED_UNICODE));
            return;
        }

        $apiKey = $this->getApiKey();
        $payload = json_encode([
            'article' => $article,
            'question' => $question,
            'history' => $history
        ], JSON_UNESCAPED_UNICODE);

        $ch = curl_init(self::QA_INTERNAL_URL . '/ask');
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $payload,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'Authorization: Bearer ' . $apiKey,
                'Content-Type: application/json',
                'Accept: application/json'
            ],
            CURLOPT_TIMEOUT => 140
        ]);

        $body = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($code === 200 && $body) {
            $this->response->setOutput($body);
        } else {
            $this->response->setOutput(json_encode([
                'status' => 'error',
                'answer' => 'Вибачте, наразі не вдалося сформувати відповідь. Будь ласка, спробуйте ще раз або зверніться до менеджера Race Expert.'
            ], JSON_UNESCAPED_UNICODE));
        }
    }

    private function getApiKey(): string
    {
        // Ключ береться з конфігурації сервера або секретів
        return getenv('PRODUCT_QA_API_KEY') ?: 're_sec_live_9f83b271d4a046c8e31298457';
    }
}
```

---

### 7.2. Frontend JavaScript скрипт віджета (`catalog/view/javascript/race_expert_ai.js`)

```javascript
/**
 * Race Expert AI Storefront Widget
 * Стиль Rozetka AI / Бічна шторка для картки товару OpenCart
 */
(function() {
  const state = {
    article: null,
    isOpen: false,
    isLoading: false,
    history: []
  };

  // DOM вузли
  let drawer, backdrop, messagesList, typingIndicator, chipsFlow, inputField, sendBtn;

  function initWidget(productArticle) {
    state.article = productArticle;
    createWidgetDOM();
    bindEvents();
    loadSuggestedQuestions(productArticle);
  }

  function createWidgetDOM() {
    // 1. Плаваюча кнопка FAB
    const fab = document.createElement('button');
    fab.className = 're-ai-fab-btn';
    fab.setAttribute('aria-label', 'Консультація Race Expert AI');
    fab.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" fill="#FFFFFF"/>
      </svg>
      <span class="re-fab-badge">AI</span>
    `;
    document.body.appendChild(fab);

    // 2. Затемнення (Backdrop)
    backdrop = document.createElement('div');
    backdrop.className = 're-ai-backdrop';
    document.body.appendChild(backdrop);

    // 3. Виїзна шторка (Drawer)
    drawer = document.createElement('div');
    drawer.className = 're-ai-drawer';
    drawer.innerHTML = `
      <div class="re-drawer-header">
        <div class="re-header-title">
          <div class="re-ai-avatar">⚡</div>
          <div>
            <h3>Race Expert AI</h3>
            <p>Спортивний консультант • Товар: <strong>${state.article}</strong></p>
          </div>
        </div>
        <button class="re-close-btn" aria-label="Закрити">&times;</button>
      </div>

      <div class="re-drawer-body">
        <div class="re-chips-section">
          <p class="re-chips-title">Швидкі запитання про цей товар:</p>
          <div class="re-chips-flow" id="re-chips-container">
            <!-- Підтягуються динамічно -->
          </div>
        </div>

        <div class="re-chat-messages" id="re-chat-container">
          <div class="re-msg-bubble re-assistant">
            <div class="re-avatar">🤖</div>
            <div class="re-text">Вітаю! Я можу відповісти на будь-які запитання щодо складу, дозування, правил прийому та сумісності цього продукту. Оберіть запитання вище або напишіть власне!</div>
          </div>
          <div class="re-typing-bubble" id="re-typing-ind" style="display: none;">
            <div class="re-avatar">🤖</div>
            <div class="re-typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="re-drawer-footer">
        <form id="re-chat-form">
          <input type="text" id="re-user-input" placeholder="Запитайте про склад, прийом чи біг..." autocomplete="off">
          <button type="submit" id="re-send-btn">Надіслати</button>
        </form>
      </div>
    `;
    document.body.appendChild(drawer);

    messagesList = drawer.querySelector('#re-chat-container');
    typingIndicator = drawer.querySelector('#re-typing-ind');
    chipsFlow = drawer.querySelector('#re-chips-container');
    inputField = drawer.querySelector('#re-user-input');
    sendBtn = drawer.querySelector('#re-send-btn');
  }

  function bindEvents() {
    // Відкриття по кліку на FAB
    document.querySelector('.re-ai-fab-btn').addEventListener('click', openDrawer);

    // Відкриття по кнопці в картці товару (якщо вона є в шаблоні)
    const pageTrigger = document.querySelector('.btn-ask-race-ai');
    if (pageTrigger) {
      pageTrigger.addEventListener('click', (e) => {
        e.preventDefault();
        openDrawer();
      });
    }

    // Закриття
    drawer.querySelector('.re-close-btn').addEventListener('click', closeDrawer);
    backdrop.addEventListener('click', closeDrawer);
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && state.isOpen) closeDrawer();
    });

    // Відправка повідомлення
    drawer.querySelector('#re-chat-form').addEventListener('submit', (e) => {
      e.preventDefault();
      const text = inputField.value.trim();
      if (text) sendQuestion(text);
    });
  }

  function openDrawer() {
    state.isOpen = true;
    drawer.classList.add('is-open');
    backdrop.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    setTimeout(() => inputField.focus(), 250);
  }

  function closeDrawer() {
    state.isOpen = false;
    drawer.classList.remove('is-open');
    backdrop.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  async function loadSuggestedQuestions(article) {
    try {
      const res = await fetch(`index.php?route=extension/module/race_expert_ai/getQuestions&article=${encodeURIComponent(article)}`);
      const data = await res.json();
      const list = data.suggested_questions || [];

      chipsFlow.innerHTML = '';
      list.forEach(q => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 're-chip-btn';
        btn.textContent = q;
        btn.addEventListener('click', () => sendQuestion(q));
        chipsFlow.appendChild(btn);
      });
    } catch (e) {
      console.warn('Не вдалося завантажити чіпи:', e);
    }
  }

  async function sendQuestion(text) {
    if (state.isLoading || !text) return;

    state.isLoading = true;
    inputField.value = '';
    inputField.disabled = true;
    sendBtn.disabled = true;

    // 1. Додаємо повідомлення юзера
    appendMessage('user', text);

    // 2. Вмикаємо typing індикатор
    showTyping();

    try {
      const response = await fetch('index.php?route=extension/module/race_expert_ai/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          article: state.article,
          question: text,
          history: state.history.slice(-3)
        })
      });

      const data = await response.json();
      hideTyping();

      if (data && data.answer) {
        state.history.push({ question: text, answer: data.answer });
        await appendMessageWithTypewriter('assistant', data.answer);
      } else {
        appendMessage('assistant', 'Вибачте, виникла помилка зв'язку. Спробуйте ще раз.');
      }
    } catch (err) {
      hideTyping();
      appendMessage('assistant', 'Сталася тимчасова помилка. Перевірте з'єднання з інтернетом.');
    } finally {
      hideTyping();
      state.isLoading = false;
      inputField.disabled = false;
      sendBtn.disabled = false;
      inputField.focus();
    }
  }

  function showTyping() {
    typingIndicator.style.display = 'flex';
    messagesList.appendChild(typingIndicator);
    messagesList.scrollTop = messagesList.scrollHeight;
  }

  function hideTyping() {
    typingIndicator.style.display = 'none';
  }

  function appendMessage(role, text) {
    const row = document.createElement('div');
    row.className = `re-msg-bubble re-${role}`;
    row.innerHTML = `
      <div class="re-avatar">${role === 'user' ? '👤' : '🤖'}</div>
      <div class="re-text">${escapeHtml(text)}</div>
    `;
    messagesList.insertBefore(row, typingIndicator);
    messagesList.scrollTop = messagesList.scrollHeight;
    return row;
  }

  async function appendMessageWithTypewriter(role, fullText) {
    const row = appendMessage(role, '');
    const textNode = row.querySelector('.re-text');
    const words = fullText.split(' ');
    let current = '';

    for (let i = 0; i < words.length; i++) {
      current += (i > 0 ? ' ' : '') + words[i];
      textNode.textContent = current;
      messagesList.scrollTop = messagesList.scrollHeight;
      await new Promise(r => setTimeout(r, 20));
    }
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // Експорт у глобальну область
  window.RaceExpertAI = { init: initWidget, open: openDrawer, close: closeDrawer };
})();
```

---

### 7.3. Стилі CSS (`catalog/view/theme/default/stylesheet/race_expert_ai.css`)

```css
/* Бренд-палітра: Race Expert Slate #253237 та Accent Blue #3960FF */

/* 1. Кнопка у картці товару */
.btn-ask-race-ai {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 10px;
  padding: 12px 18px;
  background: #f0f4ff;
  border: 1.5px solid #3960FF;
  border-radius: 10px;
  color: #3960FF;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-ask-race-ai:hover {
  background: #3960FF;
  color: #ffffff;
}

/* 2. Плаваючий FAB */
.re-ai-fab-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3960FF 0%, #1e40af 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(57, 96, 255, 0.35);
  cursor: pointer;
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.re-ai-fab-btn:hover {
  transform: translateY(-2px) scale(1.04);
  box-shadow: 0 12px 28px rgba(57, 96, 255, 0.45);
}
.re-fab-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #ef4444;
  color: #ffffff;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 10px;
  border: 2px solid #ffffff;
}

/* 3. Затемнення бекдропу */
.re-ai-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  z-index: 9999;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.28s ease, visibility 0.28s;
}
.re-ai-backdrop.is-open {
  opacity: 1;
  visibility: visible;
}

/* 4. Бічна шторка (Drawer) */
.re-ai-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 440px;
  max-width: 100%;
  height: 100%;
  background: #ffffff;
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
}
.re-ai-drawer.is-open {
  transform: translateX(0);
}

/* Шапка шторки */
.re-drawer-header {
  padding: 18px 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
}
.re-header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}
.re-ai-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #3960FF;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.re-header-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #253237;
}
.re-header-title p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #64748b;
}
.re-close-btn {
  background: transparent;
  border: none;
  font-size: 24px;
  line-height: 1;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
}
.re-close-btn:hover { color: #253237; }

/* Тіло шторки */
.re-drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Секція чіпів */
.re-chips-section {
  background: #f8fafc;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.re-chips-title {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  margin: 0 0 8px;
}
.re-chips-flow {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.re-chip-btn {
  text-align: left;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  line-height: 1.35;
  color: #1e293b;
  cursor: pointer;
  transition: all 0.15s ease;
}
.re-chip-btn:hover {
  border-color: #3960FF;
  color: #3960FF;
  background: #f0f4ff;
}

/* Повідомлення чату */
.re-chat-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.re-msg-bubble {
  display: flex;
  gap: 10px;
  max-width: 90%;
}
.re-msg-bubble.re-user {
  align-self: flex-end;
  flex-direction: row-reverse;
}
.re-avatar {
  font-size: 14px;
  line-height: 1;
}
.re-msg-bubble .re-text {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 13.5px;
  line-height: 1.45;
}
.re-msg-bubble.re-assistant .re-text {
  background: #f1f5f9;
  color: #1e293b;
  border-radius: 14px 14px 14px 2px;
}
.re-msg-bubble.re-user .re-text {
  background: #3960FF;
  color: #ffffff;
  border-radius: 14px 14px 2px 14px;
}

/* Typing індикатор */
.re-typing-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f1f5f9;
  border-radius: 12px 12px 12px 2px;
  width: fit-content;
}
.re-typing-dots {
  display: flex;
  gap: 4px;
}
.re-typing-dots span {
  width: 6px;
  height: 6px;
  background: #94a3b8;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out both;
}
.re-typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.re-typing-dots span:nth-child(2) { animation-delay: -0.16s; }

/* Футер з формою */
.re-drawer-footer {
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
  background: #ffffff;
}
#re-chat-form {
  display: flex;
  gap: 8px;
}
#re-user-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
}
#re-user-input:focus {
  border-color: #3960FF;
}
#re-send-btn {
  padding: 10px 18px;
  background: #3960FF;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}
#re-send-btn:hover { background: #2546d0; }
#re-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Мобільні пристрої */
@media (max-width: 640px) {
  .re-ai-drawer { width: 100%; }
}
```

---

## 8. Тестова автономна HTML-сторінка для тестування

Для тестувальників та фронтенд-розробника створено окремий автономний демонстраційний файл:  
👉 [`docs/api/test-widget-demo.html`](test-widget-demo.html)

Цей файл можна відкрити подвійним кліком у будь-якому браузері без встановлення OpenCart. Він повністю симулює вітрину Race Expert, дозволяє протестувати виїзд бічної шторки, чіпи з 6 запитаннями, typing-індикатор та потоковий друк відповідей.


---

## 9. Локальний запуск сервісу та тестування

### 9.1. Системні вимоги:
* Python 3.12+
* Встановлені залежності з `requirements.txt`
* Налаштований SSH-доступ до сервера бази даних або локальна копія MySQL

### 9.2. Встановлення залежностей:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 9.3. Запуск локальної сесії через тунель:
Для підключення до тестової або бойової бази OpenCart у режимі читання використовуйте захищений запускач:
```bash
python scripts/run_local_session.py --env-file .env
```
Запускач автоматично:
* Перевірить SSH host key у системному `known_hosts`.
* Відкриє тимчасовий захищений тунель до MySQL через VPS-61125.
* Запустить веб-сервер FastAPI на `http://127.0.0.1:8787` з підтримкою SSE Streaming та гарячим перезавантаженням.

### 9.4. Тестування працездатності:
```bash
# 1. Швидка перевірка стану сервісу (Liveness)
curl -i http://127.0.0.1:8787/health

# 2. Перевірка підключення до бази OpenCart (Readiness)
curl -i http://127.0.0.1:8787/ready

# 3. Отримання 6 категорійних запитань для товару
curl -i -H "Authorization: Bearer re_sec_live_9f83b271d4a046c8e31298457" \
  http://127.0.0.1:8787/api/v1/products/RE0126/suggested-questions

# 4. Тестовий потоковий запит SSE
curl -N -X POST http://127.0.0.1:8787/api/v1/ask/stream \
  -H "Authorization: Bearer re_sec_live_9f83b271d4a046c8e31298457" \
  -H "Content-Type: application/json" \
  -d '{"article": "RE0126", "question": "Як розводити водою?"}'
```
