from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_cars_inline_keyboard(user_cars: list) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком автомобилей пользователя.
    Каждый автомобиль – кнопка с callback_data="car_select_{id}".
    Также есть кнопка "Добавить автомобиль" и "Назад".
    """
    builder = InlineKeyboardBuilder()
    for car in user_cars:
        text = f"{car['brand']} {car['model']}"
        if car.get('year'):
            text += f" ({car['year']})"
        builder.row(InlineKeyboardButton(
            text=text,
            callback_data=f"car_select_{car['id']}"
        ))
    builder.row(InlineKeyboardButton(
        text="➕ Добавить автомобиль",
        callback_data="car_add"
    ))
    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="main_menu"
    ))
    return builder.as_markup()

def get_brands_by_letter_keyboard(brands_by_letter: dict) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора первой буквы марки.
    Принимает словарь {буква: [марки]} (можно игнорировать список марок, нужны только буквы).
    """
    builder = InlineKeyboardBuilder()
    letters = sorted(brands_by_letter.keys())
    # Размещаем буквы по 6 в ряд
    for i in range(0, len(letters), 6):
        row = letters[i:i+6]
        builder.row(*[
            InlineKeyboardButton(text=ch, callback_data=f"brand_letter_{ch}")
            for ch in row
        ])
    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back_to_cars"
    ))
    return builder.as_markup()

def get_brands_list_keyboard(brands: list, letter: str) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком марок на выбранную букву.
    Каждая марка – кнопка с callback_data="brand_select_{id}".
    """
    builder = InlineKeyboardBuilder()
    for brand in brands:
        builder.row(InlineKeyboardButton(
            text=brand['name'],
            callback_data=f"brand_select_{brand['id']}"
        ))
    builder.row(InlineKeyboardButton(
        text="🔙 К выбору буквы",
        callback_data="brands_by_letter"
    ))
    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back_to_cars"
    ))
    return builder.as_markup()

def get_models_keyboard(models: list) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком моделей для выбранной марки.
    Каждая модель – кнопка с callback_data="model_select_{id}".
    """
    builder = InlineKeyboardBuilder()
    for model in models:
        text = model['name']
        if model.get('start_year') or model.get('end_year'):
            years = f"{model.get('start_year', '')}–{model.get('end_year', '')}"
            text += f" ({years})"
        builder.row(InlineKeyboardButton(
            text=text,
            callback_data=f"model_select_{model['id']}"
        ))
    builder.row(InlineKeyboardButton(
        text="🔙 К выбору марки",
        callback_data="back_to_brands"
    ))
    return builder.as_markup()

def get_years_keyboard(years: list) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком годов выпуска для выбранной модели.
    Каждый год – кнопка с callback_data="year_select_{id}".
    """
    builder = InlineKeyboardBuilder()
    for year in years:
        builder.row(InlineKeyboardButton(
            text=str(year['year']),
            callback_data=f"year_select_{year['id']}"
        ))
    builder.row(InlineKeyboardButton(
        text="🔙 К выбору модели",
        callback_data="back_to_models"
    ))
    return builder.as_markup()

def get_tire_selection_keyboard(tires: list, car_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора существующего размера шин или добавления нового.
    tires – список словарей с ключами id, display (например, "205/55 R16").
    """
    builder = InlineKeyboardBuilder()
    for tire in tires:
        builder.row(InlineKeyboardButton(
            text=tire['display'],
            callback_data=f"tire_select_{tire['id']}_{car_id}"
        ))
    builder.row(InlineKeyboardButton(
        text="➕ Добавить новый размер",
        callback_data=f"tire_add_{car_id}"
    ))
    builder.row(InlineKeyboardButton(
        text="🔙 К выбору автомобиля",
        callback_data="cars_list"
    ))
    return builder.as_markup()

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения: Да / Нет."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no"),
        width=2
    )
    return builder.as_markup()

def get_back_keyboard(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Простая клавиатура с одной кнопкой 'Назад'."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data))
    return builder.as_markup()

def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'Пропустить' (для необязательных шагов)."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
    return builder.as_markup()