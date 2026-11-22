# Web Search local QA — 2026-11-19–20

## Secret handling and launch

The local launcher accepted the direct `TAVILY_API_KEY` setting through its allowlist parser; a separate key file was not required. `.env` was not opened, displayed, sourced, or copied. Each QA server was started through `scripts/run_local_session.py`, passed its read-only MySQL catalog preflight, required TLS 1.2/1.3, and shut down with its SSH tunnel. No catalog writes, staging, production, storefront integration, or deployment occurred.

## Live catalog products

Read-only `/api/search` returned one exact catalog match for each tested article:

- `RE89157` — PureGold Compact Whey Gold, salted caramel, 500 g.
- `RE1687` — Precision Hydration 1500 Tube, 10 tablets.
- `RE0731` — Sponser Classic Shaker, 500 ml.

The Ukrainian cards returned for these products contained an SKU attribute but no separate brand attribute.

## End-to-end results — 2026-11-20

The UI, legacy UI API, and authenticated versioned API were exercised against the live local service. OpenAI and Tavily were called only by submitted Q&A attempts. A temporary bearer key was generated in memory for the versioned API checks and was not saved or printed.

| Scenario | Result | Search / timing | Outcome |
| --- | --- | --- | --- |
| Browser UI flow, `RE1687` | UI page and JS loaded; product lookup succeeded | skipped; 3,859 ms total | Browser showed the waiting state, then rendered the Ukrainian card-based answer. |
| Card answer, `RE1687` | `/api/ask` HTTP 200; succeeded on v13 | skipped; 5,483 ms total | Expected “10 tablets” fact present; no search metadata in buyer response. |
| Buyer-experience question, `RE89157` | `/api/ask` HTTP 200; succeeded on v13 | Tavily used; 845 ms search, 7,128 ms total | 0 accepted exact-product sources; answer withheld an unverified review theme and had no link or private fields. |
| Versioned API authentication | Missing bearer returned 401 `unauthorized`; temporary local bearer returned HTTP 200 | — | Authorized response contained only `status` and `answer`. |
| Buyer-experience question, `RE89157` | `/api/v1/ask` HTTP 200; succeeded on v13 | Tavily used; 419 ms search, 8,605 ms total | 0 accepted exact-product sources; safe refusal; no link or private fields. |
| Unknown article | `/api/v1/ask` returned 404 `product_not_found` | no attempt created | Catalog validation stopped before the model/search path. |
| Health-related question, `RE89157` | `/api/v1/ask` HTTP 200; succeeded on v13 | skipped; 5,768 ms total | Exact fixed Ukrainian disclaimer present; no link. |
| Buyer-experience question, `RE1687` | `/api/v1/ask` HTTP 200; succeeded on v13 | Tavily used; 576 ms search, 5,719 ms total | 0 accepted exact-product sources; safe refusal; no link or private fields. |

Across the three live review attempts, no exact source was accepted. A metadata-only check confirmed zero provenance on each attempt. A separate lexical safety check found a refusal signal and no buyer-review claim pattern or link/domain in each answer; answer text and source metadata were not printed or added to this report.

## Latency sample

The local journal contained 6 successful Q&A attempts from this deliberately selected test set: search was used on 3/6 (50%). This is a test-mix share, not a forecast of normal site traffic. Nearest-rank sample estimates were:

- End-to-end p50: 5,719 ms; p95: 8,605 ms (`n=6`).
- Tavily search p50: 576 ms; p95: 845 ms (`n=3`).

These small samples are diagnostic only and do not establish an SLO or a reliable production percentile.

## Offline verification and remaining coverage

The full offline suite passed: **147 tests, 4,009 subtests**. It covers the mocked exact-source acceptance, wrong variants, unapproved hosts, review recurrence, provider failures, health disclaimer, private provenance, and request validation paths.

The live tests verified provider reachability and the no-evidence fallback, but did not find a live review result that met the then-current exact-product rule. A positive live evidence match remains unverified; the tested cards lacked a separate brand attribute, and their external pages did not yield an accepted exact SKU/model page. The URL identifier requirement was subsequently replaced by the product-name rule documented below.

## Follow-up rejection diagnosis — 2026-11-20

Two additional diagnostic Tavily requests rechecked the live catalog cards `RE89157` and `RE1687`. Each returned 5 results. For both sets, every result passed the HTTPS allowlist and topic-host checks, then failed the exact product URL-path check: the path contained neither the selected SKU nor model. The filter therefore discarded all 10 before inspecting titles, excerpts, freshness, or recurring review themes. This shows the current failure is product-identity confirmation, not a judgment that the reviews are outdated or low quality. Per-result rejection reasons were not recorded during the original three E2E calls, so the diagnostic only establishes the reason for these follow-up result sets.

The previous one-request provider check on 2026-11-19 also returned results but accepted no exact review source; it did not invoke OpenAI. No additional action against staging, production, or the storefront was taken.

## Follow-up implementation correction — 2026-11-20

The exact URL-path rejection above reflects the previous matcher, which required the catalog SKU or `model` in an external URL. The Tavily path now uses the displayed Ukrainian product name, adding explicit brand and variant/package attributes from that card when absent from the name. It excludes the internal article, barcode/SKU, and catalog `model` from the Tavily query and exact-match decision. SQL catalog lookup remains unchanged. The focused mock tests passed (34 tests across `test_search_evidence.py` and `test_web_search.py`); a positive live exact-product match has not been rechecked after this code change. No Tavily call, database session, staging action, or deployment was performed for this correction.

