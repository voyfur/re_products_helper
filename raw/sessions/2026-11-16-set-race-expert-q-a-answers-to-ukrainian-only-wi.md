---
id: "session-2026-11-16T14-39-32plus-02-00-set-race-expert-q-a-answers-to-ukrainian-only-wi"
started_at: "2026-11-16T14:00:00+02:00"
ended_at: "2026-11-16T14:39:32+02:00"
timezone: "Europe/Kiev"
agent: "codex"
task: "Set Race Expert Q&A answers to Ukrainian-only with prompt v12"
status: "completed"
transcript_source: "faithful-summary"
summary: "Created Q&A system prompt v12 requiring Ukrainian answers regardless of question language; kept v11 unchanged. Updated the application default prompt path, expected hash, journal prompt version, Dockerfile, worktree instructions/spec, and the existing journal version expectation. Built and deployed the updated image to the password-protected staging, replacing only the app container and preserving the previous image under a rollback tag. Verified the prompt SHA-256 inside the running container and /health. No automated tests or live OpenAI/Apify calls were run after the change."
files_changed: [{"path": "worktree/prompts/product-assistant-system-v12.md", "action": "created"}, {"path": "worktree/app/assistant.py", "action": "updated"}, {"path": "worktree/app/journal.py", "action": "updated"}, {"path": "worktree/Dockerfile", "action": "updated"}, {"path": "worktree/AGENTS.md", "action": "updated"}, {"path": "worktree/docs/superpowers/specs/2026-11-12-ukrainian-ui-and-ai-language-design.md", "action": "updated"}, {"path": "worktree/tests/test_journal.py", "action": "updated"}, {"path": "prompts/product-assistant-system-v12.md", "action": "created"}, {"path": "AGENTS.md", "action": "updated"}, {"path": "docs/test-harness/site-owner-quick-guide.md", "action": "updated"}, {"path": "docs/test-harness/2026-11-11-user-flow-spec.md", "action": "updated"}, {"path": "wiki/index.md", "action": "updated"}, {"path": "wiki/sources/race-expert-test-harness-runtime.md", "action": "updated"}, {"path": "wiki/sources/race-expert-ai-product-assistant.md", "action": "updated"}, {"path": "wiki/sources/race-expert-review-summary.md", "action": "updated"}, {"path": "wiki/sources/race-expert-staging-deployment.md", "action": "updated"}, {"path": "wiki/sources/mysql-readonly-access-and-product-query-guide.md", "action": "updated"}, {"path": "wiki/syntheses/race-expert-product-qa-evaluation.md", "action": "updated"}]
tags: ["activity:implementation", "task:qa-ukrainian-only-prompt-v12", "project:race-expert", "component:qa", "component:prompt", "component:deployment", "topic:language", "status:completed", "file:worktree/app/assistant.py", "file:worktree/app/journal.py", "file:worktree/prompts/product-assistant-system-v12.md", "file:worktree/Dockerfile", "file:worktree/AGENTS.md", "file:worktree/tests/test_journal.py", "file:wiki/sources/race-expert-test-harness-runtime.md", "file:wiki/sources/race-expert-staging-deployment.md"]
decisions: ["Q&A replies are always Ukrainian, independent of question language; active prompt is v12 and v11 stays unchanged for historical results.", "Keep one GPT call with no local language classifier; review texts remain outside Q&A.", "Staging update replaced only the app container; rollback tag is raceexpert-test-harness:rollback-before-uk-qa-v12-20261116."]
open_tasks: ["No live GPT request was made after deployment; verify a Russian-language question on staging only if the user asks for a live behavior check."]
next_actions: ["Continue from prompt v12 and the deployed staging. Do not describe the language behavior as live-model-tested until a post-deployment Q&A call is run."]
relevant_pages: ["wiki/sources/race-expert-test-harness-runtime.md", "wiki/sources/race-expert-staging-deployment.md", "wiki/sources/race-expert-ai-product-assistant.md", "wiki/session-handoff.md"]
verification: [{"command": "shasum -a 256 worktree/prompts/product-assistant-system-v12.md", "result": "matched expected SHA-256 d5d7f11bdc65abe95d6549f8d438153fc6e46b35ef5d16ca69a2d0b4468a41b2 and project-root copy"}, {"command": "SSH inspection of running staging container prompt hash and GET /health", "result": "prompt hash matched; /health returned {\"status\":\"ok\"}; previous image retained under rollback tag"}, {"command": "Automated test suite and live Q&A provider call", "result": "not run; no tests or post-deployment OpenAI/Apify calls were requested or made"}]
---

# Session

## Outcome

Created Q&A system prompt v12 requiring Ukrainian answers regardless of question language; kept v11 unchanged. Updated the application default prompt path, expected hash, journal prompt version, Dockerfile, worktree instructions/spec, and the existing journal version expectation. Built and deployed the updated image to the password-protected staging, replacing only the app container and preserving the previous image under a rollback tag. Verified the prompt SHA-256 inside the running container and /health. No automated tests or live OpenAI/Apify calls were run after the change.

## Changed Files

- `worktree/prompts/product-assistant-system-v12.md` — created
- `worktree/app/assistant.py` — updated
- `worktree/app/journal.py` — updated
- `worktree/Dockerfile` — updated
- `worktree/AGENTS.md` — updated
- `worktree/docs/superpowers/specs/2026-11-12-ukrainian-ui-and-ai-language-design.md` — updated
- `worktree/tests/test_journal.py` — updated
- `prompts/product-assistant-system-v12.md` — created
- `AGENTS.md` — updated
- `docs/test-harness/site-owner-quick-guide.md` — updated
- `docs/test-harness/2026-11-11-user-flow-spec.md` — updated
- `wiki/index.md` — updated
- `wiki/sources/race-expert-test-harness-runtime.md` — updated
- `wiki/sources/race-expert-ai-product-assistant.md` — updated
- `wiki/sources/race-expert-review-summary.md` — updated
- `wiki/sources/race-expert-staging-deployment.md` — updated
- `wiki/sources/mysql-readonly-access-and-product-query-guide.md` — updated
- `wiki/syntheses/race-expert-product-qa-evaluation.md` — updated

## Tags

- `activity:implementation`
- `task:qa-ukrainian-only-prompt-v12`
- `project:race-expert`
- `component:qa`
- `component:prompt`
- `component:deployment`
- `topic:language`
- `status:completed`
- `file:worktree/app/assistant.py`
- `file:worktree/app/journal.py`
- `file:worktree/prompts/product-assistant-system-v12.md`
- `file:worktree/Dockerfile`
- `file:worktree/AGENTS.md`
- `file:worktree/tests/test_journal.py`
- `file:wiki/sources/race-expert-test-harness-runtime.md`
- `file:wiki/sources/race-expert-staging-deployment.md`

## Verification

- `shasum -a 256 worktree/prompts/product-assistant-system-v12.md` — matched expected SHA-256 d5d7f11bdc65abe95d6549f8d438153fc6e46b35ef5d16ca69a2d0b4468a41b2 and project-root copy
- `SSH inspection of running staging container prompt hash and GET /health` — prompt hash matched; /health returned {"status":"ok"}; previous image retained under rollback tag
- `Automated test suite and live Q&A provider call` — not run; no tests or post-deployment OpenAI/Apify calls were requested or made
