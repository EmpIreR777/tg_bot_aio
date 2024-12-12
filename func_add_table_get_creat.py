import asyncio
from sqlalchemy import Integer, String, Text, DateTime, func
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
            {"name": "date_reg", "type": DateTime, "options": {"default": func.now()}},
        ]

        await pg_manager.create_table(table_name=table_name, columns=columns)


asyncio.run(create_table_users())
