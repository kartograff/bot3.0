from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_all_vehicle_types():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, code FROM vehicle_types ORDER BY name")
        rows = cur.fetchall()
        return [{'id': r[0], 'name': r[1], 'code': r[2]} for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_vehicle_type(type_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, code FROM vehicle_types WHERE id = %s", (type_id,))
        row = cur.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'code': row[2]}
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def create_vehicle_type(data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO vehicle_types (name, code) VALUES (%s, %s) RETURNING id",
                    (data['name'], data['code']))
        type_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Vehicle type {data['name']} created.")
        return type_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating vehicle type: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def update_vehicle_type(type_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE vehicle_types SET name = %s, code = %s WHERE id = %s",
                    (data['name'], data['code'], type_id))
        conn.commit()
        logger.info(f"Vehicle type {type_id} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating vehicle type {type_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_vehicle_type(type_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM vehicle_types WHERE id = %s", (type_id,))
        conn.commit()
        logger.info(f"Vehicle type {type_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting vehicle type {type_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)