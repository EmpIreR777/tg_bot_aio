import asyncio
import os
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import (Message, CallbackQuery,
                           FSInputFile, InputMediaVideo,
                           InputMediaPhoto,
                           ReplyKeyboardRemove)
from aiogram.utils.chat_action import ChatActionSender
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import text

from db_handler.db_funk import get_user_data, insert_user
from keyboards.all_kb import (create_rat, home_page_kb, main_kb,
                            create_spec_kb, gender_kb)
from keyboards.inline_kbs import (
    ease_link_kb, get_inline_kb, create_gst_inline_kb,
    get_login_tg, check_data)
from utils.utils import get_random_person, get_msc_date, extract_number
from utils.dict import questions
from create_bot import bot, admins, all_media_dir
from filters.is_admin import IsAdmin


class Form(StatesGroup):
    gender = State()
    age = State()
    full_name = State()
    user_login = State()
    photo = State()
    about = State()
    check_state = State()


questionnaire_router = Router()


@questionnaire_router.message(Command('start_questionnaire'))
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer('Привет. Для начала выбери свой пол: ', reply_markup=gender_kb())
    await state.set_state(Form.gender)


@questionnaire_router.message((F.text.lower().contains('мужчина')) | (F.text.lower().contains('женщина')), Form.gender)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(
        gender=message.text, user_id=message.from_user.id
        )
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer('Супер! А теперь напиши сколько тебе полных лет:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.age)


@questionnaire_router.message(F.text, Form.gender)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(2)
        await message.answer(
            'Пожалуйста, выбери вариант из тех что в клавиатуре:',
            reply_markup=gender_kb())
        await state.set_state(Form.gender)


@questionnaire_router.message(F.text, Form.age)
async def start_questionnaire_process(message: Message, state: FSMContext):
    check_age =  extract_number(message.text)
    if not check_age or not (1 <= int(message.text) <= 100):
        await message.reply("Пожалуйста, введите корректный возраст (число от 1 до 100).")
        return
    await state.update_data(age=check_age)
    await message.answer('Теперь укажите своё полное имя:')
    await state.set_state(Form.full_name)


@questionnaire_router.message(F.text, Form.full_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    text = 'Теперь укажите ваш логин, который будет использоваться в боте'
    if message.from_user.username:
        text += ' или нажмите на кнопку ниже и в этом случае вашим логином будет логин из вашего телеграмма:'
        await message.answer(text, reply_markup=get_login_tg())
    else:
        text += ' : '
        await message.answer(text)
    await state.set_state(Form.user_login)


# вариант когда мы берем логин из профиля телеграмм
@questionnaire_router.callback_query(F.data, Form.user_login)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await call.answer('Беру логин с телеграмм профиля')
    await call.message.edit_reply_markup(reply_markup=None)
    await state.update_data(user_login=call.from_user.username)
    await call.message.answer('А теперь отправьте фото, которое будет использоваться в вашем профиле: ')
    await state.set_state(Form.photo)


# вариант когда мы берем логин из введенного пользователем
@questionnaire_router.message(F.text, Form.user_login)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(user_login=message.from_user.username)
    await message.answer('А теперь отправьте фото, которое будет использоваться в вашем профиле: ')
    await state.set_state(Form.photo)


@questionnaire_router.message(F.photo, Form.photo)
async def start_questionnaire_process(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await message.answer('А теперь расскажите пару слов о себе[-1]: ')
    await state.set_state(Form.about)


@questionnaire_router.message(F.document.mime_type.startswith('image/'), Form.photo)
async def start_questionnaire_process(message: Message, state: FSMContext):
    photo_id = message.document.file_id
    await state.update_data(photo=photo_id)
    await message.answer('А теперь расскажите пару слов о себе image/: ')
    await state.set_state(Form.about)


@questionnaire_router.message(F.document, Form.photo)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, отправьте фото!')
    await state.set_state(Form.photo)


@questionnaire_router.message(F.text, Form.about)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(about=message.text)

    data = await state.get_data()

    caption = (
        f'Пожалуйста, проверьте все ли верно: \n\n'
        f'<b>Полное имя</b>: {data.get("full_name")}\n'
        f'<b>Пол</b>: {data.get("gender")}\n'
        f'<b>Возраст</b>: {data.get("age")} лет\n'
        f'<b>Логин в боте</b>: {data.get("user_login")}\n'
        f'<b>О себе</b>: {data.get("about")}'
    )

    await message.answer_photo(photo=data.get('photo'), caption=caption, reply_markup=check_data())
    await state.set_state(Form.check_state)


# сохраняем данные
@questionnaire_router.callback_query(F.data == 'correct', Form.check_state)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await call.answer('Данные сохранены')
    user_data = await state.get_data()
    user_data['date_reg'] = datetime.now().replace(second=0, microsecond=0)
    await insert_user(user_data)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        'Благодарю за регистрацию. Ваши данные успешно сохранены!', reply_markup=main_kb(call.from_user.id)
    )
    await state.clear()


@questionnaire_router.callback_query(F.data == 'incorrect', Form.check_state)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await call.answer('Запускаем сценарий с начала')
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Привет. Для начала выбери свой пол:',
                              reply_markup=gender_kb())
    await state.set_state(Form.gender)


""" Всё что ниже это без FSM."""
start_router = Router()


@start_router.message(Command('profile'))
@start_router.message(F.text.contains('Профиль'))
async def start_profile(message: Message, state: FSMContext):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        user_info = await get_user_data(user_id=message.from_user.id)
        profile_message = (
            f"<b>👤 Профиль пользователя:</b>\n"
            f"<b>🆔 ID:</b> {user_info['user_id']}\n"
            f"<b>💼 Логин:</b> @{user_info['user_login']}\n"
            f"<b>📛 Полное имя:</b> {user_info['full_name']}\n"
            f"<b>🧑‍🦰 Пол:</b> {user_info['gender']}\n"
            f"<b>🎂 Возраст:</b> {user_info['age']}\n"
            f"<b>📅 Дата регистрации:</b> {user_info['date_reg']}\n"
            f"<b>📝 О себе:</b> {user_info['about']}\n"
            f'👥 Количество приглашенных тобой пользователей: <b>{user_info.get("count_refer")}</b>\n\n'
            f"<b>🚀 Вот твоя персональная ссылка на приглашение: </b>"
            f'<code>https://t.me/new_aio_test_bot?start={message.from_user.id}</code>'
        )
        await message.answer_photo(photo=user_info.get('photo'), caption=profile_message)
        await message.answer(text='asdas', reply_markup=home_page_kb(message.from_user.id))


@start_router.message(Command('send_media_group'))
async def cmd_start(message: Message, state: FSMContext):
    photo_1 = InputMediaPhoto(type='photo',
                              media=FSInputFile(path=os.path.join(all_media_dir, 'i (1).webp')),
                              caption='Описание ко <b>ВСЕЙ</b> медиагруппе')
    photo_2 = InputMediaPhoto(type='photo',
                              media=FSInputFile(path=os.path.join(all_media_dir, 'i (2).webp')))
    photo_3 = InputMediaPhoto(type='photo',
                              media=FSInputFile(path=os.path.join(all_media_dir, 'sample-birch-400x300.jpg')))
    video_1 = InputMediaVideo(type='video',
                              media=FSInputFile(path=os.path.join(all_media_dir, 'sample-10s.mp4')))
    photo_4 = InputMediaPhoto(type='photo',
                              media=FSInputFile(path=os.path.join(all_media_dir, 'sample-blue-200x200.jpg')))
    video_2 = InputMediaVideo(type='video',
                              media=FSInputFile(path=os.path.join(all_media_dir, 'sample-9s.mp3')))

    media = [photo_1, photo_2, photo_3, video_1, photo_4, video_2]
    await message.answer_media_group(media=media)


@start_router.message(F.video_note)
async def cmd_start(message: Message, state: FSMContext):
    print(message.video_note.file_id)


@start_router.message(Command('send_voice'))
async def cmd_start(message: Message, state: FSMContext):
    async with ChatActionSender.record_voice(
        bot=bot, chat_id=message.from_user.id):
        await asyncio.sleep(3)
        await message.answer_voice(voice=FSInputFile(
            path=os.path.join(all_media_dir, 'sample-12s.mp3')))


@start_router.message(Command('send_video_note'))
async def cmd_start(message: Message, state: FSMContext):
    async with ChatActionSender.record_video_note(bot=bot, chat_id=message.from_user.id):
        await asyncio.sleep(3)
        await message.answer_video_note(
            video_note='sample-10s.mp4')


@start_router.message(Command('send_video'))
async def cmd_start(message: Message, state: FSMContext):
    video_file = FSInputFile(path=os.path.join(all_media_dir, 'sample-10s.mp4'))
    msg_1 = await message.answer_video(video=video_file, caption='Моя <b>отформатированная подпись</b> к файлу')
    await asyncio.sleep(2)
    await msg_1.edit_caption(caption='Новое описание к видео 1')

    await asyncio.sleep(2)
    new_video_file = FSInputFile(path=os.path.join(
        all_media_dir, 'sample-5s.mp4'))
    await msg_1.edit_media(
        media=InputMediaVideo(media=new_video_file, caption='Новое видео и у него новое описание.'),
        reply_markup=ease_link_kb(),
    )


@start_router.message(Command('send_video'))
async def cmd_start(message: Message, state: FSMContext):
    video_file = FSInputFile(path=os.path.join(all_media_dir, 'sample-10s.mp4'))
    msg = await message.answer_video(
        video=video_file, reply_markup=main_kb(message.from_user.id), caption='Моя отформатированная подпись к файлу'
    )
    await asyncio.sleep(2)
    await msg.answer_video(video=msg.video.file_id, caption='Новое описание к моему видео.', reply_markup=main_kb(message.from_user.id))
    await msg.delete()


@start_router.message(Command('send_photo'))
async def cmd_start(message: Message, state: FSMContext):
    # photo_file = FSInputFile(path=os.path.join(
    #     all_media_dir, 'i (2).webp'))
    # photo_id = 'AgACAgIAAxkDAAIDHGdXC3uNRjhRprdUahNZ8THx5OleAAJ-6zEbdoC4Sj46Af_y5PsLAQADAgADeQADNgQ'
    photo_url = 'https://avatars.mds.yandex.net/i?id=22a42b764502e262f9cc3af7bfa627bf_l-3563662-images-thumbs&n=13'
    msg_id = await message.answer_photo(
        photo=photo_url,
        reply_markup=main_kb(message.from_user.id),
        caption='Моя <u>отформатированная</u> подпись к <b>фото</b>',
    )
    print(msg_id.photo[-1].file_id)


@start_router.message(Command('send_audio'))
async def cmd_start(message: Message, state: FSMContext):
    # audio_file = FSInputFile(path=os.path.join(all_media_dir, 'sample-12s.mp3'), filename='audio')
    audio_id = 'CQACAgIAAxkDAAICxGdXAkv2KhExiwnm-BWD-W1AygTaAALuZgACCDO4SpN1gT2IInStNgQ'
    msg_id = await message.answer_audio(
        audio=audio_id,
        reply_markup=main_kb(message.from_user.id),
        caption='Моя <u>отформатированная</u> подпись к <b>файлу</b>',
    )


# @start_router.message(Command('test_edit_msg'))
# async def cmd_start(message: Message, state: FSMContext):
#     msg = await message.answer('<s>ПРИВЕТ!</s>')
#     print(msg.html_text)


# @start_router.message(Command('test_edit_msg'))
# async def cmd_start(message: Message, state: FSMContext):
#     msg = await message.answer('Привет!')
#     await asyncio.sleep(2)
#     old_text = msg.text
#     await msg.delete()
#     await message.answer(old_text, reply_markup=main_kb(message.from_user.id))


@start_router.message(Command('test_edit_msg'))
async def cmd_start(message: Message, state: FSMContext):
    # Бот делает отправку сообщения с сохранением объекта msg
    msg = await message.answer('Отправляю сообщение')
    # Достаем ID сообщения
    msg_id = msg.message_id
    # Имитируем набор текста 2 секунды и отправляеВ коде оставлены комментарии. Единственное, на что нужно обратить внимание, — строка:
    async with ChatActionSender(bot=bot, chat_id=message.from_user.id, action="typing"):
        await asyncio.sleep(2)
        await message.answer('Новое сообщение')
    # Делаем паузу ещё на 2 секунды
    await asyncio.sleep(2)
    # Изменяем текст сообщения, ID которого мы сохранили
    await bot.edit_message_text(text='<b>Отправляю сообщение!!!</b>', chat_id=message.from_user.id, message_id=msg_id)


@start_router.message(F.text.lower().contains('охотник'))
async def cmd_start(message: Message, state: FSMContext):
    # отправка обычного сообщения
    await message.answer('Я думаю, что ты тут про радугу рассказываешь')
    # то же действие, но через объект бота
    await bot.send_message(chat_id=message.from_user.id, text='Для меня это слишком просто')
    # ответ через цитату
    msg = await message.reply('Ну вот что за глупости!?')

    # ответ через цитату, через объект bot
    await bot.send_message(
        chat_id=message.from_user.id, text='Хотя, это забавно...', reply_to_message_id=msg.message_id
    )
    await bot.forward_message(
        chat_id=message.from_user.id, from_chat_id=message.from_user.id, message_id=msg.message_id
    )
    data_task = {
        'user_id': message.from_user.id,
        'full_name': message.from_user.full_name,
        'username': message.from_user.username,
        'message_id': message.message_id,
        'date': get_msc_date(message.date),
    }
    print(data_task)


@start_router.message(F.text.lower().contains('подписывайся'), IsAdmin(admins))
async def process_find_word(message: Message):
    await message.answer('О, админ, здарова! А тебе можно писать подписывайся.')


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
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        user_info = await get_user_data(user_id=message.from_user.id)
    if user_info:
        await message.answer(
            'Привет. Я вижу, что ты зарегистрирован, а значит тебе можно ' 'посмотреть, как выглядит твой профиль.',
            reply_markup=main_kb(message.from_user.id),
        )
    else:
        await message.answer('Привет. Для начала выбери свой пол:', reply_markup=gender_kb())
        await state.set_state(Form.gender)


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Запуск сообщения по команде /start используя фильтр CommandStart()', reply_markup=main_kb(message.from_user.id))


@start_router.message(Command('start_2'))
async def cmd_start_2(message: Message):
    await message.answer('Запуск сообщения по команде /start_2 используя фильтр Command()', reply_markup=create_spec_kb())


@start_router.message(F.text == '/start_3')
async def cmd_start_3(message: Message):
    await message.answer('Запуск сообщения по команде /start_3 используя магический фильтр F.text!', reply_markup=create_rat())
