from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards.authorization_kb import kb_authorization
from keyboards.shopping_kb import kb_shopping
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base.sqlite_db import Database
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aioschedule
import asyncio




class Scheduler:
    async def make_task(self):
        aioschedule.every().day.at("9:00").do(self.display_notification)
        #aioschedule.every(5).seconds.do(self.display_notification)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    async def family_name_sort(self, family_name_tuple):
        sorted_list = []
        family_name_tuple_len = len(family_name_tuple)
        for i in range(family_name_tuple_len):
            if family_name_tuple[i][0] not in sorted_list:
                sorted_list.append(family_name_tuple[i][0])
        return sorted_list
    async def display_notification(self):
        family_name_tuple = await Database().Notifications().get_all_family_name()
        family_name_list_sorted = await self.family_name_sort(family_name_tuple)
        for family_name in family_name_list_sorted:
            for user_id in await Database().Notifications().get_all_user_id_in_family_name(family_name):
                try:
                    read_list, product_list, amount_list = await Database().ShoppingList().sql_read(user_id)
                except TypeError:
                    print('break')
                    break
                shopping_list = ', '.join(product_list)
                try:
                    await bot.send_message(user_id[0], f'Список покупок: \n'
                                                       f'{shopping_list}.\n\n'
                                                       f'Более подробный список - */Посмотреть записи*',
                                           parse_mode='markdown')
                except:
                    print('зы')

                    #print(f'family_name = {family_name}')
                    #print(f'user_id = {user_id[0]}')
                    #print(f'read_list = {read_list}')
                    #print(f'shopping_list = {shopping_list}')
                    #print(f'----------------------------')
        return
