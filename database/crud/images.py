from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def create_image(filename, filepath, alt_text=''):
    """Save a new image record."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO images (filename, filepath, alt_text)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (filename, filepath, alt_text))
        image_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Image {image_id} created.")
        return image_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating image: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_image(image_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, filename, filepath, alt_text, uploaded_at FROM images WHERE id = %s", (image_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'filename': row[1],
                'filepath': row[2],
                'alt_text': row[3],
                'uploaded_at': row[4]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def delete_image(image_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM images WHERE id = %s", (image_id,))
        conn.commit()
        logger.info(f"Image {image_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting image {image_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_all_images():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, filename, filepath, alt_text, uploaded_at FROM images ORDER BY uploaded_at DESC")
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'filename': r[1],
            'filepath': r[2],
            'alt_text': r[3],
            'uploaded_at': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)