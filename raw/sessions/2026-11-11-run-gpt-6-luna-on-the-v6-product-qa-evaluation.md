---
id: "session-2026-11-11T14-30-50plus-02-00-run-gpt-6-luna-on-the-v6-product-qa-evaluation"
started_at: "2026-11-11T14:00:00+02:00"
ended_at: "2026-11-11T14:30:50+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Run GPT-6 Luna on the v6 product QA evaluation"
status: "completed"
transcript_source: "faithful-summary"
summary: "After explicit user approval, ran all 60 v6 product QA cases through OpenAI GPT-6 Luna. The first request configuration with temperature=0 produced HTTP 400 responses because the model rejected that parameter; the corrected Responses API run omitted temperature, used store=false, and kept model-default reasoning effort. All 60 corrected-run cases completed. Manual scoring averaged 7.95/8, with 59/60 at least 7/8 and no critical failures. One Ukrainian answer was mostly Russian; one answer omitted the known 32 g serving size. Because sampling settings differ from temperature=0 runs, this is diagnostic evidence, not a strictly comparable model ranking. Prompt and fixtures were unchanged."
files_changed: [{"path": "evals/run_eval.py", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "evals/runs/compare-v6-gpt-6-luna.jsonl", "action": "created"}, {"path": "evals/runs/compare-v6-gpt-6-luna-model-defaults.jsonl", "action": "created"}, {"path": "evals/runs/review-v6-gpt-6-luna-model-defaults.jsonl", "action": "created"}, {"path": "evals/runs/report-v6-gpt-6-luna-model-defaults.json", "action": "created"}, {"path": "evals/runs/acceptance-v6-gpt-6-luna-model-defaults.json", "action": "created"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}]
tags: ["activity:testing", "status:completed", "task:product-assistant-evaluation", "project:race-expert", "topic:openai-api", "topic:gpt-6-luna", "topic:prompt-evaluation", "topic:manual-scoring", "topic:backend-payload", "file:evals/run_eval.py", "file:evals/README.md", "file:evals/runs/compare-v6-gpt-6-luna-model-defaults.jsonl", "file:evals/runs/review-v6-gpt-6-luna-model-defaults.jsonl", "file:evals/runs/acceptance-v6-gpt-6-luna-model-defaults.json", "file:wiki/syntheses/race-expert-product-qa-evaluation.md"]
verification: [{"command": "OpenAI read-only model preflight for gpt-6-luna", "result": "passed; no generation sent"}, {"command": "GPT-6 Luna v6 run with same fingerprint and --resume", "result": "60/60 answers; 60 successful API calls"}, {"command": "evals/prepare_review.py", "result": "prepared 60 answers and all were manually scored"}, {"command": "evals/report_runs.py", "result": "60 scored answers; mean 7.95/8; zero critical failures"}, {"command": "evals/check_acceptance.py --profile regression --models gpt-6-luna", "result": "pass"}, {"command": "Python AST parse and runner --help", "result": "passed"}]
decisions: ["Keep prompt v6 and evaluation fixtures unchanged.", "Do not rank GPT-6 Luna as strictly comparable to temperature=0 runs; the API rejected explicit temperature for this model and the successful run used model defaults.", "Do not select a production model yet; the three-model OpenRouter comparison is still partial and actual page/backend retrieval remains unverified."]
open_tasks: ["Resume the OpenRouter v6 comparison after its UTC quota reset, then manually score remaining answers and repeat provider failures or critical cases.", "Obtain the actual product-page/backend implementation or runtime trace and verify product selection and payload end to end.", "After v6 analysis and prompt freeze, run v7 guardrail and holdout suites, then prepare the independent blind set."]
blockers: ["OpenRouter free daily quota is exhausted until 2026-11-12 00:00 UTC.", "No actual product-assistant page/backend implementation or runtime payload is available."]
next_actions: ["Resume evals/runs/compare-v6-openrouter.jsonl with the same fingerprint after the UTC reset.", "Continue source/runtime discovery for the actual product-page payload."]
relevant_pages: ["wiki/index.md", "wiki/session-handoff.md", "wiki/syntheses/race-expert-product-qa-evaluation.md", "evals/README.md", "evals/scoring-rubric.md", "evals/acceptance-criteria.md", "evals/runs/compare-v6-gpt-6-luna-model-defaults.jsonl", "evals/runs/review-v6-gpt-6-luna-model-defaults.jsonl", "evals/runs/acceptance-v6-gpt-6-luna-model-defaults.json"]
---

# Session

## Outcome

After explicit user approval, ran all 60 v6 product QA cases through OpenAI GPT-6 Luna. The first request configuration with temperature=0 produced HTTP 400 responses because the model rejected that parameter; the corrected Responses API run omitted temperature, used store=false, and kept model-default reasoning effort. All 60 corrected-run cases completed. Manual scoring averaged 7.95/8, with 59/60 at least 7/8 and no critical failures. One Ukrainian answer was mostly Russian; one answer omitted the known 32 g serving size. Because sampling settings differ from temperature=0 runs, this is diagnostic evidence, not a strictly comparable model ranking. Prompt and fixtures were unchanged.

## Changed Files

- `evals/run_eval.py` — updated
- `evals/README.md` — updated
- `evals/runs/compare-v6-gpt-6-luna.jsonl` — created
- `evals/runs/compare-v6-gpt-6-luna-model-defaults.jsonl` — created
- `evals/runs/review-v6-gpt-6-luna-model-defaults.jsonl` — created
- `evals/runs/report-v6-gpt-6-luna-model-defaults.json` — created
- `evals/runs/acceptance-v6-gpt-6-luna-model-defaults.json` — created
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated

## Tags

- `activity:testing`
- `status:completed`
- `task:product-assistant-evaluation`
- `project:race-expert`
- `topic:openai-api`
- `topic:gpt-6-luna`
- `topic:prompt-evaluation`
- `topic:manual-scoring`
- `topic:backend-payload`
- `file:evals/run_eval.py`
- `file:evals/README.md`
- `file:evals/runs/compare-v6-gpt-6-luna-model-defaults.jsonl`
- `file:evals/runs/review-v6-gpt-6-luna-model-defaults.jsonl`
- `file:evals/runs/acceptance-v6-gpt-6-luna-model-defaults.json`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`

## Verification

- `OpenAI read-only model preflight for gpt-6-luna` — passed; no generation sent
- `GPT-6 Luna v6 run with same fingerprint and --resume` — 60/60 answers; 60 successful API calls
- `evals/prepare_review.py` — prepared 60 answers and all were manually scored
- `evals/report_runs.py` — 60 scored answers; mean 7.95/8; zero critical failures
- `evals/check_acceptance.py --profile regression --models gpt-6-luna` — pass
- `Python AST parse and runner --help` — passed
