# handlers/common_handlers.py
from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

from keyboards.inline import get_main_settings_keyboard
from states.user_states import SettingsStates
from config import DEFAULT_LANGUAGE, DEFAULT_SUMMARY_STYLE, SUPPORTED_LANGUAGES, SUMMARY_STYLES

router = Router()


def get_user_settings(user_id: int, dp_user_settings: dict):
    if user_id not in dp_user_settings:
        dp_user_settings[user_id] = {
            "language": DEFAULT_LANGUAGE,
            "summary_style": DEFAULT_SUMMARY_STYLE,
            "summary_style_name": SUMMARY_STYLES[DEFAULT_SUMMARY_STYLE]["name"]
        }
    elif 'summary_style_name' not in dp_user_settings[user_id]:
        current_style_key = dp_user_settings[user_id].get('summary_style', DEFAULT_SUMMARY_STYLE)
        dp_user_settings[user_id]['summary_style_name'] = \
            SUMMARY_STYLES.get(current_style_key, SUMMARY_STYLES[DEFAULT_SUMMARY_STYLE])["name"]
    return dp_user_settings[user_id]


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, user_settings: dict, whisper_model: tuple):
    await state.clear()
    current_user_settings = get_user_settings(message.from_user.id, user_settings)

    user_name = message.from_user.first_name or "користувач"
    _, device = whisper_model

    current_summary_style_name = current_user_settings.get(
        'summary_style_name',
        SUMMARY_STYLES[DEFAULT_SUMMARY_STYLE]["name"]
    )

    text = (
        f"👋 Привіт, {hbold(user_name)}!\n\n"
        "Я твій ІІ-асистент, який уміє:\n"
        "1️⃣ 🗣️ Приймати голосові (.ogg) та аудіо (.mp3, .wav тощо) повідомлення.\n"
        "2️⃣ ✍️ Транскрибувати їх за допомогою Whisper.\n"
        "3️⃣ 💡 Генерувати стислий підсумок тексту за допомогою LLM.\n\n"
        f"🔹 Поточна мова транскрипції: {hbold(SUPPORTED_LANGUAGES.get(current_user_settings['language'], 'Авто'))}\n"
        f"🔹 Поточний стиль підсумку: {hbold(current_summary_style_name)}\n"
        f"🔬 Whisper працює на: {hbold(device.upper())}\n\n"
        "➡️ Надішли мені голосове, аудіо або текстове повідомлення для обробки.\n"
        "⚙️ Використовуй /settings для зміни налаштувань."
    )
    await message.answer(text)


@router.message(Command("help"))
async def cmd_help(message: types.Message, user_settings: dict):
    current_user_settings = get_user_settings(message.from_user.id, user_settings)
    current_lang_name = SUPPORTED_LANGUAGES.get(current_user_settings['language'], "Авто")

    current_style_key = current_user_settings.get('summary_style', DEFAULT_SUMMARY_STYLE)
    current_style_name = SUMMARY_STYLES.get(current_style_key, SUMMARY_STYLES[DEFAULT_SUMMARY_STYLE])["name"]

    text = (
        "ℹ️ <b>Довідка по боту:</b>\n\n"
        "📝 <b>Основні функції:</b>\n"
        "- Транскрипція голосових та аудіо повідомлень.\n"
        "- Стислий підсумок (резюме) транскрибованого або введеного тексту.\n\n"
        "🎤 <b>Як користуватись:</b>\n"
        "1. Надішліть голосове повідомлення (запис із Telegram) або аудіофайл.\n"
        "2. Або просто надішліть текст, який потрібно підсумувати.\n"
        "3. Бот автоматично обробить запит і надішле результат.\n\n"
        "⚙️ <b>Налаштування (/settings):</b>\n"
        f"- <b>Мова транскрипції:</b> Зараз — \"{current_lang_name}\". Впливає на точність розпізнавання.\n"
        f"- <b>Стиль підсумку:</b> Зараз — \"{current_style_name}\". Визначає рівень деталізації.\n\n"
        "❌ <b>Скасування:</b> Команда /cancel дозволяє перервати деякі дії (наприклад, вибір налаштувань)."
    )
    await message.answer(text)


@router.message(Command("settings"))
async def cmd_settings(message: types.Message, state: FSMContext):
    await state.set_state(SettingsStates.MAIN_SETTINGS_MENU)
    await message.answer(
        "⚙️ <b>Налаштування бота</b>\n\nОберіть, що бажаєте змінити:",
        reply_markup=get_main_settings_keyboard()
    )


@router.callback_query(F.data == "settings:close", SettingsStates.MAIN_SETTINGS_MENU)
async def cq_settings_close(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("👌 Налаштування закрито.")
    await callback.answer()


@router.message(Command("cancel"))
@router.callback_query(F.data == "cancel_state")
async def cmd_cancel(event: types.Message | types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        text = "🤷 Немає активних дій для скасування."
        if isinstance(event, types.Message):
            await event.answer(text)
        else:
            await event.answer(text, show_alert=True)
        return

    await state.clear()
    text = "✅ Дію скасовано."
    if isinstance(event, types.Message):
        await event.answer(text)
    elif isinstance(event, types.CallbackQuery) and event.message:
        try:
            await event.message.edit_text(text)
        except Exception:
            await event.message.answer(text)
        await event.answer()


@router.message(F.text.startswith('/'))
async def unhandled_command_fallback(message: types.Message):
    await message.reply("😕 Невідома команда. Спробуйте /start або /help.")
