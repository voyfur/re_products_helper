---
id: "session-2026-11-10T21-47-00plus-02-00-reject-run-metadata-that-disagrees-with-selected"
started_at: "2026-11-10T21:42:00+02:00"
ended_at: "2026-11-10T21:47:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Reject run metadata that disagrees with selected cases"
status: "partial"
transcript_source: "faithful-summary"
summary: "Audited the acceptance path and found that a run row could keep a valid case ID but report a different product, language, or category, which could skew product/language gates. Added a table-driven regression test; it failed before the production change and passed after check_acceptance.py began comparing those fields against the canonical selected case. Full suite passed 47 tests, dataset validation passed, and the Wiki content index was rebuilt and linted. Prompt, context and question inputs remain unchanged while both scheduled model jobs are live and waiting for the free quota reset. The full nine-point objective remains active."
files_changed: [{"path": "evals/check_acceptance.py", "action": "updated"}, {"path": "evals/test_acceptance.py", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "evals/acceptance-criteria.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/log.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:implementation", "topic:prompt-testing", "project:race-expert", "file:evals/check_acceptance.py", "file:evals/test_acceptance.py", "file:evals/acceptance-criteria.md"]
verification: [{"command": "python3 -m unittest evals.test_acceptance.AcceptanceTests.test_acceptance_rejects_run_metadata_that_disagrees_with_selected_case", "result": "failed for product, language and category before the production change; passed after"}, {"command": "python3 -m unittest discover -s evals -v", "result": "passed: 47 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development cases / 30 pairs; 30 holdout cases / 15 pairs"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .", "result": "passed: indexed 4 cards"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed"}, {"command": "poll inference sessions 88742 and 58631", "result": "both remained live and waiting; starts scheduled for 2026-11-11T00:05Z and 00:30Z"}]
decisions: ["Before scoring, compare each final run row's product, language and category with the canonical selected case.", "For all profiles, a RU/UA pair must have one nonempty matching category; for holdout and blind, each product must cover its required risk categories.", "Leave prompt, contexts, and case inputs unchanged until scheduled inference runs finish."]
open_tasks: ["Inspect and manually score the v6 target outputs after the quota reset.", "Complete and score the same 60-case comparison on three free models.", "Tune the prompt from observed failures and repeat failed plus neighboring cases.", "Run the frozen-candidate holdout fallback and prepare an independent blind set after prompt freeze.", "Verify the real product-page payload when backend code or a representative request becomes available."]
blockers: ["The OpenRouter free-model daily quota is exhausted; both inference processes remain live and scheduled after reset.", "The product-assistant backend/payload is absent from the inspected workspace, so real-page context verification cannot yet be completed."]
next_actions: ["Poll session 88742 after 2026-11-11T00:05Z and inspect its run and review queue.", "Keep session 58631 alive through its 2026-11-11T00:30Z start and its resumable quota windows.", "Validate output provenance and coverage, score the answers, then revise the prompt from evidenced failures."]
relevant_pages: ["evals/check_acceptance.py", "evals/test_acceptance.py", "evals/validate_eval.py", "evals/acceptance-criteria.md", "evals/README.md", "wiki/syntheses/race-expert-product-qa-evaluation.md", "prompts/product-assistant-system-v6.md"]
---

# Session

## Outcome

Audited the acceptance path and found that a run row could keep a valid case ID but report a different product, language, or category, which could skew product/language gates. Added a table-driven regression test; it failed before the production change and passed after check_acceptance.py began comparing those fields against the canonical selected case. Full suite passed 47 tests, dataset validation passed, and the Wiki content index was rebuilt and linted. Prompt, context and question inputs remain unchanged while both scheduled model jobs are live and waiting for the free quota reset. The full nine-point objective remains active.

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

- `python3 -m unittest evals.test_acceptance.AcceptanceTests.test_acceptance_rejects_run_metadata_that_disagrees_with_selected_case` — failed for product, language and category before the production change; passed after
- `python3 -m unittest discover -s evals -v` — passed: 47 tests
- `python3 evals/validate_eval.py` — passed: 60 development cases / 30 pairs; 30 holdout cases / 15 pairs
- `python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .` — passed: indexed 4 cards
- `python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed
- `poll inference sessions 88742 and 58631` — both remained live and waiting; starts scheduled for 2026-11-11T00:05Z and 00:30Z
