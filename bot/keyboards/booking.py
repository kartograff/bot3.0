from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

def get_vehicle_types_keyboard(vehicle_types: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for vt in vehicle_types:
        builder.row(InlineKeyboardButton(text=vt['name'], callback_data=f"vt_{vt['id']}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()

def get_services_keyboard(services: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for srv in services:
        text = srv['name']
        if srv.get('price'):
            text += f" - {srv['price']} ₽"
        builder.row(InlineKeyboardButton(text=text, callback_data=f"srv_{srv['id']}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_vehicle_types"))
    return builder.as_markup()

def get_date_keyboard(days_ahead: int = 14) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    today = datetime.now().date()
    for i in range(days_ahead):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        display = date.strftime("%d.%m.%Y")
        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        weekday = weekdays[date.weekday()]
        display += f" ({weekday})"
        builder.row(InlineKeyboardButton(text=display, callback_data=f"date_{date_str}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_car_selection"))
    return builder.as_markup()

def get_time_keyboard(date: str, interval_minutes: int = 30) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start_hour = 9
    end_hour = 20
    for hour in range(start_hour, end_hour):
        for minute in (0, 30):
            time_str = f"{hour:02d}:{minute:02d}"
            builder.row(InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_date"))
    return builder.as_markup()

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
        width=2
    )
    return builder.as_markup()

def get_back_keyboard(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data))
    return builder.as_markup()