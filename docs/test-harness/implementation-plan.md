# Race Expert Test Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an internal HTML test harness where a tester selects one OpenCart product, asks GPT-6 Luna questions using system prompt v11, and reviews a durable history of each attempt.

**Architecture:** First select and record the application foundation, exact source/test file map, private hosting/access method, secure database route, and separate durable history store. Then implement a thin UI over a server-side boundary with read-only OpenCart access, a server-only OpenAI key, and an independent journal store; product data and prior history never become implicit model context.

**Tech Stack:** Python 3.12, FastAPI 0.162.2, Uvicorn 0.46.0, MySQL Connector/Python 26.10.0 with mandatory verified TLS when the secure route is established, Python `sqlite3` for the separate journal, and Docker Compose on VPS-61125. Local source/test changes stay in the approved managed worktree; no push to the public source repository.

---

## Current workspace evidence and plan gate

- `rg --files` shows Wiki, prompts, evaluation scripts, and test-harness documents; there is no application source or application manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json`, or equivalent).
- `git rev-parse --show-toplevel` reports that this workspace is not a Git repository.
- GitHub metadata for `voyfur/re_products_helper` reports a public, non-archived repository with default branch `main` and size `0`.
- The approved flow is [docs/test-harness/2026-11-11-user-flow-spec.md](2026-11-11-user-flow-spec.md); the project intent is [docs/test-harness/intent.md](intent.md). Prompt v11 is [prompts/product-assistant-system-v11.md](../../prompts/product-assistant-system-v11.md).
- Since no app files exist, Task 1 must record the exact selected repository/worktree, application and test paths, runtime-specific commands, separate journal store, private access method, and deployment target in `docs/test-harness/implementation-decisions.md`. That file is the path-and-command manifest for Tasks 3–10. Its entries must be concrete before application code is created; this avoids inventing a stack or file layout in this plan.

## Task 1: Discover and record the application foundation

**Files:**
- Read: `AGENTS.md`
- Read: `wiki/index.md`
- Read: `wiki/session-handoff.md`
- Read: `docs/test-harness/intent.md`
- Read: `docs/test-harness/2026-11-11-user-flow-spec.md`
- Read: `wiki/sources/qa-mysql-readonly-access-and-product-query.md`
- Read: `prompts/product-assistant-system-v11.md`
- Create: `docs/test-harness/implementation-decisions.md`

- [x] **Step 1: Recheck the local foundation without reading secrets or running tests.**

Run:

```sh
rg --files -g 'package.json' -g 'pyproject.toml' -g 'requirements*.txt' -g 'go.mod' -g 'Cargo.toml' -g 'composer.json' -g 'Gemfile' -g 'Dockerfile' -g 'docker-compose*.yml'
git rev-parse --show-toplevel
```

Expected: no application manifest is listed; Git reports that the current folder is not a repository. Do not read `.env` or run evaluation scripts.

- [x] **Step 2: Recheck the selected remote repository.**

Use the GitHub repository metadata tool for `voyfur/re_products_helper` and inspect its default branch and top-level files.

Expected: either the repository is still empty on `main`, or any new content is reviewed before selecting it. Do not push files during discovery.

- [x] **Step 3: Compare viable foundations against the actual available runtime and operations.**

Compare at least two supported application foundations against these requirements: server-only OpenAI calls; parameterized MySQL reads with certificate verification or a protected tunnel; durable storage separate from OpenCart; internal authentication; safe rendering; locally runnable unit and browser tests; and a private deployment target. Inspect only available runtimes, existing service access, hosting capabilities, and repository policies. Select the smallest supported option that meets every requirement; record why the rejected option does not fit.

- [x] **Step 4: Record decisions and freeze the exact file map.**

Create `docs/test-harness/implementation-decisions.md` with: selected source repository/worktree; runtime and framework versions; exact application, test, migration, and configuration file paths for Tasks 3–10; verbatim install, unit-test, integration-test, browser-test, build, and local-run commands with expected results; separate journal-store type/location and backup/retention controls; internal identity/access mechanism and private host; secret variable names (names only, no values); and the database identity/transport decision. Keep the file free of credentials, endpoint secrets, customer data, and unsupported infrastructure claims.

- [x] **Step 5: Stop for review of the foundation record before creating application code.**

Expected: the file map and exact commands are complete, the chosen host denies public/buyer access, the journal is separate from OpenCart, and no persistent MySQL connection relies on plaintext or disabled certificate verification. If any requirement lacks evidence, record the concrete discovery needed and do not proceed to implementation.

## Task 2: Establish the verified read-only OpenCart route

**Files:**
- Update: `docs/test-harness/implementation-decisions.md`
- Infrastructure: use the verified route and FastPanel owner process recorded in that file; do not change the live database from an unmanaged shell.

- [ ] **Step 1: Confirm that the selected endpoint is the current website database.**

Obtain confirmation from the site/database administrator and compare the endpoint/database identity with the current website configuration through the approved administrative path. The previous endpoint selected `raceexpertcomua`, but its self-signed certificate did not verify a trusted CA and matching hostname, so it is not yet confirmed as the live website database.

- [ ] **Step 2: Configure an authenticated transport for persistent use.**

Use either a trusted CA with certificate-chain and hostname verification, or a protected VPN/SSH tunnel approved for this service. Configure MySQL TLS where supported. Do not use plaintext, `VERIFY_CA` without hostname verification when the hostname is required, or a production setting that disables certificate checks. Apply MySQL/Firewall changes through FastPanel where required.

- [ ] **Step 3: Provision the narrow read-only application account.**

Request a service account with `SELECT` only on `oc_product`, `oc_product_description`, `oc_product_attribute`, `oc_attribute_description`, and `oc_stock_status`. Do not grant writes or access to reviews, orders, or other tables for this first stage. Keep all credentials in the selected server-side secret store; never copy `.env` contents into a document or command history. Do not source the whole local `.env`, whose SSH and MySQL blocks reuse `HOST` and `PASSWORD` names.

- [ ] **Step 4: Confirm the store's currency source before deciding whether price can appear.**

Verify the storefront currency source through the approved site configuration or administrator. If the source and conversion rules cannot be confirmed, record that result and keep price excluded from both the card and model context. Do not infer a currency from a numeric `oc_product.price` value.

- [ ] **Step 5: Verify the database route and grants after the secure path is configured.**

Run these read-only SQL checks through the chosen verified connection:

```sql
SELECT DATABASE();
SELECT 1;
SHOW GRANTS FOR CURRENT_USER;
SHOW COLUMNS FROM oc_product;
SHOW COLUMNS FROM oc_product_description;
SHOW COLUMNS FROM oc_product_attribute;
SHOW COLUMNS FROM oc_attribute_description;
SHOW COLUMNS FROM oc_stock_status;
```

Expected: the administrator confirms this is the current website schema; `SELECT 1` succeeds; the account has only the five required `SELECT` grants and no write grants; the five table definitions match the current query guide. Record only non-secret verification results in `docs/test-harness/implementation-decisions.md`.

## Task 3: Define the durable journal store and record model

**Files:**
- Update: `docs/test-harness/implementation-decisions.md`
- Create/modify: exact journal-store and migration files listed in its frozen file map.
- Test: exact journal tests listed in its frozen file map.

- [x] **Step 1: Define one row per submitted question attempt.**

Store an opaque attempt ID, UTC submission time, OpenCart `product_id`, submitted article, product `model` and `sku`, product name for history display, question text, outcome (`pending`, `succeeded`, or normalized `error`), answer when successful, normalized error code when unsuccessful, model ID `gpt-6-luna`, and prompt version `v11`. Store no product-context snapshot, API key, password, raw provider diagnostic, or customer/review/order data.

- [x] **Step 2: Keep the journal physically or logically separate from OpenCart.**

Use the store selected in Task 1. The app's OpenCart connection remains read-only and cannot write journal rows. Set indefinite retention for this first stage, add no automatic purge, and provide no user-facing delete action. Backups and restricted administrator access follow the documented journal-store choice.

- [x] **Step 3: Add persistence and retry tests before connecting the UI.**

Test against a disposable local journal store. Expected: a submitted question survives app restart; an error row contains no answer; a new retry creates a second row while the original remains unchanged; history is ordered newest first; no row contains the product-context snapshot or secret fields. Use the exact unit-test command recorded in `docs/test-harness/implementation-decisions.md` and expect all journal tests to pass.

## Task 4: Add internal access control and server-only configuration

**Files:**
- Update: `docs/test-harness/implementation-decisions.md`
- Create/modify: exact authentication, server configuration, and access tests listed in its frozen file map.
- Test: exact access-control tests listed in its frozen file map.

- [x] **Step 1: Apply the private-access mechanism selected in Task 1.**

Require the approved internal identity or protected network before serving the harness. Do not expose a public buyer route, anonymous question submission, or public history listing. Keep only non-secret variable names in configuration examples; store secret values in the server-side secret facility.

- [x] **Step 2: Keep provider and database credentials on the server.**

Use unique configuration names for MySQL settings rather than loading the mixed `.env` blocks as a generic dotenv file. Keep `OPENAI_API_KEY` server-side. Ensure HTML, JavaScript bundles, browser storage, journal records, normal logs, and user-facing errors never include credentials.

- [ ] **Step 3: Verify access and secret boundaries.**

Implementation note: client assets, neutral errors, disabled API docs, loopback-only Compose binding, and local secret-file loading are covered by automated tests. Access to the deployed VPS and SSH tester-account restrictions remain unverified until a deployment is separately authorized.

Expected automated results: unauthenticated requests are rejected or redirected to the selected internal login; an authenticated test user can open the harness; client assets contain no API key or DB password; responses and logs contain no SQL, stack trace, endpoint secret, or provider payload. Run the exact access test command from the decision record.

## Task 5: Implement product search and localized read-only context

**Files:**
- Read: `wiki/sources/qa-mysql-readonly-access-and-product-query.md`
- Update: `docs/test-harness/implementation-decisions.md`
- Create/modify: exact catalog adapter, context builder, and tests listed in its frozen file map.
- Test: exact catalog tests listed in its frozen file map.

- [x] **Step 1: Search by exact model/SKU with bound parameters and ambiguity detection.**

Use whole-field equality with the same submitted article bound to both `model` and `sku`, ordered deterministically and limited to two rows. Verify the current column collation and test the chosen case-sensitivity behavior; do not use prefix or substring matching. Never concatenate user text into SQL. Zero matches leave no active product; one match selects that product; two matches require explicit tester selection. Keep the internal `product_id` out of ordinary UI text and do not activate an ambiguous selection. A new search replaces the active product only after a valid selection and never changes earlier journal rows.

- [x] **Step 2: Load only the five approved product tables.**

For the selected `product_id`, load product fields, language rows, named attribute values, and localized stock label using `language_id=1` for Russian and `language_id=6` for Ukrainian. Fetch both localized versions for the initial card, then choose the language of each supported question. Do not fall back to another language when the selected language is absent.

- [x] **Step 3: Build the visible card from supported fields only.**

Show product name, submitted article, model, SKU, available description, named attributes and localized stock label. Exclude price until its currency source is confirmed; if Task 2 cannot verify the source, omit price from both UI and model context for the first implementation. Never present `quantity`, `subtract`, `status`, or internal IDs as availability evidence. Do not fabricate missing descriptions or attributes.

- [x] **Step 4: Test the lookup outcomes with fixtures and a read-only integration check.**

Implementation note: fixture tests cover unique, zero, ambiguous, missing-locale, and missing-attribute states. A one-time SSH-forwarded read-only lookup returned the expected RE0731/RE1687 IDs and SKUs; confirmation that this endpoint is the current live website database remains open in Task 2.

Fixtures must cover one exact match, no match, two matches, missing localized description, missing attributes, and conflicting quantity/status versus localized stock label. Expected: only one match or a tester-selected option becomes active; missing language stays missing; no unsupported availability claim is derived. Once Task 2 is complete, perform a narrow read-only lookup for `RE0731` and `RE1687`; if they still resolve as in the current schema, expect `RE0731 → product_id=586, sku=20004101` and `RE1687 → product_id=2017, sku=5060623633844`. A mismatch is a data-source investigation, not a reason to hard-code old IDs.

## Task 6: Safely render descriptions and responses

**Files:**
- Create/modify: exact text-normalizer, renderer, and security tests listed in the frozen file map.
- Test: exact rendering tests listed in the frozen file map.

- [x] **Step 1: Convert product HTML into safe structured text.**

Treat database descriptions as untrusted HTML. Remove active content and attributes; preserve paragraph boundaries, list items, and table row/heading-value relationships in the text shown to the tester and sent to the model. Do not execute scripts, event handlers, embedded media, or arbitrary URLs.

- [x] **Step 2: Render the model answer as text.**

Display answer text without interpreting provider output as HTML or executable Markdown. Preserve line breaks and do not rewrite factual content.

- [x] **Step 3: Add adversarial rendering tests.**

Use fixture descriptions containing `<script>`, event-handler attributes, links, a list, and a multi-column table; use an answer containing HTML tags. Expected: no script or event handler executes or survives as active content; list order and table labels/values remain understandable; answer tags display as inert text. Run the exact test command from the decision record.

## Task 7: Implement the independent question-to-answer flow

**Files:**
- Read: `prompts/product-assistant-system-v11.md`
- Read: `evals/README.md` for the existing v11 request settings and model identifier.
- Create/modify: exact question service, OpenAI client, and request-contract tests listed in the frozen file map.
- Test: exact model-request tests listed in the frozen file map.

- [x] **Step 1: Validate language and active product before a model request.**

Accept only Russian or Ukrainian questions. If the language is unsupported or unclear, ask for a Russian or Ukrainian rephrasing and send no model request. If there is no selected product, send no model request. Select the matching localized fields for each question and update the displayed language for that question.

- [x] **Step 2: Construct a single-turn request from visible facts only.**

Use model ID `gpt-6-luna`, system prompt v11, the current question, and only current-product facts shown in the tester's card. Keep prompt version `v11`; verify the checked-in source prompt matches SHA-256 `5775f9e8c3909bc9cc39668f312b9e6838aa82c0c00b234b7f0671bf384c854d` before wiring it in. Use the Responses API with `store=false`, `reasoning={"effort":"medium"}`, `max_output_tokens=2048`, and no explicit `temperature`; the request syntax was checked against the official OpenAI reference during implementation.

- [x] **Step 3: Persist before sending and retain provider failures safely.**

Create the journal attempt before the external request. On success, save the answer and `succeeded`; on failure or timeout, save a normalized error code without raw provider diagnostics and show a neutral message. Do not silently retry a provider call. A tester-initiated retry is a new attempt and a new journal row.

- [x] **Step 4: Verify the request payload with a fake OpenAI client.**

Expected: the call uses `gpt-6-luna`, prompt v11, and `store=false`; contains one selected product's visible fields and the current question; contains no `product_id`, price, raw flags, reviews, customer/order data, another product, previous Q&A, API key, or hidden context snapshot. Unsupported-language and no-product cases make zero calls. Do not send a live model request as part of automated tests.

## Task 8: Implement the tester UI and durable history actions

**Files:**
- Create/modify: exact page, components, styles, and browser tests listed in the frozen file map.
- Test: exact browser tests listed in the frozen file map.

- [x] **Step 1: Build the initial search and history view.**

Provide an article input, “ОК” action, and access to the journal. Disable question submission until a unique product is active. On no match, preserve the typed article and invite correction; on a database error, preserve it and offer a retry action without technical details.

- [x] **Step 2: Show product variants and localized card states.**

For multiple exact matches, show each choice's name, model, and SKU and wait for selection. Before the first question show the available RU and UA fields; after each question show the corresponding language for the same selected product. Missing fields remain visibly absent; never substitute another language or infer purchase availability.

- [x] **Step 3: Show answers, errors, and attempt history.**

Show neutral DB/API errors without technical details. List journal rows newest first with product name/article, question, answer or error status, time, model, and prompt version. “Использовать как черновик” copies only the original question to the input; it does not mutate the saved row, change the selected product, or preload old Q&A into the model request. A retry uses that question with the currently selected product data and creates another row; the original attempt remains unchanged.

- [x] **Step 4: Exercise the browser flow with a disposable store and fake services.**

Expected: search/selection gates are enforced; language switches per latest question; history remains after a full page reload and app restart; draft edits leave the old row untouched; retry leaves the first error row intact; there is no delete or automatic-cleanup action. Use the browser-test command fixed in `docs/test-harness/implementation-decisions.md`.

## Task 9: Complete acceptance, security, and release checks

**Files:**
- Update: `docs/test-harness/implementation-decisions.md` with verified non-secret results.
- Update: the application README and deployment/access instructions at the exact paths recorded in the frozen file map.
- Test: unit, integration, browser, and build commands recorded in that file.

- [ ] **Step 1: Run the local test suite without production services.**

Implementation note: unit (33), local integration (10), and Chromium browser tests (5) pass; the local Uvicorn health check returns HTTP 200. The Docker Compose build remains unverified because the local Docker CLI has no Compose plugin, and VPS build/deployment has not been authorized.

Run the exact unit, integration, browser, and build commands recorded in the foundation decision file. Expected: all pass using fixture catalog data, a disposable journal store, and a fake OpenAI client; no test requires production credentials or live MySQL/OpenAI calls.

- [ ] **Step 2: Verify the live database only after Task 2 evidence is complete.**

Run the SQL checks from Task 2 through the verified route and the app's narrow read-only lookup. Expected: verified website schema, only required `SELECT` grants, both RU/UA context rows where present, and no write statements or reads from reviews/orders.

- [ ] **Step 3: Verify internal access on the selected private host.**

Expected: an unauthenticated browser request cannot view the UI or history; the approved internal tester can use the harness; no public buyer route or site integration exists. Confirm TLS/access controls using the hosting provider's supported mechanism selected in Task 1.

- [x] **Step 4: Audit artifacts before any GitHub push.**

Implementation note: the worktree contains local application files only; `.env` is ignored and no push has been made. Repeat the full secret/artifact review if publication is later requested.

Review the complete staged file list and diff for `.env`, API keys, passwords, private keys, raw customer/review/order data, and private infrastructure details. Expected: none are staged. Do not push or deploy publicly; any later publication requires the user's separate instruction.

## Acceptance coverage map

| Approved criterion | Planned tasks |
| --- | --- |
| Exact product opens; zero and multiple matches are safe | 5, 8, 9 |
| Card shows supported fields, both languages initially, no inferred availability or unverified price | 5, 6, 8 |
| One selected product and question-language context; unsupported language is blocked | 5, 7, 8 |
| Success and failure attempts persist; retries are separate; history survives reload | 3, 7, 8, 9 |
| Draft reuse does not alter old record or pass old Q&A to model | 7, 8, 9 |
| Read-only catalog, separate journal, server-only key, safe content, private access | 2, 3, 4, 6, 7, 9 |

## Plan review

Review this plan and the discovery gate before assigning implementation. No code, tests, database connection, secret inspection, repository push, or deployment is authorized by this plan-writing task.
