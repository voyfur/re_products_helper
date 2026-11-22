# Race Expert: research of product review platforms

**Date:** 2026-11-19  
**Purpose:** Identify public domains that may supply independent, exact-product buyer-experience evidence to the proposed one-request Web Search flow.  
**Scope:** Targeted sample across Race Expert's public categories and representative listed brands. This is a source-coverage study, not a full product-by-product audit of the catalog. No review text or reviewer identity is reproduced here.

## Executive recommendation

Use **rozetka.com.ua** as the first Ukrainian product-review candidate and **prom.ua** as a conditional second candidate. Add **makeup.com.ua** only for relevant dietary-supplement products where an exact item page exists. Keep **epicentrk.ua** as a low-priority fallback until a matching product page has usable reviews. The source registry should approve exact hostnames and distinguish product reviews from store/seller ratings.

This list does not guarantee two usable review sources for every product. In the sampled endurance category, GU and SiS product pages appeared on both Rozetka and Prom, but the exact sampled pages had no buyer reviews. For Race Expert's own-label accessories, this search did not confirm an independent product-review page. If the single capped Tavily response does not contain two exact-product pages from two different approved registrable domains, omit the review theme.

## Platform findings

| Platform domain | Best-fit Race Expert groups | Evidence and quality | Recommendation |
| --- | --- | --- | --- |
| `rozetka.com.ua` (observed exact product host: `fit.rozetka.com.ua`) | Sports nutrition, protein/creatine, amino acids, some supplements and sports gear | Item pages have a separate product-review area. A Myprotein Creatine Monohydrate 500 g page identifies EAN `5055534302019` and showed 17 product reviews in the captured page. A NOW Foods L-Arginine 1000 mg / 120-tablet listing showed 15. Official seller guidance says reviews appear on product pages and warns that products grouped with similar seller listings may share a combined review list. | **Primary candidate.** If the implementation allowlist uses exact hosts, explicitly approve `fit.rozetka.com.ua` (and any other required host individually). For source independence, treat all Rozetka subdomains as one platform/domain; never count `fit.rozetka.com.ua` and `rozetka.com.ua` separately. |
| `prom.ua` | Sports nutrition and supplements sold by marketplace vendors | Product pages have a product-review section distinct from seller-review counts. Prom's seller documentation says a product review is tied to an order/receipt or inspection and limits a buyer to one review per product. A Myprotein Creatine Monohydrate 500 g listing showed two product reviews; other seller listings for the same product showed zero. A NOW Foods L-Arginine 1000 mg / 120-tablet listing showed product reviews. | **Conditional secondary candidate.** Use the item review section only; ignore seller-rating counts. Listings are seller-specific and duplicate product pages are common, so verify article/EAN, formula, flavor and package. Multiple pages on `prom.ua` still count as one platform. |
| `makeup.com.ua` | Vitamins and dietary supplements, especially NOW Foods items | Product pages have item-specific review sections, and sampled pages showed a “confirmed purchase” marker on some reviews. Coverage includes dietary supplement product pages. Some pages also display a platform-generated review summary; this is not an original buyer review and should not be passed as evidence. | **Conditional supplement fallback.** Only use an exact Race Expert product/variant page and original, short buyer-review excerpts. Exclude health outcomes, efficacy, safety and dosage claims; this category's review text often discusses those topics. |
| `epicentrk.ua` | Sports supplements where an exact listed item exists | Item pages expose a product-review section, but sampled exact pages for Myprotein Creatine Monohydrate 150 g and Nutrend BCAA Liquid 500 ml showed no product reviews. | **Reserve candidate, low observed coverage.** Do not count the review form or an empty section as review evidence. Enable it only after a product in the catalog has a populated exact-item page. |

## Coverage by product group

### Protein, creatine and sports nutrition

