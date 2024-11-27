import re
from datetime import datetime
import asyncio
import logging
from aiogram import F, html
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message, FSInputFile, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hide_link
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from config_reader import config

import httpx

logging.basicConfig(level=logging.INFO)


bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


@dp.message(Command("special_buttons"))
async def cmd_special_buttons(message: types.Message):
    builder = ReplyKeyboardBuilder()
    # метод row позволяет явным образом сформировать ряд
    # из одной или нескольких кнопок. Например, первый ряд
    # будет состоять из двух кнопок...
    builder.row(
        types.KeyboardButton(text="Запросить геолокацию", request_location=True),
        types.KeyboardButton(text="Запросить контакт", request_contact=True),
    )
    # ... второй из одной ...
    builder.row(types.KeyboardButton(text="Создать викторину", request_poll=types.KeyboardButtonPollType(type="quiz")))
    # ... а третий снова из двух
    builder.row(
        types.KeyboardButton(
            text="Выбрать премиум пользователя",
            request_user=types.KeyboardButtonRequestUser(request_id=1, user_is_premium=True),
        ),
        types.KeyboardButton(
            text="Выбрать супергруппу с форумами",
            request_chat=types.KeyboardButtonRequestChat(request_id=2, chat_is_channel=False, chat_is_forum=True),
        ),
    )
    # WebApp-ов пока нет, сорри :(

    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@dp.message(Command('reply_builder'))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        'Выберите число:', reply_markup=builder.as_markup(
            resize_keyboard=True, one_time_keyboard=True)
    )


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text='С пюрешкой'),
        types.KeyboardButton(text='Без пюрешки')]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите способ подачи')
    await message.answer('Как подавать котлеты?', reply_markup=keyboard)


@dp.message(F.text.lower() == 'с пюрешкой')
async def with_puree(message: types.Message):
    await message.reply('Отличный выбор!', reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text.lower() == 'без пюрешки')
async def withour_puree(message: types.Message):
    await message.reply('Так не вкустно!', reply_markup=types.ReplyKeyboardRemove())


@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    # Получение случайного факта о котах и изображения
    async with httpx.AsyncClient() as client:
        fact_response = await client.get('https://cat-fact.herokuapp.com/facts/random')
        image_response = await client.get('https://api.thecatapi.com/v1/images/search')

        # Извлечение факта и изображения
        fact = fact_response.json().get('text', 'Факт не найден')
        image_url = image_response.json()[0].get('url')

    hidden_link_text = f"[Скрытая ссылка]({fact_response.url})"

    await message.answer(
        f"{hidden_link_text} "
        f"Факт о котах: *{fact}*n"
        "Документация Telegram: *существует*n"
        "Пользователи: *не читают документацию*n"
        "Груша:",
        disable_web_page_preview=False,  # Включить предпросмотр ссылки
        parse_mode=ParseMode.MARKDOWN,  # Используйте Markdown для форматирования
    )

    # Отправка изображения кота
    if image_url:
        await message.answer_photo(image_url, caption="Вот случайное изображение кота!")


@dp.message(Command("album"))
async def cmd_album(message: Message):
    album_builder = MediaGroupBuilder(
        caption="Общая подпись для будущего альбома"
    )
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg")
        # caption="Подпись к конкретному медиа"

    )
    # Если мы сразу знаем тип, то вместо общего add
    # можно сразу вызывать add_<тип>
    album_builder.add_photo(
        # Для ссылок или file_id достаточно сразу указать значение
        media="https://picsum.photos/seed/groosha/400/300"
    )
    album_builder.add_photo(
        media="<ваш file_id>"
    )
    await message.answer_media_group(
        # Не забудьте вызвать build()
        media=album_builder.build()
    )


@dp.message(F.animation)
async def echo_gif(message: Message):
    await message.reply_animation(message.animation.file_id)


@dp.message(Command('help'))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == 'help'
))
async def cmd_start_help(message: Message):
    await message.answer('Это сообщение со справкой')


@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    book_number = command.args.split("_")[1]
    await message.answer(f"Sending book №{book_number}")


@dp.message(Command("settimer"))  #  prefix='%' меняем с чего начать
async def cmd_settimer(message: Message, command: CommandObject):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer("Ошибка: не переданы аргументы")
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer("Ошибка: неправильный формат команды. Пример:\n" "/settimer <time> <message>")
        return
    await message.answer("Таймер добавлен!\n" f"Время: {delay_time}\n" f"Текст: {text_to_send}")


# @dp.message(F.text)
# async def extract_data(message: Message):
#     data = {"url": "<N/A>", "email": "<N/A>", "code": "<N/A>"}
#     entities = message.entities or []
#     for item in entities:
#         if item.type in data.keys():
#             # Неправильно
#             # data[item.type] = message.text[item.offset : item.offset+item.length]
#             # Правильно
#             data[item.type] = item.extract_from(message.text)
#     await message.reply(
#         "Вот что я нашёл:\n"
#         f"URL: {html.quote(data['url'])}\n"
#         f"E-mail: {html.quote(data['email'])}\n"
#         f"Пароль: {html.quote(data['code'])}"
#     )


@dp.message(F.text)
async def echo_with_time(message: Message):
    # Получаем текущее время в часовом поясе ПК
    time_now = datetime.now().strftime('%H:%M')
    # Создаём подчёркнутый текст
    added_text = html.underline(f"Создано в {time_now}")
    # Отправляем новое сообщение с добавленным текстом
    await message.answer(f"{message.text}\n\n{added_text}", parse_mode="HTML")


@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    content = Text('Hello, ', Bold(message.from_user.full_name))
    await message.answer(**content.as_kwargs())


@dp.message(F.text, Command("test"))
async def any_message(message: Message):
    await message.answer("Hello, <b>world</b>!",
                          parse_mode=ParseMode.HTML)
    await message.answer("Hello, *world*\!",
                          parse_mode=ParseMode.MARKDOWN_V2)


@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    await message.answer(f"Бот запущен {started_at}")


@dp.message(Command('reply'))
async def cmd_reply(message: types.Message):
    await message.reply("Это ответ с 'ответом'")


@dp.message(Command('answer'))
async def cmd_answer(message: types.Message):
    await message.answer('Это простой ответ')


@dp.message(Command('dice'))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji='🎲')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
