import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from decouple import config
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from asyncpg_lite import DatabaseManager

pg_manager = DatabaseManager(db_url=config('PG_URL'),
                              deletion_password=config('ROOT_PASS'))


questions = {
    1: {'qst': 'Столица Италии?', 'answer': 'Рим'},
    2: {'qst': 'Сколько континентов на Земле?', 'answer': 'Семь'},
    3: {'qst': 'Самая длинная река в мире?', 'answer': 'Нил'},
    4: {'qst': 'Какой элемент обозначается символом "O"?', 'answer': 'Кислород'},
    5: {'qst': 'Как зовут главного героя книги "Гарри Поттер"?', 'answer': 'Гарри Поттер'},
    6: {'qst': 'Сколько цветов в радуге?', 'answer': 'Семь'},
    7: {'qst': 'Какая планета третья от Солнца?', 'answer': 'Земля'},
    8: {'qst': 'Кто написал "Войну и мир"?', 'answer': 'Лев Толстой'},
    9: {'qst': 'Что такое H2O?', 'answer': 'Вода'},
    10: {'qst': 'Какой океан самый большой?', 'answer': 'Тихий океан'},
}


storage = RedisStorage.from_url(config('REDIS_URL'))
redis_url = config('REDIS_URL')
dp = Dispatcher(storage=storage)

# from db_handler.db_class import PostgresHandler
all_media_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'all_media')
# pg_db = PostgresHandler(config('PG_LINK'))
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
admins = [int(admin_id) for admin_id in config('ADMIN_ID').split(',')]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=config('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher(storage=MemoryStorage())
