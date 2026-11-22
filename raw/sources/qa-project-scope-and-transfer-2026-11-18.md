# Q&A project separation record — 2026-11-18

This project was separated from the combined Race Expert product-assistant workspace at the user's request. It contains a standalone question-answer application, the active Q&A prompt, historical Q&A prompts, evaluation fixtures and results, Q&A design documents, and a Q&A-only Wiki.

The runtime selects one product by exact model or SKU, confirms the selected product again before answering, and sends the Ukrainian card context plus the current question to GPT-6 Luna. Prompt v12 requires Ukrainian answers regardless of the question language. The local SQLite journal stores Q&A attempts only.

The new app reads product-card fields from five OpenCart tables using read-only SQL. It requires TLS CA and server-identity verification. No credentials were copied. This project was not connected to the live database, did not call OpenAI, and was not deployed during the transfer. The existing staging application remains unchanged.

Q&A evaluation records, including human scoring of model answers, were retained because they assess the question-answer system. They are not buyer-written product feedback. No feedback ingestion or summarization runtime was transferred.
