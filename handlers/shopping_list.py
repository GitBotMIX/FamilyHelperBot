from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards.authorization_kb import kb_authorization
from keyboards.shopping_kb import kb_shopping
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base.sqlite_db import Database
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ShoppingList:
    class Add:
        async def add_item(self, message: types.Message):
            if await Database().sql_check_user_id(message.from_user.id) == False:
                await message.answer('Необходимо зарегистрироваться!❌', reply_markup=kb_authorization)
                return
            await message.answer('Что нужно купить:')
            await ShoppingList().Add().AddNoteStates.ADD_ITEM.set()
            await ShoppingList().Add().AddNoteStates.next()

        async def add_amount(self, message: types.Message, state: FSMContext):
            await message.answer('Количество:')
            async with state.proxy() as data:
                data['item'] = message.text
            await ShoppingList().Add().AddNoteStates.next()

        async def add_total(self, message: types.Message, state: FSMContext):
            async with state.proxy() as data:
                data['amount'] = message.text
                await message.answer(f'"{data["item"]}" успешно добавлено!')
            await Database().ShoppingList().sql_add(state, message)
            async with state.proxy() as data:
                for userid in await Database().Notifications().get_all_user_id_in_family_message(message):

                    if str(message.from_user.id) != str(userid[0]):
                        await bot.send_message(userid[0], f'Добавлена запись "{data["item"]}" '
                                                     f'пользователем {message.from_user.first_name}')
            await state.finish()

        class AddNoteStates(StatesGroup):
            ADD_ITEM = State()
            ADD_AMOUNT = State()
            ADD_TOTAL = State()

    class Read:
        async def read(self, message: types.Message, delete=False):
            if await Database().sql_check_user_id(message.from_user.id) == False:
                await message.answer('Необходимо зарегистрироваться!❌', reply_markup=kb_authorization)
                return
            try:
                read_list, product_list, amount_list = await Database().ShoppingList().sql_read(message)
            except TypeError:
                await message.answer(f'Список покупок пуст')
                return False
            if delete:
                for i in range(len(product_list)):
                    await message.answer(f'Купить: *{product_list[i]}*\nКоличество: {amount_list[i]}',
                                         parse_mode='markdown',
                                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(f'Удилить запись'
                                                                                                      f' "{product_list[i]}"',
                                                                                                      callback_data=f'del {product_list[i]}'
                                                                                                      )))
            else:
                read_list = '\n'.join(read_list)
                await message.answer(f'{read_list}', parse_mode='markdown')

    class Delete:
        class DeleteStates(StatesGroup):
            ITEM_SELECT = State()
            ITEM_DELETE = State()

        @staticmethod
        @dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
        async def delete_callback_execute(callback_query: types.CallbackQuery):
            if await Database().sql_check_user_id(callback_query.from_user.id) == False:
                await bot.send_message(callback_query.from_user.id, 'Необходимо зарегистрироваться!❌', reply_markup=kb_authorization)
                return
            callback_query.data = callback_query.data.replace('del ', '')
            await Database().ShoppingList().sql_delete(callback_query)
            await callback_query.answer(text=f'Запись "{callback_query.data}" успешно удалена')
            await callback_query.message.delete()
            for userid in await Database().Notifications().get_all_user_id_in_family_message(callback_query):
                if str(callback_query.from_user.id) != str(userid[0]):
                    await bot.send_message(userid[0], f'Запись "{callback_query.data}" удалена '
                                                      f'пользователем {callback_query.from_user.first_name}')



        async def delete_select(self, message: types.Message, state: FSMContext):
            if await ShoppingList().Read().read(message, delete=True) == False:
                await state.finish()
                return

        async def delete_execute(self, message: types.Message, state: FSMContext):
            if await Database().ShoppingList().sql_item_check(message):
                await Database().ShoppingList().sql_delete(message)
                await message.answer(f'Запись о "{message.text}" успешно удалена')
            else:
                await message.answer('Такой записи нет в таблице')


        async def delete_all(self, message: types.Message):
            if await Database().sql_check_user_id(message.from_user.id) == False:
                await bot.send_message(message.from_user.id, 'Необходимо зарегистрироваться!❌', reply_markup=kb_authorization)
                return

            await Database().ShoppingList().sql_delete_all(message)
            await message.answer('Все записи о покупках удалены')
            for userid in await Database().Notifications().get_all_user_id_in_family_message(message):
                if str(message.from_user.id) != str(userid[0]):
                    await bot.send_message(userid[0], f'Пользователь "{message.from_user.first_name}" '
                                                      f'удалил все записи о покупках')

    class Edit:
        async def edit(self, message: types.Message):
            pass




def register_handlers_client(dp: Dispatcher):
    # ADD
    dp.register_message_handler(ShoppingList().Add().add_item, text_contains=['Добавить запись➕'])
    dp.register_message_handler(ShoppingList().Add().add_amount, state=ShoppingList().Add().AddNoteStates.ADD_AMOUNT)
    dp.register_message_handler(ShoppingList().Add().add_total, state=ShoppingList().Add().AddNoteStates.ADD_TOTAL)
    # /ADD

    # READ
    dp.register_message_handler(ShoppingList().Read().read, text_contains=['Посмотреть записи👀'])
    # /READ

    # DELETE
    dp.register_message_handler(ShoppingList().Delete().delete_select, text_contains=['Удалить запись➖'])
    dp.register_message_handler(ShoppingList().Delete().delete_all, text_contains=['Удалить все записи✖'])
    dp.register_message_handler(ShoppingList().Delete().delete_execute, state=ShoppingList().Delete().DeleteStates.
                                ITEM_DELETE)
    #dp.callback_query_handler(ShoppingList().Delete().delete_calback_execute, func=lambda c: c.data == 'delete')
    # /DELETE
