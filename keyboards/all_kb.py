from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                            KeyboardButtonPollType, ReplyKeyboardRemove)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from create_bot import admins, bot


def home_page_kb(user_telegram_id: int):
    kb_list = [[KeyboardButton(text="🔙 Назад")]]
    if user_telegram_id in admins:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
    return ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Воспользуйтесь меню:"
    )


def gender_kb():
    kb_list = [[KeyboardButton(text="👨‍🦱Мужчина")], [KeyboardButton(text="👩‍🦱Женщина")]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери пол:"
    )
    return keyboard


def create_rat():
    builder = ReplyKeyboardBuilder()
    for item in [str(i) for i in range(1, 11)]:
        builder.button(text=item)
    builder.button(text='Назад')
    builder.adjust(4, 4, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def main_kb(user_telegram_id: int):
    kb_list = [
        [KeyboardButton(text='Рандомный пользователь!'),
          KeyboardButton(text='👤 Профиль')
          ]]
    if user_telegram_id in admins:
        kb_list.append([KeyboardButton(text="⚙️ Админ панель")])
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard


def create_spec_kb():
    kb_list = [
        [KeyboardButton(text='Отправить гео', request_location=True)],
        [KeyboardButton(text='Поделиться номером', request_contact=True)],
        [KeyboardButton(text='Отправить викторину/опрос',
                         request_poll=KeyboardButtonPollType())]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Воспользуйтесь специальной клавиатурой:'
    )
    return keyboard
