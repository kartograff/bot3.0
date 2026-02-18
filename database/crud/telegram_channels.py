from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def add_channel(channel_id, channel_name, channel_username=None, added_by=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO telegram_channels (channel_id, channel_name, channel_username, added_by)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (channel_id) DO UPDATE SET
                channel_name = EXCLUDED.channel_name,
                channel_username = EXCLUDED.channel_username,
                is_active = TRUE
            RETURNING id
        """, (channel_id, channel_name, channel_username, added_by))
        db_id = cur.fetchone()[0]
        conn.commit()
        # Initialize default settings
        _init_default_settings(db_id)
        logger.info(f"Channel {channel_name} added with id {db_id}.")
        return db_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding channel: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def _init_default_settings(channel_db_id):
    """Insert default publish settings for a new channel."""
    default_templates = {
        'new_appointment': '📅 *Новая запись!*\n\n👤 Клиент: {client_name}\n🔧 Услуга: {service_name}\n📆 Дата: {date}\n⏰ Время: {time}\n\n#новаязапись',
        'new_review': '⭐ *Новый отзыв!*\n\n👤 {client_name} оценил нас на {rating}/5\n\n💬 {review_text}\n\n#отзыв',
        'appointment_confirmed': '✅ *Запись подтверждена!*\n\n👤 {client_name}\n📆 {date} в {time}\n🔧 {service_name}',
        'appointment_cancelled': '❌ *Запись отменена*\n\n👤 {client_name}\n📆 {date} в {time}\n🔧 {service_name}',
        'completed_appointment': '🎉 *Услуга оказана!*\n\n👤 {client_name}\n🔧 {service_name}\n📆 {date}\n\nБлагодарим за доверие!',
    }
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for event, tmpl in default_templates.items():
            cur.execute("""
                INSERT INTO channel_publish_settings (channel_id, event_type, message_template)
                VALUES (%s, %s, %s)
                ON CONFLICT (channel_id, event_type) DO NOTHING
            """, (channel_db_id, event, tmpl))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing channel settings: {e}")
    finally:
        cur.close()
        return_db_connection(conn)

def get_all_channels(only_active=True):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = "SELECT id, channel_id, channel_name, channel_username, is_active FROM telegram_channels"
        if only_active:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY channel_name"
        cur.execute(query)
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'channel_id': r[1],
            'channel_name': r[2],
            'channel_username': r[3],
            'is_active': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def update_channel_status(channel_db_id, is_active):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE telegram_channels SET is_active = %s WHERE id = %s", (is_active, channel_db_id))
        conn.commit()
        logger.info(f"Channel {channel_db_id} status set to {is_active}.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating channel status: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_channel(channel_db_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM telegram_channels WHERE id = %s", (channel_db_id,))
        conn.commit()
        logger.info(f"Channel {channel_db_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting channel: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_channel_settings(channel_db_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT event_type, is_enabled, message_template
            FROM channel_publish_settings
            WHERE channel_id = %s
            ORDER BY event_type
        """, (channel_db_id,))
        rows = cur.fetchall()
        return [{
            'event_type': r[0],
            'is_enabled': r[1],
            'message_template': r[2]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def update_channel_setting(channel_db_id, event_type, is_enabled, message_template):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE channel_publish_settings SET
                is_enabled = %s,
                message_template = %s
            WHERE channel_id = %s AND event_type = %s
        """, (is_enabled, message_template, channel_db_id, event_type))
        conn.commit()
        logger.info(f"Channel {channel_db_id} setting for {event_type} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating channel setting: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def add_post_to_history(channel_db_id, event_type, related_id, message_id, status='success'):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO channel_posts (channel_id, event_type, related_id, message_id, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (channel_db_id, event_type, related_id, message_id, status))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding post to history: {e}")
    finally:
        cur.close()
        return_db_connection(conn)

def get_posts_history(limit=50):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT cp.id, tc.channel_name, cp.event_type, cp.related_id, cp.published_at, cp.status
            FROM channel_posts cp
            JOIN telegram_channels tc ON cp.channel_id = tc.id
            ORDER BY cp.published_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'channel_name': r[1],
            'event_type': r[2],
            'related_id': r[3],
            'published_at': r[4],
            'status': r[5]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)