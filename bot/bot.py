import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent
from config import Config
from bot.middlewares.logging import LoggingMiddleware
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

logger = logging.getLogger(__name__)

bot = Bot(token=Config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Register middlewares
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())
dp.message.middleware(AuthMiddleware())
dp.callback_query.middleware(AuthMiddleware())
dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.5))

# Import routers
from bot.handlers import (
    common,
    registration,
    main_menu,
    my_cars,
    booking,
    my_appointments,
    about,
)
from bot.handlers.admin import broadcast, statistics

dp.include_router(common.router)
dp.include_router(registration.router)
dp.include_router(main_menu.router)
dp.include_router(my_cars.router)
dp.include_router(booking.router)
dp.include_router(my_appointments.router)
dp.include_router(about.router)
dp.include_router(broadcast.router)
dp.include_router(statistics.router)

# Global error handler for aiogram 3.x
@dp.error()
async def global_error_handler(event: ErrorEvent) -> None:
    """Глобальный обработчик необработанных исключений."""
    logger.error(
        f"Update {event.update.update_id} caused error {event.exception}",
        exc_info=event.exception
    )
    # Попытка уведомить пользователя (если возможно)
    try:
        if event.update.message:
            await event.update.message.answer(
                "❌ Произошла внутренняя ошибка. Администратор уже уведомлён."
            )
        elif event.update.callback_query:
            await event.update.callback_query.message.answer(
                "❌ Произошла внутренняя ошибка. Администратор уже уведомлён."
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке пользователю: {e}")