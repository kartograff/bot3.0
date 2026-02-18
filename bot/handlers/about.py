import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.crud.settings import get_setting
from bot.keyboards.common import get_main_menu
from utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)
router = Router()

async def get_setting_cached(key: str, default: str = None):
    """
    Асинхронно получает значение настройки с кешированием на 5 минут.
    """
    cache_key = f'setting_{key}'
    cached = get_cache(cache_key)
    if cached is not None:
        return cached
    value = await asyncio.to_thread(get_setting, key)
    if value is None:
        value = default
    set_cache(cache_key, value)
    return value

@router.message(F.text == "ℹ️ О нас")
@router.message(Command("about"))
async def show_about(message: Message):
    user_id = message.from_user.id

    # Асинхронно получаем все настройки (каждая может быть закеширована)
    shop_name = await get_setting_cached('shop_name', 'Наш сервис')
    about_text = await get_setting_cached('about_info', 'Информация о нас отсутствует.')
    phone = await get_setting_cached('phone', 'не указан')
    address = await get_setting_cached('address', 'не указан')
    working_hours = await get_setting_cached('working_hours', 'не указаны')

    text = (
        f"🏢 *{shop_name}*\n\n"
        f"{about_text}\n\n"
        f"📍 *Адрес:* {address}\n"
        f"📞 *Телефон:* {phone}\n"
        f"🕒 *Режим работы:* {working_hours}"
    )

    logger.info(f"Sending about text: {text}")

    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu(user_id))