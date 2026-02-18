from database.connection import get_db_connection, return_db_connection
import json
import logging

logger = logging.getLogger(__name__)

def log_error(level, source, message, user_id=None, traceback=None, request_data=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO error_logs (level, source, user_id, message, traceback, request_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (level, source, user_id, message, traceback, json.dumps(request_data) if request_data else None))
        conn.commit()
    except Exception as e:
        conn.rollback()
        # Fallback to print
        print(f"Error logging to DB: {e}")
    finally:
        cur.close()
        return_db_connection(conn)

def get_error_logs(page=1, per_page=50, level=None, search=None):
    conn = get_db_connection()
    cur = conn.cursor()
    offset = (page - 1) * per_page
    params = []
    where = []
    if level:
        where.append("level = %s")
        params.append(level)
    if search:
        where.append("message ILIKE %s")
        params.append(f'%{search}%')
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    try:
        query = f"""
            SELECT id, level, source, user_id, message, created_at
            FROM error_logs
            {where_sql}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        cur.execute(query, params + [per_page, offset])
        rows = cur.fetchall()
        # Count
        count_query = f"SELECT COUNT(*) FROM error_logs {where_sql}"
        cur.execute(count_query, params)
        total = cur.fetchone()[0]
        logs = [{
            'id': r[0],
            'level': r[1],
            'source': r[2],
            'user_id': r[3],
            'message': r[4],
            'created_at': r[5]
        } for r in rows]
        return logs, total
    finally:
        cur.close()
        return_db_connection(conn)

def get_log_details(log_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT level, source, user_id, message, traceback, request_data, created_at
            FROM error_logs WHERE id = %s
        """, (log_id,))
        row = cur.fetchone()
        if row:
            return {
                'level': row[0],
                'source': row[1],
                'user_id': row[2],
                'message': row[3],
                'traceback': row[4],
                'request_data': row[5],
                'created_at': row[6].isoformat() if row[6] else None
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def get_error_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, error_type, count, first_seen, last_seen, resolved
            FROM error_stats
            ORDER BY last_seen DESC
        """)
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'error_type': r[1],
            'count': r[2],
            'first_seen': r[3],
            'last_seen': r[4],
            'resolved': r[5]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def mark_error_resolved(stat_id, comment=''):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE error_stats SET resolved = TRUE, resolved_at = NOW(), comment = %s WHERE id = %s",
                    (comment, stat_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error marking error resolved: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)