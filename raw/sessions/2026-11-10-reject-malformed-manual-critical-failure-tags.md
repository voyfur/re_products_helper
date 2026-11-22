---
id: "session-2026-11-10T21-59-00plus-02-00-reject-malformed-manual-critical-failure-tags"
started_at: "2026-11-10T21:54:00+02:00"
ended_at: "2026-11-10T21:59:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Reject malformed manual critical-failure tags"
status: "partial"
transcript_source: "faithful-summary"
summary: "Hardened manual-score validation after a regression test showed that a list-valued critical_failure_tag could crash report generation with TypeError, while blank and duplicate tags were accepted. Acceptance now requires unique, nonempty string tags and rejects malformed annotation before aggregation. Full evaluation suite passed 49 tests; dataset validation passed. Updated scoring and acceptance documentation, rebuilt and linted the Wiki content index. Both model runs remain live and waiting for the UTC quota reset; prompt/context/case inputs are unchanged. The nine-point goal remains active."
files_changed: [{"path": "evals/check_acceptance.py", "action": "updated"}, {"path": "evals/test_acceptance.py", "action": "updated"}, {"path": "evals/scoring-rubric.md", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "evals/acceptance-criteria.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/log.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:implementation", "topic:prompt-testing", "project:race-expert", "file:evals/check_acceptance.py", "file:evals/test_acceptance.py", "file:evals/scoring-rubric.md"]
verification: [{"command": "python3 -m unittest evals.test_acceptance.AcceptanceTests.test_acceptance_rejects_malformed_critical_failure_tags", "result": "failed before the production change; malformed tags are rejected after"}, {"command": "python3 -m unittest discover -s evals -v", "result": "passed: 49 tests"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development cases / 30 pairs; 30 holdout cases / 15 pairs"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .", "result": "passed: indexed 4 cards"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed"}, {"command": "poll inference sessions 88742 and 58631", "result": "both remained live and waiting; scheduled starts are 2026-11-11T00:05Z and 00:30Z"}]
decisions: ["Manual critical_failure_tags must be unique, nonempty strings; use [] when no critical error is present.", "Compare acceptance requires the explicit expected-model list; run-row metadata must match the canonical selected case.", "Keep prompt, context, and case inputs unchanged until scheduled model runs finish."]
open_tasks: ["Inspect and manually score v6 target outputs after the quota reset.", "Complete and score the same 60-case comparison on three free models.", "Tune the prompt from observed failures and repeat failed plus neighboring cases.", "Run frozen-candidate holdout fallback and prepare an independent blind set after prompt freeze.", "Verify the real product-page payload when backend code or a representative request becomes available."]
blockers: ["The OpenRouter free-model daily quota is exhausted; both inference processes remain live and scheduled after reset.", "The product-assistant backend/payload is absent from the inspected workspace, so real-page context verification cannot yet be completed."]
next_actions: ["Poll session 88742 after 2026-11-11T00:05Z and inspect its run and review queue.", "Keep session 58631 alive through its 2026-11-11T00:30Z start and its resumable quota windows.", "Verify run provenance and coverage, score outputs, and tune prompt only from observed failures."]
relevant_pages: ["evals/check_acceptance.py", "evals/test_acceptance.py", "evals/scoring-rubric.md", "evals/acceptance-criteria.md", "evals/README.md", "wiki/syntheses/race-expert-product-qa-evaluation.md", "prompts/product-assistant-system-v6.md"]
---

# Session

## Outcome

Hardened manual-score validation after a regression test showed that a list-valued critical_failure_tag could crash report generation with TypeError, while blank and duplicate tags were accepted. Acceptance now requires unique, nonempty string tags and rejects malformed annotation before aggregation. Full evaluation suite passed 49 tests; dataset validation passed. Updated scoring and acceptance documentation, rebuilt and linted the Wiki content index. Both model runs remain live and waiting for the UTC quota reset; prompt/context/case inputs are unchanged. The nine-point goal remains active.

## Changed Files

- `evals/check_acceptance.py` — updated
- `evals/test_acceptance.py` — updated
- `evals/scoring-rubric.md` — updated
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
- `file:evals/scoring-rubric.md`

## Verification

- `python3 -m unittest evals.test_acceptance.AcceptanceTests.test_acceptance_rejects_malformed_critical_failure_tags` — failed before the production change; malformed tags are rejected after
- `python3 -m unittest discover -s evals -v` — passed: 49 tests
- `python3 evals/validate_eval.py` — passed: 60 development cases / 30 pairs; 30 holdout cases / 15 pairs
- `python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .` — passed: indexed 4 cards
- `python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed
- `poll inference sessions 88742 and 58631` — both remained live and waiting; scheduled starts are 2026-11-11T00:05Z and 00:30Z
