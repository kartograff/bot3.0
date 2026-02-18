-- =====================================================
-- Backups management
-- =====================================================

CREATE TABLE IF NOT EXISTS backups (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(512) NOT NULL,
    filesize BIGINT,
    type VARCHAR(50) DEFAULT 'manual',      -- 'manual' or 'automatic'
    status VARCHAR(50) DEFAULT 'completed', -- 'completed', 'failed', 'in_progress'
    created_at TIMESTAMP DEFAULT NOW(),
    created_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    comment TEXT,
    restored_at TIMESTAMP,
    restored_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_backups_created_at ON backups(created_at);