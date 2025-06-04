# voice_audio_handler.py
import logging
import os
import tempfile

from aiogram import Bot, F, Router, types
from aiogram.utils.markdown import hbold

from config import (
    MAX_MESSAGE_LENGTH,
    SUMMARY_STYLES,
    SUPPORTED_LANGUAGES,
    TRANSCRIPTION_DISPLAY_CHUNK_SIZE
)
from handlers.common_handlers import get_user_settings
from services.summarization import generate_summary
from services.transcription import transcribe_audio

router = Router()


async def process_audio_message(message: types.Message, bot: Bot, user_settings: dict, whisper_model: tuple):
    user_id = message.from_user.id
    logger = logging.getLogger(__name__)
    status_msg = await message.answer("⏳ Обробляю аудіо, будь ласка, зачекайте...")

    user_prefs = get_user_settings(user_id, user_settings)
    selected_language = user_prefs.get("language")
    selected_summary_style = user_prefs.get("summary_style")

    whisper_model_instance, _ = whisper_model
    temp_path = None
    try:
        if message.voice:
            file_entity = message.voice
            file_suffix = '.ogg'
        elif message.audio:
            file_entity = message.audio
            file_suffix = os.path.splitext(file_entity.file_name)[1] if file_entity.file_name else '.mp3'
        elif message.document and message.document.mime_type and message.document.mime_type.startswith("audio"):
            file_entity = message.document
            file_suffix = os.path.splitext(file_entity.file_name)[1] if file_entity.file_name else ''
        else:
            await status_msg.edit_text("⚠️ Помилка: не вдалося обробити цей тип файлу.")
            return

        file_info = await bot.get_file(file_entity.file_id)
        with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_file:
            temp_path = temp_file.name

        await status_msg.edit_text("📥 Завантажую файл...")
        await bot.download_file(file_info.file_path, destination=temp_path)

        await status_msg.edit_text(
            f"✍️ Транскрибую ({selected_language if selected_language != 'auto' else 'автовизначення мови'})..."
        )
        transcription = await transcribe_audio(whisper_model_instance, temp_path, selected_language)

        if not transcription:
            await status_msg.edit_text("⚠️ Не вдалося розпізнати мову або аудіо є порожнім.")
            return

        await status_msg.edit_text("💡 Генерую підсумок...")
        summary = await generate_summary(transcription, selected_summary_style)

        transcription_header = f"📜 <b>Транскрипція</b> (Мова: {SUPPORTED_LANGUAGES.get(selected_language, 'Авто')}):"
        summary_header = f"💡 <b>Стислий підсумок</b> (Стиль: {SUMMARY_STYLES.get(selected_summary_style, {}).get('name', 'Стандартний')}):"
        full_response_text = f"{transcription_header}\n{transcription}\n\n{summary_header}\n{summary}"

        if len(full_response_text) <= MAX_MESSAGE_LENGTH:
            await status_msg.edit_text(full_response_text)
        else:
            await status_msg.edit_text("✅ Аудіо оброблено! Надсилаю результат частинами...")
            await message.answer(transcription_header)
            if len(transcription) > TRANSCRIPTION_DISPLAY_CHUNK_SIZE:
                for i in range(0, len(transcription), TRANSCRIPTION_DISPLAY_CHUNK_SIZE):
                    chunk = transcription[i:i + TRANSCRIPTION_DISPLAY_CHUNK_SIZE]
                    await message.answer(chunk)
            else:
                await message.answer(transcription)
            await message.answer(summary_header)
            if len(summary) > TRANSCRIPTION_DISPLAY_CHUNK_SIZE:
                for i in range(0, len(summary), TRANSCRIPTION_DISPLAY_CHUNK_SIZE):
                    chunk = summary[i:i + TRANSCRIPTION_DISPLAY_CHUNK_SIZE]
                    await message.answer(chunk)
            else:
                await message.answer(summary)
    except Exception as e:
        await status_msg.edit_text(f"❌ Сталася помилка під час обробки аудіо: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.message(F.voice)
async def handle_voice_message(message: types.Message, bot: Bot, user_settings: dict, whisper_model: tuple):
    await process_audio_message(message, bot, user_settings, whisper_model)


@router.message(F.audio)
async def handle_audio_message(message: types.Message, bot: Bot, user_settings: dict, whisper_model: tuple):
    await process_audio_message(message, bot, user_settings, whisper_model)


@router.message(F.document.mime_type.startswith("audio"))
async def handle_document_audio(message: types.Message, bot: Bot, user_settings: dict, whisper_model: tuple):
    await process_audio_message(message, bot, user_settings, whisper_model)
