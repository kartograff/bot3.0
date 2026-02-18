-- =====================================================
-- Add vehicle_type_id to car_models (if not already present)
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='car_models' AND column_name='vehicle_type_id') THEN
        ALTER TABLE car_models ADD COLUMN vehicle_type_id INTEGER REFERENCES vehicle_types(id) ON DELETE SET NULL;
        CREATE INDEX idx_car_models_vehicle_type ON car_models(vehicle_type_id);
    END IF;
END $$;

-- Optionally set a default vehicle type for existing rows
UPDATE car_models SET vehicle_type_id = 1 WHERE vehicle_type_id IS NULL;