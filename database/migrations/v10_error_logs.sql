-- =====================================================
-- Error logging tables
-- =====================================================

-- Detailed error logs
CREATE TABLE IF NOT EXISTS error_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,           -- 'ERROR', 'CRITICAL', 'WARNING'
    source VARCHAR(255),
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    traceback TEXT,
    request_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_error_logs_level ON error_logs(level);
CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON error_logs(created_at);

-- Error statistics (grouped)
CREATE TABLE IF NOT EXISTS error_stats (
    id SERIAL PRIMARY KEY,
    error_hash VARCHAR(64),               -- hash for grouping similar errors
    error_type VARCHAR(255),
    count INTEGER DEFAULT 1,
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    comment TEXT
);