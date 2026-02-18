-- =====================================================
-- Complete automotive catalog
-- =====================================================

-- Car brands
CREATE TABLE IF NOT EXISTS car_brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    first_letter CHAR(1) GENERATED ALWAYS AS (UPPER(LEFT(name, 1))) STORED,
    logo_url VARCHAR(255),
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_car_brands_first_letter ON car_brands(first_letter);

-- Car models (now with vehicle_type_id)
CREATE TABLE IF NOT EXISTS car_models (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER NOT NULL REFERENCES car_brands(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    start_year INTEGER,
    end_year INTEGER,
    vehicle_type_id INTEGER REFERENCES vehicle_types(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(brand_id, name)
);

CREATE INDEX IF NOT EXISTS idx_car_models_brand_id ON car_models(brand_id);
CREATE INDEX IF NOT EXISTS idx_car_models_vehicle_type ON car_models(vehicle_type_id);

-- Car years
CREATE TABLE IF NOT EXISTS car_years (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES car_models(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(model_id, year)
);

CREATE INDEX IF NOT EXISTS idx_car_years_model_id ON car_years(model_id);

-- Tire sizes
CREATE TABLE IF NOT EXISTS tire_sizes (
    id SERIAL PRIMARY KEY,
    width INTEGER NOT NULL CHECK (width > 0),
    profile INTEGER NOT NULL CHECK (profile > 0),
    diameter NUMERIC(3,1) NOT NULL CHECK (diameter > 0),
    display_string VARCHAR(50) GENERATED ALWAYS AS (width || '/' || profile || ' R' || diameter) STORED,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(width, profile, diameter)
);

CREATE INDEX IF NOT EXISTS idx_tire_sizes_width ON tire_sizes(width);
CREATE INDEX IF NOT EXISTS idx_tire_sizes_diameter ON tire_sizes(diameter);

-- User cars
CREATE TABLE IF NOT EXISTS user_cars (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    brand_id INTEGER NOT NULL REFERENCES car_brands(id),
    model_id INTEGER NOT NULL REFERENCES car_models(id),
    year_id INTEGER REFERENCES car_years(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_cars_user_id ON user_cars(user_id);

-- User car tires
CREATE TABLE IF NOT EXISTS user_car_tires (
    id SERIAL PRIMARY KEY,
    user_car_id INTEGER NOT NULL REFERENCES user_cars(id) ON DELETE CASCADE,
    tire_size_id INTEGER NOT NULL REFERENCES tire_sizes(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    quantity INTEGER DEFAULT 4,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_car_id, tire_size_id)
);

CREATE INDEX IF NOT EXISTS idx_user_car_tires_car_id ON user_car_tires(user_car_id);

-- Add foreign keys to appointments (if not already present)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='appointments' AND column_name='user_car_id') THEN
        ALTER TABLE appointments ADD COLUMN user_car_id INTEGER REFERENCES user_cars(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='appointments' AND column_name='tire_size_id') THEN
        ALTER TABLE appointments ADD COLUMN tire_size_id INTEGER REFERENCES tire_sizes(id) ON DELETE SET NULL;
    END IF;
END $$;