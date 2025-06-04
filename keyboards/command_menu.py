from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description="🚀 Запустити бота"),
        BotCommand(command="/help", description="ℹ️ Допомога"),
        BotCommand(command="/settings", description="⚙️ Налаштування"),
        BotCommand(command="/cancel", description="❌ Скасувати поточну дію")
    ]
    await bot.set_my_commands(main_menu_commands, BotCommandScopeDefault())