## Mock end-to-end batch — 2026-11-20

Ran 100 synthetic `/api/ask` requests through the FastAPI route, assistant orchestration, search evidence filter, and temporary SQLite journal. Fifty used factual-search stubs and fifty used two independent review-platform stubs. All 100 attempts succeeded; every stored provenance record used `product_name` matching, catalog article/model/SKU values were absent from Tavily queries, and search metadata stayed out of buyer responses. The catalog, OpenAI, and Tavily boundaries were mocked; this run did not connect to MySQL or call external APIs. The full offline suite also passed: 147 tests and 4,009 subtests.

## Live end-to-end batch — 2026-11-20

Ran 100 sequential buyer-experience requests through the local QA app started by `scripts/run_local_session.py`. The approved launcher completed its read-only catalog preflight over SSH with MySQL TLS 1.3. The three known catalog products were resolved by article, and each request completed with HTTP 200 and a succeeded attempt. All 100 invoked Tavily; there were no provider/search errors. The attempt journal shows 0 accepted sources and 0 `product_name` matches, so the final answers used the safe no-evidence path. A metadata-free lexical scan found refusal language in all 100 answers, no URL/domain output, and no apparent review claim without refusal language; this is a safety signal, not a semantic quality evaluation.

Nearest-rank latency estimates for the 100 attempts: end-to-end p50 5,468 ms and p95 8,914 ms; Tavily p50 530 ms and p95 743 ms. The local server shut down cleanly and closed its tunnel. No staging, storefront, production, or deployment action occurred. The search path is live, but a positive exact-product evidence match after the product-name change remains unverified.

## Targeted source-matching follow-up — 2026-11-20

The 100-request live batch above tested only buyer-experience questions. It verified the provider call and safe no-evidence behavior, but not a factual answer grounded in an accepted manufacturer source. In the earlier live review batch, result-level rejection reasons were not retained, so they cannot be reconstructed for all 100 responses.

The focused diagnosis found that the prior matcher required the full localized card name as one exact phrase in a result title or URL path. The known cards also had no explicit brand attribute, which left factual manufacturer domains unavailable. The matcher now infers only an exact known allowlisted brand phrase from the displayed product name, supports word-order and selected Ukrainian-to-English name normalization, and keeps flavor/package tokens mandatory. A brand-scoped manufacturer/supplier host may confirm the brand; it cannot waive model, flavor, or package checks.

| Check | Result | Timing |
| --- | --- | --- |
| Factual search for `RE0732` | Tavily returned 5 HTTPS results on approved product-scoped hosts; safe excerpts and product pages passed, but none identified the selected 600 ml variant in the title/path. No source was accepted; the app returned its safe fallback. | 11,407 ms search; 25,664 ms total |
| Manufacturer match for `RE89157` | One exact manufacturer result matched the product line, translated flavor, and 500 g package after the matcher update. | Direct Tavily check |
| Factual `/api/ask` for `RE89157` | One factual source passed allowlist and `product_name` matching. The model abstained because the accepted excerpt did not support a new fact absent from the catalog card. Private provenance stayed out of the buyer response. | 1,135 ms search; 8,228 ms total |
| Card-covered question for `RE89157` | Search was correctly skipped because the card already contained the requested information. | 5,122 ms total |

One additional local request made after a long idle period received a catalog 503; restarting the approved launcher restored the read-only catalog path. No catalog write occurred. The successful source acceptance and the model’s safe abstention exercise the source pipeline, but a positive answer containing a fact available only from an external source remains unverified. Do not present this as a successful source-grounded answer test.

The updated offline suite passed: **150 tests, 4,009 subtests**. New regression cases verify name-based brand scoping, reordered/localized product-name matching, and rejection of a wrong capacity or flavor.

## Ten-card live factual-search batch — 2026-11-20

Selected ten products from public Race Expert product cards and read each article from its product page: `RE89157`, `RE0126`, `RE3287`, `RE3096`, `RE0723`, `RE5921`, `RE2466`, `RE2199`, `RE5702`, and `RE4901`. The local catalog lookup returned one product for each article. Ten sequential local `/api/ask` requests completed with HTTP 200 and succeeded attempts.

| Measure | Result |
| --- | ---: |
| Tavily invoked | 4/10 |
| Search skipped by the assistant | 6/10 |
| Tavily/search failures | 0/10 |
| Accepted exact sources | 1 total, on `RE89157` |
| Search latency median (n=4) | 816 ms (646–1,098 ms) |
| End-to-end latency median (n=10) | 5,152 ms (2,963–10,111 ms) |

Three of the four Tavily calls accepted no exact source. The accepted-source response included a refusal caveat and an unnegated claim for the requested formulation fact. A separate check of the official manufacturer page confirmed that claim for the exact 500 g salted caramel variant. This confirms one positive live source-grounded factual answer; the six skipped searches are not counted as external-source tests. Nine live buyer response payloads were directly checked for private search fields; the first response was returned successfully but its API field check was interrupted by the initial read-only SQLite metrics issue. The buyer serializer and privacy behavior remain covered by the offline tests described above.

The journal audit used immutable read-only SQLite access and reported only aggregate counts and latencies. No question text, answer text, source title, URL, domain, or provenance was added here. The launcher shut down cleanly with its SSH tunnel. No catalog write, staging, storefront, production, or deployment action occurred. Three Tavily calls in this batch still returned no accepted source; one exact source-grounded factual answer was confirmed for `RE89157`.
