import pytest
import asyncio
from flask import Flask
from database.connection import get_db_connection, init_db
from config import Config

# Fixture for Flask test client
@pytest.fixture
def app():
    from web.app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Fixture for database connection (test database)
@pytest.fixture
def db_connection():
    # Override config for test database
    test_config = {
        'DB_NAME': 'sharahbot_test',
        'DB_USER': Config.DB_USER,
        'DB_PASSWORD': Config.DB_PASSWORD,
        'DB_HOST': Config.DB_HOST,
        'DB_PORT': Config.DB_PORT
    }
    # You might want to create a separate test database
    conn = get_db_connection(test_config)
    yield conn
    conn.close()

# Fixture for event loop (for async tests)
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()