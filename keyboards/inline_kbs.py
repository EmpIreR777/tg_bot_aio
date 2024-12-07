from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           WebAppInfo)
from aiogram.utils.keyboard import InlineKeyboardBuilder


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