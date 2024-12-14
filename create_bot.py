import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncpg_lite import DatabaseManager

from config import setting


pg_manager = DatabaseManager(db_url=setting.get_db_url(),
                              deletion_password=setting.get_db_root_password())

# redis_url = config('REDIS_URL')
storage = RedisStorage.from_url(setting.get_redis_url())
dp = Dispatcher(storage=storage)

# dp = Dispatcher(storage=MemoryStorage())
# from db_handler.db_class import PostgresHandler
all_media_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'all_media')

# pg_db = PostgresHandler(config('PG_LINK'))

scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
admins = [int(admin_id) for admin_id in setting.get_id_admin().split(',')]

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=setting.get_bot_token(),
           default=DefaultBotProperties(parse_mode=ParseMode.HTML))
