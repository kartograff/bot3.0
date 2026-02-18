from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def create_backup_record(filename, filepath, filesize, backup_type='manual', user_id=None, status='completed', comment=''):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO backups (filename, filepath, filesize, type, status, created_by, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (filename, filepath, filesize, backup_type, status, user_id, comment))
        backup_id = cur.fetchone()[0]
        conn.commit()
        return backup_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating backup record: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_backups(limit=50):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, filename, filepath, filesize, type, status, created_at, comment, restored_at, restored_by
            FROM backups
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'filename': r[1],
            'filepath': r[2],
            'filesize': r[3],
            'type': r[4],
            'status': r[5],
            'created_at': r[6],
            'comment': r[7],
            'restored_at': r[8],
            'restored_by': r[9]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def update_backup_restored(backup_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE backups SET restored_at = NOW(), restored_by = %s WHERE id = %s", (user_id, backup_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating backup restored: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_backup_record(backup_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM backups WHERE id = %s", (backup_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting backup record {backup_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)