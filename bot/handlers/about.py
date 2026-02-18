import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.crud.settings import get_setting
from bot.keyboards.common import get_main_menu

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "ℹ️ О нас")
@router.message(Command("about"))
async def show_about(message: Message):
    user_id = message.from_user.id
    shop_name = get_setting('shop_name') or 'Наш сервис'
    about_text = get_setting('about_info') or 'Информация о нас отсутствует.'
    phone = get_setting('phone') or 'не указан'
    address = get_setting('address') or 'не указан'
    working_hours = get_setting('working_hours') or 'не указаны'

    text = (
        f"🏢 *{shop_name}*\n\n"
        f"{about_text}\n\n"
        f"📍 *Адрес:* {address}\n"
        f"📞 *Телефон:* {phone}\n"
        f"🕒 *Режим работы:* {working_hours}"
    )

    # Логирование для отладки
    logger.info(f"Sending about text: {text}")

    await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu(user_id))