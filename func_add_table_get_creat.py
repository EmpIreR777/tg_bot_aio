import asyncio
from sqlalchemy import Integer, String, Text, DateTime, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from create_bot import pg_manager


async def create_table_users(table_name='users_reg'):
    async with pg_manager:
        columns = [
            {"name": "user_id", "type": Integer, "options": {"primary_key": True, "autoincrement": False}},
            {"name": "gender", "type": String(50)},
            {"name": "age", "type": Integer},
            {"name": "full_name", "type": String(255)},
            {"name": "user_login", "type": String(255), "options": {"unique": True}},
            {"name": "photo", "type": Text},
            {"name": "about", "type": Text},
            {"name": "date_reg", "type": DateTime, "options": {"server_default": text("now()")}},
        ]

        await pg_manager.create_table(table_name=table_name, columns=columns)


asyncio.run(create_table_users())


# Достать данные о пользователе из указанной таблицы
async def get_user_data(user_id: int, table_name='users_reg'):
    async with pg_manager:
        user_info = await pg_manager.select_data(
            table_name=table_name, where_dict={'user_id': user_id}, one_dict=True)
        if user_info:
            return user_info
        else:
            return None


#
async def insert_user(user_data: dict, table_name='users_reg'):
    async with pg_manager:
        await pg_manager.insert_data_with_update(
            table_name=table_name, records_data=user_data, conflict_column='user_id', update_on_conflict=True)
