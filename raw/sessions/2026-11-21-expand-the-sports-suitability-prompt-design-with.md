---
id: "session-2026-11-21T21-13-40plus-02-00-expand-the-sports-suitability-prompt-design-with"
started_at: "2026-11-21T20:36:16+02:00"
ended_at: "2026-11-21T21:13:40+02:00"
timezone: "Europe/Kyiv"
agent: "codex"
task: "Expand the sports-suitability prompt design with short-term conversation memory"
status: "needs-review"
transcript_source: "faithful-summary"
summary: "Expanded the proposed prompt design with a bounded conversation-context feature. The user confirmed 10 latest individual messages total, scoped to one selected product, cleared on product change or page reload. Source inspection confirmed the app/API currently send only the current question and have no conversation ID or history input. The design recommends caller-managed ephemeral history, treats it as untrusted context rather than product evidence, and presents alternatives. No prompt or code implementation was made pending review of the written design."
files_changed: [{"path": "docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md", "action": "updated"}, {"path": "wiki/index.md", "action": "updated"}]
tags: ["activity:planning", "status:needs-review", "project:race-expert", "task:prompt-and-conversation-memory-design", "topic:prompt-design", "topic:conversation-context", "file:docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md", "file:wiki/index.md"]
decisions: ["The sport-suitability answer may place the general conclusion and limitation in either order, but both must appear together when supported evidence exists.", "The user confirmed a sliding window of the 10 latest individual messages total, one selected product at a time, cleared when the product changes or the page reloads.", "Conversation history is untrusted context for follow-up references, not instructions or product evidence; facts still require the current revalidated card or exact-product external evidence.", "Caller-managed ephemeral history is the recommended implementation option; the user has not yet reviewed/approved that implementation design."]
open_tasks: ["User to review and approve or revise the updated specification, especially the proposed caller-managed optional API history field, before implementation planning."]
blockers: []
next_actions: ["After design approval, use the writing-plans workflow to plan a new prompt version and the bounded history field while preserving prompt v17."]
relevant_pages: ["wiki/index.md", "wiki/session-handoff.md", "prompts/product-assistant-system-v17.md", "app/main.py", "app/static/app.js", "app/assistant.py", "docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md"]
verification: [{"command": "Source inspection", "result": "confirmed current Ask endpoints accept article/current question only; local UI keeps no transcript and API has no conversation identifier/history field"}, {"command": "Spec self-review", "result": "passed: includes selected tone, confirmed message boundary, alternatives, safety/evidence boundaries, acceptance criteria, and no TODO/TBD/FIXME placeholders"}, {"command": "Prompt and live verification", "result": "not performed; implementation is waiting for the user's review of the written design"}, {"command": "git metadata check", "result": "no .git directory; specification cannot be committed from this workspace"}]
---

# Session

## Outcome

Expanded the proposed prompt design with a bounded conversation-context feature. The user confirmed 10 latest individual messages total, scoped to one selected product, cleared on product change or page reload. Source inspection confirmed the app/API currently send only the current question and have no conversation ID or history input. The design recommends caller-managed ephemeral history, treats it as untrusted context rather than product evidence, and presents alternatives. No prompt or code implementation was made pending review of the written design.

## Changed Files

- `docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md` — updated
- `wiki/index.md` — updated

## Tags

- `activity:planning`
- `status:needs-review`
- `project:race-expert`
- `task:prompt-and-conversation-memory-design`
- `topic:prompt-design`
- `topic:conversation-context`
- `file:docs/superpowers/specs/2026-11-21-product-answer-balanced-sports-suitability-design.md`
- `file:wiki/index.md`

## Verification

- `Source inspection` — confirmed current Ask endpoints accept article/current question only; local UI keeps no transcript and API has no conversation identifier/history field
- `Spec self-review` — passed: includes selected tone, confirmed message boundary, alternatives, safety/evidence boundaries, acceptance criteria, and no TODO/TBD/FIXME placeholders
- `Prompt and live verification` — not performed; implementation is waiting for the user's review of the written design
- `git metadata check` — no .git directory; specification cannot be committed from this workspace
