from database.connection import get_db_connection, return_db_connection
import logging

logger = logging.getLogger(__name__)

def create_appointment(data):
    """Create a new appointment."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO appointments
                (user_id, service_id, user_car_id, tire_size_id, date, time, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data['user_id'],
            data.get('service_id'),
            data.get('user_car_id'),
            data.get('tire_size_id'),
            data['date'],
            data['time'],
            data.get('status', 'pending'),
            data.get('notes')
        ))
        apt_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Appointment {apt_id} created.")
        return apt_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating appointment: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_appointment(appointment_id):
    """Get appointment by ID with related data."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.id, a.user_id, u.full_name, u.phone, a.date, a.time,
                   s.name as service_name, a.status, a.notes,
                   cb.name as brand, cm.name as model, cy.year,
                   ts.width, ts.profile, ts.diameter
            FROM appointments a
            LEFT JOIN users u ON a.user_id = u.user_id
            LEFT JOIN services s ON a.service_id = s.id
            LEFT JOIN user_cars uc ON a.user_car_id = uc.id
            LEFT JOIN car_brands cb ON uc.brand_id = cb.id
            LEFT JOIN car_models cm ON uc.model_id = cm.id
            LEFT JOIN car_years cy ON uc.year_id = cy.id
            LEFT JOIN tire_sizes ts ON a.tire_size_id = ts.id
            WHERE a.id = %s
        """, (appointment_id,))
        row = cur.fetchone()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'client_name': row[2],
                'phone': row[3],
                'date': row[4],
                'time': row[5],
                'service': row[6],
                'status': row[7],
                'notes': row[8],
                'car': f"{row[9]} {row[10]} {row[11]}" if row[9] else None,
                'tire': f"{row[12]}/{row[13]} R{row[14]}" if row[12] else None
            }
        return None
    finally:
        cur.close()
        return_db_connection(conn)

def get_appointments(page=1, per_page=50, date=None, status=None):
    """Get paginated list of appointments with filters."""
    conn = get_db_connection()
    cur = conn.cursor()
    offset = (page - 1) * per_page
    params = []
    where_clauses = []
    if date:
        where_clauses.append("a.date = %s")
        params.append(date)
    if status:
        where_clauses.append("a.status = %s")
        params.append(status)
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    try:
        query = f"""
            SELECT a.id, a.date, a.time, u.full_name, s.name, a.status
            FROM appointments a
            JOIN users u ON a.user_id = u.user_id
            LEFT JOIN services s ON a.service_id = s.id
            {where_sql}
            ORDER BY a.date DESC, a.time DESC
            LIMIT %s OFFSET %s
        """
        cur.execute(query, params + [per_page, offset])
        rows = cur.fetchall()

        # Count total
        count_query = f"""
            SELECT COUNT(*) FROM appointments a
            {where_sql}
        """
        cur.execute(count_query, params)
        total = cur.fetchone()[0]

        appointments = [{
            'id': r[0],
            'date': r[1],
            'time': r[2],
            'client_name': r[3],
            'service': r[4],
            'status': r[5]
        } for r in rows]
        return appointments, total
    finally:
        cur.close()
        return_db_connection(conn)

def get_appointments_by_date(date):
    """Get all appointments for a specific date."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.id, a.time, u.full_name, s.name, a.status
            FROM appointments a
            JOIN users u ON a.user_id = u.user_id
            LEFT JOIN services s ON a.service_id = s.id
            WHERE a.date = %s
            ORDER BY a.time
        """, (date,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'time': str(r[1]),
            'client_name': r[2],
            'service': r[3],
            'status': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)

def update_appointment_status(appointment_id, status, admin_comment=None):
    """Update appointment status."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE appointments SET status = %s, admin_comment = %s
            WHERE id = %s
        """, (status, admin_comment, appointment_id))
        conn.commit()
        logger.info(f"Appointment {appointment_id} status updated to {status}.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating appointment {appointment_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def delete_appointment(appointment_id):
    """Delete appointment."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        conn.commit()
        logger.info(f"Appointment {appointment_id} deleted.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting appointment {appointment_id}: {e}")
        raise
    finally:
        cur.close()
        return_db_connection(conn)

def get_appointments_count(status=None):
    """Get count of appointments (optionally by status)."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if status:
            cur.execute("SELECT COUNT(*) FROM appointments WHERE status = %s", (status,))
        else:
            cur.execute("SELECT COUNT(*) FROM appointments")
        return cur.fetchone()[0]
    finally:
        cur.close()
        return_db_connection(conn)

def get_appointments_today_count():
    """Get count of appointments for today."""
    from datetime import date
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM appointments WHERE date = %s", (date.today(),))
        return cur.fetchone()[0]
    finally:
        cur.close()
        return_db_connection(conn)

def get_user_appointments(user_id: int) -> list:
    """
    Возвращает список записей для конкретного пользователя.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT a.id, a.date, a.time, s.name as service, a.status
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            WHERE a.user_id = %s
            ORDER BY a.date DESC, a.time DESC
        """, (user_id,))
        rows = cur.fetchall()
        return [{
            'id': r[0],
            'date': r[1],
            'time': str(r[2]),
            'service': r[3],
            'status': r[4]
        } for r in rows]
    finally:
        cur.close()
        return_db_connection(conn)