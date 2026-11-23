# Session Handoff

## Active Context

- Last session: `raw/sessions/2026-11-23-deploy-rozetka-ai-style-demo-with-sports-skills-.md`
- Current objective: Deploy Rozetka-AI style demo with sports skills, intent classifier, and 24-category questions matrix

## Current Decisions

- Впроваджено UI у функціональному стилі Rozetka AI з брендуванням Race Expert: плаваюча кнопка Race Expert AI, бічна шторка з карткою товару, ціною, наявністю та вибором артикулу.
- Активовано prompt v18 та модуль Intent Classifier (app/intent_classifier.py): 4 доменні модулі знань (Endurance, Supplements, Combat/Gym, General) динамічно збагачують системний промпт.
- Виправлено таймінг та усунено роботизовані відмови: консультант підтримує логіку бігуна, пояснює питний режим на дистанції (100–150 мл кожні 15–20 хв) та підтверджує прийом на фініші для швидкого відновлення глікогену.
- Реалізовано ієрархічну матрицю швидких запитань (app/suggested_questions.py): 24 групи/підгрупи (100% каталогу OpenCart), рівно по 6 найчастіших запитань для кожної групи (144 запитання). Питання підтягуються динамічно через /api/search та оновлюються на фронтенді.
- Розгорнуто оновлений Docker-образ на VPS: перевірено автоматичним browser-агентом та live API на https://n8n.raceexpert-tools.net.ua/re-products-demo/.

## Open Tasks

- Зібрати додатковий зворотний зв'язок від замовника після тестування оновленого функціоналу.

## Blockers

- No blockers recorded.

## Next Action

- Надати клієнту публічне посилання на перевірене live demo: https://n8n.raceexpert-tools.net.ua/re-products-demo/.

## Relevant Pages

- wiki/index.md
- wiki/session-handoff.md
- wiki/sources/race-expert-qa-project.md
- wiki/syntheses/race-expert-qa-production-readiness.md
