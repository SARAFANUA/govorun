from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import SUPPORTED_LANGUAGES, SUMMARY_STYLES


def get_main_settings_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🗣️ Мова транскрипції", callback_data="settings:language")
    builder.button(text="💡 Стиль підсумку", callback_data="settings:summary_style")
    builder.button(text="◀️ Закрити налаштування", callback_data="settings:close")
    builder.adjust(1)
    return builder.as_markup()


def get_language_keyboard(current_lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, name in SUPPORTED_LANGUAGES.items():
        text = f"✅ {name}" if code == current_lang else name
        builder.button(text=text, callback_data=f"select_lang:{code}")
    builder.button(text="◀️ Назад до налаштувань", callback_data="settings:main")
    builder.adjust(1)
    return builder.as_markup()


def get_summary_style_keyboard(current_style: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, style_info in SUMMARY_STYLES.items():
        name = style_info["name"]
        text = f"✅ {name}" if code == current_style else name
        builder.button(text=text, callback_data=f"select_style:{code}")
    builder.button(text="◀️ Назад до налаштувань", callback_data="settings:main")
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_state")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
