---
id: "session-2026-11-11T14-43-48plus-02-00-draft-the-gpt-6-luna-v8-prompt-design"
started_at: "2026-11-11T14:30:00+02:00"
ended_at: "2026-11-11T14:43:48+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Draft the GPT-6 Luna v8 prompt design"
status: "needs-review"
transcript_source: "faithful-summary"
summary: "The user selected prompt plus evaluation as the current result and approved a focused v8 design based on v7. Current run artifacts verify 60/60 GPT-6 Luna v6 responses, regression acceptance pass, mean 7.95/8, and zero critical failures. Two observed shortcomings are an answer mostly in Russian to a Ukrainian question and omission of the known 32 g serving in one numeric abstention. The workspace contains no product-assistant application/backend source. A design spec was written and self-reviewed; no prompt changes or model runs were made pending user review of the written spec."
files_changed: [{"path": "docs/superpowers/specs/2026-11-11-gpt-6-luna-product-assistant-v8-design.md", "action": "created"}]
tags: ["activity:planning", "status:needs-review", "task:gpt-6-luna-v8-design", "project:race-expert", "topic:prompt-evaluation", "topic:openai-api", "topic:manual-scoring", "topic:backend-payload", "file:docs/superpowers/specs/2026-11-11-gpt-6-luna-product-assistant-v8-design.md"]
verification: [{"command": "Current v6 GPT-6 Luna artifacts inspected", "result": "60/60 answered; regression acceptance pass; 7.95/8; zero critical failures"}, {"command": "Current app/backend source inventory", "result": "zero application source files found outside eval tooling"}, {"command": "Prompt design self-review", "result": "checked scope, holdout boundary, model request settings, placeholders, and backend completion boundary"}]
decisions: ["Use GPT-6 Luna for the product assistant prompt and evaluation work.", "Build v8 from v7, preserving guardrails and adding only language consistency and numeric-abstention clarifications.", "Use Responses API with store=false and omit temperature because GPT-6 Luna rejected temperature=0; record the model-default sampling profile.", "Do not claim live integration without actual backend/runtime evidence; do not call the current holdout an independent blind test."]
open_tasks: ["User review of docs/superpowers/specs/2026-11-11-gpt-6-luna-product-assistant-v8-design.md.", "After spec approval, create the implementation plan, author v8, run regression, then freeze and run holdout and guardrails on GPT-6 Luna.", "Obtain actual backend source or runtime trace for live integration verification.", "Obtain an independently authored 60-case blind set before claiming the independent blind gate."]
blockers: ["No product-assistant backend/application source or runtime payload exists in the current workspace.", "No independent author or independent blind test set is available in the workspace."]
next_actions: ["Review or revise the v8 design spec; after approval, write the execution plan and implement the prompt version."]
relevant_pages: ["wiki/index.md", "wiki/session-handoff.md", "wiki/syntheses/race-expert-product-qa-evaluation.md", "prompts/product-assistant-system-v6.md", "prompts/product-assistant-system-v7.md", "evals/README.md", "evals/scoring-rubric.md", "evals/acceptance-criteria.md", "docs/superpowers/specs/2026-11-11-gpt-6-luna-product-assistant-v8-design.md"]
---

# Session

## Outcome

The user selected prompt plus evaluation as the current result and approved a focused v8 design based on v7. Current run artifacts verify 60/60 GPT-6 Luna v6 responses, regression acceptance pass, mean 7.95/8, and zero critical failures. Two observed shortcomings are an answer mostly in Russian to a Ukrainian question and omission of the known 32 g serving in one numeric abstention. The workspace contains no product-assistant application/backend source. A design spec was written and self-reviewed; no prompt changes or model runs were made pending user review of the written spec.

## Changed Files

- `docs/superpowers/specs/2026-11-11-gpt-6-luna-product-assistant-v8-design.md` — created

## Tags

- `activity:planning`
- `status:needs-review`
- `task:gpt-6-luna-v8-design`
- `project:race-expert`
- `topic:prompt-evaluation`
- `topic:openai-api`
- `topic:manual-scoring`
- `topic:backend-payload`
- `file:docs/superpowers/specs/2026-11-11-gpt-6-luna-product-assistant-v8-design.md`

## Verification

- `Current v6 GPT-6 Luna artifacts inspected` — 60/60 answered; regression acceptance pass; 7.95/8; zero critical failures
- `Current app/backend source inventory` — zero application source files found outside eval tooling
- `Prompt design self-review` — checked scope, holdout boundary, model request settings, placeholders, and backend completion boundary
