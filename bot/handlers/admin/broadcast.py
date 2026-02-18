import asyncio
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.crud.users import get_all_users, is_admin
from bot.bot import bot

logger = logging.getLogger(__name__)
router = Router()

class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    confirming = State()

# Проверка на администратора (можно вынести в декоратор, но проще в хендлере)
async def check_admin(message: Message) -> bool:
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет прав для этой команды.")
        return False
    return True

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if not await check_admin(message):
        return
    await message.answer(
        "📢 Введите текст для рассылки всем пользователям:"
    )
    await state.set_state(BroadcastStates.waiting_for_text)

@router.message(BroadcastStates.waiting_for_text)
async def process_broadcast_text(message: Message, state: FSMContext):
    text = message.text
    if not text:
        await message.answer("❌ Сообщение не может быть пустым. Попробуйте ещё раз.")
        return
    await state.update_data(text=text)
    
    # Показываем подтверждение
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить", callback_data="broadcast_confirm")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel")]
    ])
    await message.answer(
        f"📝 Текст рассылки:\n\n{text}\n\nПодтвердите отправку:",
        reply_markup=kb
    )
    await state.set_state(BroadcastStates.confirming)

@router.callback_query(BroadcastStates.confirming, F.data == "broadcast_confirm")
async def broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⏳ Начинаю рассылку...")
    data = await state.get_data()
    text = data['text']
    
    users = get_all_users()  # предполагаем, что возвращает список user_id
    if not users:
        await callback.message.answer("❌ Нет пользователей для рассылки.")
        await state.clear()
        return
    
    success = 0
    failed = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, text)
            success += 1
            await asyncio.sleep(0.05)  # небольшая задержка, чтобы избежать флуд-контроля
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            failed += 1
    
    await callback.message.answer(
        f"✅ Рассылка завершена.\n"
        f"📨 Успешно отправлено: {success}\n"
        f"❌ Ошибок: {failed}"
    )
    await state.clear()

@router.callback_query(BroadcastStates.confirming, F.data == "broadcast_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Рассылка отменена.")
    await state.clear()