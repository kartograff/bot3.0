from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def create_service(data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO services (name, description, price, vehicle_type_id, is_active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (data['name'], data.get('description'), data.get('price'), data.get('vehicle_type_id'), data.get('is_active', True)))
        svc_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Service {svc_id} created.")
        return svc_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating service: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_service(service_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT s.id, s.name, s.description, s.price, vt.name as vehicle_type, s.is_active
            FROM services s
            LEFT JOIN vehicle_types vt ON s.vehicle_type_id = vt.id
            WHERE s.id = %s
        """, (service_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'vehicle_type': row[4],
                'is_active': row[5]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def get_services(vehicle_type_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if vehicle_type_id:
            cur.execute("""
                SELECT s.id, s.name, s.description, s.price, vt.name as vehicle_type, s.is_active
                FROM services s
                LEFT JOIN vehicle_types vt ON s.vehicle_type_id = vt.id
                WHERE s.vehicle_type_id = %s OR s.vehicle_type_id IS NULL
                ORDER BY s.name
            """, (vehicle_type_id,))
        else:
            cur.execute("""
                SELECT s.id, s.name, s.description, s.price, vt.name as vehicle_type, s.is_active
                FROM services s
                LEFT JOIN vehicle_types vt ON s.vehicle_type_id = vt.id
                ORDER BY s.name
            """)
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'name': r[1],
            'description': r[2],
            'price': r[3],
            'vehicle_type_name': r[4],
            'is_active': r[5]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def update_service(service_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE services SET
                name = %s,
                description = %s,
                price = %s,
                vehicle_type_id = %s,
                is_active = %s
            WHERE id = %s
        """, (data['name'], data.get('description'), data.get('price'), data.get('vehicle_type_id'), data.get('is_active'), service_id))
        conn.commit()
        logger.info(f"Service {service_id} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating service {service_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_service(service_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
        conn.commit()
        logger.info(f"Service {service_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting service {service_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_services_count():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM services WHERE is_active = TRUE")
        return cur.fetchone()[0]
    finally:
        cur.close()
        return_db_connection(conn)