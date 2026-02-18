import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states.booking import BookingStates
from database.crud.vehicle_types import get_all_vehicle_types
from database.crud.services import get_services, get_service
from database.crud.user_cars import get_user_cars, get_user_car
from database.crud.user_car_tires import get_tires_for_user_car
from database.crud.tire_sizes import get_tire_size
from database.crud.appointments import create_appointment
from database.crud.users import is_user_registered

from bot.keyboards.booking import (
    get_vehicle_types_keyboard,
    get_services_keyboard,
    get_date_keyboard,
    get_time_keyboard,
    get_confirmation_keyboard
)
from bot.keyboards.cars import (
    get_cars_inline_keyboard as get_cars_keyboard,
    get_tire_selection_keyboard as get_tires_keyboard,
    get_back_keyboard
)
from bot.keyboards.common import get_main_menu
from utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)
router = Router()

# ---------- Кеширование справочных данных ----------
async def get_cached_vehicle_types():
    """Получить типы ТС с кешированием на 5 минут."""
    cached = get_cache('vehicle_types')
    if cached is not None:
        return cached
    types = await asyncio.to_thread(get_all_vehicle_types)
    set_cache('vehicle_types', types)
    return types

async def get_cached_services(vehicle_type_id: int):
    """Получить услуги с кешированием на 5 минут (по типу ТС)."""
    cache_key = f'services_{vehicle_type_id}'
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    services = await asyncio.to_thread(get_services, vehicle_type_id=vehicle_type_id)
    set_cache(cache_key, services)
    return services

# ---------- Основная логика ----------
async def start_booking_process(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Проверка регистрации (не кешируется, т.к. данные индивидуальны)
    if not await asyncio.to_thread(is_user_registered, user_id):
        await message.answer("Сначала нужно зарегистрироваться. Используйте /start")
        return
    vehicle_types = await get_cached_vehicle_types()
    await message.answer(
        "Выберите тип транспортного средства:",
        reply_markup=get_vehicle_types_keyboard(vehicle_types)
    )
    await state.set_state(BookingStates.choosing_vehicle_type)

@router.message(F.text == "📝 Записаться")
async def booking_handler(message: Message, state: FSMContext):
    await start_booking_process(message, state)

@router.message(Command("book"))
async def cmd_book(message: Message, state: FSMContext):
    await start_booking_process(message, state)

cmd_booking = booking_handler

@router.callback_query(BookingStates.choosing_vehicle_type, F.data.startswith("vt_"))
async def process_vehicle_type(callback: CallbackQuery, state: FSMContext):
    vt_id = int(callback.data.split("_")[1])
    await state.update_data(vehicle_type_id=vt_id)
    services = await get_cached_services(vt_id)
    await callback.message.edit_text(
        "Выберите услугу:",
        reply_markup=get_services_keyboard(services)
    )
    await state.set_state(BookingStates.choosing_service)
    await callback.answer()

@router.callback_query(BookingStates.choosing_service, F.data.startswith("srv_"))
async def process_service(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[1])
    service = await asyncio.to_thread(get_service, service_id)
    if not service:
        await callback.message.edit_text("Услуга не найдена. Попробуйте снова.")
        await state.clear()
        return
    await state.update_data(service_id=service_id, service_name=service['name'])
    user_id = callback.from_user.id
    cars = await asyncio.to_thread(get_user_cars, user_id)
    if cars:
        await callback.message.edit_text(
            "Выберите автомобиль:",
            reply_markup=get_cars_keyboard(cars)
        )
        await state.set_state(BookingStates.choosing_car)
    else:
        await callback.message.edit_text(
            "У вас нет добавленных автомобилей. Сначала добавьте автомобиль.",
            reply_markup=get_back_keyboard("main_menu")
        )
    await callback.answer()

@router.callback_query(BookingStates.choosing_car, F.data.startswith("car_select_"))
async def process_car(callback: CallbackQuery, state: FSMContext):
    car_id = int(callback.data.split("_")[2])
    car = await asyncio.to_thread(get_user_car, car_id)
    if not car:
        await callback.message.edit_text("Автомобиль не найден.")
        await state.clear()
        return
    car_display = f"{car['brand']} {car['model']}"
    if car.get('year'):
        car_display += f" ({car['year']})"
    await state.update_data(user_car_id=car_id, car_display=car_display)
    tires = await asyncio.to_thread(get_tires_for_user_car, car_id)
    if tires:
        await callback.message.edit_text(
            "Выберите размер шин (или пропустите):",
            reply_markup=get_tires_keyboard(tires, car_id)
        )
        await state.set_state(BookingStates.choosing_tire)
    else:
        await callback.message.edit_text(
            "У этого автомобиля нет добавленных шин. Хотите добавить?",
            reply_markup=get_back_keyboard("back_to_cars")
        )
        await state.set_state(BookingStates.choosing_tire)
    await callback.answer()

@router.callback_query(BookingStates.choosing_tire, F.data.startswith("tire_select_"))
async def process_tire_select(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    tire_id = int(parts[2])
    tire = await asyncio.to_thread(get_tire_size, tire_id)
    if tire:
        tire_display = f"{tire['width']}/{tire['profile']} R{tire['diameter']}"
        await state.update_data(tire_size_id=tire_id, tire_display=tire_display)
    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=get_date_keyboard()
    )
    await state.set_state(BookingStates.choosing_date)
    await callback.answer()

@router.callback_query(BookingStates.choosing_tire, F.data == "skip_tire")
async def process_tire_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(tire_size_id=None, tire_display="не указаны")
    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=get_date_keyboard()
    )
    await state.set_state(BookingStates.choosing_date)
    await callback.answer()

@router.callback_query(BookingStates.choosing_date, F.data.startswith("date_"))
async def process_date(callback: CallbackQuery, state: FSMContext):
    date = callback.data.split("_")[1]
    await state.update_data(date=date)
    await callback.message.edit_text(
        "Выберите время:",
        reply_markup=get_time_keyboard(date)
    )
    await state.set_state(BookingStates.choosing_time)
    await callback.answer()

@router.callback_query(BookingStates.choosing_time, F.data.startswith("time_"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data.split("_")[1]
    await state.update_data(time=time)
    data = await state.get_data()
    text = (
        f"📅 **Подтверждение записи**\n\n"
        f"**Услуга:** {data.get('service_name', '?')}\n"
        f"**Автомобиль:** {data.get('car_display', '?')}\n"
        f"**Шины:** {data.get('tire_display', 'не указаны')}\n"
        f"**Дата:** {data['date']}\n"
        f"**Время:** {data['time']}\n\n"
        f"Всё верно?"
    )
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_confirmation_keyboard()
    )
    await state.set_state(BookingStates.confirmation)
    await callback.answer()

@router.callback_query(BookingStates.confirmation, F.data == "confirm")
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        appointment_id = await asyncio.to_thread(
            create_appointment,
            {
                'user_id': callback.from_user.id,
                'service_id': data['service_id'],
                'user_car_id': data.get('user_car_id'),
                'tire_size_id': data.get('tire_size_id'),
                'date': data['date'],
                'time': data['time'],
                'status': 'pending',
                'notes': None
            }
        )
        await callback.message.edit_text(
            "✅ Запись создана! Ожидайте подтверждения администратора.",
            reply_markup=get_main_menu(callback.from_user.id)
        )
    except Exception as e:
        logger.exception("Error creating appointment")
        await callback.message.edit_text(
            "❌ Произошла ошибка при создании записи. Попробуйте позже.",
            reply_markup=get_main_menu(callback.from_user.id)
        )
    await state.clear()
    await callback.answer()

@router.callback_query(BookingStates.confirmation, F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "❌ Запись отменена.",
        reply_markup=get_main_menu(callback.from_user.id)
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "back_to_vehicle_types")
async def back_to_vehicle_types(callback: CallbackQuery, state: FSMContext):
    vehicle_types = await get_cached_vehicle_types()
    await callback.message.edit_text(
        "Выберите тип транспортного средства:",
        reply_markup=get_vehicle_types_keyboard(vehicle_types)
    )
    await state.set_state(BookingStates.choosing_vehicle_type)
    await callback.answer()

@router.callback_query(F.data == "back_to_car_selection")
async def back_to_car_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cars = await asyncio.to_thread(get_user_cars, user_id)
    await callback.message.edit_text(
        "Выберите автомобиль:",
        reply_markup=get_cars_keyboard(cars)
    )
    await state.set_state(BookingStates.choosing_car)
    await callback.answer()

@router.callback_query(F.data == "back_to_date")
async def back_to_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите дату:",
        reply_markup=get_date_keyboard()
    )
    await state.set_state(BookingStates.choosing_date)
    await callback.answer()