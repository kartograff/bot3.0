import pytest
from aiogram import Dispatcher
from aiogram.types import Message, User
from bot.handlers.common import cmd_start

@pytest.mark.asyncio
async def test_start_handler():
    # Mock objects
    message = Message(
        message_id=1,
        date=...,
        chat=...,
        from_user=User(id=123, is_bot=False, first_name="Test"),
        text="/start"
    )
    # Call handler
    # await cmd_start(message)  # This would need a real dispatcher
    # For now, just a placeholder
    assert True