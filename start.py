#!/usr/bin/env python
# start.py
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import asyncio
import logging
from threading import Thread
from config import Config
from bot.bot import bot, dp
from web.app import app

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_flask():
    """Запуск Flask-приложения (блокирующий)."""
    host = getattr(Config, 'WEB_HOST', '127.0.0.1')
    port = getattr(Config, 'WEB_PORT', 333)
    logger.info(f"Flask server starting at http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)

async def main():
    logger.info("Starting SharahBot...")

    # Запуск бота (поллинг) в фоновом режиме
    polling_task = asyncio.create_task(dp.start_polling(bot))
    logger.info("Bot polling started")

    # Запуск Flask в отдельном потоке (чтобы не блокировать asyncio)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask server started in daemon thread")

    # Держим основной asyncio-цикл живым
    try:
        while True:
            await asyncio.sleep(3600)  # бесконечное ожидание
    except asyncio.CancelledError:
        logger.info("Shutting down...")
        polling_task.cancel()
        await polling_task
        # Поток Flask завершится автоматически при выходе из программы

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")