from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.keyboards.main_menu import get_main_menu
from database.crud.users import create_user
from utils.cache import delete_cache

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_contact = State()

@router.callback_query(F.data == "need_registration")
async def need_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Для использования этой функции нужно зарегистрироваться.\n"
        "Нажмите кнопку ниже, чтобы отправить ваш номер телефона.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Отправить контакт", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(RegistrationStates.waiting_for_contact)
    await callback.answer()

@router.message(RegistrationStates.waiting_for_contact, F.contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.contact
    user_id = message.from_user.id
    phone = contact.phone_number
    full_name = message.from_user.full_name
    username = message.from_user.username

    # Создаём пользователя в БД
    create_user(user_id, full_name, phone)
    # Инвалидируем кеш статуса регистрации для этого пользователя
    delete_cache(f'user_registered_{user_id}')

    await message.answer(
        "Регистрация прошла успешно!",
        reply_markup=get_main_menu(user_id)
    )
    await state.clear()

@router.message(RegistrationStates.waiting_for_contact)
async def contact_invalid(message: Message):
    await message.answer(
        "Пожалуйста, отправьте контакт, используя кнопку ниже."
    )