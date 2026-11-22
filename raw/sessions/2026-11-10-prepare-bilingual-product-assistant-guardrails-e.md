---
id: "session-2026-11-10T22-23-00plus-02-00-prepare-bilingual-product-assistant-guardrails-e"
started_at: "2026-11-10T22:13:00+02:00"
ended_at: "2026-11-10T22:23:00+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Prepare bilingual product assistant guardrails evaluation"
status: "partial"
transcript_source: "faithful-summary"
summary: "Added system prompt v7 guardrails and a separate 30-case RU/UA evaluation suite covering rude but valid product questions, abuse-only messages, nonsense, prompt/secret extraction, and other buyers' data. Added validation and an acceptance profile. All 54 unit tests and dataset validation pass; model inference remains pending review of the frozen v6 comparison. The real website payload remains unverified."
files_changed: [{"path": "prompts/product-assistant-system-v7.md", "action": "created"}, {"path": "evals/guardrail-cases.jsonl", "action": "created"}, {"path": "evals/validate_eval.py", "action": "updated"}, {"path": "evals/check_acceptance.py", "action": "updated"}, {"path": "evals/report_runs.py", "action": "updated"}, {"path": "evals/test_acceptance.py", "action": "updated"}, {"path": "evals/test_pipeline.py", "action": "updated"}, {"path": "evals/test_report.py", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "evals/acceptance-criteria.md", "action": "updated"}, {"path": "evals/scoring-rubric.md", "action": "updated"}, {"path": "docs/superpowers/specs/2026-11-10-product-assistant-guardrails-design.md", "action": "created"}, {"path": "docs/superpowers/plans/2026-11-10-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/index.md", "action": "updated"}, {"path": "wiki/log.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt"}, {"path": "wiki/session-handoff.md", "action": "updated after save_memory"}]
tags: ["activity:implementation", "task:product-assistant-guardrails", "project:race-expert", "topic:prompt-testing", "file:prompts/product-assistant-system-v7.md", "file:evals/guardrail-cases.jsonl", "file:evals/check_acceptance.py", "file:wiki/syntheses/race-expert-product-qa-evaluation.md"]
verification: [{"command": "python3 -m unittest discover -s evals -v", "result": "passed: 54 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development, 30 holdout, 30 guardrail cases; sources and contexts resolve"}, {"command": "python3 evals/check_acceptance.py --help", "result": "passed: guardrail profile is available"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py . && python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed: indexed 4 cards; content lint passed"}]
decisions: ["Keep the v6 prompt and inputs frozen for the already scheduled model comparison.", "Test guardrails separately with v7 after v6 answers have been manually reviewed.", "Treat prompt rules as behavior guidance, not access control; the backend must never send secrets or other buyers' data."]
open_tasks: ["Inspect and manually score the v6 spotcheck and full three-model comparison after their scheduled runs.", "After v6 review, test v7 on 30 guardrail cases across the three free models and manually score all 90 outputs.", "Tune from observed failures, then complete holdout/blind evaluation and verify the real product-page payload when backend code is available."]
blockers: ["OpenRouter free daily quota is exhausted until the UTC reset; v6 inference jobs are waiting in scheduled processes."]
next_actions: ["Poll session 88742 after 2026-11-11T00:05Z and session 58631 after 2026-11-11T00:30Z.", "Manually score v6 answers before creating the v7 guardrail run."]
relevant_pages: ["wiki/syntheses/race-expert-product-qa-evaluation.md", "evals/README.md", "evals/acceptance-criteria.md", "prompts/product-assistant-system-v6.md", "prompts/product-assistant-system-v7.md", "evals/guardrail-cases.jsonl"]
---

# Session

## Outcome

Added system prompt v7 guardrails and a separate 30-case RU/UA evaluation suite covering rude but valid product questions, abuse-only messages, nonsense, prompt/secret extraction, and other buyers' data. Added validation and an acceptance profile. All 54 unit tests and dataset validation pass; model inference remains pending review of the frozen v6 comparison. The real website payload remains unverified.

## Changed Files

- `prompts/product-assistant-system-v7.md` — created
- `evals/guardrail-cases.jsonl` — created
- `evals/validate_eval.py` — updated
- `evals/check_acceptance.py` — updated
- `evals/report_runs.py` — updated
- `evals/test_acceptance.py` — updated
- `evals/test_pipeline.py` — updated
- `evals/test_report.py` — updated
- `evals/README.md` — updated
- `evals/acceptance-criteria.md` — updated
- `evals/scoring-rubric.md` — updated
- `docs/superpowers/specs/2026-11-10-product-assistant-guardrails-design.md` — created
- `docs/superpowers/plans/2026-11-10-product-qa-evaluation.md` — updated
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated
- `wiki/index.md` — updated
- `wiki/log.md` — updated
- `wiki/content-index.jsonl` — rebuilt
- `wiki/session-handoff.md` — updated after save_memory

## Tags

- `activity:implementation`
- `task:product-assistant-guardrails`
- `project:race-expert`
- `topic:prompt-testing`
- `file:prompts/product-assistant-system-v7.md`
- `file:evals/guardrail-cases.jsonl`
- `file:evals/check_acceptance.py`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`

## Verification

- `python3 -m unittest discover -s evals -v` — passed: 54 tests
- `python3 evals/validate_eval.py` — passed: 60 development, 30 holdout, 30 guardrail cases; sources and contexts resolve
- `python3 evals/check_acceptance.py --help` — passed: guardrail profile is available
- `python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py . && python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed: indexed 4 cards; content lint passed
