import logging
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from config import SUPPORTED_LANGUAGES, SUMMARY_STYLES
from handlers.common_handlers import get_user_settings
from keyboards.inline import (
    get_language_keyboard,
    get_main_settings_keyboard,
    get_summary_style_keyboard
)
from states.user_states import SettingsStates

logger = logging.getLogger(__name__)
router = Router()
logger.info("settings_handlers.router created.")


@router.callback_query(F.data == "settings:main")
async def cq_back_to_main_settings(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f"cq_back_to_main_settings called by user {callback.from_user.id}")
    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)
    await callback.message.edit_text(
        "⚙️ <b>Налаштування бота</b>\n\nОберіть, що бажаєте змінити:",
        reply_markup=get_main_settings_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings:language", SettingsStates.MAIN_SETTINGS_MENU)
async def cq_select_language_menu(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    user_id = callback.from_user.id
    logger.info(f"cq_select_language_menu called by user {user_id}")
    user_prefs = get_user_settings(user_id, user_settings)
    await state.set_state(SettingsStates.CHOOSING_LANGUAGE)
    await callback.message.edit_text(
        "🗣️ Оберіть мову для транскрипції аудіо:",
        reply_markup=get_language_keyboard(user_prefs["language"])
    )
    await callback.answer()


@router.callback_query(SettingsStates.CHOOSING_LANGUAGE, F.data.startswith("select_lang:"))
async def cq_set_language(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    user_id = callback.from_user.id
    lang_code = callback.data.split(":")[1]
    logger.info(f"cq_set_language called by user {user_id}, lang_code: {lang_code}")

    if lang_code not in SUPPORTED_LANGUAGES:
        logger.warning(f"Invalid lang_code '{lang_code}' from user {user_id}")
        await callback.answer("❌ Невірний код мови.", show_alert=True)
        return

    user_prefs = get_user_settings(user_id, user_settings)
    user_prefs["language"] = lang_code
    logger.info(f"User {user_id} language set to {lang_code}")

    await callback.answer(f"✅ Мову встановлено: {SUPPORTED_LANGUAGES[lang_code]}", show_alert=False)
    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)
    await callback.message.edit_text(
        f"⚙️ <b>Налаштування бота</b>\n\nМову транскрипції змінено на: {hbold(SUPPORTED_LANGUAGES[lang_code])}\nОберіть, що бажаєте змінити:",
        reply_markup=get_main_settings_keyboard()
    )


@router.callback_query(F.data == "settings:summary_style", SettingsStates.MAIN_SETTINGS_MENU)
async def cq_select_summary_style_menu(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    user_id = callback.from_user.id
    logger.info(f"cq_select_summary_style_menu called by user {user_id}")
    user_prefs = get_user_settings(user_id, user_settings)
    await state.set_state(SettingsStates.CHOOSING_SUMMARY_STYLE)
    await callback.message.edit_text(
        "💡 Оберіть стиль для згенерованого підсумку:",
        reply_markup=get_summary_style_keyboard(user_prefs["summary_style"])
    )
    await callback.answer()


@router.callback_query(SettingsStates.CHOOSING_SUMMARY_STYLE, F.data.startswith("select_style:"))
async def cq_set_summary_style(callback: types.CallbackQuery, state: FSMContext, user_settings: dict):
    user_id = callback.from_user.id
    style_code = callback.data.split(":")[1]
    logger.info(f"cq_set_summary_style called by user {user_id}, style_code: {style_code}")

    if style_code not in SUMMARY_STYLES:
        logger.warning(f"Invalid style_code '{style_code}' from user {user_id}")
        await callback.answer("❌ Невірний стиль підсумку.", show_alert=True)
        return

    user_prefs = get_user_settings(user_id, user_settings)
    user_prefs["summary_style"] = style_code
    user_prefs["summary_style_name"] = SUMMARY_STYLES[style_code]["name"]
    logger.info(f"User {user_id} summary style set to {style_code}")

    await callback.answer(f"✅ Стиль підсумку встановлено: {SUMMARY_STYLES[style_code]['name']}", show_alert=False)
    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)
    await callback.message.edit_text(
        f"⚙️ <b>Налаштування бота</b>\n\nСтиль підсумку змінено на: {hbold(SUMMARY_STYLES[style_code]['name'])}\nОберіть, що бажаєте змінити:",
        reply_markup=get_main_settings_keyboard()
    )
