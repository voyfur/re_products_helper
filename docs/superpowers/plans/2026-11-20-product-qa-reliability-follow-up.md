# Product Q&A Reliability Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Prevent unsupported off-topic answers and personal dosing guidance, give the model an explicit backend-verified product identity for accepted evidence, and make catalog readiness observable.

**Architecture:** Add prompt v14 without editing v12 or v13. Use a structured product-relevance decision plus a deterministic guard for clearly off-topic and personal-health requests; return fixed Ukrainian buyer-safe responses before search where the answer is known. Preserve the existing allowlist and exact-title/path filter, but attach the selected card's verified display name to compact model evidence. Add a private readiness endpoint that performs read-only `SELECT 1`; keep `/health` as process liveness.

**Tech Stack:** Python 3.12, FastAPI, OpenAI Responses API strict JSON schema, Tavily evidence filter, SQLite attempt journal, pytest.

---

## Evidence and acceptance criteria

The 2026-11-20 live report recorded 21/50 answers to explicitly unrelated questions, 41/50 personal-health answers that repeated label quantities despite a disclaimer, 217 Tavily calls with five name-matched source records but no positively confirmed exact-variant fact, and a local SQL tunnel loss that left `/health` green while catalog calls returned `catalog_unavailable`.

The work is accepted when:

1. Explicitly off-topic questions receive a short Ukrainian product redirect without a model or Tavily call. For uncued questions, the structured model decision must include `product_related`; any missing or false value fails closed to the same redirect.
2. Personal health, condition, medication, pregnancy, child, allergy, or individualized-dose questions receive a fixed Ukrainian safety response with the existing disclaimer and no product quantity/dose. A non-personal factual label question remains eligible for the normal card/search path.
3. An accepted exact-product search excerpt reaches the final model together with the backend-verified card display name. The model payload still contains no source title, URL, or domain. Wrong flavor/size and unapproved-host results remain excluded.
4. `/health` remains liveness. `/ready` returns `200 {"status":"ready"}` only after a read-only catalog connection check and `503 {"status":"unavailable"}` when the catalog cannot be reached.
5. The active journal prompt version is v14; v12 and v13 prompt files and their existing hashes remain unchanged. Buyer API serialization remains free of search metadata.
6. Focused tests and the full offline suite pass. No live API, MySQL, staging, storefront, or deployment call is part of this plan.

## Files

- Create `prompts/product-assistant-system-v14.md`.
- Modify `app/assistant.py` for prompt activation, scope and personal-health gates, and safe responses.
- Modify `app/openai_client.py` for required structured `product_related` fields in direct and final model responses and search tool arguments.
- Modify `app/search_evidence.py` so compact evidence carries a backend-verified product display name, without exposing provenance.
- Modify `app/main.py` to add the internal `/ready` route while keeping it out of the public OpenAPI contract.
- Modify `app/journal.py` to record v14 on new attempts.
- Extend `tests/test_web_search.py`, `tests/test_search_evidence.py`, and `tests/test_qa_app.py` with failing-first regression cases.
- Update `AGENTS.md` and `wiki/syntheses/race-expert-qa-evaluation.md` to name the active prompt and the new guardrails; update `wiki/session-handoff.md` with verified remaining work.

## Tasks

### Task 1: Fail closed on off-topic questions

**Files:** `app/assistant.py`, `app/openai_client.py`, `prompts/product-assistant-system-v14.md`, `tests/test_web_search.py`.

- [x] Add tests proving a direct model result with `product_related=false` is replaced with the fixed redirect, does not call Tavily, and does not expose the model's off-topic answer.
- [x] Add tests proving an explicit cue such as `Не про цей товар: яка столиця Японії?` is redirected before `provider.decide()`.
- [x] Add tests proving a search-tool request with `product_related=false`, a missing value, or a malformed value does not invoke Tavily.
- [x] Run `pytest tests/test_web_search.py -q`; confirm each new behavior test fails for the expected missing scope gate.
- [x] Add `product_related: bool` as a required strict field to direct answers, final answers, and `request_product_search` arguments. Parse missing/invalid values as a sanitized provider error or fail-closed false; never treat them as true.
- [x] Add an explicit off-topic cue detector for Russian, Ukrainian, and English forms used by the live test set. Return `OUT_OF_SCOPE_ANSWER` before model/search when the question explicitly says it is unrelated.
- [x] If a model direct answer or final answer sets `product_related=false`, replace its text with `OUT_OF_SCOPE_ANSWER`.
- [x] Create prompt v14 instructions that say not to answer general knowledge, translation, math, or unrelated topics; return only the structured scope flag, and let the backend supply the redirect.
- [x] Re-run `pytest tests/test_web_search.py -q`; expect all tests to pass.

### Task 2: Suppress dosage in personal-health scenarios

**Files:** `app/assistant.py`, `prompts/product-assistant-system-v14.md`, `tests/test_web_search.py`.

