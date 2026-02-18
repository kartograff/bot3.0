import logging
from aiogram import Bot
from database.crud.telegram_channels import (
    get_all_channels, get_channel_settings, add_post_to_history
)

logger = logging.getLogger(__name__)

class ChannelPublisher:
    """Publishes messages to connected Telegram channels."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def publish_to_all_channels(self, event_type: str, context: dict, related_id: int = None):
        """
        Publish a message to all active channels that have this event type enabled.
        context: dict with template variables.
        """
        channels = await get_all_channels(only_active=True)
        
        for channel in channels:
            settings = await get_channel_settings(channel['id'])
            setting = next((s for s in settings if s['event_type'] == event_type), None)
            
            if not setting or not setting['is_enabled']:
                continue
            
            # Format message
            try:
                message_text = setting['message_template'].format(**context)
            except KeyError as e:
                logger.error(f"Template formatting error for channel {channel['channel_name']}: {e}")
                continue
            
            # Send
            try:
                sent = await self.bot.send_message(
                    chat_id=channel['channel_id'],
                    text=message_text,
                    parse_mode="Markdown"
                )
                await add_post_to_history(
                    channel_db_id=channel['id'],
                    event_type=event_type,
                    related_id=related_id,
                    message_id=sent.message_id,
                    status='success'
                )
                logger.info(f"Published to {channel['channel_name']}: {event_type}")
            except Exception as e:
                logger.error(f"Failed to publish to {channel['channel_name']}: {e}")
                await add_post_to_history(
                    channel_db_id=channel['id'],
                    event_type=event_type,
                    related_id=related_id,
                    message_id=None,
                    status=f'failed: {str(e)[:50]}'
                )