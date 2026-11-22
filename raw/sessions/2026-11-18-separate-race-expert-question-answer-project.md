---
id: "session-2026-11-18T19-28-00plus-02-00-separate-race-expert-question-answer-project"
started_at: "2026-11-18T18:40:00+02:00"
ended_at: "2026-11-18T19:28:00+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Separate Race Expert question-answer project"
status: "completed"
transcript_source: "faithful-summary"
summary: "Created a standalone Q&A-only project with its own app, SQLite attempt journal, v12 prompt, historical Q&A prompts, evaluation sets/results, selected design docs, and Wiki. The original combined test harness was left untouched. No live database or OpenAI calls were made and nothing was deployed."
files_changed: [{"path": "app/main.py", "action": "created"}, {"path": "app/catalog.py", "action": "created"}, {"path": "app/journal.py", "action": "created"}, {"path": "app/openai_client.py", "action": "created"}, {"path": "app/static/app.js", "action": "created"}, {"path": "prompts/product-assistant-system-v12.md", "action": "copied"}, {"path": "evals/", "action": "copied"}, {"path": "wiki/", "action": "created"}]
tags: ["activity:implementation", "project:race-expert", "file:app/main.py", "file:wiki/index.md"]
verification: [{"command": "Python 3.12 compileall app and tests", "result": "passed"}, {"command": "node --check app/static/app.js", "result": "passed"}, {"command": "python3.12 evals/validate_eval.py", "result": "passed: 60 base, 30 holdout, 30 guardrail cases; sources resolve"}, {"command": "python3.12 -m unittest discover -s evals -p test_*.py", "result": "passed: 82 tests"}, {"command": "Manual Q&A service and TLS configuration smoke", "result": "passed"}, {"command": "pytest app route tests", "result": "not run: pytest and FastAPI are not installed in the available Python environment"}]
decisions: ["The new QA folder contains only question-answer runtime modules; product-summary and customer-feedback runtime modules were not transferred.", "Q&A grading artifacts named review-* were retained because they grade model answers and contain no buyer feedback records.", "Historical source references were redirected or left as locator-only files where original database audit evidence was excluded."]
open_tasks: ["Install requirements-dev.txt in the intended Python environment and run pytest for the new FastAPI route tests.", "Before any deployment, independently confirm the MySQL CA and hostname and set access controls and request limits."]
blockers: ["FastAPI and pytest are absent from the current environment, so app route tests could not be executed."]
next_actions: ["Review the standalone app in the QA folder.", "Run its pytest suite after installing the project dependencies."]
relevant_pages: ["wiki/sources/race-expert-qa-project.md", "wiki/syntheses/race-expert-qa-evaluation.md"]
---

# Session

## Outcome

Created a standalone Q&A-only project with its own app, SQLite attempt journal, v12 prompt, historical Q&A prompts, evaluation sets/results, selected design docs, and Wiki. The original combined test harness was left untouched. No live database or OpenAI calls were made and nothing was deployed.

## Changed Files

- `app/main.py` — created
- `app/catalog.py` — created
- `app/journal.py` — created
- `app/openai_client.py` — created
- `app/static/app.js` — created
- `prompts/product-assistant-system-v12.md` — copied
- `evals/` — copied
- `wiki/` — created

## Tags

- `activity:implementation`
- `project:race-expert`
- `file:app/main.py`
- `file:wiki/index.md`

## Verification

- `Python 3.12 compileall app and tests` — passed
- `node --check app/static/app.js` — passed
- `python3.12 evals/validate_eval.py` — passed: 60 base, 30 holdout, 30 guardrail cases; sources resolve
- `python3.12 -m unittest discover -s evals -p test_*.py` — passed: 82 tests
- `Manual Q&A service and TLS configuration smoke` — passed
- `pytest app route tests` — not run: pytest and FastAPI are not installed in the available Python environment
