# Q&A evaluation source-reference migration — 2026-11-18

Evaluation cases and historical run artifacts were copied from the source project. The cases' original source_ref values pointed to product-card context and schema-audit notes in the combined workspace. The source notes were not transferred wholesale because they also described unrelated database areas. The product facts and Q&A test expectations are preserved in evals/product-contexts.json, evals/model-contexts.json, evals/guardrail-model-contexts.json, and the case files.

During transfer, source_ref fields in case files were redirected to this migration record. Questions, expected behavior, model contexts, saved model outputs, scores, and reports were otherwise retained.
