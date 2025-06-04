# services/pdf_parser.py
import logging
import asyncio
from typing import Optional

try:
    import pypdf
except ImportError:
    logging.error("pypdf is not installed. Please install it using 'pip install pypdf'")
    raise

logger = logging.getLogger(__name__)

async def parse_pdf_to_text(file_path: str) -> Optional[str]:
    """
    Асинхронно парсить текст з PDF-файлу.
    Ігнорує нерозпізнаний текст (наприклад, з зображень).
    Обробляє файли без пароля.
    """
    
    try:
        loop = asyncio.get_running_loop()
        
        # Функція, яка буде виконуватися в окремому потоці (синхронно)
        def _sync_parse():
            local_full_text = [] # <--- Ініціалізуємо тут, щоб вона була локальною для потоку
            try:
                reader = pypdf.PdfReader(file_path)
                
                if reader.is_encrypted:
                    logger.warning(f"PDF file '{file_path}' is encrypted. Attempting to decrypt with empty password.")
                    try:
                        reader.decrypt('') # Спроба з порожнім паролем
                    except pypdf.errors.PdfReadError:
                        logger.error(f"Failed to decrypt PDF file '{file_path}' with empty password.")
                        return None # Повідомити, що не вдалося дешифрувати
                    
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    try:
                        text = page.extract_text()
                        if text:
                            local_full_text.append(text)
                    except Exception as e:
                        logger.warning(f"Could not extract text from page {page_num + 1} of '{file_path}': {e}")
                return "\n".join(local_full_text) # Об'єднуємо весь текст
            except pypdf.errors.PdfReadError as e:
                logger.error(f"Failed to read PDF file (pypdf.errors.PdfReadError) in _sync_parse: {e}")
                return None
            except Exception as e:
                logger.error(f"An unexpected error occurred in _sync_parse while parsing PDF: {e}", exc_info=True)
                return None
            
        parsed_content = await loop.run_in_executor(None, _sync_parse)
        
        return parsed_content

    except pypdf.errors.PdfReadError as e:
        logger.error(f"Failed to read PDF file '{file_path}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while parsing PDF '{file_path}': {e}", exc_info=True)
        return None