The best documented overlap is Myprotein Creatine Monohydrate 500 g: a Rozetka page identifies the 500 g item by EAN, while Prom has a seller listing with two item-level reviews. The Prom page found in this sample did not expose a matching EAN, so this is a promising pair rather than a fully verified same-SKU pair. Confirm the article/EAN or sufficiently exact model, form, flavor and size on both pages before counting them together. [Rozetka item/reviews](https://fit.rozetka.com.ua/ua/myprotein-5055534302019/p363011121/comments/) · [Prom item page](https://prom.ua/ua/m-7891758356035514930-creatine-monohydrate-myprotein.html)

### Amino acids and dietary supplements

NOW Foods L-Arginine 1000 mg / 120 tablets appears on both Rozetka and Prom with product-level reviews. This demonstrates better review coverage for a mainstream supplement than for the sampled gels, but the cross-site EAN/lot was not verified. [Rozetka item page](https://fit.rozetka.com.ua/ua/410652471/p410652471/) · [Prom item page](https://prom.ua/ua/p1338757189-now-foods-arginine.html)

Makeup is a possible additional source for vitamin/supplement products. Its NOW Foods product pages have item-specific reviews, but they need the same exact-variant check as other marketplaces. Never use a platform's generated review summary as a second independent review source. [Makeup dietary-supplement page example](https://makeup.com.ua/ua/product/772233/)

### Gels, hydration and endurance fuel

The sampled GU Energy Gel 32 g page on Rozetka and the sampled GU 32 g page on Prom both had zero item reviews. SiS GO Energy Powder 1.6 kg also appeared on both domains; the sampled pages showed no useful review evidence. These results show that a domain may carry a product without providing any buyer-experience evidence. Don't substitute a different gel flavor, caffeine variant, format, or size to satisfy the two-domain threshold. [GU on Rozetka](https://fit.rozetka.com.ua/ua/502797924/p502797924/) · [GU on Prom](https://prom.ua/p2499725615-gel-energeticheskij-original.html) · [SiS on Rozetka](https://fit.rozetka.com.ua/ua/490261339/p490261339/) · [SiS on Prom](https://prom.ua/ua/m-8134836161834654343-napij-energetichnij-sis.html)

### Accessories, clothing and Race Expert own-label goods

The public Race Expert catalog includes running accessories, flasks, buffs, apparel, medals and own-label items. A Race Expert black buff is listed under article `REE2185`, but the targeted search did not confirm an exact external product-review page for it. Treat exact-product review coverage in these groups as **unverified**, not as absent from the whole internet. Do not apply reviews of generic buffs, bottles or clothing to Race Expert-branded or variant-specific products. [Race Expert accessories](https://raceexpert.com.ua/aksesuari/) · [Race Expert black buff](https://raceexpert.com.ua/5417-baf-race-expert-chornij-ree2185-769-grn-ree2185-bafi)

## Important domain and identity distinctions

- The Race Expert storefront (`raceexpert.com.ua`) is the product-question interface, not an independent review platform.
- Race Expert's homepage links to Revizion for **store-level** reviews. Those reviews describe the shop, not an exact SKU, and do not count toward a product-review theme. [Race Expert homepage](https://raceexpert.com.ua/)
- Product-review counts and seller/store ratings are different evidence. Prom explicitly maintains product-review and seller-review areas. Rozetka also distinguishes reviews about a product from reviews about a seller/store. [Prom product-review rules](https://support.prom.ua/hc/uk/articles/19026061932189-%D0%9F%D1%80%D0%B0%D0%B2%D0%B8%D0%BB%D0%B0-%D0%BF%D1%83%D0%B1%D0%BB%D1%96%D0%BA%D0%B0%D1%86%D1%96%D1%97-%D0%B2%D1%96%D0%B4%D0%B3%D1%83%D0%BA%D1%96%D0%B2-%D0%BF%D1%80%D0%BE-%D1%82%D0%BE%D0%B2%D0%B0%D1%80%D0%B8-%D1%82%D0%B0-%D0%BA%D0%BE%D0%BC%D0%B5%D0%BD%D1%82%D0%B0%D1%80%D1%96%D0%B2-%D0%B4%D0%BE-%D0%BD%D0%B8%D1%85-%D0%BD%D0%B0-Prom-ua) · [Rozetka product review guidance](https://sellerhelp.rozetka.com.ua/p187-product-reviews.html) · [Rozetka review rules](https://rozetka.com.ua/ua/pages/kommentarii_otzivy/)
- A different seller page on the same marketplace is not a second independent domain. The same is true of `fit.rozetka.com.ua` versus `rozetka.com.ua`.
- Manufacturer-hosted reviews are useful only as manufacturer-site material under the product-facts policy; they do not count as independent review platforms for the two-domain threshold.
- Marketplace pages may group product variants or seller listings. Require the exact article/EAN where available; otherwise match the full product name, formula, flavor, format and package size. Reject family-level matches when the excerpt does not identify its variant.

## Recommended fast search policy

1. For a buyer-experience question, build the query from the selected product's brand, complete model, exact variant/package, and a constrained experience topic. Do not send reviewer identity or arbitrary personal details.
2. Use one fast Tavily request, capped at five results, restricted to approved product-review domains. Start with `rozetka.com.ua` and `prom.ua`; add `makeup.com.ua` for supplements. Include `epicentrk.ua` only when an exact catalog item has a populated page.
3. Verify the result belongs to the exact item. Count at most one source per registrable domain; deduplicate copied/syndicated pages and shared review snippets.
4. Pass no more than short, redacted excerpts from two distinct qualifying domains to the final model call. If there are fewer than two, omit the theme.
5. Allow only subjective, non-medical experience themes such as taste, texture, solubility, package convenience or fit/comfort. Reject review-derived claims about benefits, symptom changes, side effects, safety, dosage, interactions or efficacy. Do not quote or name reviewers or claim how common a theme is.

## Limits of this research

- The search sampled public category and item pages; it did not enumerate the full Race Expert catalog or measure review coverage for each SKU.
- A page's current review count is volatile. Counts above are discovery evidence only, not a guarantee of future availability.
- This report did not make a Tavily API call, test Tavily's result access to any platform, crawl/retrieve full review pages, query the product database, or inspect `.env`.
- Before using any domain in production, review provider reachability and the platform's current access/usage terms. A platform being publicly indexed does not establish permission for every form of automated reuse.
