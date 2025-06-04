# main_bot.py
import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv

# Імпортуємо всі наші хендлери, включаючи pdf_handler
from handlers import common_handlers, settings_handlers, voice_audio_handler, text_input_handler, pdf_handler # <--- Переконайтесь, що тут pdf_handler
from keyboards.command_menu import set_main_menu
from services.transcription import load_whisper_model
from config import TELEGRAM_BOT_TOKEN 

async def main():
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp['user_settings'] = {}
    
    logger.info("Loading Whisper model...")
    dp['whisper_model'] = load_whisper_model()
    logger.info("Whisper model loaded.")

    await set_main_menu(bot)

    # Реєстрація роутерів
    dp.include_router(common_handlers.router)
    dp.include_router(settings_handlers.router)
    dp.include_router(pdf_handler.router) # <--- Переконайтесь, що тут pdf_handler.router
    dp.include_router(voice_audio_handler.router)
    dp.include_router(text_input_handler.router)
    
    logger.info("Starting bot polling...")
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down bot...")
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())