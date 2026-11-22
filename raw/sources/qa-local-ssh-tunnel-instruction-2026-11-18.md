# Инструкция локального SSH-подключения — зафиксированный источник

Дата фиксации: 2026-11-18.

Эта заметка сохраняет относящуюся к локальному запуску инструкцию из:

- `/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/AGENTS.md`, раздел о локальной работе.
- `/Users/anatoly/.codex/worktrees/raceexpert-test-harness/raceexpert-re-products-helper-source/docs/test-harness/local-session-runbook.md`.

В исходной инструкции локальный стенд подключается к MySQL через временный SSH-туннель с локального компьютера через VPS-61125. Проверка ключа VPS включена (`StrictHostKeyChecking=yes`). MySQL TLS обязателен; допускаются TLS 1.2/1.3, plaintext запрещён. Проверка MySQL-сертификата и имени endpoint отключена только в явно одобренной локальной сессии, так как endpoint использует самоподписанный сертификат без подходящего SAN. Это не подтверждает личность MySQL endpoint и не является конфигурацией для staging или production.

Исходная инструкция относится к комбинированному стенду. Для отдельной QA-папки создан Q&A-only запускатель и сокращённый runbook: он сохраняет туннель и TLS-политику, но не запускает product overview, review-summary или Apify-код.

Секреты и фактические значения `.env` в эту заметку не копировались.
