# Q&A staging boundary and access — captured 2026-11-18

## Scope

This note records the latest known Q&A deployment state so the standalone QA project is not confused with the older combined staging app. It contains no credentials.

## Latest recorded state

The Q&A prompt v12 was deployed to the existing combined test harness on 2026-11-16. The latest project status record dated 2026-11-17 says the combined staging image was raceexpert-test-harness:product-overview-v4-20261116 and the Q&A route still used prompt v12. The standalone project in the QA folder was not deployed there. It remains a local project.

The shared staging URL is https://n8n.raceexpert-tools.net.ua/re-products-demo/. Basic Auth was disabled by the user on 2026-11-16. The page, JavaScript, health endpoint, Q&A API, and product-overview API are therefore reachable without a password. The application has no GPT request-rate limit; use of the public link can create OpenAI charges. Production and storefront integration are not part of this project.

No Q&A model request was made after the v12 deployment in the recorded rollout. This status is from project notes and the historical rollout record; it was not rechecked over the network during this QA-folder audit.

## How to use this information

Do not treat the shared combined staging app as the standalone QA application. Do not deploy this folder to that host or send requests to its model APIs unless the user explicitly asks. The local Q&A-only run instructions are in docs/test-harness/local-session-runbook.md.

## Provenance

Captured from the Q&A v12 rollout record in raw/sessions/2026-11-16-set-race-expert-q-a-answers-to-ukrainian-only-wi.md and the current shared-project AGENTS.md status notes. This summary preserves only Q&A deployment/access facts.
