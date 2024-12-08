import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender

from keyboards.all_kb import create_rat, main_kb, create_spec_kb
from keyboards.inline_kbs import ease_link_kb, get_inline_kb, create_gst_inline_kb
from utils.utils import get_random_person
from create_bot import questions, bot


start_router = Router()


@start_router.message(F.text.lower().contains('подписывайся'))
async def process_find_word(message: Message):
    await message.answer('В твоем сообщении было найдено слово "подписывайся", а у нас такое писать запрещено!')


@start_router.message(Command(commands=["settings", "about"]))
async def univers_cmd_handler(message: Message, command: CommandObject):
    command_args: str = command.args
    command_name = 'settings' if 'settings' in message.text else 'about'
    response = f'Была вызвана команда /{command_name}'
    if command_args:
        response += f' с меткой <b>{command_args}</b>'
    else:
        response += ' без метки'
    await message.answer(response)


@start_router.callback_query(F.data.startswith('qst_'))
async def cmd_start(call: CallbackQuery):
    await call.answer()
    qst_id = int(call.data.replace('qst_', ''))
    qst_data = questions[qst_id]
    msg_text = f'Ответ на вопрос {qst_data.get("qst")}\n\n' \
               f'<b>{qst_data.get("answer")}</b>\n\n' \
               f'Выбери другой вопрос:'
    async with ChatActionSender(bot=bot, chat_id=call.from_user.id,
                                action='typing'):
        await asyncio.sleep(2)
        await call.message.answer(
            msg_text,
            reply_markup=create_gst_inline_kb(questions))


@start_router.message(Command('faq'))
async def cmd_start_2(message: Message):
    await message.answer('Сообщение с инлайн клавиатурой с вопросами',
                         reply_markup=create_gst_inline_kb(questions))


@start_router.callback_query(F.data == 'back_home')
async def cmd_back_home(call: CallbackQuery):
    async with ChatActionSender(bot=bot, chat_id=call.from_user.id,
                                action='typing'):
        await asyncio.sleep(2)
        await call.answer('Вы вернулись на главный экран!', show_alert=False)
        main_screen_message = await call.message.answer('Главный экран', reply_markup=main_kb(call.from_user.id))

        # Удаляем клавиатуру
        await call.message.edit_reply_markup(reply_markup=None)

        # Удаляем сообщение "Главный экран" через некоторое время или по какому-то условию
        await asyncio.sleep(5)  # Ждём, например  секунд
        await main_screen_message.delete()  # Удаляем сообщение "Главный экран"


@start_router.callback_query(F.data == 'get_person')
async def send_random_person(call: CallbackQuery):
    await call.answer('Генерирую случайного пользователя', show_alert=False)
    user = get_random_person()
    formatted_message = (
        f"👤 <b>Имя:</b> {user['name']}\n"
        f"🏠 <b>Адрес:</b> {user['address']}\n"
        f"📧 <b>Email:</b> {user['email']}\n"
        f"📞 <b>Телефон:</b> {user['phone_number']}\n"
        f"🎂 <b>Дата рождения:</b> {user['birth_date']}\n"
        f"🏢 <b>Компания:</b> {user['company']}\n"
        f"💼 <b>Должность:</b> {user['job']}\n"
    )
    async with ChatActionSender(bot=bot, chat_id=call.from_user.id,
                                action='typing'):
        await asyncio.sleep(2)
        await call.message.answer(formatted_message)
        await call.message.edit_reply_markup(reply_markup=None)


@start_router.message(F.text == 'Давай инлайн!')
async def get_inline_btn_link(message: Message):
    await message.answer(
        'Вот тебе инлай клавиатура со ссылками!',
        reply_markup=get_inline_kb()
    )


@start_router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    command_args: str = command.args
    if command_args:
        await message.answer(
            f'Запуск сообщения по команде /start используя фильтр CommandStart() с меткой <b>{command_args}</b>',
            reply_markup=main_kb(message.from_user.id),
        )
    else:
        await message.answer(
            f'Запуск сообщения по команде /start используя фильтр CommandStart() без метки',
            reply_markup=main_kb(message.from_user.id),
        )


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Запуск сообщения по команде /start используя фильтр CommandStart()', reply_markup=main_kb(message.from_user.id))


@start_router.message(Command('start_2'))
async def cmd_start_2(message: Message):
    await message.answer('Запуск сообщения по команде /start_2 используя фильтр Command()', reply_markup=create_spec_kb())


@start_router.message(F.text == '/start_3')
async def cmd_start_3(message: Message):
    await message.answer('Запуск сообщения по команде /start_3 используя магический фильтр F.text!', reply_markup=create_rat())
