from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def create_review(user_id, appointment_id, rating, text=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO reviews (user_id, appointment_id, rating, text)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, appointment_id, rating, text))
        review_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Review {review_id} created.")
        return review_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating review: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_review(review_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT r.id, r.user_id, u.full_name, r.appointment_id, a.date, a.time,
                   r.rating, r.text, r.created_at
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            LEFT JOIN appointments a ON r.appointment_id = a.id
            WHERE r.id = %s
        """, (review_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'user_name': row[2],
                'appointment_id': row[3],
                'appointment_date': row[4],
                'appointment_time': row[5],
                'rating': row[6],
                'text': row[7],
                'created_at': row[8]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def get_recent_reviews(limit=5):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT r.id, u.full_name, r.rating, r.text, r.created_at
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            ORDER BY r.created_at DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'client_name': r[1],
            'rating': r[2],
            'text': r[3],
            'created_at': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_reviews_by_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, appointment_id, rating, text, created_at
            FROM reviews
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'appointment_id': r[1],
            'rating': r[2],
            'text': r[3],
            'created_at': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def delete_review(review_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        conn.commit()
        logger.info(f"Review {review_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting review {review_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)