- [x] Add tests for pregnancy, medication/condition, under-18, allergy, and personalized-dose wording. Assert a fixed refusal plus disclaimer, zero model calls, zero search calls, and no dose amount copied from the product context.
- [x] Add a control test showing `Який розмір порції вказано на етикетці?` still reaches the normal answer path.
- [x] Run the focused new tests and confirm they fail because `AssistantService.submit()` currently forwards those questions to the model.
- [x] Add a conservative multilingual personal-health intent helper. It must match personal condition/medication/pregnancy/child/allergy context and individualized-dose requests, but not a plain factual label question.
- [x] Before calling the model, complete a matched attempt with a fixed Ukrainian refusal, the existing health disclaimer, `search_status="skipped"`, and timings. Do not include any catalog serving quantity in this response.
- [x] Add v14 instructions that distinguish personal health advice from a neutral label-fact request and forbid repeating label quantities in the personal-advice refusal.
- [x] Re-run focused tests and verify the product-label control remains answerable.

### Task 3: Pass backend-verified product identity with evidence

**Files:** `app/search_evidence.py`, `prompts/product-assistant-system-v14.md`, `tests/test_search_evidence.py`, `tests/test_web_search.py`.

- [x] Add a regression test using an exact `NUTREND Enduro Orange 700 ml` result and assert model evidence includes `verified_product_name` equal to the selected Ukrainian card name.
- [x] Assert model evidence contains only `source_type`, `verified_product_name`, and sanitized `excerpt`; assert no title, URL, hostname, or provenance field appears.
- [x] Keep and extend the wrong-flavor and wrong-capacity tests to prove those results still yield an empty evidence bundle.
- [x] Run `pytest tests/test_search_evidence.py tests/test_web_search.py -q`; confirm the new identity assertion fails before implementation.
- [x] Add `verified_product_name` to `ModelEvidence` and its compact payload. Populate it only after the existing allowlist and exact product-name/variant title-or-path validation accepts the result.
- [x] Update v14 to explain that this field confirms source-page identity only; the excerpt must still support the requested fact, and conflicting or missing variant evidence must remain unverified.
- [x] Re-run focused tests and verify buyer-facing API and SQLite provenance fields remain unchanged.

### Task 4: Expose catalog readiness separately from liveness

**Files:** `app/main.py`, `tests/conftest.py`, `tests/test_qa_app.py`, `docs/test-harness/local-session-runbook.md`.

- [x] Add tests asserting `/health` remains `{"status":"ok"}`, `/ready` returns `{"status":"ready"}` when `SELECT 1` succeeds, and `/ready` returns only `{"status":"unavailable"}` with HTTP 503 when opening/checking the catalog fails.
- [x] Run `pytest tests/test_qa_app.py -q`; confirm the readiness tests fail because `/ready` is not registered.
- [x] Implement `/ready` with a read-only `SELECT 1`, close its cursor/connection in `finally`, log only sanitized catalog failure metadata, and set `include_in_schema=False` so the site API contract is unchanged.
- [x] Update the local-session runbook to check `/ready` during long QA runs and explain that `/health` is process liveness only.
- [x] Re-run `pytest tests/test_qa_app.py -q` and verify ready/unavailable behavior.

### Task 5: Activate v14, update memory, and verify the complete change

**Files:** `app/assistant.py`, `app/journal.py`, `AGENTS.md`, `wiki/syntheses/race-expert-qa-evaluation.md`, `wiki/session-handoff.md`, `tests/test_web_search.py`, `tests/test_journal.py`.

- [x] Add tests that default prompt loading selects v14, v12 and v13 files still load with their existing content hashes, and new journal attempts store `prompt_version="v14"`.
- [x] Run the focused prompt/journal tests and confirm the new expectations fail before activation.
- [x] Add v14 to `PROMPT_PATHS` and `EXPECTED_PROMPT_HASHES`, compute its SHA-256 from the final file, set it as `DEFAULT_PROMPT_VERSION`, and set the journal's new-attempt version to v14. Keep v12 and v13 constants/files unchanged.
- [x] Update `AGENTS.md` and the evaluation synthesis to describe v14 scope, personal-health behavior, exact-source identity context, and preserved v12/v13 history. Update the handoff with test results and unresolved live source coverage.
- [x] Run the focused tests for search evidence, assistant, prompt loading, journal, API privacy, and readiness; then run `pytest -q` for the complete offline suite.
- [x] Run the repository's existing Wiki index/lint commands only if a Wiki card/log/index was changed. Do not read `.env`, connect to MySQL, call Tavily/OpenAI, or deploy.
- [x] Review the targeted implementation files and verify prompt v12/v13 hashes are unchanged; this workspace has no Git metadata, so a VCS diff is unavailable.

## Execution note

Execute inline with `superpowers:executing-plans`; subagent delegation is unavailable in this session. The current workspace has no Git metadata, so use the provided project directory in place and do not attempt a commit or claim a clean Git diff.

## Completion record

- Offline verification: `.venv/bin/pytest -q` — 168 passed, 4009 subtests passed.
- Wiki verification: 4 content cards indexed; `lint_content.py` passed.
- Prompt hashes verified from disk: v12 `d5d7f11bdc65abe95d6549f8d438153fc6e46b35ef5d16ca69a2d0b4468a41b2`, v13 `d845e2278a11c3cf62f7ceb48d70fca808f026454d2d3a52729f0d6ea354e7c7`, v14 `c78822fcec4d4148099dbce6a8fce54c447750594f65f3d3ef9506ca46d772a6`.
- No `.env` was read; no database, OpenAI, or Tavily calls, staging, storefront integration, or deployment occurred.
- The workspace has no Git metadata; the listed files were reviewed directly, and no VCS diff or clean-tree claim is available.
