from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.crud.users import is_user_registered
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: dict):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id:
            registered = is_user_registered(user_id)
            data['is_registered'] = registered
        else:
            data['is_registered'] = False
        
        return await handler(event, data)