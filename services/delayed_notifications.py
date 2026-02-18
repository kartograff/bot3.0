import asyncio
import json
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.connection import get_db_connection
from database.crud.settings import get_setting
from services.notifications import NotificationService
import logging

logger = logging.getLogger(__name__)

class DelayedNotificationProcessor:
    """Processes delayed notifications and sends them at scheduled time."""
    
    def __init__(self, bot):
        self.bot = bot
        self.notification_service = NotificationService(bot)
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def process_pending_notifications(self):
        """Send all pending notifications whose time has come."""
        logger.info("Processing delayed notifications...")
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, notification_type, user_id, appointment_id,
                       message_text, notification_data, retry_count
                FROM silenced_notifications
                WHERE status = 'pending' AND scheduled_for <= NOW()
                ORDER BY scheduled_for
                LIMIT 100
            """)
            notifs = cur.fetchall()
            if not notifs:
                logger.debug("No pending notifications.")
                return
            
            for notif in notifs:
                await self._send_notification(cur, notif)
            conn.commit()
        except Exception as e:
            logger.error(f"Error processing delayed notifications: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    async def _send_notification(self, cur, notif):
        """Send a single delayed notification."""
        notif_id, n_type, user_id, apt_id, msg_text, data_json, retry = notif
        try:
            data = json.loads(data_json) if data_json else {}
            admin_ids = data.get('admin_ids', [])
            kwargs = data.get('kwargs', {})
            
            # Optionally prepend marker
            if msg_text and not msg_text.startswith('(🔔 Отложенное)'):
                msg_text = f"(🔔 Отложенное с {datetime.now().strftime('%H:%M')})\n\n{msg_text}"
            
            sent = 0
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(admin_id, msg_text, **kwargs)
                    sent += 1
                except Exception as e:
                    logger.error(f"Failed to send to admin {admin_id}: {e}")
            
            if sent > 0:
                cur.execute("UPDATE silenced_notifications SET status = 'sent', last_attempt = NOW() WHERE id = %s", (notif_id,))
                logger.info(f"Delayed notification {notif_id} sent to {sent} admins.")
            else:
                # Retry logic
                max_retries = int(get_setting('max_notification_retries') or 3)
                new_retry = retry + 1
                if new_retry >= max_retries:
                    cur.execute("UPDATE silenced_notifications SET status = 'failed', last_attempt = NOW() WHERE id = %s", (notif_id,))
                    logger.error(f"Notification {notif_id} failed after {max_retries} attempts.")
                else:
                    from services.silent_hours import silent_hours_service
                    new_schedule = silent_hours_service.calculate_next_morning_time()
                    cur.execute("UPDATE silenced_notifications SET scheduled_for = %s, retry_count = %s, last_attempt = NOW() WHERE id = %s",
                                (new_schedule, new_retry, notif_id))
                    logger.info(f"Notification {notif_id} rescheduled to {new_schedule}")
        except Exception as e:
            logger.error(f"Critical error sending notification {notif_id}: {e}")
            cur.execute("UPDATE silenced_notifications SET status = 'failed', last_attempt = NOW() WHERE id = %s", (notif_id,))
    
    async def cleanup_old_notifications(self):
        """Remove old notifications from database."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM silenced_notifications WHERE created_at < NOW() - INTERVAL '30 days' AND status IN ('sent','failed')")
            deleted = cur.rowcount
            conn.commit()
            logger.info(f"Cleaned up {deleted} old notifications.")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def start(self):
        if self.is_running:
            return
        self.scheduler.add_job(self.process_pending_notifications, 'interval', minutes=1, id='process_delayed')
        self.scheduler.add_job(self.cleanup_old_notifications, 'cron', hour=3, minute=0, id='cleanup_notifications')
        self.scheduler.start()
        self.is_running = True
        logger.info("Delayed notification processor started.")
    
    def stop(self):
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Delayed notification processor stopped.")