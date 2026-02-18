from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_years_by_model(model_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, year FROM car_years WHERE model_id = %s AND is_active = TRUE ORDER BY year", (model_id,))
        rows = cur.fetchall()
        return [{'id': r[0], 'year': r[1]} for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def create_year(data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO car_years (model_id, year, is_active)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (data['model_id'], data['year'], data.get('is_active', True)))
        year_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Year {data['year']} for model {data['model_id']} created.")
        return year_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating car year: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def update_year(year_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE car_years SET
                year = %s,
                is_active = %s
            WHERE id = %s
        """, (data['year'], data.get('is_active'), year_id))
        conn.commit()
        logger.info(f"Year {year_id} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating car year {year_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_year(year_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM car_years WHERE id = %s", (year_id,))
        conn.commit()
        logger.info(f"Year {year_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting car year {year_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)