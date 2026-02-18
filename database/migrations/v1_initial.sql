-- =====================================================
-- Initial schema: users, appointments, services, settings
-- =====================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    is_admin BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle types (for services)
CREATE TABLE IF NOT EXISTS vehicle_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE
);

-- Services
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    vehicle_type_id INTEGER REFERENCES vehicle_types(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Appointments
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(id) ON DELETE SET NULL,
    user_car_id INTEGER,  -- will be referenced later
    tire_size_id INTEGER, -- will be referenced later
    date DATE NOT NULL,
    time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    admin_comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Settings
CREATE TABLE IF NOT EXISTS settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    description TEXT
);

-- Insert default settings
INSERT INTO settings (key, value, description) VALUES
    ('shop_name', 'Автосервис', 'Название предприятия'),
    ('about_info', 'Информация о нас отсутствует. Добавьте её в настройках.', 'Текст раздела "О нас"'),
    ('phone', '', 'Контактный телефон'),
    ('address', '', 'Адрес'),
    ('working_hours', 'Пн-Пт: 9:00-19:00, Сб: 10:00-17:00, Вс: выходной', 'Режим работы')
ON CONFLICT (key) DO NOTHING;

-- Insert default vehicle types
INSERT INTO vehicle_types (name, code) VALUES
    ('Легковой автомобиль', 'car'),
    ('Джип', 'suv'),
    ('Грузовой автомобиль', 'truck'),
    ('Мотоцикл', 'motorcycle')
ON CONFLICT (code) DO NOTHING;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);