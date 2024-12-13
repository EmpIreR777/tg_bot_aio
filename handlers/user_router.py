from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import Message

from create_bot import bot
from db_handler.db_funk import get_user_data, insert_user
from keyboards.all_kb import main_kb#, home_page_kb
from utils.utils import get_refer_id
from aiogram.utils.chat_action import ChatActionSender


user_router = Router()


universe_text = 'Чтоб получить информацию о своем профиле воспользуйся кнопкой "Мой профиль" или специальной командой из командного меню.'


@user_router.message(F.text.contains('Назад'))
async def cmd_start(message: Message):
    await message.answer(
        f'{message.from_user.first_name}, Вижу что вы уже в моей базе данных. {universe_text}',
        reply_markup=main_kb(message.from_user.id),
    )


@user_router.message(Command('start_2'))
async def cmd_start(message: Message, command: CommandObject):
    async with ChatActionSender.typing(bot=bot, chat_id=message.from_user.id):
        user_info = await get_user_data(user_id=message.from_user.id)

    if user_info:
        response_text = f'{user_info.get("full_name")}, вижу что вы уже в моей базе данных. {universe_text}'
    else:
        refer_id = get_refer_id(command.args)
        await insert_user(
            user_data={
                'user_id': message.from_user.id,
                'full_name': message.from_user.full_name,
                'user_login': message.from_user.username,
                'refer_id': refer_id,
            }
        )
        if refer_id:
            response_text = (
                f'{message.from_user.full_name}, вы зарегистрированы в боте и закреплены за '
                f'пользователем с ID <b>{refer_id}</b>. {universe_text}'
            )
        else:
            response_text = (
                f'{message.from_user.full_name}, вы зарегистрированы в боте и ни за кем не закреплены. '
                f'{universe_text}'
            )

    await message.answer(text=response_text, reply_markup=main_kb(message.from_user.id))
