from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def create_user_car(user_id, brand_id, model_id, year_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO user_cars (user_id, brand_id, model_id, year_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, brand_id, model_id, year_id))
        car_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"User car {car_id} created for user {user_id}.")
        return car_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating user car: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_user_cars(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT uc.id, cb.name, cm.name, cy.year, uc.is_active
            FROM user_cars uc
            JOIN car_brands cb ON uc.brand_id = cb.id
            JOIN car_models cm ON uc.model_id = cm.id
            LEFT JOIN car_years cy ON uc.year_id = cy.id
            WHERE uc.user_id = %s AND uc.is_active = TRUE
            ORDER BY uc.created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'brand': r[1],
            'model': r[2],
            'year': r[3],
            'is_active': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_user_car(car_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT uc.id, uc.user_id, cb.name, cm.name, cy.year, uc.is_active
            FROM user_cars uc
            JOIN car_brands cb ON uc.brand_id = cb.id
            JOIN car_models cm ON uc.model_id = cm.id
            LEFT JOIN car_years cy ON uc.year_id = cy.id
            WHERE uc.id = %s
        """, (car_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'brand': row[2],
                'model': row[3],
                'year': row[4],
                'is_active': row[5]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def delete_user_car(car_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM user_cars WHERE id = %s", (car_id,))
        conn.commit()
        logger.info(f"User car {car_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting user car {car_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)