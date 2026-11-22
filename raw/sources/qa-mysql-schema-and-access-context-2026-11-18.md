# Q&A MySQL schema, grants, and connection context — captured 2026-11-18

## Provenance and scope

This Q&A-only capture summarizes the connection and product-schema evidence needed by the standalone QA app. It was distilled from the combined project's read-only database audit, its MySQL query guide, and the current project instructions. It intentionally excludes review text, order records, review-summary behavior, unrelated OpenCart tables, credentials, and raw product descriptions.

## Database route and trust boundary

The historical read-only check connected through VPS-61125 (185.25.119.96) to the MySQL endpoint from the local environment, selected schema raceexpertcomua, and passed SELECT 1. On 2026-11-10 the server negotiated TLS 1.3; the CA and hostname were not verified. The configured endpoint was not independently confirmed by the database administrator as the current live-site database.

The standalone QA folder has its own .env and protected files under secrets/. The local runner checks the VPS SSH host key with StrictHostKeyChecking=yes, creates a temporary SSH forward, and requires MySQL TLS 1.2 or 1.3. It disables MySQL certificate and hostname checks only for that local session. This encrypts the MySQL connection but does not verify the MySQL server's identity. The direct connector requires a trusted CA and hostname verification; the corresponding local CA file is absent. Do not deploy the local-session setting.

A current local-filesystem audit confirmed that the QA .env and required MySQL password, OpenAI key, and SSH-key files exist with restrictive permissions, that the launcher can load its configuration without printing values, and that a matching VPS host-key entry exists in system known_hosts. SSH authentication, MySQL authentication, and OpenAI key validity were not tested by that audit.

## Current read-only permissions

The historical SHOW GRANTS FOR CURRENT_USER returned USAGE ON *.* and SELECT on seven tables:

- oc_product
- oc_product_description
- oc_product_attribute
- oc_attribute_description
- oc_stock_status
- oc_review
- oc_remarketing_orders

The Q&A code reads only the first five tables. The account therefore has broader read-only access than Q&A needs. Before any persistent deployment, use a dedicated MySQL account with SELECT only on the five Q&A tables. Q&A must not query oc_review, oc_remarketing_orders, orders, or customer records.

## Q&A table schema

The 2026-11-10 schema audit found these column counts and query-relevant keys:

| Table | Columns | Q&A fields and role |
|---|---:|---|
| oc_product | 35 | product_id primary key; model indexed but not unique; sku; selected-product identifier |
| oc_product_description | 10 | composite key product_id + language_id; name, description |
| oc_product_attribute | 4 | product_id, attribute_id, language_id, text |
| oc_attribute_description | 3 | composite key attribute_id + language_id; localized attribute name |
| oc_stock_status | 3 | composite key stock_status_id + language_id; localized stock name |

Language IDs 1 (Russian) and 6 (Ukrainian) were present in all localized tables. Schema counts and grants are a dated audit, not a guarantee the live schema is unchanged. Recheck the five tables with SHOW COLUMNS and SELECT * ... LIMIT 0 before changing SQL; these checks return metadata and no product rows.

## Runtime query boundary

app/catalog.py is the executable source of truth. Search compares the submitted article exactly against model and sku, binds values as parameters, sorts deterministically, and limits candidates to two so ambiguous matches are surfaced. After a user selects a product, /api/ask searches again and confirms that the submitted article still resolves to the submitted product_id.

The query reads the fields needed for model/SKU identity and the selected language cards: product name, description, localized stock label, and localized attributes. The model receives only the Ukrainian (language_id=6) card context and current question. The prompt is prompts/product-assistant-system-v12.md; response language is Ukrainian regardless of question language. Price, raw quantity, orders, buyers, other products, reviews, and previous questions are not supplied to the model.

## Historical locator files

The files raw/sources/mysql-current-product-schema-and-query-results-2026-11-10.md, raw/sources/mysql-readonly-product-context-re89157-2026-11-10.md, and raw/sources/phpmyadmin-opencart-product-audit-2026-11-03.md were retained as provenance locators during the Q&A transfer; they are not full copies of their original evidence. Q&A-specific schema, access, and route facts needed for future work are preserved in this capture and in wiki/sources/qa-mysql-readonly-access-and-product-query.md. Evaluation product facts remain in the versioned files under evals/.
