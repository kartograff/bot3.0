from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def add_tire_to_user_car(user_car_id, tire_size_id, is_primary=False, quantity=4):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO user_car_tires (user_car_id, tire_size_id, is_primary, quantity)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_car_id, tire_size_id) DO UPDATE SET
                is_primary = EXCLUDED.is_primary,
                quantity = EXCLUDED.quantity
        """, (user_car_id, tire_size_id, is_primary, quantity))
        conn.commit()
        logger.info(f"Tire {tire_size_id} added to car {user_car_id}.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding tire to car: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_tires_for_user_car(user_car_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT ts.id, ts.width, ts.profile, ts.diameter, ts.description,
                   uct.is_primary, uct.quantity
            FROM user_car_tires uct
            JOIN tire_sizes ts ON uct.tire_size_id = ts.id
            WHERE uct.user_car_id = %s
        """, (user_car_id,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'width': r[1],
            'profile': r[2],
            'diameter': float(r[3]),
            'description': r[4],
            'is_primary': r[5],
            'quantity': r[6],
            'display': f"{r[1]}/{r[2]} R{r[3]}"
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def remove_tire_from_user_car(user_car_id, tire_size_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM user_car_tires WHERE user_car_id = %s AND tire_size_id = %s",
                    (user_car_id, tire_size_id))
        conn.commit()
        logger.info(f"Tire {tire_size_id} removed from car {user_car_id}.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error removing tire: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)