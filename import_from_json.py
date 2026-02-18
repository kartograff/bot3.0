#!/usr/bin/env python3
"""
Импорт марок и моделей автомобилей из JSON-файла (json.csv) в PostgreSQL.
Файл должен быть в формате JSON (массив объектов) с полями:
    brand, model, start_year, end_year
"""

import json
import asyncio
import logging
from database.connection import get_db_connection, return_db_connection
from database.crud.car_brands import create_brand, get_brand_by_name  # нужна функция поиска марки по имени
from database.crud.car_models import create_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JSON_FILE = "json.csv"  # хотя расширение .csv, это JSON

def load_data():
    """Загружает данные из JSON-файла."""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_brand_id_by_name(name):
    """Возвращает ID марки по имени, если она уже существует."""
    # Можно добавить функцию в car_brands.py: get_brand_by_name
    # Здесь временно используем прямой запрос
    from database.connection import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM car_brands WHERE name = %s", (name,))
    row = cur.fetchone()
    cur.close()
    return_db_connection(conn)
    return row[0] if row else None

async def import_brands_and_models():
    data = load_data()
    logger.info(f"Загружено записей: {len(data)}")

    brand_cache = {}  # имя марки -> её ID в БД

    for item in data:
        brand_name = item['brand'].strip()
        model_name = item['model'].strip()
        start_year = item['start_year']
        end_year = item['end_year']

        # Преобразуем пустые строки в None
        start_year = int(start_year) if start_year and start_year.strip() else None
        end_year = int(end_year) if end_year and end_year.strip() else None

        # Проверяем, есть ли марка в кеше
        if brand_name not in brand_cache:
            # Ищем марку в БД
            brand_id = get_brand_id_by_name(brand_name)
            if not brand_id:
                # Создаём новую марку
                brand_data = {
                    'name': brand_name,
                    'country': None,
                    'logo_url': None,
                    'is_active': True,
                    'sort_order': 0
                }
                brand_id = await asyncio.to_thread(create_brand, brand_data)
                logger.info(f"Создана марка: {brand_name} (ID {brand_id})")
            brand_cache[brand_name] = brand_id

        brand_id = brand_cache[brand_name]

        # Создаём модель
        model_data = {
            'brand_id': brand_id,
            'name': model_name,
            'start_year': start_year,
            'end_year': end_year,
            'vehicle_type_id': 1,  # по умолчанию легковой автомобиль
            'is_active': True
        }
        try:
            new_model_id = await asyncio.to_thread(create_model, model_data)
            logger.info(f"Создана модель: {model_name} (ID {new_model_id}) для марки {brand_name}")
        except Exception as e:
            logger.error(f"Ошибка при создании модели {model_name}: {e}")

    logger.info("Импорт завершён.")

async def main():
    await import_brands_and_models()

if __name__ == "__main__":
    asyncio.run(main())