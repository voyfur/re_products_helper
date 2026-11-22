---
id: "session-2026-11-10T20-21-00plus-02-00-implement-and-verify-automatic-evaluation-accept"
started_at: "2026-11-10T20:06:00+02:00"
ended_at: "2026-11-10T20:21:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Implement and verify automatic evaluation acceptance gates"
status: "partial"
transcript_source: "faithful-summary"
summary: "Audited report_runs.py and found that it aggregated scores but did not enforce predeclared acceptance thresholds or produce an acceptance verdict. Added check_acceptance.py for regression, diagnostic holdout, and independent blind profiles. It validates case counts and bilingual pairs, completeness and manual score coverage, critical failures, score thresholds, product/language means, RU/UK gaps, fallback availability, and explicit reasons for unanswered fallback cases. Quality and provider availability remain separate; compare-mode provider errors yield incomplete evaluation rather than a model-quality failure. Added boundary tests and documented CLI use."
files_changed: [{"path": "evals/check_acceptance.py", "action": "created"}, {"path": "evals/test_acceptance.py", "action": "created"}, {"path": "evals/README.md", "action": "updated"}, {"path": "evals/acceptance-criteria.md", "action": "updated"}, {"path": "docs/superpowers/plans/2026-11-10-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "regenerated"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:implementation", "task:product-qa-evaluation", "project:race-expert", "file:evals/check_acceptance.py", "file:evals/test_acceptance.py", "file:evals/README.md", "file:evals/acceptance-criteria.md", "file:docs/superpowers/plans/2026-11-10-product-qa-evaluation.md", "file:wiki/syntheses/race-expert-product-qa-evaluation.md", "file:wiki/content-index.jsonl", "file:wiki/session-handoff.md"]
verification: [{"command": "python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance", "result": "passed: 39 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs; sources and contexts resolve"}, {"command": "PYTHONPYCACHEPREFIX=/private/tmp/race-expert-eval-pycache python3 -m py_compile evals/check_acceptance.py evals/test_acceptance.py", "result": "passed"}, {"command": "python3 evals/check_acceptance.py --help", "result": "passed"}, {"command": "synthetic CLI check", "result": "passed: perfect holdout exits 0; below-threshold holdout exits 1"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed"}, {"command": "write_stdin(session_id=88742)", "result": "still running; scheduled wake at 2026-11-11T00:05:00Z; no v6 output yet"}]
decisions: ["An API/provider failure is reported as an availability issue and leaves compare quality incomplete; it is not scored as a model-quality failure.", "A fallback run with one permitted unanswered case only passes availability when the case has an explicit reproducible status or provider reason.", "Use the acceptance checker only after every answer has a human review score; leave the model prompt unchanged until v6 targeted results are adjudicated."]
open_tasks: ["Poll session 88742 at or after 2026-11-11T00:05:00Z; collect and manually score the v6 batch.", "After prompt decision, run the full 60-case same-set comparison for three free models across UTC quota windows, then score and repeat failures.", "After freezing the prompt, create the independent 60-question blind set and run it against the defined gate.", "Verify the actual product-page backend payload when it becomes available."]
blockers: ["OpenRouter free-model quota is exhausted until the UTC reset; the v6 spotcheck is sleeping until 2026-11-11T00:05:00Z.", "The actual product-page assistant backend/payload remains unavailable in the inspected workspace."]
next_actions: ["At the scheduled reset, inspect run JSONL and review queue; do not tune from holdout answers.", "If v6 passes targeted checks, use check_acceptance.py after full run and manual scoring."]
relevant_pages: ["evals/README.md", "evals/acceptance-criteria.md", "evals/check_acceptance.py", "wiki/syntheses/race-expert-product-qa-evaluation.md", "docs/superpowers/plans/2026-11-10-product-qa-evaluation.md"]
---

# Session

## Outcome

Audited report_runs.py and found that it aggregated scores but did not enforce predeclared acceptance thresholds or produce an acceptance verdict. Added check_acceptance.py for regression, diagnostic holdout, and independent blind profiles. It validates case counts and bilingual pairs, completeness and manual score coverage, critical failures, score thresholds, product/language means, RU/UK gaps, fallback availability, and explicit reasons for unanswered fallback cases. Quality and provider availability remain separate; compare-mode provider errors yield incomplete evaluation rather than a model-quality failure. Added boundary tests and documented CLI use.

## Changed Files

- `evals/check_acceptance.py` — created
- `evals/test_acceptance.py` — created
- `evals/README.md` — updated
- `evals/acceptance-criteria.md` — updated
- `docs/superpowers/plans/2026-11-10-product-qa-evaluation.md` — updated
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated
- `wiki/content-index.jsonl` — regenerated
- `wiki/session-handoff.md` — updated

## Tags

- `activity:implementation`
- `task:product-qa-evaluation`
- `project:race-expert`
- `file:evals/check_acceptance.py`
- `file:evals/test_acceptance.py`
- `file:evals/README.md`
- `file:evals/acceptance-criteria.md`
- `file:docs/superpowers/plans/2026-11-10-product-qa-evaluation.md`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`
- `file:wiki/content-index.jsonl`
- `file:wiki/session-handoff.md`

## Verification

- `python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance` — passed: 39 tests
- `python3 evals/validate_eval.py` — passed: 60 development outputs / 30 pairs; 30 current holdout outputs / 15 pairs; sources and contexts resolve
- `PYTHONPYCACHEPREFIX=/private/tmp/race-expert-eval-pycache python3 -m py_compile evals/check_acceptance.py evals/test_acceptance.py` — passed
- `python3 evals/check_acceptance.py --help` — passed
- `synthetic CLI check` — passed: perfect holdout exits 0; below-threshold holdout exits 1
- `python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed
- `write_stdin(session_id=88742)` — still running; scheduled wake at 2026-11-11T00:05:00Z; no v6 output yet
