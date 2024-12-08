from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           WebAppInfo)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from create_bot import questions


def create_gst_inline_kb(questions: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for question_id, question_data in questions.items():
        builder.row(
            InlineKeyboardButton(
                text=question_data.get('qst'),
                callback_data=f'qst_{question_id}'
            )
        )
    builder.row(
        InlineKeyboardButton(
            text='На главную',
            callback_data='back_home'
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def get_inline_kb():
    inline_kb_list = [
        [InlineKeyboardButton(
            text='Генерировать пользователя', callback_data='get_person')],
        [InlineKeyboardButton(
            text='На главную', callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def ease_link_kb():
    inline_kb_list = [
        [InlineKeyboardButton(
            text='Мой хабр', url='https://habr.com/ru/users/EmpIreR777/')],
        [InlineKeyboardButton(
            text='Мой телеграм', url='tg://resolve?domain=EmpIreR7')],
        [InlineKeyboardButton(
            text='Веб приложение',
              web_app=WebAppInfo(url='https://tg-promo-bot.ru/questions'))]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
