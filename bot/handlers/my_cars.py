import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states.add_car import AddCarStates
from bot.states.add_tire import AddTireStates
from database.crud.users import is_user_registered
from database.crud.user_cars import get_user_cars, get_user_car, create_user_car, delete_user_car
from database.crud.car_brands import get_brands_grouped_by_letter, get_brands_by_letter
from database.crud.car_models import get_models_by_brand
from database.crud.car_years import get_years_by_model
from database.crud.tire_sizes import get_common_tire_sizes, get_or_create_tire_size
from database.crud.user_car_tires import get_tires_for_user_car, add_tire_to_user_car
from database.crud.vehicle_types import get_all_vehicle_types

from bot.keyboards.cars import (
    get_cars_inline_keyboard,
    get_brands_by_letter_keyboard,
    get_brands_list_keyboard,
    get_models_keyboard,
    get_years_keyboard,
    get_tire_selection_keyboard,
    get_confirm_keyboard,
    get_back_keyboard,
    get_skip_keyboard
)
from bot.keyboards.common import get_main_menu, back_keyboard, skip_keyboard, cancel_keyboard
from bot.keyboards.booking import get_vehicle_types_keyboard
from utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)
router = Router()

# ---------- Кеширование справочных данных ----------
async def get_cached_vehicle_types():
    """Типы ТС с кешем 5 минут."""
    cached = get_cache('vehicle_types')
    if cached is not None:
        return cached
    types = await asyncio.to_thread(get_all_vehicle_types)
    set_cache('vehicle_types', types)
    return types

async def get_cached_brands_grouped_by_letter():
    """Марки, сгруппированные по буквам (кеш 5 мин)."""
    cached = get_cache('brands_grouped')
    if cached is not None:
        return cached
    brands = await asyncio.to_thread(get_brands_grouped_by_letter)
    set_cache('brands_grouped', brands)
    return brands

async def get_cached_brands_by_letter(letter: str):
    """Марки для конкретной буквы (кеш 5 мин)."""
    cache_key = f'brands_{letter}'
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    brands = await asyncio.to_thread(get_brands_by_letter, letter)
    set_cache(cache_key, brands)
    return brands

async def get_cached_models_by_brand(brand_id: int, vehicle_type_id: int = None):
    """Модели для марки (кеш 5 мин, зависит от типа ТС)."""
    cache_key = f'models_{brand_id}_{vehicle_type_id}'
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    models = await asyncio.to_thread(get_models_by_brand, brand_id, vehicle_type_id=vehicle_type_id)
    set_cache(cache_key, models)
    return models

async def get_cached_years_by_model(model_id: int):
    """Годы для модели (кеш 5 мин)."""
    cache_key = f'years_{model_id}'
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    years = await asyncio.to_thread(get_years_by_model, model_id)
    set_cache(cache_key, years)
    return years

async def get_cached_common_tire_sizes(limit: int = 10):
    """Популярные размеры шин (кеш 5 мин)."""
    cache_key = f'common_tires_{limit}'
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    tires = await asyncio.to_thread(get_common_tire_sizes, limit=limit)
    set_cache(cache_key, tires)
    return tires

# ---------- Основные хендлеры ----------
@router.message(F.text == "🚗 Мои автомобили")
@router.message(Command("my_cars"))
async def show_my_cars(message: Message):
    user_id = message.from_user.id
    if not await asyncio.to_thread(is_user_registered, user_id):
        await message.answer("Сначала нужно зарегистрироваться. Используйте /start")
        return
    cars = await asyncio.to_thread(get_user_cars, user_id)
    if not cars:
        await message.answer(
            "У вас пока нет добавленных автомобилей.",
            reply_markup=get_cars_inline_keyboard([])
        )
    else:
        await message.answer(
            "Ваши автомобили:",
            reply_markup=get_cars_inline_keyboard(cars)
        )

@router.callback_query(F.data == "back_to_cars")
async def back_to_cars(callback: CallbackQuery):
    user_id = callback.from_user.id
    cars = await asyncio.to_thread(get_user_cars, user_id)
    await callback.message.edit_text(
        "Ваши автомобили:",
        reply_markup=get_cars_inline_keyboard(cars)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("car_select_"))
