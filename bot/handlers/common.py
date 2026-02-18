import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from bot.keyboards.common import get_main_menu
from database.crud.users import is_user_registered, create_user

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Показывает главное меню.
    """
    user_id = message.from_user.id
    # Проверяем, зарегистрирован ли пользователь
    if not is_user_registered(user_id):
        # Автоматически создаём запись пользователя с минимальными данными
        username = message.from_user.username
        full_name = message.from_user.full_name
        create_user(user_id, username, full_name, phone=None)
        logger.info(f"Новый пользователь {user_id} (@{username}) автоматически зарегистрирован.")

    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=get_main_menu(user_id)
    )

@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message):
    """Возврат в главное меню."""
    user_id = message.from_user.id
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu(user_id)
    )