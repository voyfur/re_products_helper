---
id: "session-2026-11-10T20-28-00plus-02-00-document-reproducible-fallback-evaluation-run"
started_at: "2026-11-10T20:25:00+02:00"
ended_at: "2026-11-10T20:28:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Document reproducible fallback evaluation run"
status: "partial"
transcript_source: "faithful-summary"
summary: "Added an exact fallback-mode command for the 30-question diagnostic holdout, including retry behavior, quota-safe resume, manual scoring, and the holdout acceptance check. Documented that the same prompt must be frozen and the holdout must not be used for tuning. Verified the unchanged suite: 40 tests pass and the dataset validator confirms 60 development outputs / 30 pairs and 30 holdout outputs / 15 pairs. Process 88742 is still live waiting for 2026-11-11T00:05:00Z; no model result exists yet."
files_changed: [{"path": "evals/README.md", "action": "updated"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:documentation", "task:product-qa-evaluation", "project:race-expert", "file:evals/README.md", "file:wiki/session-handoff.md"]
verification: [{"command": "python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance", "result": "passed: 40 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs"}, {"command": "write_stdin(session_id=88742)", "result": "live at 2026-11-10T18:27:19Z; waits until 2026-11-11T00:05:00Z"}]
decisions: ["Run fallback on holdout only after prompt freeze and the full compare; do not tune the prompt from the holdout responses.", "Use the default three verified free models in fallback and require manual scoring before checking the holdout acceptance gate."]
open_tasks: ["Poll session 88742 after 2026-11-11T00:05:00Z, score the v6 target batch, and decide whether to freeze v6 or revise it.", "Complete same-set regression comparison for three models and score outputs, retrying failed cases plus neighbors.", "Run fallback on the frozen candidate holdout and validate its quality and availability gates.", "Create an independently authored 60-question blind set after prompt freeze.", "Verify the actual assistant backend payload when available."]
blockers: ["Free OpenRouter quota is exhausted until the next UTC reset; the scheduled v6 spotcheck is still running its wait.", "No actual product-page assistant backend/payload has been located in the inspected workspace."]
next_actions: ["At quota reset, inspect v6 output and review queue; manually adjudicate before changing prompt or launching full regression.", "After the prompt decision, run compare and then frozen-candidate fallback using the documented commands."]
relevant_pages: ["evals/README.md", "evals/acceptance-criteria.md", "evals/check_acceptance.py", "wiki/syntheses/race-expert-product-qa-evaluation.md"]
---

# Session

## Outcome

Added an exact fallback-mode command for the 30-question diagnostic holdout, including retry behavior, quota-safe resume, manual scoring, and the holdout acceptance check. Documented that the same prompt must be frozen and the holdout must not be used for tuning. Verified the unchanged suite: 40 tests pass and the dataset validator confirms 60 development outputs / 30 pairs and 30 holdout outputs / 15 pairs. Process 88742 is still live waiting for 2026-11-11T00:05:00Z; no model result exists yet.

## Changed Files

- `evals/README.md` — updated
- `wiki/session-handoff.md` — updated

## Tags

- `activity:documentation`
- `task:product-qa-evaluation`
- `project:race-expert`
- `file:evals/README.md`
- `file:wiki/session-handoff.md`

## Verification

- `python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance` — passed: 40 tests
- `python3 evals/validate_eval.py` — passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs
- `write_stdin(session_id=88742)` — live at 2026-11-10T18:27:19Z; waits until 2026-11-11T00:05:00Z
