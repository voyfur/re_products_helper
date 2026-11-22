ALTER TABLE attempts ADD COLUMN search_status TEXT NOT NULL DEFAULT 'skipped'
    CHECK (search_status IN ('skipped', 'used', 'failed'));
ALTER TABLE attempts ADD COLUMN search_provider TEXT;
ALTER TABLE attempts ADD COLUMN search_latency_ms INTEGER;
ALTER TABLE attempts ADD COLUMN total_latency_ms INTEGER;
ALTER TABLE attempts ADD COLUMN source_metadata_json TEXT NOT NULL DEFAULT '[]';
