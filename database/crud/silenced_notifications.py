from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_pending_notifications(limit=100):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, notification_type, user_id, appointment_id, message_text,
                   notification_data, retry_count, scheduled_for
            FROM silenced_notifications
            WHERE status = 'pending' AND scheduled_for <= NOW()
            ORDER BY scheduled_for
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'type': r[1],
            'user_id': r[2],
            'appointment_id': r[3],
            'message': r[4],
            'data': r[5],
            'retry_count': r[6],
            'scheduled_for': r[7]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def update_notification_status(notif_id, status, last_attempt=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if last_attempt:
            cur.execute("UPDATE silenced_notifications SET status = %s, last_attempt = %s WHERE id = %s",
                        (status, last_attempt, notif_id))
        else:
            cur.execute("UPDATE silenced_notifications SET status = %s WHERE id = %s", (status, notif_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating notification {notif_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def increment_retry_and_reschedule(notif_id, new_schedule):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE silenced_notifications
            SET retry_count = retry_count + 1, scheduled_for = %s, last_attempt = NOW()
            WHERE id = %s
        """, (new_schedule, notif_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error incrementing retry for {notif_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_notification(notif_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM silenced_notifications WHERE id = %s", (notif_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting notification {notif_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)