---
id: "session-2026-11-10T23-03-00plus-02-00-strengthen-product-assistant-guardrail-evaluatio"
started_at: "2026-11-10T22:54:00+02:00"
ended_at: "2026-11-10T23:03:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Strengthen product assistant guardrail evaluation"
status: "partial"
transcript_source: "faithful-summary"
summary: "Confirmed Guardrails are a separate bilingual evaluation: answer a useful product question calmly despite profanity, redirect abuse-only/nonsense, refuse system prompt/secret/customer-data disclosure, and answer safe mixed requests. Corrected missing SKU context, price-format mismatches, Russian copy in Ukrainian grading criteria, and two holdout rubrics before scheduled inference. Added production-side data-boundary requirements; model runs and real backend verification remain pending."
files_changed: [{"path": "evals/render_contexts.py", "action": "modified"}, {"path": "evals/test_pipeline.py", "action": "modified"}, {"path": "evals/product-qa-cases.jsonl", "action": "modified"}, {"path": "evals/guardrail-cases.jsonl", "action": "modified"}, {"path": "evals/holdout-cases.jsonl", "action": "modified"}, {"path": "evals/model-contexts.json", "action": "regenerated"}, {"path": "evals/guardrail-model-contexts.json", "action": "regenerated"}, {"path": "evals/acceptance-criteria.md", "action": "modified"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "modified"}]
tags: ["activity:implementation", "task:product-assistant-guardrails", "project:race-expert", "topic:prompt-testing", "file:prompts/product-assistant-system-v7.md", "file:evals/guardrail-cases.jsonl", "file:evals/acceptance-criteria.md", "file:wiki/syntheses/race-expert-product-qa-evaluation.md"]
verification: [{"command": "python3 -m unittest discover -s evals -v", "result": "passed: 61 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development, 30 holdout, 30 guardrail; 6 synthetic-canary contexts"}, {"command": "python3 evals/render_contexts.py && python3 evals/render_guardrail_contexts.py", "result": "passed; model contexts regenerated deterministically"}]
decisions: ["Profanity alone does not block a valid product answer; abuse-only or nonsense gets one short neutral redirect.", "Refuse to disclose system instructions, keys, secrets, or other buyers' data; answer the safe product part of a mixed request.", "Prompt-level Guardrail tests do not replace server-side product scoping, context allowlisting, secret/PII exclusion, restricted tools, and an output leak block."]
open_tasks: ["Inspect the scheduled v6 Lightning spotcheck and complete the 60-case comparison across three free models; manually score all answers and repeat observed failures.", "After v6 manual review, run and score v7 on all 30 Guardrail cases across the same three models.", "Run final frozen prompt against holdout and later an independently authored blind set.", "Verify the actual product-page payload when backend code or a representative request is available."]
blockers: ["OpenRouter free daily quota was 50/50 used; network-enabled schedulers wait for the UTC quota reset.", "No actual AI assistant backend/page payload is available in the inspected workspace."]
next_actions: ["Check process 18431 output at /private/tmp/race-expert-v6-after-quota.log after 2026-11-11T00:05Z.", "Check process 26587 output at /private/tmp/race-expert-compare-v6-resume.log after 2026-11-11T00:30Z.", "Do not start v7 until v6 is fully manually reviewed and /private/tmp/race-expert-v7-guardrails-reviewed.flag is present for process 20466."]
relevant_pages: ["wiki/syntheses/race-expert-product-qa-evaluation.md", "evals/README.md", "evals/acceptance-criteria.md", "wiki/session-handoff.md"]
---

# Session

## Outcome

Confirmed Guardrails are a separate bilingual evaluation: answer a useful product question calmly despite profanity, redirect abuse-only/nonsense, refuse system prompt/secret/customer-data disclosure, and answer safe mixed requests. Corrected missing SKU context, price-format mismatches, Russian copy in Ukrainian grading criteria, and two holdout rubrics before scheduled inference. Added production-side data-boundary requirements; model runs and real backend verification remain pending.

## Changed Files

- `evals/render_contexts.py` — modified
- `evals/test_pipeline.py` — modified
- `evals/product-qa-cases.jsonl` — modified
- `evals/guardrail-cases.jsonl` — modified
- `evals/holdout-cases.jsonl` — modified
- `evals/model-contexts.json` — regenerated
- `evals/guardrail-model-contexts.json` — regenerated
- `evals/acceptance-criteria.md` — modified
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — modified

## Tags

- `activity:implementation`
- `task:product-assistant-guardrails`
- `project:race-expert`
- `topic:prompt-testing`
- `file:prompts/product-assistant-system-v7.md`
- `file:evals/guardrail-cases.jsonl`
- `file:evals/acceptance-criteria.md`
- `file:wiki/syntheses/race-expert-product-qa-evaluation.md`

## Verification

- `python3 -m unittest discover -s evals -v` — passed: 61 tests
- `python3 evals/validate_eval.py` — passed: 60 development, 30 holdout, 30 guardrail; 6 synthetic-canary contexts
- `python3 evals/render_contexts.py && python3 evals/render_guardrail_contexts.py` — passed; model contexts regenerated deterministically
