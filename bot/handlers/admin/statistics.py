import logging
import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime

from database.crud.users import get_users_count, is_admin
from database.crud.appointments import get_appointments_count, get_appointments_today_count
from database.crud.services import get_services_count
from database.crud.car_brands import get_brands_count

logger = logging.getLogger(__name__)
router = Router()

async def check_admin(message: Message) -> bool:
    """Проверка прав администратора (асинхронная)."""
    if not await asyncio.to_thread(is_admin, message.from_user.id):
        await message.answer("⛔ У вас нет прав для этой команды.")
        return False
    return True

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not await check_admin(message):
        return

    # Асинхронно собираем статистику
    users_total, users_today, appointments_total, appointments_today, services_total, brands_total = await asyncio.gather(
        asyncio.to_thread(get_users_count),
        asyncio.to_thread(get_users_count, registered_after=datetime.now().date()),  # если функция не поддерживает такой параметр, нужно исправить
        asyncio.to_thread(get_appointments_count),
        asyncio.to_thread(get_appointments_today_count),
        asyncio.to_thread(get_services_count),
        asyncio.to_thread(get_brands_count)
    )

    text = (
        "📊 **Статистика бота**\n\n"
        f"👥 **Пользователи:**\n"
        f"├ Всего: {users_total}\n"
        f"└ За сегодня: {users_today}\n\n"
        f"📅 **Записи:**\n"
        f"├ Всего: {appointments_total}\n"
        f"└ Сегодня: {appointments_today}\n\n"
        f"🔧 **Услуги:** {services_total}\n"
        f"🚗 **Марки авто:** {brands_total}"
    )

    await message.answer(text, parse_mode="Markdown")