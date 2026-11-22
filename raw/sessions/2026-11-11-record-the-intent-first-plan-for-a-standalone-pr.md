---
id: "session-2026-11-11T17-42-07plus-02-00-record-the-intent-first-plan-for-a-standalone-pr"
started_at: "2026-11-11T17:37:00+02:00"
ended_at: "2026-11-11T17:42:07+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Record the intent-first plan for a standalone product-assistant test harness"
status: "partial"
transcript_source: "conversation-2026-11-11"
summary: "Зафиксировано предложение сначала собрать отдельный HTML-тестовый стенд без интеграции в сайт: ввод артикула, загрузка и удобное отображение данных товара, вопросы GPT-6 Luna с prompt v11 и сохранение всех пользовательских вопросов в истории. В следующем чате сначала сформулировать intent, затем на его основе подготовить спецификацию потока; сейчас реализацию не начинать."
files_changed: [{"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "modified"}, {"path": "wiki/index.md", "action": "modified"}, {"path": "wiki/session-handoff.md", "action": "modified"}, {"path": "wiki/log.md", "action": "modified"}, {"path": "wiki/session-index.jsonl", "action": "modified"}, {"path": "wiki/content-index.jsonl", "action": "modified"}]
tags: ["activity:planning", "project:race-expert", "task:test-harness-intent", "topic:prompt-testing", "file:wiki/syntheses/race-expert-product-qa-evaluation.md"]
decisions: ["До интеграции виджета с сайтом нужен самостоятельный тестовый стенд с HTML-интерфейсом.", "Пользователь вводит артикул и подтверждает поиск; стенд показывает данные найденного товара в удобной карточке.", "Вопросы задаются GPT-6 Luna с текущим системным prompt v11.", "Все вопросы пользователя сохраняются в истории; сохранять ли дополнительно ответы, время и другие поля — уточнить в intent/spec.", "OpenAI API key должен использоваться на серверной стороне и не попадать в HTML/JavaScript браузера.", "Следующий чат начинается с формулировки intent; по утверждённому intent создаётся спецификация пользовательского потока; до этого не реализовывать."]
open_tasks: ["В следующем чате составить и утвердить intent тестового стенда.", "После утверждения intent описать поток: поиск товара по артикулу, карточка данных, чат, сохранение истории, ошибки поиска и детали хранения истории.", "Позже подготовить независимый blind-набор для отдельной проверки prompt.", "Проверить live-интеграцию сайта при появлении backend source/runtime payload."]
blockers: ["Backend source и runtime payload сайта отсутствуют; production-интеграция не проверена.", "Маршрут безопасного доступа тестового сервиса к базе и точный состав показываемого контекста нужно определить в intent/spec."]
next_actions: ["В следующем чате сформулировать intent тестового HTML-стенда, включая обязательную историю всех введённых вопросов.", "На основании согласованного intent подготовить спецификацию потока и только после её утверждения переходить к реализации.", "Предусмотреть серверное использование API key и read-only ограничение для поиска товара."]
relevant_pages: ["wiki/index.md", "wiki/session-handoff.md", "wiki/syntheses/race-expert-product-qa-evaluation.md", "prompts/product-assistant-system-v11.md", "wiki/sources/mysql-readonly-access-and-product-query-guide.md"]
verification: [{"command": "rebuild_content_index.py", "result": "passed: indexed 5 content cards"}, {"command": "lint_content.py", "result": "passed"}, {"command": "review of updated Wiki synthesis and index", "result": "passed: intent-first next-chat plan recorded; implementation not started"}]
---

# Session

## Outcome

Зафиксировано предложение сначала собрать отдельный HTML-тестовый стенд без интеграции в сайт: ввод артикула, загрузка и удобное отображение данных товара, вопросы GPT-6 Luna с prompt v11 и сохранение всех пользовательских вопросов в истории. В следующем чате сначала сформулировать intent, затем на его основе подготовить спецификацию потока; сейчас реализацию не начинать.

## Changed Files

- `wiki/syntheses/race-expert-product-qa-evaluation.md` — modified
- `wiki/index.md` — modified
- `wiki/session-handoff.md` — modified
- `wiki/log.md` — modified
- `wiki/session-index.jsonl` — modified
- `wiki/content-index.jsonl` — modified

## Tags

- `activity:planning`
- `project:race-expert`
- `task:test-harness-intent`
- `topic:prompt-testing`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`

## Verification

- `rebuild_content_index.py` — passed: indexed 5 content cards
- `lint_content.py` — passed
- `review of updated Wiki synthesis and index` — passed: intent-first next-chat plan recorded; implementation not started
