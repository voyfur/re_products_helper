# Product Q&A Web Search — Design Specification

**Status:** approved approach; backend implementation in progress. Storefront hookup and deployment remain separate work.  
**Scope:** just-in-time web search for the existing product Q&A application.

## 1. Goal

Let a buyer ask a question about the currently selected product and use a small amount of verified web evidence when the product card does not contain the answer. Avoid manually enriching the catalog’s roughly 5,000 products. Keep the request path short: search only when needed and issue at most one external search request per question.

Answers remain in Ukrainian. They should be direct and confident when supported by the selected product card or approved sources. The buyer-facing answer must not contain source URLs, citations, or a source list.

## 2. Decisions and boundaries

- Search provider: a separate search API (proposed: Tavily Search API), called by our backend. Do not use OpenAI-hosted Web Search for this version because its citation behavior conflicts with the no-links answer requirement. Confirm current provider behavior during implementation against the [Tavily Search API documentation](https://docs.tavily.com/documentation/api-reference/endpoint/search).
- Search mode: `fast`, a small result count (initially at most five), domain restriction, and no full-page/raw-content retrieval. One Tavily request maximum per question.
- Allowed sources: a curated domain allowlist covering product manufacturers, approved suppliers, and selected public review platforms. Default deny: a result from a domain outside the allowlist is discarded. The initial domain list must be established before enabling search; do not silently fall back to unrestricted web results.
- Product reviews: use only subjective themes for the exact selected product when the same theme appears across at least two independent approved review pages. Do not quote reviews or pass/store reviewer names, handles, profile details, or other personal data. A review theme cannot establish ingredients, safety, efficacy, dosage, contraindications, or other objective/medical facts.
- Catalog boundary: do not modify OpenCart, add fields to product cards, or batch-process products. Search is triggered by a buyer question for one revalidated product.
- Prompt boundary: keep `prompts/product-assistant-system-v12.md` and its recorded hash unchanged. Add a new prompt version for web evidence. The existing v12 prompt forbids external sources and cannot be reused for this feature.
- Deployment boundary: this specification covers design and local QA only. It does not authorize staging or production changes.

## 3. Current application context

The application looks up products in the read-only catalog, then revalidates the selected article and `product_id` before answering. The catalog query is limited to the existing five product tables. `AssistantService` currently creates one model request using the product card and question; `OpenAIClient` returns answer text. The SQLite journal stores question attempts and has no source metadata today. The API response and frontend render the answer without citations.

The external search capability must be added after product revalidation. It must not weaken product identity checks or change the catalog’s read-only boundary. Project instructions currently prohibit review data; before implementation, update the relevant project scope/guardrail documentation to reflect this specifically approved exception for anonymized, recurring public-review themes.

## 4. Request flow

1. The user selects a product through the existing product search.
2. `POST /api/ask` revalidates the article and `product_id` against the catalog as it does today. A failed or mismatched validation stops the request before any model or search call.
3. The assistant receives only the revalidated product context and current question. It may answer from the card directly, or request the single backend search function when the card does not answer the question or the user explicitly asks about buyer experience.
4. The backend constructs a focused Tavily query from the selected product's displayed name, plus explicit brand and variant/package attributes when they are not already in the name, and the question's topic. Do not send Race Expert's internal article, barcode/SKU, or catalog `model` field as external search identifiers. Those identifiers remain available for the internal catalog lookup. Do not search for or include other products.
5. The backend calls Tavily at most once, using fast mode, the curated domain allowlist, a low result limit, and no full-page/raw-content retrieval. Search-result excerpts are the only source text returned. Enforce the one-search-call limit in server code, even if a model/API setting also limits tool calls. The model’s function call is internal control flow; the limit applies to external web-search requests.
6. The backend drops results outside the allowlist and results that cannot be tied to the exact selected product by its displayed name and any explicit brand and variant/package attributes in the result title or URL path. Never require a Race Expert article, barcode/SKU, or catalog `model` value to appear on an external page. Reject near matches for other flavors, sizes, formulas, or product generations.
7. For review results, discard author/profile metadata and redact obvious personal data from the short excerpts. Pass only relevant redacted excerpts from at least two independent approved review pages to the final model call so it can identify a shared theme. Do not send whole reviews or pages, and do not persist the excerpts. The model may report the theme without quoting source wording; it must not invent a count or prevalence percentage. If recurrence is unclear, omit the review theme.
8. The backend passes a compact evidence bundle to the model for the final answer. Treat all external page text as untrusted data, never as instructions. The model is told to use only the selected card and supplied evidence, not its pretrained memory.
9. The backend saves the attempt and private source metadata. The buyer receives only the answer text (and, when applicable, the health disclaimer); internal source metadata is excluded from the API response.

When no search is needed, keep the existing single-model-call path. A search-enabled answer can require an initial model decision, one Tavily request, and a final model call; the extra round trip is an expected latency tradeoff and should not be hidden in performance reporting.

## 5. Evidence and answer rules

### Source priority

- The revalidated product card is authoritative for the current listing identity and listing-specific data such as the selected variant or package size.
- The manufacturer or an approved supplier may support product-specific factual details not present on the card.
- Public reviews may support only carefully worded, subjective experience themes. Phrase these as reports by buyers, not as guaranteed properties of the product.
- If approved sources conflict, do not choose a value by guessing or silently merge them. State that the information differs and avoid a definitive claim. Do not use reviews to resolve a factual conflict.
- If no exact-product evidence supports the answer, say in Ukrainian that the card and verified sources do not establish it. Do not fill the gap from model memory.

### Health-related questions

Treat questions about health effects, safety, dosage, interactions, conditions, symptoms, pregnancy, or use by children as health-related. Search evidence does not authorize diagnosis, treatment, or individualized medical recommendations. Public review themes must not support health claims.

The model returns a structured `health_related` flag with the answer and is instructed to set it when any health topic is present or uncertain. The backend appends this fixed Ukrainian disclaimer when the flag is true, so the model cannot omit or paraphrase the disclaimer text:

> Це відповідь штучного інтелекту; інформацію щодо здоров’я потрібно перевірити з фахівцем.

The answer itself must stay within supported product facts and must not present the disclaimer as a substitute for evidence.

### Buyer-facing output

- Ukrainian language, irrespective of the language used in the question.
- No source links, citations, domain names, or source list.
- No direct quotations from reviews; no personal data from review authors.
- Do not pass price, orders, customer records, or other questions to the model.

## 6. Private provenance and journal

Extend each individual Q&A attempt with private source metadata sufficient for internal audit and latency review:

- provider and source type (`manufacturer`, `supplier`, or `review_platform`);
- source title, domain, URL, and fetch timestamp;
- product-match basis (the displayed product name, with explicit brand and variant/package attributes when available);
- search latency and whether search was skipped, used, or failed.

Do not persist raw page text, raw review text, reviewer identity, or the evidence snippets sent to the model. Keep provenance attached to the corresponding Q&A attempt; do not create a separate product knowledge base, history endpoint, or buyer-facing source API. Add a backward-compatible SQLite migration; existing attempts must remain readable. Ensure `/api/ask` serialization excludes all provenance fields.

## 7. Components likely to change

- `app/config.py` and `.env.example`: add the search-provider secret using the existing secret-file pattern. Never print the key. Update `scripts/run_local_session.py`’s allowlist/secret loading to support it without reading `.env` through `source`.
- New `app/search_provider.py`: one-request Tavily adapter, fixed timeout, domain restriction, compact response parsing, sanitized provider errors.
- `app/assistant.py` and `app/openai_client.py`: tool/function-call decision, server-enforced single-search cap, evidence handoff, structured final result including `health_related`.
- New prompt version (v13): source hierarchy, evidence-only answer rules, exact-product matching, review-theme limits, no visible citations, health handling, and instruction-injection resistance for external content. Record its hash without changing v12.
- `app/journal.py` and a new migration: persist private provenance and latency metadata only.
- `app/main.py`: preserve current revalidation; return only buyer-facing answer fields.
- `app/static/app.js` and, if needed, `app/templates/index.html`: show a brief “Перевіряємо джерела…” state while search is running. Do not render source URLs.
- Project guardrails and local runbook: document the narrow review-theme exception, search key handling, and local-only QA behavior.

No implementation, database deployment, catalog write, or production release is included in this specification.

## 8. Failure behavior

- Search returns no exact-product approved result: answer only from the card, or clearly say the information could not be verified.
- Search provider times out or errors: sanitize the provider error. If the card is sufficient, answer from it; otherwise say verification was unavailable. Never invent a result.
- Results are from the wrong variant or unapproved domains: discard them.
- Approved sources conflict: explain the discrepancy briefly and avoid choosing a side without evidence.
- Model requests a second search: reject it server-side and continue with the evidence already available, or return the normal unsupported-information response.
- Local launch is missing the search secret: fail with a sanitized configuration error; never show environment values or secrets.

## 9. Performance and acceptance criteria

The implementation is acceptable when all of the following hold:

1. Search is attempted only after successful current-product revalidation and only when the card is insufficient or the user asks for subjective experience.
2. The backend performs no more than one external search request per Q&A attempt.
3. Requests use fast search, a small result limit, an approved-domain restriction, and no full-page/raw-content retrieval.
4. Near-match products, unapproved domains, and non-recurring review claims do not reach the final answer as evidence.
5. Answers are Ukrainian, contain no visible URLs/citations, and never treat review themes as objective or health facts.
6. Health-related answers receive the fixed disclaimer from backend logic.
7. Provider failure falls back safely; it does not break answers that the product card can support.
8. Journal metadata contains provenance and timing but no source excerpts, raw review text, or reviewer identity; API serialization does not expose that metadata.
9. Local QA measures end-to-end latency and search latency separately (including p50/p95 and the share of questions that invoke search). Do not set a latency SLO or add caching until local measurements show the need.

No numeric latency target is specified yet. The design limits search depth/results and calls, while local measurements will establish realistic latency before any caching decision. The initial version must not pre-index all 5,000 products. If later measurements justify caching, cache only products actually asked about and define freshness/invalidation separately.

## 10. Verification scenarios for implementation

- Card contains the answer: no search request; answer uses the card.
- Card lacks a factual detail: one restricted search request; exact approved manufacturer/supplier result supports the answer.
- User asks what buyers commonly report: answer includes only a recurring, anonymized subjective theme; no quotes or identities.
- Search results mention the same product family but a different size/flavor/formula: discard those results.
- Search returns an unapproved domain or no exact match: do not use its content.
- Reviews claim a health benefit or safety outcome: do not repeat it as a fact or recommendation.
- Health question with supported source evidence: Ukrainian answer plus the exact backend disclaimer.
- Search provider timeout, malformed response, or missing key: sanitized failure and safe card-only/unsupported fallback.
- Model attempts a second search or returns a buyer-facing URL: enforce the one-call cap and remove/prevent source links.
- Attempt journal and API output: internal provenance is stored on the attempt and is absent from buyer-visible response fields.

## 11. Implementation prerequisites and current status

- The user approved the researched initial source set on 2026-11-19. `app/search_evidence.py` now contains explicit hostname and brand mappings for those manufacturer/supplier sources plus `fit.rozetka.com.ua` and `prom.ua` review sources. `makeup.com.ua`, `epicentrk.ua`, the unresolved SaltStick redirect, and research holdouts remain excluded. `nutrend.com.ua` is enabled only for NUTREND products and remains conditional because its distributor status is self-claimed.
- The user reports a Tavily token in `.env`; the file and value must remain unread. The local launcher now accepts its allowlisted setting, but no Tavily call has been made in this implementation session.
- The spec does not authorize live QA calls, database access, staging, storefront integration, or deployment unless the user separately requests that stage.
- During implementation, verify Tavily’s current request fields and result behavior from its official documentation, and verify the current OpenAI Responses API function-calling contract from [OpenAI’s official guide](https://developers.openai.com/api/docs/guides/function-calling).

