---
id: "session-2026-11-10T21-04-00plus-02-00-require-provenance-in-evaluation-acceptance-gate"
started_at: "2026-11-10T20:50:00+02:00"
ended_at: "2026-11-10T21:04:00+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Require provenance in evaluation acceptance gate"
status: "partial"
transcript_source: "faithful-summary"
summary: "TDD exposed and fixed an acceptance-gate gap: complete synthetic runs without run fingerprints were previously reported as pass. The gate now requires every run row to carry valid lowercase SHA-256 run_fingerprint, prompt_sha256, and context_sha256, and requires a single fingerprint and prompt hash per file; invalid provenance returns incomplete without a quality pass. Updated tests, docs, Wiki synthesis/log, and rebuilt content index. Scheduled model jobs remain live and waiting for quota reset; no inference outputs yet."
files_changed: [{"path": "evals/check_acceptance.py", "action": "updated"}, {"path": "evals/test_acceptance.py", "action": "updated"}, {"path": "evals/README.md", "action": "updated"}, {"path": "evals/acceptance-criteria.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}, {"path": "wiki/log.md", "action": "updated"}, {"path": "wiki/content-index.jsonl", "action": "rebuilt"}, {"path": "wiki/session-handoff.md", "action": "updated"}]
tags: ["activity:implementation", "topic:prompt-testing", "project:race-expert", "file:evals/check_acceptance.py", "file:evals/test_acceptance.py"]
verification: [{"command": "python3 -m unittest evals.test_acceptance", "result": "passed: 14 acceptance tests; RED was observed first for missing fingerprint"}, {"command": "python3 evals/validate_eval.py", "result": "passed: 60 development questions / 30 bilingual pairs and 30 holdout questions / 15 pairs"}, {"command": "python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance", "result": "passed: 43 tests"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .", "result": "passed: indexed 4 content cards"}, {"command": "python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .", "result": "passed"}, {"command": "poll sessions 88742 and 58631", "result": "both remain live; scheduled for 00:05 UTC and 00:30 UTC respectively"}]
decisions: ["Treat invalid or mixed run provenance as incomplete, never as a passing evaluation.", "Leave the v6 prompt and its fixtures unchanged while scheduled inference jobs are pending."]
open_tasks: ["Inspect and manually score the v6 diagnostic responses once generated.", "Complete and manually score the 60-case comparison across three free models.", "Tune the next prompt version from observed errors, retest failures and neighboring cases, then freeze a candidate for holdout.", "Run the frozen candidate on the 30-case holdout, run fallback, and verify acceptance thresholds.", "Prepare and evaluate the independent 60-case blind set after prompt freeze.", "Verify the actual site payload when backend code becomes available."]
blockers: ["Current free-model quota is exhausted until the next UTC window; both scheduled evaluation sessions are sleeping, not failed.", "No product-assistant backend or real page payload is present in the inspected Race Expert workspace."]
next_actions: ["Poll session 88742 after 2026-11-11T00:05:00Z and inspect target output/review files.", "Keep session 58631 alive; it starts the full compare at 00:30 UTC and resumes across quota windows.", "After results appear, validate provenance and coverage, manually score answers, and make the next prompt change."]
relevant_pages: ["evals/check_acceptance.py", "evals/test_acceptance.py", "evals/acceptance-criteria.md", "evals/README.md", "evals/runs/summary-2026-11-10.md", "prompts/product-assistant-system-v6.md", "wiki/syntheses/race-expert-product-qa-evaluation.md"]
---

# Session

## Outcome

TDD exposed and fixed an acceptance-gate gap: complete synthetic runs without run fingerprints were previously reported as pass. The gate now requires every run row to carry valid lowercase SHA-256 run_fingerprint, prompt_sha256, and context_sha256, and requires a single fingerprint and prompt hash per file; invalid provenance returns incomplete without a quality pass. Updated tests, docs, Wiki synthesis/log, and rebuilt content index. Scheduled model jobs remain live and waiting for quota reset; no inference outputs yet.

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

## Verification

- `python3 -m unittest evals.test_acceptance` — passed: 14 acceptance tests; RED was observed first for missing fingerprint
- `python3 evals/validate_eval.py` — passed: 60 development questions / 30 bilingual pairs and 30 holdout questions / 15 pairs
- `python3 -m unittest evals.test_pipeline evals.test_runner evals.test_report evals.test_prepare_review evals.test_acceptance` — passed: 43 tests
- `python3 .agents/skills/llm-wiki-session-memory/scripts/rebuild_content_index.py .` — passed: indexed 4 content cards
- `python3 .agents/skills/llm-wiki-session-memory/scripts/lint_content.py .` — passed
- `poll sessions 88742 and 58631` — both remain live; scheduled for 00:05 UTC and 00:30 UTC respectively
