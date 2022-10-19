from aiogram.utils import executor
from create_bot import dp, bot
from data_base.sqlite_db import Database
from handlers.notifications import Scheduler
import asyncio
import aioschedule


async def start(*args):
    print('DOLJNIK bot start')
    Database.sql_start()
    asyncio.create_task(Scheduler().make_task())


from handlers import authorization, shopping_list
authorization.register_handlers_client(dp)
shopping_list.register_handlers_client(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=start)
