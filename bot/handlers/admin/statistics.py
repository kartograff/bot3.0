import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta

from database.crud.users import get_users_count
from database.crud.appointments import get_appointments_count, get_appointments_today_count
from database.crud.services import get_services_count
from database.crud.car_brands import get_brands_count

logger = logging.getLogger(__name__)
router = Router()

async def check_admin(message: Message) -> bool:
    from database.crud.users import is_admin
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав для этой команды.")
        return False
    return True

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not await check_admin(message):
        return
    
    # Собираем статистику
    users_total = get_users_count()
    users_today = get_users_count(registered_after=datetime.now().date())  # если есть такой параметр
    appointments_total = get_appointments_count()
    appointments_today = get_appointments_today_count()
    services_total = get_services_count()
    brands_total = get_brands_count()
    
    # Формируем ответ
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