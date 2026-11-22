---
id: "session-2026-11-10T23-15-12plus-02-00-audit-bilingual-evaluation-rubrics-and-context-f"
started_at: "2026-11-10T23:04:00+02:00"
ended_at: "2026-11-10T23:15:12+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Audit bilingual evaluation rubrics and context facts"
status: "partial"
transcript_source: "faithful-summary"
summary: "Audited the complete base, holdout, and Guardrail datasets before scheduled inference. Localized manual scoring criteria, corrected remaining Ukrainian grading phrases, and added numeric must_cover-to-context validation so a case cannot demand a number absent from its product-language context. The validator now rejects a deliberately injected missing numeric fact; the full suites contain 60/30/30 bilingual cases and pass 64 unit tests. Scheduled free-model runs remain pending; real backend payload remains unavailable."
files_changed: [{"path": "evals/product-qa-cases.jsonl", "action": "modified"}, {"path": "evals/holdout-cases.jsonl", "action": "modified"}, {"path": "evals/validate_eval.py", "action": "modified"}, {"path": "evals/test_pipeline.py", "action": "modified"}, {"path": "evals/README.md", "action": "modified"}, {"path": "docs/superpowers/specs/2026-11-10-product-assistant-guardrails-design.md", "action": "modified"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "modified"}]
tags: ["activity:implementation", "task:product-assistant-evaluation", "project:race-expert", "topic:prompt-testing", "file:evals/validate_eval.py", "file:evals/product-qa-cases.jsonl", "file:evals/holdout-cases.jsonl", "file:evals/test_pipeline.py", "file:evals/README.md"]
verification: [{"command": "python3 -m unittest discover -s evals -v", "result": "passed: 64 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development, 30 holdout, 30 guardrail cases and six canary contexts"}, {"command": "numeric must_cover/context audit across all three suites", "result": "zero required-number/context mismatches"}, {"command": "dataset counts by product/language", "result": "base 20/product and 10/language; holdout and guardrail 10/product and 5/language"}]
decisions: ["All manual must_cover criteria should use the case language except product names, identifiers, and standard abbreviations.", "Validator checks that numeric must_cover values exist in the matching product-language context; human review still checks meaning and units.", "v6 prompt, contexts, and cases are frozen after all pre-inference corrections; model comparison uses the three free models."]
open_tasks: ["Inspect v6 Lightning spotcheck and complete the 60-case three-model comparison; manually score outputs and repeat failures.", "After v6 manual scoring, run and score v7 over the separate 30-case Guardrail set on the same three free models.", "Freeze the final prompt before using current holdout and creating an independently authored blind set.", "Verify the real product-page payload when assistant backend code or a representative request becomes available."]
blockers: ["OpenRouter free-model quota was exhausted at the last preflight; scheduled processes wait for UTC reset.", "No AI assistant backend or representative page payload is in the inspected workspace."]
next_actions: ["Process 18431 should start the Lightning spotcheck at 2026-11-11T00:05Z; inspect /private/tmp/race-expert-v6-after-quota.log.", "Process 26587 should start full v6 comparison at 2026-11-11T00:30Z; inspect /private/tmp/race-expert-compare-v6-resume.log and let it resume across quota windows.", "Process 20466 should run v7 only after full v6 manual review and /private/tmp/race-expert-v7-guardrails-reviewed.flag."]
relevant_pages: ["wiki/syntheses/race-expert-product-qa-evaluation.md", "evals/acceptance-criteria.md", "evals/README.md", "wiki/session-handoff.md"]
---

# Session

## Outcome

Audited the complete base, holdout, and Guardrail datasets before scheduled inference. Localized manual scoring criteria, corrected remaining Ukrainian grading phrases, and added numeric must_cover-to-context validation so a case cannot demand a number absent from its product-language context. The validator now rejects a deliberately injected missing numeric fact; the full suites contain 60/30/30 bilingual cases and pass 64 unit tests. Scheduled free-model runs remain pending; real backend payload remains unavailable.

## Changed Files

- `evals/product-qa-cases.jsonl` — modified
- `evals/holdout-cases.jsonl` — modified
- `evals/validate_eval.py` — modified
- `evals/test_pipeline.py` — modified
- `evals/README.md` — modified
- `docs/superpowers/specs/2026-11-10-product-assistant-guardrails-design.md` — modified
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — modified

## Tags

- `activity:implementation`
- `task:product-assistant-evaluation`
- `project:race-expert`
- `topic:prompt-testing`
- `file:evals/validate_eval.py`
- `file:evals/product-qa-cases.jsonl`
- `file:evals/holdout-cases.jsonl`
- `file:evals/test_pipeline.py`
- `file:evals/README.md`

## Verification

- `python3 -m unittest discover -s evals -v` — passed: 64 tests
- `python3 evals/validate_eval.py` — passed: 60 development, 30 holdout, 30 guardrail cases and six canary contexts
- `numeric must_cover/context audit across all three suites` — zero required-number/context mismatches
- `dataset counts by product/language` — base 20/product and 10/language; holdout and guardrail 10/product and 5/language
