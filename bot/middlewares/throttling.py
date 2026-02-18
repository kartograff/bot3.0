import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from cachetools import TTLCache

throttle_cache = TTLCache(maxsize=1000, ttl=60)

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit

    async def __call__(self, handler, event, data: dict):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            last_time = throttle_cache.get(user_id)
            now = asyncio.get_event_loop().time()
            if last_time and (now - last_time) < self.rate_limit:
                if isinstance(event, Message):
                    await event.answer("⏳ Пожалуйста, не спамьте. Подождите немного.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⏳ Слишком часто", show_alert=False)
                return
            throttle_cache[user_id] = now

        return await handler(event, data)