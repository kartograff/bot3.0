from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_all_tire_sizes():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, width, profile, diameter, description
            FROM tire_sizes
            ORDER BY width, profile, diameter
        """)
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'width': r[1],
            'profile': r[2],
            'diameter': float(r[3]),
            'description': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_tire_size(size_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, width, profile, diameter, description
            FROM tire_sizes WHERE id = %s
        """, (size_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'width': row[1],
                'profile': row[2],
                'diameter': float(row[3]),
                'description': row[4]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def create_tire_size(data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO tire_sizes (width, profile, diameter, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data['width'], data['profile'], data['diameter'], data.get('description')))
        size_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Tire size {data['width']}/{data['profile']} R{data['diameter']} created.")
        return size_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating tire size: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def update_tire_size(size_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE tire_sizes SET
                width = %s,
                profile = %s,
                diameter = %s,
                description = %s
            WHERE id = %s
        """, (data['width'], data['profile'], data['diameter'], data.get('description'), size_id))
        conn.commit()
        logger.info(f"Tire size {size_id} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating tire size {size_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_tire_size(size_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM tire_sizes WHERE id = %s", (size_id,))
        conn.commit()
        logger.info(f"Tire size {size_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting tire size {size_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)


def get_common_tire_sizes(limit: int = 20) -> list:
    """
    Возвращает список популярных размеров шин.
    Используется для быстрого выбора при добавлении автомобиля.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, width, profile, diameter, description,
                   width || '/' || profile || ' R' || diameter as display
            FROM tire_sizes
            WHERE is_active = TRUE
            ORDER BY width, profile, diameter
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'width': r[1],
            'profile': r[2],
            'diameter': float(r[3]),
            'description': r[4],
            'display': r[5]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_or_create_tire_size(width: int, profile: int, diameter: float, description: str = None) -> int:
    """
    Возвращает ID существующего размера шин или создаёт новый, если такого нет.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Сначала пытаемся найти существующий
        cur.execute("""
            SELECT id FROM tire_sizes
            WHERE width = %s AND profile = %s AND diameter = %s
        """, (width, profile, diameter))
        row = cur.fetchone()
        if row:
            return row[0]
        
        # Если не нашли, создаём новый
        cur.execute("""
            INSERT INTO tire_sizes (width, profile, diameter, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (width, profile, diameter, description))
        tire_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Created new tire size: {width}/{profile} R{diameter}")
        return tire_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in get_or_create_tire_size: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def add_tire_to_user_car(user_car_id: int, tire_size_id: int, is_primary: bool = False, quantity: int = 4) -> None:
    """
    Привязывает размер шин к автомобилю пользователя.
    """
    # Реэкспорт из модуля user_car_tires
    from database.crud.user_car_tires import add_tire_to_user_car as _add
    return _add(user_car_id, tire_size_id, is_primary, quantity)