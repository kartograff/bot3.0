import logging
from services.silent_hours import silent_hours_service
from database.crud.telegram_channels import get_admin_ids

logger = logging.getLogger(__name__)

class NotificationService:
    """Handles sending notifications to admins with silent hours logic."""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def send_to_admin(self, admin_id, text, notification_type='general',
                           user_id=None, appointment_id=None, **kwargs):
        """
        Send a notification to a single admin, respecting silent hours.
        Returns dict with status info.
        """
        should_send, delay_info = silent_hours_service.should_notify_now(
            notification_type=notification_type,
            user_id=user_id,
            message_text=text,
            appointment_id=appointment_id,
            admin_ids=[admin_id],
            **kwargs
        )
        
        if not should_send:
            if delay_info and delay_info.get('delayed'):
                logger.info(f"Notification {notification_type} delayed until {delay_info['scheduled_for']}")
                return {
                    'sent': False,
                    'delayed': True,
                    'notification_id': delay_info['notification_id'],
                    'scheduled_for': delay_info['scheduled_for']
                }
            return {'sent': False, 'delayed': False}
        
        try:
            await self.bot.send_message(admin_id, text, **kwargs)
            logger.info(f"Notification sent to admin {admin_id}")
            return {'sent': True, 'delayed': False}
        except Exception as e:
            logger.error(f"Failed to send to admin {admin_id}: {e}")
            return {'sent': False, 'delayed': False, 'error': str(e)}
    
    async def broadcast_to_admins(self, text, notification_type='general',
                                  user_id=None, appointment_id=None, **kwargs):
        """
        Send notification to all admins.
        """
        admin_ids = await get_admin_ids()
        should_send, delay_info = silent_hours_service.should_notify_now(
            notification_type=notification_type,
            user_id=user_id,
            message_text=text,
            appointment_id=appointment_id,
            admin_ids=admin_ids,
            **kwargs
        )
        
        if not should_send:
            if delay_info and delay_info.get('delayed'):
                logger.info(f"Broadcast {notification_type} delayed until {delay_info['scheduled_for']}")
                return {
                    'sent_count': 0,
                    'total': len(admin_ids),
                    'delayed': True,
                    'notification_id': delay_info['notification_id'],
                    'scheduled_for': delay_info['scheduled_for']
                }
            return {'sent_count': 0, 'total': len(admin_ids), 'delayed': False}
        
        sent_count = 0
        for admin_id in admin_ids:
            try:
                await self.bot.send_message(admin_id, text, **kwargs)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send to admin {admin_id}: {e}")
        
        return {'sent_count': sent_count, 'total': len(admin_ids), 'delayed': False}