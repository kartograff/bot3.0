import sqlite3
import psycopg2
from psycopg2 import sql, extras

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ К POSTGRESQL (ЗАМЕНИТЕ НА СВОИ) ---
PG_HOST = 'localhost'
PG_PORT = 5432
PG_DB = 'cars'          # имя базы данных в PostgreSQL
PG_USER = 'postgres'
PG_PASSWORD = 'password'

# --- ПОДКЛЮЧЕНИЕ К SQLITE ---
sqlite_conn = sqlite3.connect('cars.db')
sqlite_conn.row_factory = sqlite3.Row  # чтобы обращаться по именам столбцов
sqlite_cursor = sqlite_conn.cursor()

# --- ПОДКЛЮЧЕНИЕ К POSTGRESQL ---
pg_conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASSWORD
)
pg_cursor = pg_conn.cursor()

# --- СОЗДАНИЕ ТАБЛИЦ В POSTGRESQL (ЕСЛИ НЕ СУЩЕСТВУЮТ) ---
create_tables_sql = """
-- Таблица марок
CREATE TABLE IF NOT EXISTS brands (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

-- Таблица моделей
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL
);
"""
pg_cursor.execute(create_tables_sql)
pg_conn.commit()
print("Таблицы brands и models проверены/созданы в PostgreSQL.")

# --- ПЕРЕНОС ДАННЫХ ИЗ ТАБЛИЦЫ brands ---
print("Перенос данных из brands...")
sqlite_cursor.execute("SELECT id, name FROM brands")
brands_data = sqlite_cursor.fetchall()

insert_brand = """
INSERT INTO brands (id, name) VALUES (%s, %s)
ON CONFLICT (id) DO NOTHING
"""
for row in brands_data:
    pg_cursor.execute(insert_brand, (row['id'], row['name']))
pg_conn.commit()
print(f"Добавлено/пропущено марок: {len(brands_data)}")

# --- ПЕРЕНОС ДАННЫХ ИЗ ТАБЛИЦЫ models ---
print("Перенос данных из models...")
sqlite_cursor.execute("SELECT id, brand_id, name FROM models")
models_data = sqlite_cursor.fetchall()

insert_model = """
INSERT INTO models (id, brand_id, name) VALUES (%s, %s, %s)
ON CONFLICT (id) DO NOTHING
"""
for row in models_data:
    pg_cursor.execute(insert_model, (row['id'], row['brand_id'], row['name']))
pg_conn.commit()
print(f"Добавлено/пропущено моделей: {len(models_data)}")

# --- ЗАКРЫТИЕ СОЕДИНЕНИЙ ---
sqlite_cursor.close()
sqlite_conn.close()
pg_cursor.close()
pg_conn.close()

print("Перенос завершён.")