from database.connection import get_db_connection, return_db_connection
import json
import logging

logger = logging.getLogger(__name__)

def log_action(user_id, action, details=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO logs (user_id, action, details)
            VALUES (%s, %s, %s)
        """, (user_id, action, json.dumps(details) if details else None))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error logging action: {e}")
    finally:
        cur.close()
        return_db_connection(conn)