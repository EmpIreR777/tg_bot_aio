import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault

from create_bot import bot, dp, admins
from handlers.admin_panel import admin_router
from handlers.user_router import user_router
from db_handler.db_funk import get_all_users
from handlers.start import start_router, questionnaire_router
# from work_time.time_func import send_time_msg

async def set_commands():
    commands = [  # Настройка командного меню через код слева от скрепки
        BotCommand(command='start', description='Старт'),
        BotCommand(command='start_2', description='Старт 2'),
        BotCommand(command='faq', description='Частые вопросы'),
        BotCommand(command='profile', description='Мой профиль'),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая выполнится когда бот запустится
async def start_bot():
    count_users = await get_all_users(count=True)
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, f'Я запущен🥳. Сейчас в базе данных <b>{count_users}</b> пользователей.')
    except:
        pass


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен. За что?😔')
    except:
        pass


async def main():
    # регистрация роутеров
    dp.include_router(user_router)
    dp.include_router(admin_router)

    # регистрация функций при старте и завершении работы бота
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_router(questionnaire_router)
    dp.include_router(start_router)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot, allowed_updates=dp.resolve_used_update_types())
        await set_commands()
    except Exception:
        raise 'Всё катиться в тартарары!!!'
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
