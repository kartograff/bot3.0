from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from utils.cache import get_user_registration_status

def get_main_menu(user_id: int = None) -> ReplyKeyboardMarkup:
    """
    Главное меню бота.
    Если пользователь не зарегистрирован, показывает только 'Записаться' и 'О нас'.
    Статус регистрации берётся из кеша (с обновлением раз в 5 минут).
    """
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="📝 Записаться"),
        KeyboardButton(text="ℹ️ О нас"),
        width=2
    )

    if user_id and get_user_registration_status(user_id):
        builder.row(
            KeyboardButton(text="📋 Мои записи"),
            KeyboardButton(text="🚗 Мои автомобили"),
            width=2
        )

    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие")

def back_keyboard(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Простая инлайн-клавиатура с кнопкой 'Назад'."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data))
    return builder.as_markup()

def skip_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура с кнопками 'Пропустить' и 'Назад'."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
    return builder.as_markup()

def start_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Старт", callback_data="start_command"))
    return builder.as_markup()

def cancel_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура с кнопкой 'Отмена'."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()