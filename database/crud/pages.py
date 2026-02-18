from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def get_page(slug):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, slug, title, content, meta_title, meta_description,
                   meta_keywords, image_id, is_published, created_at, updated_at
            FROM pages WHERE slug = %s
        """, (slug,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'slug': row[1],
                'title': row[2],
                'content': row[3],
                'meta_title': row[4],
                'meta_description': row[5],
                'meta_keywords': row[6],
                'image_id': row[7],
                'is_published': row[8],
                'created_at': row[9],
                'updated_at': row[10]
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def get_all_pages(include_unpublished=False):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        query = "SELECT id, slug, title, is_published FROM pages"
        if not include_unpublished:
            query += " WHERE is_published = TRUE"
        query += " ORDER BY title"
        cur.execute(query)
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'slug': r[1],
            'title': r[2],
            'is_published': r[3]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def create_page(data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO pages (slug, title, content, meta_title, meta_description,
                              meta_keywords, image_id, is_published)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['slug'], data['title'], data.get('content'),
            data.get('meta_title'), data.get('meta_description'),
            data.get('meta_keywords'), data.get('image_id'),
            data.get('is_published', True)
        ))
        page_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Page {data['slug']} created.")
        return page_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating page: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def update_page(slug, data):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE pages SET
                title = %s,
                content = %s,
                meta_title = %s,
                meta_description = %s,
                meta_keywords = %s,
                image_id = %s,
                is_published = %s,
                updated_at = NOW()
            WHERE slug = %s
        """, (
            data['title'], data.get('content'),
            data.get('meta_title'), data.get('meta_description'),
            data.get('meta_keywords'), data.get('image_id'),
            data.get('is_published', True), slug
        ))
        conn.commit()
        logger.info(f"Page {slug} updated.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating page {slug}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_page(slug):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM pages WHERE slug = %s", (slug,))
        conn.commit()
        logger.info(f"Page {slug} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting page {slug}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)