-- =====================================================
-- Delayed notifications table (for silent hours)
-- =====================================================

-- Table to store notifications that should be sent later
CREATE TABLE IF NOT EXISTS silenced_notifications (
    id SERIAL PRIMARY KEY,
    notification_type VARCHAR(50) NOT NULL,
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE SET NULL,
    message_text TEXT,
    scheduled_for TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    notification_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    last_attempt TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_silenced_notifications_scheduled ON silenced_notifications(scheduled_for) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_silenced_notifications_created ON silenced_notifications(created_at);

-- Ensure related settings exist
INSERT INTO settings (key, value, description) VALUES
    ('morning_notification_time', '09:00', 'Время утренней отправки отложенных уведомлений'),
    ('max_notification_retries', '3', 'Максимальное количество попыток отправки отложенных уведомлений')
ON CONFLICT (key) DO NOTHING;