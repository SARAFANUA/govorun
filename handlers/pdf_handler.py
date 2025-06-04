# handlers/pdf_handler.py (знову pdf_handler.py)
import logging
import os
import tempfile

from aiogram import Bot, F, Router, types
from aiogram.utils.markdown import hbold

from config import MAX_MESSAGE_LENGTH, SUMMARY_STYLES, TRANSCRIPTION_DISPLAY_CHUNK_SIZE
from handlers.common_handlers import get_user_settings
from services.pdf_parser import parse_pdf_to_text # <--- Залишаємо тільки PDF парсер
from services.summarization import generate_summary, summarize_long_text
from keyboards.inline import get_cancel_keyboard

router = Router()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE_PDF = 20 * 1024 * 1024 

# @router.message(F.document)
# async def debug_document_handler(message: types.Message):
#     logger.info(f"DEBUG: Received a document. File Name: {message.document.file_name}, MIME Type: {message.document.mime_type}")
#     if message.document.mime_type == "application/pdf":
#         logger.info(f"DEBUG: Document is PDF: {message.document.file_name}")
#     else:
#         logger.info(f"DEBUG: Document is NOT PDF, MIME Type: {message.document.mime_type}")
#         pass # Даємо наступному хендлеру (handle_pdf_document) шанс

@router.message(F.document.mime_type == "application/pdf")
async def handle_pdf_document(message: types.Message, bot: Bot, user_settings: dict):
    logger.info(f"PDF handler activated for file: {message.document.file_name}")
    user_id = message.from_user.id
    document = message.document
    
    logger.info(f"User {user_id} sent a PDF file: {document.file_name}, size: {document.file_size} bytes")

    if document.file_size > MAX_FILE_SIZE_PDF:
        await message.answer(
            f"❌ Розмір файлу `{document.file_name}` ({document.file_size / (1024 * 1024):.2f} MB) "
            f"перевищує максимально допустимий розмір для обробки ({MAX_FILE_SIZE_PDF / (1024 * 1024):.2f} MB). "
            "Будь ласка, завантажте менший файл.",
            parse_mode="Markdown"
        )
        return

    status_msg = await message.answer(f"📄 Файл `{document.file_name}` отримано. Будь ласка, зачекайте...",
                                      parse_mode="Markdown")

    user_prefs = get_user_settings(user_id, user_settings)
    selected_summary_style = user_prefs.get("summary_style")

    temp_file_path = None
    try:
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, document.file_name)
        
        await bot.download(document.file_id, destination=temp_file_path)
        logger.info(f"PDF file downloaded to: {temp_file_path}")

        await status_msg.edit_text("🔍 Аналізую документ...")

        pdf_text = await parse_pdf_to_text(temp_file_path)
        
        if pdf_text is None:
            await status_msg.edit_text("❌ Не вдалося розпізнати текст у PDF-файлі. Можливо, файл пошкоджений або захищений паролем.")
            return
        
        if not pdf_text.strip():
            await status_msg.edit_text("❌ У PDF-файлі не знайдено розпізнаваного тексту.")
            return

        logger.info(f"Text extracted from PDF. Length: {len(pdf_text)} characters.")

        await status_msg.edit_text("💡 Генерую підсумок...")

        summary = await summarize_long_text(pdf_text, selected_summary_style)
        logger.info(f"Summary generated for PDF from user {user_id}. Length: {len(summary)}")

        summary_header = f"💡 <b>Стислий підсумок</b> (Стиль: {hbold(SUMMARY_STYLES.get(selected_summary_style, {}).get('name', 'Стандартний'))}):"
        full_response_text = f"{summary_header}\n{summary}"

        await status_msg.edit_text("✅ Готово! Надсилаю підсумок...")

        if len(full_response_text) <= MAX_MESSAGE_LENGTH:
            await message.answer(full_response_text)
        else:
            await message.answer(summary_header)
            for i in range(0, len(summary), TRANSCRIPTION_DISPLAY_CHUNK_SIZE):
                chunk = summary[i:i + TRANSCRIPTION_DISPLAY_CHUNK_SIZE]
                await message.answer(chunk)

    except Exception as e:
        logger.exception(f"Error processing PDF for user {user_id}: {e}")
        await status_msg.edit_text(f"❌ Сталася помилка під час обробки PDF: {e}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            logger.info(f"Deleted temporary PDF file: {temp_file_path}")
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            os.rmdir(temp_dir)
            logger.info(f"Deleted temporary directory: {temp_dir}")