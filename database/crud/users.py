from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def create_user(user_id, username, full_name, phone=None, is_admin=False):
    """Create a new user record."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (user_id, username, full_name, phone, is_admin)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                phone = EXCLUDED.phone,
                is_admin = EXCLUDED.is_admin
            RETURNING user_id
        """, (user_id, username, full_name, phone, is_admin))
        new_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"User {new_id} created/updated.")
        return new_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating user {user_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_user(user_id):
    """Get user by ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT user_id, username, full_name, phone, is_admin, notes, created_at
            FROM users WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'full_name': row[2],
                'phone': row[3],
                'is_admin': row[4],
                'notes': row[5],
                'created_at': row[6]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def get_users(page=1, per_page=50, search=''):
    """Get paginated list of users."""
    conn = get_db_connection()
    cur = conn.cursor()
    offset = (page - 1) * per_page
    try:
        if search:
            cur.execute("""
                SELECT user_id, username, full_name, phone, notes, is_admin, created_at
                FROM users
                WHERE username ILIKE %s OR full_name ILIKE %s OR phone ILIKE %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (f'%{search}%', f'%{search}%', f'%{search}%', per_page, offset))
            rows = cur.fetchall()
            # Get total count
            cur.execute("""
                SELECT COUNT(*) FROM users
                WHERE username ILIKE %s OR full_name ILIKE %s OR phone ILIKE %s
            """, (f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            cur.execute("""
                SELECT user_id, username, full_name, phone, notes, is_admin, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM users")
        total = cur.fetchone()[0]
        users = [{
            'user_id': r[0],
            'username': r[1],
            'full_name': r[2],
            'phone': r[3],
            'notes': r[4],
            'is_admin': r[5],
            'created_at': r[6]
        } for r in rows]
        return users, total
    finally:
        cur.close()
        return_db_connection(conn)

def update_user(user_id, data):
    """Update user fields (notes, is_admin, etc)."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE users SET
                notes = COALESCE(%s, notes),
                is_admin = COALESCE(%s, is_admin)
            WHERE user_id = %s
        """, (data.get('notes'), data.get('is_admin'), user_id))
        conn.commit()
        logger.info(f"User {user_id} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_user(user_id):
    """Delete user (and related records due to CASCADE)."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        logger.info(f"User {user_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def is_user_registered(user_id):
    """Check if user exists."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
        return cur.fetchone() is not None
    finally:
        cur.close()
        return_db_connection(conn)

def get_admin_ids():
    """Get list of admin user IDs."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id FROM users WHERE is_admin = TRUE")
        return [row[0] for row in cur.fetchall()]
    finally:
        cur.close()
        return_db_connection(conn)

def get_users_count(registered_after=None):
    """Get total number of users (optionally after date)."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if registered_after:
            cur.execute("SELECT COUNT(*) FROM users WHERE created_at >= %s", (registered_after,))
        else:
            cur.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]
    finally:
        cur.close()
        return_db_connection(conn)

def get_all_users(only_active: bool = True) -> list:
    """
    Возвращает список всех пользователей (обычно для рассылки).
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = "SELECT user_id, username, full_name, phone, is_admin, notes, created_at FROM users"
        if only_active:
            query += " WHERE is_active = TRUE"  # предполагаем, что есть поле is_active
        query += " ORDER BY created_at DESC"
        cur.execute(query)
        rows = cur.fetchall()
        return [{
            'user_id': r[0],
            'username': r[1],
            'full_name': r[2],
            'phone': r[3],
            'is_admin': r[4],
            'notes': r[5],
            'created_at': r[6]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def is_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь администратором.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT is_admin FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        return bool(row and row[0])
    finally:
        cur.close()
        return_db_connection(conn)