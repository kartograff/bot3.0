from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_all_brands():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, name, first_letter, logo_url, country, is_active, sort_order
            FROM car_brands
            ORDER BY sort_order, name
        """)
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'name': r[1],
            'first_letter': r[2],
            'logo_url': r[3],
            'country': r[4],
            'is_active': r[5],
            'sort_order': r[6]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_brand(brand_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, name, first_letter, logo_url, country, is_active, sort_order
            FROM car_brands WHERE id = %s
        """, (brand_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'first_letter': row[2],
                'logo_url': row[3],
                'country': row[4],
                'is_active': row[5],
                'sort_order': row[6]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def create_brand(data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO car_brands (name, logo_url, country, is_active, sort_order)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (data['name'], data.get('logo_url'), data.get('country'), data.get('is_active', True), data.get('sort_order', 0)))
        brand_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Brand {data['name']} created with id {brand_id}.")
        return brand_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating brand: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def update_brand(brand_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE car_brands SET
                name = %s,
                logo_url = %s,
                country = %s,
                is_active = %s,
                sort_order = %s
            WHERE id = %s
        """, (data['name'], data.get('logo_url'), data.get('country'), data.get('is_active'), data.get('sort_order'), brand_id))
        conn.commit()
        logger.info(f"Brand {brand_id} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating brand {brand_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_brand(brand_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM car_brands WHERE id = %s", (brand_id,))
        conn.commit()
        logger.info(f"Brand {brand_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting brand {brand_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_brands_count():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM car_brands WHERE is_active = TRUE")
        return cur.fetchone()[0]
    finally:
        cur.close()
        return_db_connection(conn)


def get_brands_grouped_by_letter():
    """
    Возвращает словарь {буква: [марки]} для всех активных марок.
    Используется для построения клавиатуры выбора по первой букве.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT first_letter, id, name, logo_url
            FROM car_brands
            WHERE is_active = TRUE
            ORDER BY first_letter, name
        """)
        rows = cur.fetchall()
        result = {}
        for letter, brand_id, name, logo_url in rows:
            if letter not in result:
                result[letter] = []
            result[letter].append({
                'id': brand_id,
                'name': name,
                'logo_url': logo_url
            })
        return result
    finally:
        cur.close()
        return_db_connection(conn)

def get_brands_by_letter(letter):
    """
    Возвращает список марок, начинающихся на указанную букву.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, name, logo_url, country
            FROM car_brands
            WHERE first_letter = %s AND is_active = TRUE
            ORDER BY name
        """, (letter,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'name': r[1],
            'logo_url': r[2],
            'country': r[3]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)