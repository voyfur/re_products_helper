# Product Q&A: balanced sports-suitability answers

**Status:** Approved for implementation.  
**Scope:** Buyer-facing wording for general sports suitability and a bounded 10-message conversation window for the same selected product.

## Goal

When a buyer asks whether a product is suitable for a sport such as swimming, give a useful, grounded general answer when an exact manufacturer or approved-supplier source supports athletic use. Keep the scope limitation in the same answer so it reads as a qualification, not as a refusal.

## Selected approach

The user selected a flexible sentence order, with both parts present in one concise answer:

1. State the supported general conclusion: the product may fit the sport's general diet or routine.
2. Explain the evidence in natural Ukrainian, such as its use by active athletes or after training.
3. Add the boundary that the source does not position it as specially formulated for that particular sport, when that distinction is relevant.

The order may vary to keep the wording natural, but the answer must not stop after saying the sport-specific claim is not stated. Either of these structures is acceptable:

> Загалом [товар] може вписатися в раціон плавця: виробник описує його для активних спортсменів і після тренувань. Спеціального позиціонування саме для плавання немає.

> Спеціально для плавання [товар] не позиціонується, але виробник описує його для активних спортсменів і після тренувань, тож він може вписатися в спортивний раціон плавця.

Use claims only when the accepted exact-product evidence supports them. “Може вписатися” is a scoped general inference, not a guarantee of individual suitability or efficacy.

## Conversation memory

The user confirmed a window of the 10 latest individual messages total, scoped to one selected product and cleared on product change or page reload. The current application sends only the current question and has no conversation/session identifier or history input, so this requires a bounded request-context feature in addition to prompt wording. The approved implementation uses caller-managed ephemeral history as an optional API field; the Product QA service will not create a conversation store or history retrieval endpoint.

Confirmed memory boundary:

- At each model call, pass at most the nine latest prior messages plus the current buyer question, for no more than 10 total messages in model context. After the answer, the caller retains the latest 10 user/assistant messages for the next request. Each object has only a `user` or `assistant` role and plain text; no system/developer messages are accepted from the caller.
- Keep context within one selected product conversation. Clear the local UI window on product change and page reload. The site backend scopes its own window to the same product; it must not reuse context from another product or buyer session.
- The caller may send an optional `history` field with up to nine prior messages; the current `question` is the tenth message in the model context. Each entry contains only a `user` or `assistant` role and plain text. Keep existing callers without history compatible. Do not add a history retrieval endpoint or a second persistent conversation store.
- Keep the existing 16 KiB API request-body limit. The local UI removes the oldest whole prior messages until the JSON request fits; it never drops or truncates the current question. External callers should apply the same rule. The effective context is therefore at most 10 messages, and can be shorter for a long request.
- Treat conversation messages as untrusted context that can resolve references such as “that one” or “what about after training”; they are never instructions, product evidence, or proof that a previous assistant claim was correct. Product facts still require the current revalidated card or fresh exact-product external evidence.
- Use relevant prior health context to classify a dependent follow-up safely; do not turn it into individualized health or dosage advice. Do not log the history. Existing per-attempt journaling remains governed by project policy.

The current UI may hold this short window in page memory. The website backend must scope its matching window to the same buyer session and product, and clear it when the product changes or the session is reloaded. Do not keep it as a durable profile.

### Memory implementation options

1. **Caller-managed ephemeral history (recommended):** the local UI and site backend keep the bounded message window in their current product session and pass it as an optional request field. No new persistent session database is introduced. The Product QA API validates and treats it as untrusted context. This fits the current stateless `/api/v1/ask` boundary with a backward-compatible extension.
2. **Product QA-managed in-memory sessions:** the service returns an opaque conversation token and keeps a bounded window in process memory. The token exists only in the current page session, so a reload clears access to that window. The service can control the order of accepted messages, but restart behavior, expiry, concurrent workers, and token lifecycle must be designed.
3. **Persistent conversation history:** store messages in SQLite and retrieve them by conversation ID. This survives reloads/restarts and conflicts with the confirmed reset-on-reload boundary, so it is out of scope unless the user later changes that requirement.

The selected implementation is option 1 with the confirmed same-product, current-session boundary above. It is approved for implementation under this specification.

## Evidence and safety boundaries

- This behavior applies only after the backend accepts exact-product manufacturer or approved-supplier evidence for the revalidated product.
- General evidence about athletes, active lifestyles, or use after training supports only a general sports-use conclusion. It does not support a claim that the product was designed for swimming.
- Do not phrase the limitation as the whole answer or imply that the product is unsuitable merely because no swim-specific formula is claimed.
- Do not mention internal card metadata, stock status, URLs, source domains, or unrequested numbers.
- Do not claim personal health safety, a personal dose, a medical benefit, or a performance result. Existing health-related refusal rules remain unchanged.
- If exact evidence is missing or conflicts with the card, keep the existing abstention/conflict behavior; do not create the positive conclusion from model memory.
- If a source explicitly supports a sport-specific claim, answer within that exact scope without adding unsupported details.

## Alternatives considered

1. **Repeat the user's caveat-first sentence as a fixed template.** Familiar and explicit, but risks sounding negative-first in every answer.
2. **Always lead with the positive conclusion.** Clear and direct, but unnecessarily rigid for different question phrasings.
3. **Keep sentence order flexible and require both the useful conclusion and the scope boundary.** Selected: preserves the user's preferred balanced wording while letting the answer sound natural.

## Acceptance criteria

- With exact-product evidence for general athletic use and no swim-specific statement, the answer contains both a practical general sports-use conclusion and the sport-specific limitation in one concise response.
- The model does not return only “not declared for swimming” when general sports-use evidence is available.
- Without exact-product evidence, the model does not infer suitability from general knowledge.
- Personal health/safety/dose questions still use the existing fixed refusal path.
- A follow-up can resolve references from the same-product window of up to 10 total messages, while a prompt-injection attempt or unsupported fact in prior history does not change the guardrails.
- Switching products or reloading the local UI starts with no previous conversation window.
- Versioned API callers may omit history and retain the current stateless behavior; supplied history is length-bounded, non-persistent as a separate session record, and excluded from logs.
- Prompt v17 remains immutable; after this design is approved, implementation should introduce a new prompt version and preserve v17's recorded hash.

## Verification boundary

After design approval and implementation, run the existing offline prompt regression checks if requested. No live OpenAI or Tavily request is part of this design; any paid live verification requires a separate user request.