async def select_car(callback: CallbackQuery):
    car_id = int(callback.data.split("_")[2])
    car = await asyncio.to_thread(get_user_car, car_id)
    if not car:
        await callback.message.edit_text("Автомобиль не найден.")
        await callback.answer()
        return
    tires = await asyncio.to_thread(get_tires_for_user_car, car_id)
    car_text = f"🚗 {car['brand']} {car['model']}"
    if car.get('year'):
        car_text += f" ({car['year']})"
    if tires:
        car_text += "\n\nШины:"
        for tire in tires:
            primary = " (основной)" if tire['is_primary'] else ""
            car_text += f"\n• {tire['display']}{primary}"
    else:
        car_text += "\n\nШины не добавлены"

    await callback.message.edit_text(car_text, reply_markup=get_back_keyboard("back_to_cars"))
    await callback.answer()

@router.callback_query(F.data == "car_add")
async def add_car_start(callback: CallbackQuery, state: FSMContext):
    vehicle_types = await get_cached_vehicle_types()
    await callback.message.edit_text(
        "Сначала выберите тип транспортного средства:",
        reply_markup=get_vehicle_types_keyboard(vehicle_types)
    )
    await state.set_state(AddCarStates.choosing_vehicle_type)
    await callback.answer()

@router.callback_query(AddCarStates.choosing_vehicle_type, F.data.startswith("vt_"))
async def process_vehicle_type(callback: CallbackQuery, state: FSMContext):
    vt_id = int(callback.data.split("_")[1])
    await state.update_data(vehicle_type_id=vt_id)
    brands_by_letter = await get_cached_brands_grouped_by_letter()
    await callback.message.edit_text(
        "Выберите первую букву марки автомобиля:",
        reply_markup=get_brands_by_letter_keyboard(brands_by_letter)
    )
    await state.set_state(AddCarStates.choosing_letter)
    await callback.answer()

@router.callback_query(AddCarStates.choosing_letter, F.data.startswith("brand_letter_"))
async def choose_brand_by_letter(callback: CallbackQuery, state: FSMContext):
    letter = callback.data.split("_")[2]
    # При необходимости можно передавать vehicle_type_id в get_brands_by_letter, если функция поддерживает
    brands = await get_cached_brands_by_letter(letter)
    await callback.message.edit_text(
        f"Марки на букву {letter.upper()}:",
        reply_markup=get_brands_list_keyboard(brands, letter)
    )
    await state.set_state(AddCarStates.choosing_brand)
    await callback.answer()

@router.callback_query(AddCarStates.choosing_brand, F.data.startswith("brand_select_"))
async def choose_model(callback: CallbackQuery, state: FSMContext):
    brand_id = int(callback.data.split("_")[2])
    await state.update_data(brand_id=brand_id)
    data = await state.get_data()
    models = await get_cached_models_by_brand(brand_id, vehicle_type_id=data.get('vehicle_type_id'))
    await callback.message.edit_text(
        "Выберите модель:",
        reply_markup=get_models_keyboard(models)
    )
    await state.set_state(AddCarStates.choosing_model)
    await callback.answer()

@router.callback_query(AddCarStates.choosing_model, F.data.startswith("model_select_"))
async def choose_year(callback: CallbackQuery, state: FSMContext):
    model_id = int(callback.data.split("_")[2])
    await state.update_data(model_id=model_id)
    years = await get_cached_years_by_model(model_id)
    if years:
        await callback.message.edit_text(
            "Выберите год выпуска:",
            reply_markup=get_years_keyboard(years)
        )
        await state.set_state(AddCarStates.choosing_year)
    else:
        await callback.message.edit_text("Год выпуска не указан. Переходим к выбору шин.")
        await process_year_skip(callback, state)
    await callback.answer()

@router.callback_query(AddCarStates.choosing_year, F.data.startswith("year_select_"))
async def process_year(callback: CallbackQuery, state: FSMContext):
    year_id = int(callback.data.split("_")[2])
    await state.update_data(year_id=year_id)
    await process_tire_selection(callback, state)

