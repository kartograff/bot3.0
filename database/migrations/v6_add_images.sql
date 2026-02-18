-- =====================================================
-- Silent hours and delayed notifications
-- =====================================================

-- Add silent hours settings to settings table (if not exists)
INSERT INTO settings (key, value, description) VALUES
    ('silent_hours_enabled', 'false', 'Включить тихие часы'),
    ('silent_hours_start', '22:00', 'Начало тихого периода'),
    ('silent_hours_end', '07:00', 'Окончание тихого периода'),
    ('silent_hours_timezone', 'Europe/Moscow', 'Часовой пояс'),
    ('silent_hours_allow_emergency', 'false', 'Разрешить экстренные уведомления'),
    ('emergency_keywords', 'срочно,важно,критично', 'Ключевые слова для экстренных уведомлений'),
    ('emergency_user_ids', '', 'ID пользователей, от которых всегда пропускать'),
    ('morning_notification_time', '09:00', 'Время утренней отправки уведомлений'),
    ('max_notification_retries', '3', 'Максимальное количество попыток отправки')
ON CONFLICT (key) DO NOTHING;

-- Delayed notifications table
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