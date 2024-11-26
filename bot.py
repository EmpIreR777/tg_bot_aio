from datetime import datetime
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config_reader import config


logging.basicConfig(level=logging.INFO)


bot = Bot(token=config.bot_token.get_secret_value())
db = Dispatcher()
db["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


@db.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    await message.answer(f"Бот запущен {started_at}")


@db.message(Command('reply'))
async def cmd_reply(message: types.Message):
    await message.reply("Это ответ с 'ответом'")


@db.message(Command('answer'))
async def cmd_answer(message: types.Message):
    await message.answer('Это простой ответ')


@db.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Hello')


@db.message(Command('dice'))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji='🎲')


async def main():
    await db.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
