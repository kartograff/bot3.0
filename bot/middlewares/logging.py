import time
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        start_time = time.time()
        
        if isinstance(event, Message):
            user_id = event.from_user.id
            username = event.from_user.username or "no_username"
            text = event.text or "[non-text]"
            logger.info(f"Message from {user_id} (@{username}): {text}")
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            username = event.from_user.username or "no_username"
            data_cb = event.data
            logger.info(f"Callback from {user_id} (@{username}): {data_cb}")
        
        result = await handler(event, data)
        
        duration = time.time() - start_time
        logger.info(f"Event handled in {duration:.3f}s")
        
        return result