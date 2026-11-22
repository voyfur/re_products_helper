# Product QA Evaluation Pack Implementation Plan

> **For agentic workers:** Execute inline in this Codex session. Steps use checkbox syntax for tracking.

**Goal:** Create a reusable bilingual evaluation pack for three verified product snapshots, compare free OpenRouter models on an initial batch, and improve the system prompt from observed failures.

**Architecture:** Keep product facts in a compact fixture file, test cases in JSONL, the system prompt in a versioned Markdown file, and scores/results in a run record. Select only currently listed text models with zero prompt and completion price; never store or print the API key.

**Tech Stack:** Markdown, JSON, JSONL, Python 3 standard library, OpenRouter Chat Completions API.

---

### Task 1: Create evaluation inputs

**Files:**
- Create: `prompts/product-assistant-system-v0.md`
- Create: `evals/product-contexts.json`
- Create: `evals/product-qa-cases.jsonl`
- Create: `evals/scoring-rubric.md`
- Create: `evals/README.md`

- [x] Include 20 cases per product and 10 cases per language per product.
- [x] Keep expected answers and failure conditions grounded in the saved product snapshots.
- [x] Validate JSON, JSONL line count, IDs, and language distribution with Python 3.

### Task 2: Run the initial comparison

**Files:**
- Create: `evals/runs/round-01-2026-11-10.md`
- Create: `raw/sources/openrouter-product-qa-eval-round-01-2026-11-10.md`

- [x] Choose three text-in/text-out `:free` models from OpenRouter's live catalog and verify prompt/completion prices are zero; the read-only preflight passed on 2026-11-10.
- [ ] Run the same six representative cases against each available model, preserving the same prompt and product context. The common v3 batch covered four cases; the full same-set comparison remains in Point 6.
- [x] Record provider errors and empty answers separately from answer quality; never store the key.

### Task 3: Review and refine the prompt

**Files:**
- Create: `prompts/product-assistant-system-v1.md`
- Modify: `evals/runs/round-01-2026-11-10.md`

- [x] Score all answerable responses using `evals/scoring-rubric.md`; empty/provider-error results remain unscored.
- [x] Change the prompt only to address observed failure patterns.
- [x] Re-run failed or borderline cases on available free models and record the before/after comparison.

### Task 4: Add durable project memory

**Files:**
- Create: `wiki/syntheses/race-expert-product-qa-evaluation.md`
- Modify: `wiki/index.md`
- Modify: `wiki/source-manifest.md`
- Modify: `wiki/log.md`
- Modify: `wiki/session-handoff.md`
- Regenerate: `wiki/content-index.jsonl` and session memory using the project Wiki scripts.

- [x] Record the prompt version, evaluated cases, model availability, results, limitations, and next batch.
- [x] Run JSON/JSONL validation, Wiki content lint, and memory lint. No new raw external source was added, so `wiki/source-manifest.md` did not need a new entry.

---

## Phase II: Raise preparation and verification to release quality

### Point 1: Freeze development set and create a held-out set

- [x] Keep the original 60 cases as the development/regression set.
- [x] Add 30 new RU/UA holdout cases, balanced as 5 bilingual pairs per product.
- [x] Record that this holdout was created in the same workstream and is not an independent blind test.
- [x] Audit the effective sample size: 30 holdout outputs represent 15 paired RU/UA scenarios, five per product; the current 29/30 threshold is an output-level gate.
- [ ] Keep holdout results out of prompt tuning after the candidate is frozen; create a separately authored holdout for a strict blind score.
- [ ] For the final blind 10/10 gate, prepare 60 outputs from 30 paired RU/UA scenarios, ten unique scenarios per product, authored independently after prompt freeze.

### Point 2: Generate readable contexts deterministically

- [x] Build localized text contexts from the structured product fixture.
- [x] Verify stable output, coverage of key facts, historical notes, and absence of internal JSON field names.
- [x] Review every rendered statement against its source fixture and raw source; add the omitted DigeZyme per-100-g value.

### Point 3: Add a reusable runner with retries and fallback

- [x] Add compare mode and fallback mode, retrying transient errors and increasing token limit after truncation.
- [x] Verify each requested model is currently text-in/text-out and zero-priced before inference.
- [x] Keep output resumable only when run fingerprint matches; avoid writing API credentials.
- [x] Stop on daily free quota exhaustion without retries or cross-model calls.
- [x] Cap each invocation by the live `free_model_daily_requests.remaining` value from OpenRouter `GET /api/v1/key`; stop before inference at zero and resume later with the same fingerprint.

### Point 4: Validate datasets and report evaluation results

- [x] Validate IDs, language/product balance, pairs, contexts, and source references.
- [x] Add a review queue, structured manual scores, and an aggregate report by model, prompt, product, language, and failure category.
- [x] Add a pass/fail/incomplete acceptance checker with separate quality and availability gates for regression, holdout, and blind profiles.
- [x] Add a separate 30-question bilingual guardrail set and a matching acceptance profile for abuse, off-topic nonsense, prompt/secret extraction, and customer-data requests.
- [x] Add isolated synthetic canary contexts and an automatic acceptance check that fails on canary echoes; no actual credentials or customer data are used.

### Point 5: Define acceptance thresholds

- [x] Write explicit quality, critical-failure, language-balance, and availability gates before the final holdout run.
- [x] Mark the existing held-out set as non-independent because it was authored in the prompt workstream.
- [x] Define a separate guardrail quality gate requiring all 30 outputs to be available and manually scored, with zero critical safety failures.

### Point 6: Compare three free models on the same full regression set

- [ ] Complete all 60 cases per model (180 model-case evaluations), keeping quality and provider availability separate.
- [ ] After the v6 comparison, evaluate the v7 guardrail pack on the same three free models and manually score all 90 answers.

### Point 7: Run the frozen candidate on the held-out set

- [ ] After tuning is frozen, run all 30 holdout cases with v5 or its successor on each candidate model.

### Point 8: Score, adjudicate, and repeat failures

- [ ] Manually score all answerable outputs; adjudicate every critical-risk case and repeat failures plus regression cases.

### Point 9: Verify the context shape used by the eventual product flow

- [ ] Compare the generated evaluation context with the data projection that a future product-page backend will actually send; do not assume the current database endpoint is production-confirmed.
- Inspection found a neighboring `../1C OpenCart Master` service, but it is a catalog/price monitor, not the AI assistant backend. Its OpenCart query selects identifiers, localized product name, price, quantity/status, and optionally manufacturer; it does not provide the full description/attribute context needed by this assistant. Do not count it as point 9 evidence.
