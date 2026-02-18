from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_setting(key, default=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
        row = cur.fetchone()
        return row[0] if row else default
    finally:
        cur.close()
        return_db_connection(conn)

def update_setting(key, value):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO settings (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, (key, value))
        conn.commit()
        logger.info(f"Setting {key} updated to {value}.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating setting {key}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_silent_hours_settings():
    """Return dict of silent hours settings."""
    return {
        'enabled': get_setting('silent_hours_enabled') == 'true',
        'start': get_setting('silent_hours_start') or '22:00',
        'end': get_setting('silent_hours_end') or '07:00',
        'timezone': get_setting('silent_hours_timezone') or 'Europe/Moscow',
        'allow_emergency': get_setting('silent_hours_allow_emergency') == 'true',
        'emergency_keywords': (get_setting('emergency_keywords') or 'срочно,важно,критично').split(','),
        'emergency_user_ids': (get_setting('emergency_user_ids') or '').split(',') if get_setting('emergency_user_ids') else []
    }