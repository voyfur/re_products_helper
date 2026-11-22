---
id: "session-2026-11-10T21-53-00plus-02-00-require-explicit-model-list-for-compare-acceptan"
started_at: "2026-11-10T21:49:00+02:00"
ended_at: "2026-11-10T21:53:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Require explicit model list for compare acceptance"
status: "partial"
transcript_source: "faithful-summary"
summary: "Found that compare acceptance inferred expected model IDs from observed outputs, allowing a model with zero rows to disappear from the gate. Added a regression test that failed before the change; compare mode now requires the caller to provide the explicit expected-model list. The full evaluation suite passed 48 tests and dataset validation passed. Updated the README, acceptance criteria, Wiki synthesis and log, then rebuilt and linted the content index. The two scheduled model runs remain alive and waiting; no prompt/context/case inputs changed. The full nine-point objective remains active."
files_changed: [{"path": "evals/check_acceptance.py", "action": "updated"}, {"path": "evals/test_acceptance.py", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "evals/acceptance-criteria.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/log.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:implementation", "topic:prompt-testing", "project:race-expert", "file:evals/check_acceptance.py", "file:evals/test_acceptance.py", "file:evals/acceptance-criteria.md"]
verification: [{"command": "python3 -m unittest evals.test_acceptance.AcceptanceTests.test_compare_acceptance_requires_explicit_expected_models", "result": "failed before the production change, passed after"}, {"command": "python3 -m unittest discover -s evals -v", "result": "passed: 48 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development cases / 30 pairs; 30 holdout cases / 15 pairs"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .", "result": "passed: indexed 4 cards"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed"}, {"command": "poll inference sessions 88742 and 58631", "result": "both remained live, scheduled for 2026-11-11T00:05Z and 00:30Z"}]
decisions: ["Compare-mode acceptance requires an explicit full expected-model list; fallback mode does not use this list.", "Run result product, language and category must match the canonical selected case.", "Keep prompt, contexts and case inputs unchanged until scheduled inference jobs complete."]
open_tasks: ["Inspect and manually score v6 target outputs after the quota reset.", "Complete and score the same 60-case comparison on three free models.", "Tune the prompt from observed failures and repeat failed plus neighboring cases.", "Run a frozen-candidate holdout fallback and prepare an independent blind set after prompt freeze.", "Verify the real product-page payload when backend code or a representative request becomes available."]
blockers: ["The OpenRouter free-model daily quota is exhausted; the two inference processes remain alive and scheduled after reset.", "The product-assistant backend/payload is absent from the inspected workspace, so real-page context verification cannot yet be completed."]
next_actions: ["Poll session 88742 after 2026-11-11T00:05Z and inspect its run and review queue.", "Keep session 58631 alive through its 2026-11-11T00:30Z start and its resumable quota windows.", "Validate provenance and coverage, score the answers, and tune the prompt from evidenced failures."]
relevant_pages: ["evals/check_acceptance.py", "evals/test_acceptance.py", "evals/validate_eval.py", "evals/acceptance-criteria.md", "evals/README.md", "wiki/syntheses/race-expert-product-qa-evaluation.md", "prompts/product-assistant-system-v6.md"]
---

# Session

## Outcome

Found that compare acceptance inferred expected model IDs from observed outputs, allowing a model with zero rows to disappear from the gate. Added a regression test that failed before the change; compare mode now requires the caller to provide the explicit expected-model list. The full evaluation suite passed 48 tests and dataset validation passed. Updated the README, acceptance criteria, Wiki synthesis and log, then rebuilt and linted the content index. The two scheduled model runs remain alive and waiting; no prompt/context/case inputs changed. The full nine-point objective remains active.

## Changed Files

- `evals/check_acceptance.py` — updated
- `evals/test_acceptance.py` — updated
- `evals/README.md` — updated
- `evals/acceptance-criteria.md` — updated
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated
- `wiki/log.md` — updated
- `wiki/content-index.jsonl` — rebuilt
- `wiki/session-handoff.md` — updated

## Tags

- `activity:implementation`
- `topic:prompt-testing`
- `project:race-expert`
- `file:evals/check_acceptance.py`
- `file:evals/test_acceptance.py`
- `file:evals/acceptance-criteria.md`

## Verification

- `python3 -m unittest evals.test_acceptance.AcceptanceTests.test_compare_acceptance_requires_explicit_expected_models` — failed before the production change, passed after
- `python3 -m unittest discover -s evals -v` — passed: 48 tests
- `python3 evals/validate_eval.py` — passed: 60 development cases / 30 pairs; 30 holdout cases / 15 pairs
- `python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .` — passed: indexed 4 cards
- `python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed
- `poll inference sessions 88742 and 58631` — both remained live, scheduled for 2026-11-11T00:05Z and 00:30Z
