---
id: "session-2026-11-10T18-01-00plus-02-00-harden-the-race-expert-product-qa-evaluation-wor"
started_at: "2026-11-10T17:40:00+02:00"
ended_at: "2026-11-10T18:01:00+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Harden the Race Expert product QA evaluation workflow"
status: "partial"
transcript_source: "faithful-summary"
summary: "Expanded the product QA evaluation from prepared cases into a reproducible local workflow: deterministic context rendering, validation, safe free-model runner with retry/fallback and resume fingerprints, manual review queue, score aggregation, and fixed acceptance gates. Added a 30-case held-out set and clearly marked that it is not independent blind evidence. Local validation and 24 unit tests pass. Full model comparison and manual scoring remain pending because local logs already contain at least 56 API attempts today against OpenRouter's published 50/day free cap."
files_changed: [{"path": "evals/product-contexts.json", "action": "updated"}, {"path": "evals/model-contexts.json", "action": "regenerated"}, {"path": "evals/test_pipeline.py", "action": "updated"}, {"path": "evals/run_eval.py", "action": "hardened"}, {"path": "evals/test_runner.py", "action": "expanded"}, {"path": "evals/report_runs.py", "action": "expanded"}, {"path": "evals/test_report.py", "action": "expanded"}, {"path": "evals/prepare_review.py", "action": "created"}, {"path": "evals/test_prepare_review.py", "action": "created"}, {"path": "evals/README.md", "action": "rewritten"}, {"path": "evals/scoring-rubric.md", "action": "updated"}, {"path": "evals/acceptance-criteria.md", "action": "updated"}, {"path": "docs/superpowers/plans/2026-11-10-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/index.md", "action": "updated"}]
tags: ["activity:implementation", "status:partial", "task:product-qa-evaluation-pipeline", "project:race-expert", "topic:prompt-evaluation", "topic:openrouter", "file:evals/run_eval.py", "file:evals/report_runs.py", "file:evals/prepare_review.py", "file:evals/acceptance-criteria.md", "file:evals/README.md", "file:wiki/syntheses/race-expert-product-qa-evaluation.md"]
verification: [{"command": "python3 evals/render_contexts.py", "result": "passed; rendered six localized contexts"}, {"command": "python3 evals/validate_eval.py", "result": "passed; 60 base cases and 30 holdout cases, all pairs and references resolve"}, {"command": "python3 -m unittest discover -s evals -p 'test_*.py'", "result": "passed; 24 tests"}]
decisions: ["Treat the current 30-case holdout as held-out but not independent blind evidence because it was authored in the same workstream as the prompt.", "Stop the current day's free-model completion calls after the logged attempt count exceeds the published daily free cap; do not buy credits for evaluation.", "Do not claim product integration verification until the actual product-page backend payload is available."]
open_tasks: ["Complete the same 60-case compare run on three currently free models after quota reset, preserving one run fingerprint and resuming across days.", "Manually score every answerable model result and adjudicate critical-risk cases using the rubric.", "Freeze a prompt candidate and run all 30 held-out cases; use a separately authored holdout for strict blind evidence.", "When product backend code is available, compare its actual context payload with the evaluation context and verify product/language identity."]
blockers: ["At least 56 completion attempts are present in today's run logs while OpenRouter currently publishes a 50-per-day free cap; full inference must wait for reset.", "The workspace has no product-page backend/runtime implementation, so the production context shape cannot yet be verified."]
next_actions: ["After the free quota resets, run the 60-case compare command from evals/README.md in batches and use --resume with the unchanged fingerprint.", "Generate review queues from completed JSONL runs, fill scores, and produce aggregate reports.", "Update prompt only from development results, then evaluate the held-out set after freezing it."]
relevant_pages: ["wiki/syntheses/race-expert-product-qa-evaluation.md", "evals/README.md", "evals/acceptance-criteria.md", "evals/scoring-rubric.md", "docs/superpowers/plans/2026-11-10-product-qa-evaluation.md"]
---

# Session

## Outcome

Expanded the product QA evaluation from prepared cases into a reproducible local workflow: deterministic context rendering, validation, safe free-model runner with retry/fallback and resume fingerprints, manual review queue, score aggregation, and fixed acceptance gates. Added a 30-case held-out set and clearly marked that it is not independent blind evidence. Local validation and 24 unit tests pass. Full model comparison and manual scoring remain pending because local logs already contain at least 56 API attempts today against OpenRouter's published 50/day free cap.

## Changed Files

- `evals/product-contexts.json` — updated
- `evals/model-contexts.json` — regenerated
- `evals/test_pipeline.py` — updated
- `evals/run_eval.py` — hardened
- `evals/test_runner.py` — expanded
- `evals/report_runs.py` — expanded
- `evals/test_report.py` — expanded
- `evals/prepare_review.py` — created
- `evals/test_prepare_review.py` — created
- `evals/README.md` — rewritten
- `evals/scoring-rubric.md` — updated
- `evals/acceptance-criteria.md` — updated
- `docs/superpowers/plans/2026-11-10-product-qa-evaluation.md` — updated
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated
- `wiki/index.md` — updated

## Tags

- `activity:implementation`
- `status:partial`
- `task:product-qa-evaluation-pipeline`
- `project:race-expert`
- `topic:prompt-evaluation`
- `topic:openrouter`
- `file:evals/run_eval.py`
- `file:evals/report_runs.py`
- `file:evals/prepare_review.py`
- `file:evals/acceptance-criteria.md`
- `file:evals/README.md`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`

## Verification

- `python3 evals/render_contexts.py` — passed; rendered six localized contexts
- `python3 evals/validate_eval.py` — passed; 60 base cases and 30 holdout cases, all pairs and references resolve
- `python3 -m unittest discover -s evals -p 'test_*.py'` — passed; 24 tests
