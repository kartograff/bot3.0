from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.crud.users import is_user_registered

def get_main_menu(user_id: int = None) -> ReplyKeyboardMarkup:
    """
    Формирует главное меню в зависимости от статуса регистрации пользователя.
    Если пользователь не зарегистрирован, кнопки "Мои записи" и "Мои автомобили" не показываются.
    """
    builder = ReplyKeyboardBuilder()
    
    # Кнопки, доступные всем
    builder.row(
        KeyboardButton(text="📝 Записаться"),
        KeyboardButton(text="ℹ️ О нас"),
        width=2
    )
    
    # Кнопки для зарегистрированных пользователей
    if user_id and is_user_registered(user_id):
        builder.row(
            KeyboardButton(text="📋 Мои записи"),
            KeyboardButton(text="🚗 Мои автомобили"),
            width=2
        )
    
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие")