from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from database.crud.users import is_user_registered
from bot.keyboards.cars import get_cars_inline_keyboard
from bot.handlers.booking import cmd_booking as start_booking
from bot.handlers.my_appointments import show_my_appointments
from bot.handlers.about import show_about
from bot.handlers.my_cars import show_my_cars
from bot.states.registration import RegistrationStates
import asyncio

router = Router()

@router.message(F.text == "📝 Записаться")
async def handle_book(message: Message, state: FSMContext):
    user_id = message.from_user.id
    is_registered = await asyncio.to_thread(is_user_registered, user_id)
    if not is_registered:
        # Предложим зарегистрироваться
        await message.answer(
            "Для записи нужно зарегистрироваться.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Отправить контакт", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        # Можно также установить состояние регистрации
        await state.set_state(RegistrationStates.waiting_for_contact)
    else:
        await start_booking(message, state)

@router.message(F.text == "📋 Мои записи")
async def handle_my_appointments(message: Message):
    user_id = message.from_user.id
    is_registered = await asyncio.to_thread(is_user_registered, user_id)
    if not is_registered:
        await message.answer("Сначала зарегистрируйтесь.")
        return
    await show_my_appointments(message)

@router.message(F.text == "🚗 Мои автомобили")
async def handle_my_cars(message: Message):
    user_id = message.from_user.id
    is_registered = await asyncio.to_thread(is_user_registered, user_id)
    if not is_registered:
        await message.answer("Сначала зарегистрируйтесь.")
        return
    await show_my_cars(message)

@router.message(F.text == "ℹ️ О нас")
async def handle_about(message: Message):
    await show_about(message)