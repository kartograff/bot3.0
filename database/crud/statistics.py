from database.connection import get_db_connection, return_db_connection
from datetime import date, timedelta

def get_dashboard_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        today = date.today()
        # Today's appointments
        cur.execute("SELECT COUNT(*) FROM appointments WHERE date = %s", (today,))
        today_appointments = cur.fetchone()[0]
        # Pending appointments
        cur.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'")
        pending = cur.fetchone()[0]
        # Total users
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]
        # Monthly revenue (assuming price in services)
        first_day = today.replace(day=1)
        cur.execute("""
            SELECT COALESCE(SUM(s.price), 0)
            FROM appointments a
            JOIN services s ON a.service_id = s.id
            WHERE a.date >= %s AND a.status IN ('confirmed', 'completed')
        """, (first_day,))
        monthly_revenue = cur.fetchone()[0] or 0
        return {
            'today_appointments': today_appointments,
            'pending_appointments': pending,
            'total_users': total_users,
            'monthly_revenue': monthly_revenue
        }
    finally:
        cur.close()
        return_db_connection(conn)

def get_appointments_stats(days=30):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        start_date = date.today() - timedelta(days=days)
        cur.execute("""
            SELECT date, COUNT(*)
            FROM appointments
            WHERE date >= %s
            GROUP BY date
            ORDER BY date
        """, (start_date,))
        rows = cur.fetchall()
        return [{'date': r[0].isoformat(), 'count': r[1]} for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_popular_services(limit=10):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT s.name, COUNT(a.id) as cnt
            FROM appointments a
            JOIN services s ON a.service_id = s.id
            GROUP BY s.name
            ORDER BY cnt DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        return [{'service': r[0], 'count': r[1]} for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def get_revenue_stats(days=30):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        start_date = date.today() - timedelta(days=days)
        cur.execute("""
            SELECT a.date, SUM(s.price)
            FROM appointments a
            JOIN services s ON a.service_id = s.id
            WHERE a.date >= %s AND a.status IN ('confirmed', 'completed')
            GROUP BY a.date
            ORDER BY a.date
        """, (start_date,))
        rows = cur.fetchall()
        return [{'date': r[0].isoformat(), 'revenue': float(r[1]) if r[1] else 0} for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)