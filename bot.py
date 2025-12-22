from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from redis.asyncio import Redis

from config import settings

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
