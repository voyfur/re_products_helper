---
id: "session-2026-11-10T20-35-00plus-02-00-include-exact-model-context-in-review-rows"
started_at: "2026-11-10T20:32:00+02:00"
ended_at: "2026-11-10T20:35:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Include exact model context in review rows"
status: "partial"
transcript_source: "faithful-summary"
summary: "Extended prepare_review.py to load the context file used for inference, include the exact context text in each manual review row, and verify that its SHA-256 matches context_sha256 from the run. Review rows already carry pair IDs and case-level expectations; now a reviewer can judge the answer against the exact model input without looking it up elsewhere. Added a test using a custom context file. Updated README and Wiki synthesis, rebuilt/linted Wiki content. All 40 tests and the eval validator pass. The scheduled v6 process remains live, waiting until 2026-11-11T00:05:00Z; no inference output is present."
files_changed: [{"path": "evals/prepare_review.py", "action": "updated"}, {"path": "evals/test_prepare_review.py", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "regenerated"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:implementation", "task:product-qa-evaluation", "project:race-expert", "file:evals/prepare_review.py", "file:evals/test_prepare_review.py", "file:evals/README.md", "file:wiki/syntheses/race-expert-product-qa-evaluation.md", "file:wiki/content-index.jsonl", "file:wiki/session-handoff.md"]
verification: [{"command": "python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance", "result": "passed: 40 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .", "result": "passed: indexed 4 content cards"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed"}, {"command": "write_stdin(session_id=88742)", "result": "live at 2026-11-10T18:34:40Z; waits until 2026-11-11T00:05:00Z"}]
decisions: ["Review the exact context text passed to the model, and verify its hash, rather than scoring from the product fixture alone.", "Keep expected critical tags separate from actual scorer tags."]
open_tasks: ["Poll session 88742 at or after 2026-11-11T00:05:00Z and manually score the v6 target outputs against the exact included context.", "Complete the same-set 60-case comparison for three free models with retry/resume, score outputs, and repeat failures with neighboring cases.", "Run fallback on the frozen candidate holdout and check quality and availability gates.", "Create and evaluate an independently authored 60-question blind holdout after prompt freeze.", "Verify the actual product-page assistant payload when available."]
blockers: ["Free OpenRouter daily quota is exhausted until UTC reset; the v6 batch is still sleeping.", "The actual product-page assistant backend/payload has not been located in the inspected workspace."]
next_actions: ["After quota reset, inspect the v6 run JSONL and review queue; adjudicate every available answer.", "Use the acceptance gate only after all answerable outputs have manual scores."]
relevant_pages: ["evals/prepare_review.py", "evals/test_prepare_review.py", "evals/README.md", "evals/scoring-rubric.md", "evals/check_acceptance.py", "wiki/syntheses/race-expert-product-qa-evaluation.md"]
---

# Session

## Outcome

Extended prepare_review.py to load the context file used for inference, include the exact context text in each manual review row, and verify that its SHA-256 matches context_sha256 from the run. Review rows already carry pair IDs and case-level expectations; now a reviewer can judge the answer against the exact model input without looking it up elsewhere. Added a test using a custom context file. Updated README and Wiki synthesis, rebuilt/linted Wiki content. All 40 tests and the eval validator pass. The scheduled v6 process remains live, waiting until 2026-11-11T00:05:00Z; no inference output is present.

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

- `python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance` — passed: 40 tests
- `python3 evals/validate_eval.py` — passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs
- `python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .` — passed: indexed 4 content cards
- `python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed
- `write_stdin(session_id=88742)` — live at 2026-11-10T18:34:40Z; waits until 2026-11-11T00:05:00Z
