import asyncio
from aiogram import Bot, Dispatcher
from os import getenv
from sys import exit
import Expenses
from aiogram.types.bot_command import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage




# берем токен бота из переменной окружения, если нет - выходим
bot_token = getenv('BOT_TOKEN')
if not bot_token:
    exit("Error: no token provided")

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/save", description="Записать расходы"),
        BotCommand(command="/load", description="Прочитать расходы")
    ]
    await bot.set_my_commands(commands)


async def main():
    # инициализируем бота
    bot = Bot(token=bot_token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    Expenses.register_handlers_expense(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())