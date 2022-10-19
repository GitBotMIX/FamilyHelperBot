import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

API_TOKEN = '5657697656:AAGxYLiTimWYiFxxw77twIxY4EaIQ58sZ9M'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)