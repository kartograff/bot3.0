from datetime import datetime, time
import pytz
import json
from database.crud.settings import get_silent_hours_settings, get_setting
from database.connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

class SilentHoursService:
    """Handles silent hours logic: check if now is silent and delay notifications."""
    
    def __init__(self):
        self.settings = None
        self.tz = None
        self._load_settings()
    
    def _load_settings(self):
        self.settings = get_silent_hours_settings()
        try:
            self.tz = pytz.timezone(self.settings['timezone'])
        except Exception as e:
            logger.error(f"Timezone error: {e}, using UTC")
            self.tz = pytz.UTC
    
    def _parse_time(self, time_str):
        try:
            if isinstance(time_str, str):
                return datetime.strptime(time_str, '%H:%M').time()
            return time_str
        except:
            return time(22, 0)
    
    def is_silent_hours_now(self):
        """Return True if current time is within silent hours."""
        if not self.settings['enabled']:
            return False
        
        now = datetime.now(self.tz)
        current_time = now.time()
        start = self._parse_time(self.settings['start'])
        end = self._parse_time(self.settings['end'])
        
        if start <= end:
            is_silent = start <= current_time <= end
        else:
            # overnight interval (e.g., 22:00-07:00)
            is_silent = current_time >= start or current_time <= end
        
        return is_silent
    
    def calculate_next_morning_time(self):
        """Return datetime (UTC) when to send delayed notifications."""
        now = datetime.now(self.tz)
        morning_time_str = get_setting('morning_notification_time') or '09:00'
        morning_time = self._parse_time(morning_time_str)
        
        scheduled = now.replace(
            hour=morning_time.hour,
            minute=morning_time.minute,
            second=0,
            microsecond=0
        )
        if now > scheduled:
            scheduled += timedelta(days=1)
        
        scheduled_utc = scheduled.astimezone(pytz.UTC)
        return scheduled_utc.replace(tzinfo=None)
    
    def is_emergency_message(self, message_text, user_id):
        """Check if message is marked as emergency."""
        if not self.settings['allow_emergency']:
            return False
        
        text_lower = message_text.lower()
        for keyword in self.settings['emergency_keywords']:
            if keyword.strip().lower() in text_lower:
                logger.info(f"Emergency keyword triggered: {keyword}")
                return True
        
        if str(user_id) in self.settings['emergency_user_ids']:
            logger.info(f"Emergency user ID: {user_id}")
            return True
        
        return False
    
    def save_delayed_notification(self, notification_type, user_id,
                                  appointment_id=None, message_text=None,
                                  admin_ids=None, **kwargs):
        """Store notification for later delivery."""
        scheduled_for = self.calculate_next_morning_time()
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO silenced_notifications
                (notification_type, user_id, appointment_id, message_text,
                 scheduled_for, status, notification_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                notification_type,
                user_id,
                appointment_id,
                message_text[:500] if message_text else None,
                scheduled_for,
                'pending',
                json.dumps({'admin_ids': admin_ids, 'kwargs': kwargs})
            ))
            notif_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f"Saved delayed notification {notif_id} for {scheduled_for}")
            return notif_id
        except Exception as e:
            logger.error(f"Error saving delayed notification: {e}")
            conn.rollback()
            return None
        finally:
            cur.close()
            conn.close()
    
    def should_notify_now(self, notification_type, user_id, message_text="",
                          appointment_id=None, admin_ids=None, **kwargs):
        """
        Determine if notification should be sent now or delayed.
        Returns (should_send_now, delay_info).
        """
        if not self.settings['enabled']:
            return True, None
        
        if self.is_emergency_message(message_text, user_id):
            return True, None
        
        if not self.is_silent_hours_now():
            return True, None
        
        # Delay
        notif_id = self.save_delayed_notification(
            notification_type, user_id, appointment_id, message_text,
            admin_ids, **kwargs
        )
        return False, {'delayed': True, 'notification_id': notif_id,
                       'scheduled_for': self.calculate_next_morning_time()}

# Global instance
silent_hours_service = SilentHoursService()