async def process_year_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(year_id=None)
    await process_tire_selection(callback, state)

async def process_tire_selection(callback: CallbackQuery, state: FSMContext):
    common_tires = await get_cached_common_tire_sizes(limit=10)
    data = await state.get_data()
    if common_tires:
        await callback.message.edit_text(
            "Выберите размер шин или добавьте новый:",
            reply_markup=get_tire_selection_keyboard(common_tires, data.get('temp_car_id'))
        )
        await state.set_state(AddCarStates.choosing_tire_action)
    else:
        await callback.message.edit_text(
            "Введите диаметр диска (R):\nНапример: 16, 17, 18...",
            reply_markup=get_back_keyboard("back_to_cars")
        )
        await state.set_state(AddTireStates.adding_diameter)
    await callback.answer()

@router.callback_query(AddCarStates.choosing_tire_action, F.data.startswith("tire_select_"))
async def select_existing_tire(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    tire_id = int(parts[2])
    data = await state.get_data()
    user_car_id = await asyncio.to_thread(
        create_user_car,
        user_id=callback.from_user.id,
        brand_id=data['brand_id'],
        model_id=data['model_id'],
        year_id=data.get('year_id')
    )
    await asyncio.to_thread(add_tire_to_user_car, user_car_id, tire_id, is_primary=True)
    await callback.message.edit_text(
        "✅ Автомобиль успешно добавлен!",
        reply_markup=get_main_menu(callback.from_user.id)
    )
    await state.clear()
    await callback.answer()

@router.callback_query(AddCarStates.choosing_tire_action, F.data.startswith("tire_add_"))
async def add_new_tire_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите диаметр диска (R):\nНапример: 16, 17, 18...",
        reply_markup=get_back_keyboard("back_to_cars")
    )
    await state.set_state(AddTireStates.adding_diameter)
    await callback.answer()

@router.message(AddTireStates.adding_diameter)
async def add_tire_diameter(message: Message, state: FSMContext):
    try:
        diameter = float(message.text.replace('R', '').strip())
        await state.update_data(diameter=diameter)
        await message.answer(
            "Введите ширину шины (в мм):\nНапример: 205, 215, 225...",
            reply_markup=get_back_keyboard("back_to_cars")
        )
        await state.set_state(AddTireStates.adding_width)
    except ValueError:
        await message.answer("Пожалуйста, введите число (диаметр в дюймах)")

@router.message(AddTireStates.adding_width)
async def add_tire_width(message: Message, state: FSMContext):
    try:
        width = int(message.text)
        await state.update_data(width=width)
        await message.answer(
            "Введите высоту профиля (в %):\nНапример: 55, 60, 65...",
            reply_markup=get_back_keyboard("back_to_cars")
        )
        await state.set_state(AddTireStates.adding_profile)
    except ValueError:
        await message.answer("Пожалуйста, введите целое число")

@router.message(AddTireStates.adding_profile)
async def add_tire_profile(message: Message, state: FSMContext):
    try:
        profile = int(message.text)
        data = await state.get_data()
        tire_id = await asyncio.to_thread(
            get_or_create_tire_size,
            width=data['width'],
            profile=profile,
            diameter=data['diameter']
        )
        user_car_id = await asyncio.to_thread(
            create_user_car,
            user_id=message.from_user.id,
            brand_id=data['brand_id'],
            model_id=data['model_id'],
            year_id=data.get('year_id')
        )
        await asyncio.to_thread(add_tire_to_user_car, user_car_id, tire_id, is_primary=True)
        await message.answer(
            "✅ Автомобиль и размер шин успешно добавлены!",
            reply_markup=get_main_menu(message.from_user.id)
        )
        await state.clear()
    except Exception as e:
        logger.exception("Error adding tire profile")
        await message.answer(f"❌ Ошибка: {str(e)}")

@router.callback_query(F.data.startswith("car_delete_"))
async def delete_car(callback: CallbackQuery):
    car_id = int(callback.data.split("_")[2])
    await asyncio.to_thread(delete_user_car, car_id)
    await callback.message.edit_text("✅ Автомобиль удалён.")
    await back_to_cars(callback)