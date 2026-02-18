from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_models_by_brand(brand_id, vehicle_type_id=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = """
            SELECT cm.id, cm.name, cm.start_year, cm.end_year, cm.is_active,
                   vt.name as vehicle_type_name
            FROM car_models cm
            LEFT JOIN vehicle_types vt ON cm.vehicle_type_id = vt.id
            WHERE cm.brand_id = %s
        """
        params = [brand_id]
        if vehicle_type_id:
            query += " AND cm.vehicle_type_id = %s"
            params.append(vehicle_type_id)
        query += " ORDER BY cm.name"
        cur.execute(query, params)
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'name': r[1],
            'start_year': r[2],
            'end_year': r[3],
            'is_active': r[4],
            'vehicle_type_name': r[5]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_model(model_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT cm.id, cm.name, cm.start_year, cm.end_year, cm.is_active,
                   cm.vehicle_type_id, cb.id as brand_id, cb.name as brand_name
            FROM car_models cm
            JOIN car_brands cb ON cm.brand_id = cb.id
            WHERE cm.id = %s
        """, (model_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'start_year': row[2],
                'end_year': row[3],
                'is_active': row[4],
                'vehicle_type_id': row[5],
                'brand_id': row[6],
                'brand_name': row[7]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def create_model(data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO car_models (brand_id, name, start_year, end_year, vehicle_type_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (data['brand_id'], data['name'], data.get('start_year'), data.get('end_year'), data['vehicle_type_id'], data.get('is_active', True)))
        model_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Model {data['name']} created with id {model_id}.")
        return model_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating model: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def update_model(model_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE car_models SET
                name = %s,
                start_year = %s,
                end_year = %s,
                vehicle_type_id = %s,
                is_active = %s
            WHERE id = %s
        """, (data['name'], data.get('start_year'), data.get('end_year'), data['vehicle_type_id'], data.get('is_active'), model_id))
        conn.commit()
        logger.info(f"Model {model_id} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating model {model_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_model(model_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM car_models WHERE id = %s", (model_id,))
        conn.commit()
        logger.info(f"Model {model_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting model {model_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)