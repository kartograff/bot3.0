-- =====================================================
-- Cleanup: remove unused or obsolete tables
-- =====================================================

-- Drop tables that are not needed in the current architecture
DROP TABLE IF EXISTS wheel_sizes CASCADE;
DROP TABLE IF EXISTS car_tire_fits CASCADE;
DROP TABLE IF EXISTS car_wheel_fits CASCADE;
DROP TABLE IF EXISTS tire_seasons CASCADE;

-- Drop any temporary or test tables if they exist
DROP TABLE IF EXISTS temp_data CASCADE;
DROP TABLE IF EXISTS test_users CASCADE;
DROP TABLE IF EXISTS test_appointments CASCADE;
DROP TABLE IF EXISTS old_migrations CASCADE;