import pytest
from database.crud.users import create_user, get_user, is_user_registered
from database.connection import get_db_connection

@pytest.mark.asyncio
async def test_create_user(db_connection):
    user_id = 12345
    username = "testuser"
    full_name = "Test User"
    phone = "+71234567890"
    
    # Create user
    await create_user(user_id, username, full_name, phone)
    
    # Check if user exists
    assert await is_user_registered(user_id) is True
    
    # Retrieve user
    user = await get_user(user_id)
    assert user is not None
    assert user['user_id'] == user_id
    assert user['username'] == username
    assert user['full_name'] == full_name
    assert user['phone'] == phone

@pytest.mark.asyncio
async def test_get_nonexistent_user(db_connection):
    user = await get_user(99999)
    assert user is None