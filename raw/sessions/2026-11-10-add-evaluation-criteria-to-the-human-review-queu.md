---
id: "session-2026-11-10T20-32-00plus-02-00-add-evaluation-criteria-to-the-human-review-queu"
started_at: "2026-11-10T20:29:00+02:00"
ended_at: "2026-11-10T20:32:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Add evaluation criteria to the human review queue"
status: "partial"
transcript_source: "faithful-summary"
summary: "Expanded prepare_review.py so each answered output carries its expected behavior, must-cover facts, prohibited claims, expected critical tags, source reference, and RU/UA pair ID alongside the model answer. This removes repeated lookup in the source case file during manual scoring and keeps expected critical tags separate from actual reviewer tags. Added a failing-first regression test, updated the README and Wiki synthesis, rebuilt and linted the content index. Full 40-test suite and dataset validation pass. The scheduled v6 process remains live and waits for 2026-11-11T00:05:00Z; no output file has been produced yet."
files_changed: [{"path": "evals/prepare_review.py", "action": "updated"}, {"path": "evals/test_prepare_review.py", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "regenerated"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:implementation", "task:product-qa-evaluation", "project:race-expert", "file:evals/prepare_review.py", "file:evals/test_prepare_review.py", "file:evals/README.md", "file:wiki/syntheses/race-expert-product-qa-evaluation.md", "file:wiki/content-index.jsonl", "file:wiki/session-handoff.md"]
verification: [{"command": "python3 -m unittest evals.test_prepare_review", "result": "passed: 2 tests"}, {"command": "python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance", "result": "passed: 40 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .", "result": "passed: indexed 4 content cards"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed"}, {"command": "write_stdin(session_id=88742)", "result": "live at 2026-11-10T18:31:27Z; waits until 2026-11-11T00:05:00Z"}]
decisions: ["Keep expected critical failure tags separate from actual manual reviewer tags in the review queue.", "Do not change prompt v6 until its targeted responses can be scored against the case criteria."]
open_tasks: ["Poll session 88742 at or after 2026-11-11T00:05:00Z and manually score the v6 target batch.", "Complete same-set 60-case comparison for three free models with retries/resume; score all outputs and repeat failures with neighboring cases.", "Run fallback on the frozen prompt's diagnostic holdout and check its availability and quality gates.", "Create and run an independently authored 60-question blind holdout after prompt freeze.", "Verify the actual product assistant payload when it becomes available."]
blockers: ["Free OpenRouter quota remains exhausted until UTC reset; the v6 process is still sleeping.", "Actual product-page assistant backend/payload has not been located in the inspected workspace."]
next_actions: ["After quota reset, inspect run JSONL and new review queue, then manually adjudicate all available answers.", "Use the acceptance gate only after every answerable output has a manual score."]
relevant_pages: ["evals/prepare_review.py", "evals/README.md", "evals/scoring-rubric.md", "evals/check_acceptance.py", "wiki/syntheses/race-expert-product-qa-evaluation.md"]
---

# Session

## Outcome

Expanded prepare_review.py so each answered output carries its expected behavior, must-cover facts, prohibited claims, expected critical tags, source reference, and RU/UA pair ID alongside the model answer. This removes repeated lookup in the source case file during manual scoring and keeps expected critical tags separate from actual reviewer tags. Added a failing-first regression test, updated the README and Wiki synthesis, rebuilt and linted the content index. Full 40-test suite and dataset validation pass. The scheduled v6 process remains live and waits for 2026-11-11T00:05:00Z; no output file has been produced yet.

## Changed Files

- `evals/prepare_review.py` — updated
- `evals/test_prepare_review.py` — updated
- `evals/README.md` — updated
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated
- `wiki/content-index.jsonl` — regenerated
- `wiki/session-handoff.md` — updated

## Tags

- `activity:implementation`
- `task:product-qa-evaluation`
- `project:race-expert`
- `file:evals/prepare_review.py`
- `file:evals/test_prepare_review.py`
- `file:evals/README.md`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`
- `file:wiki/content-index.jsonl`
- `file:wiki/session-handoff.md`

## Verification

- `python3 -m unittest evals.test_prepare_review` — passed: 2 tests
- `python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance` — passed: 40 tests
- `python3 evals/validate_eval.py` — passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs
- `python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .` — passed: indexed 4 content cards
- `python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed
- `write_stdin(session_id=88742)` — live at 2026-11-10T18:31:27Z; waits until 2026-11-11T00:05:00Z
