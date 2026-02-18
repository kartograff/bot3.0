-- =====================================================
-- Telegram channels integration
-- =====================================================

-- Channels table
CREATE TABLE IF NOT EXISTS telegram_channels (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL UNIQUE,
    channel_name VARCHAR(255) NOT NULL,
    channel_username VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    added_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    added_at TIMESTAMP DEFAULT NOW()
);

-- Publish settings per channel
CREATE TABLE IF NOT EXISTS channel_publish_settings (
    channel_id INTEGER REFERENCES telegram_channels(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    message_template TEXT,
    PRIMARY KEY (channel_id, event_type)
);

-- Posts history
CREATE TABLE IF NOT EXISTS channel_posts (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES telegram_channels(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    related_id INTEGER,
    message_id INTEGER,
    published_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'success'
);

CREATE INDEX IF NOT EXISTS idx_channel_posts_channel ON channel_posts(channel_id);
CREATE INDEX IF NOT EXISTS idx_channel_posts_published ON channel_posts(published_at);