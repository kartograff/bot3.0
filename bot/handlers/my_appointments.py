import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.crud.appointments import get_user_appointments
from bot.keyboards.common import get_main_menu

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "📋 Мои записи")
@router.message(Command("my_appointments"))
async def show_my_appointments(message: Message):
    """Показывает список записей пользователя."""
    user_id = message.from_user.id
    appointments = get_user_appointments(user_id)
    if not appointments:
        await message.answer(
            "У вас пока нет записей.",
            reply_markup=get_main_menu(user_id)
        )
        return
    
    text = "Ваши записи:\n\n"
    for apt in appointments:
        text += f"📅 {apt['date']} {apt['time']} — {apt['service']}\n"
        text += f"Статус: {apt['status']}\n\n"
    
    await message.answer(text, reply_markup=get_main_menu(user_id))