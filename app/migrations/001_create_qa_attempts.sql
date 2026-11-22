CREATE TABLE IF NOT EXISTS attempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    submitted_at TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    article TEXT NOT NULL,
    product_model TEXT,
    product_sku TEXT,
    product_name TEXT,
    question TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'succeeded', 'error')),
    answer TEXT,
    error_code TEXT,
    model_name TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    CHECK (
        (status = 'pending' AND answer IS NULL AND error_code IS NULL)
        OR (status = 'succeeded' AND answer IS NOT NULL AND error_code IS NULL)
        OR (status = 'error' AND answer IS NULL AND error_code IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_attempts_history
    ON attempts (submitted_at DESC, attempt_id DESC);
