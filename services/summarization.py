# services/summarization.py
import g4f
import logging
import re # Додаємо імпорт для регулярних виразів
from config import SUMMARY_STYLES

logger = logging.getLogger(__name__)

MAX_CHARS_PER_CHUNK = 8000
MIN_CHARS_FOR_RECURSIVE = 10000 
SUMMARY_CHUNK_OVERLAP = 500 


def _clean_summary_text(text: str) -> str:
    """
    Видаляє рекламний блок, що починається з "--- Sponsor" (з урахуванням пробілів та регістру).
    """
    pattern = r"\s*---\s**Sponsor.**"
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)
    return cleaned_text.strip()


async def generate_summary(text: str, style_key: str) -> str:
    style_info = SUMMARY_STYLES.get(style_key, SUMMARY_STYLES["default"])
    system_prompt = style_info["prompt"]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4o_mini,
            messages=messages,
            stream=False
        )
        if response and isinstance(response, str) and response.strip():
            # Застосовуємо фільтрацію тут
            cleaned_response = _clean_summary_text(response.strip())
            return cleaned_response
        else:
            logger.warning(f"Empty or invalid LLM response for summary: {response}")
            return "⚠️ Ошибка: пустой или некорректный ответ от LLM."
    except Exception as e:
        logger.exception(f"Failed to get LLM response for summary: {e}")
        return f"⚠️ Не удалось получить ответ от LLM: {str(e)}"

async def summarize_long_text(text: str, style_key: str) -> str:
    if len(text) < MIN_CHARS_FOR_RECURSIVE:
        logger.info(f"Text length ({len(text)}) is below recursive threshold. Generating single summary.")
        return await generate_summary(text, style_key)

    logger.info(f"Starting recursive summarization for text of length: {len(text)}")

    chunks = []
    start_index = 0
    while start_index < len(text):
        end_index = min(start_index + MAX_CHARS_PER_CHUNK, len(text))
        chunk = text[start_index:end_index]
        chunks.append(chunk)
        start_index += (MAX_CHARS_PER_CHUNK - SUMMARY_CHUNK_OVERLAP)
        if start_index >= len(text):
            break
        if start_index + SUMMARY_CHUNK_OVERLAP >= len(text):
            start_index = len(text)

    logger.info(f"Divided text into {len(chunks)} chunks.")
    
    summaries = []
    for i, chunk in enumerate(chunks):
        logger.debug(f"Summarizing chunk {i+1}/{len(chunks)} (length: {len(chunk)})...")
        summary_chunk = await generate_summary(chunk, "default")
        summaries.append(summary_chunk)
        logger.debug(f"Chunk {i+1} summary length: {len(summary_chunk)}")

    combined_summary = "\n\n".join(summaries)
    logger.info(f"Combined {len(summaries)} chunk summaries. Total length: {len(combined_summary)}")

    if len(combined_summary) > MIN_CHARS_FOR_RECURSIVE:
        logger.info(f"Combined summary still too long ({len(combined_summary)}). Recursively summarizing again.")
        return await summarize_long_text(combined_summary, style_key)
    else:
        logger.info(f"Final summarization of combined text (length: {len(combined_summary)}).")
        return await generate_summary(combined_summary, style_key)