import sqlite3 as sq
from create_bot import bot
from data_base.sqlite_db_authorization import DatabaseAuthorization


class Database:
    @staticmethod
    def sql_start():
        global base, cur
        base = sq.connect('FamilyDatabase.db')
        cur = base.cursor()
        if base:
            print('Data base connected OK!')
        base.execute('CREATE TABLE IF NOT EXISTS authorization(family_name TEXT, password TEXT, user_id TEXT)')
        base.execute('CREATE TABLE IF NOT EXISTS shopping(item TEXT, amount TEXT, family_name TEXT, user_id TEXT)')
        base.commit()
        return cur, base

    async def get_cursor(self):
        return cur, base

        # AUTHORIZATION
    @staticmethod
    async def get_all_user_id():
        all_user_id = cur.execute('SELECT user_id FROM authorization').fetchall()
        return all_user_id


    async def sql_get_family_name(self, message):
        try:
            user_id = str(message.from_user.id)
            return await DatabaseAuthorization(cur, base).get_family_name(user_id)
        except:
            return await DatabaseAuthorization(cur, base).get_family_name(message[0])

    async def sql_registration(self, state, message):
        async with state.proxy() as data:
            tuple_data = tuple(data.values()) + (str(message.from_user.id),)
            await DatabaseAuthorization(cur, base).execute_registration(tuple_data)

    async def sql_sign_in(self, state, message):
        async with state.proxy() as data:
            tuple_data = tuple(data.values())
            if await DatabaseAuthorization(cur, base).sign_in_user_exist(tuple_data):
                if await DatabaseAuthorization(cur, base).existance_check_user_id(str(message.from_user.id)) == False:
                    await DatabaseAuthorization(cur, base).execute_registration(
                        tuple_data + (str(message.from_user.id),))
                    return True
                else:
                    return True
            else:
                return False

    async def sql_check_login(self, data):
        return await DatabaseAuthorization(cur, base).existence_check_login(data)

    async def sql_check_password(self, data):
        return await DatabaseAuthorization(cur, base).existence_check_password(data)

    async def sql_check_user_id(self, data):
        return await DatabaseAuthorization(cur, base).existance_check_user_id(data)

    async def sql_delete_user(self, user_id):
        cur.execute(f'DELETE FROM authorization WHERE user_id == ?', (user_id,))
        cur.execute(f'DELETE FROM shopping WHERE user_id == ?', (user_id,))
        base.commit()
        # /AUTHORIZATION

    class ShoppingList:
        async def check_value_exist(self, data):
            if data == None:
                return False
            return True

        async def sql_item_check(self, message, family_name=None):
            try:
                item = message.text
            except AttributeError:
                item = message
            if not family_name:
                family_name = await Database().sql_get_family_name(message)
            check = cur.execute(f'SELECT item FROM shopping WHERE item == ? AND family_name == ?',
                                (item, family_name,)).fetchone()
            return check

        async def sql_add_state(self, state, message):
            async with state.proxy() as data:
                family_name = await Database().sql_get_family_name(message)
                tuple_data = tuple(data.values()) + (str(family_name),) + (str(message.from_user.id),)
                cur.execute(f'INSERT INTO shopping VALUES (?, ?, ?, ?)', tuple_data)
                base.commit()
                return True

        async def sql_add(self, *values):
            #tuple_data = tuple(data.values()) + (str(family_name),) + (str(message.from_user.id),)
            cur.execute(f'INSERT INTO shopping VALUES (?, ?, ?, ?)', values)
            base.commit()
            return True

        async def sql_read(self, message):
            family_name = await Database().sql_get_family_name(message)
            readList = []
            product_list = []
            amount_list = []
            for ret in cur.execute(f'SELECT item, amount FROM shopping WHERE family_name == ?',
                                   (family_name,)).fetchall():
                readList.append(f'\nКупить: `{ret[0]}`\nКоличество: {ret[1]}')
                product_list.append(ret[0])
                amount_list.append(ret[1])
            if readList == []:
                return False
            return readList, product_list, amount_list

        async def sql_delete(self, message):
            family_name = await Database().sql_get_family_name(message)
            try:
                cur.execute(f'DELETE FROM shopping WHERE item == ? AND family_name == ?', (message.text, family_name,))
            except AttributeError:
                cur.execute(f'DELETE FROM shopping WHERE item == ? AND family_name == ?', (message.data, family_name,))
            base.commit()

        async def sql_delete_all(self, message):
            family_name = await Database().sql_get_family_name(message)
            cur.execute(f'DELETE FROM shopping WHERE family_name == ?', (family_name,))
            base.commit()

        @staticmethod
        async def update_amount(item, amount, message, family_name=None):
            if not family_name:
                family_name = await Database().sql_get_family_name(message)
            cur.execute(f'UPDATE shopping SET amount == ? WHERE family_name == ? AND item == ?', (amount, family_name, item))
            base.commit()
    class Notifications:
        async def get_all_family_name(self):
            return cur.execute(f'SELECT family_name FROM authorization').fetchall()

        async def get_all_user_id_in_family_message(self, message):
            family_name = await Database().sql_get_family_name(message)
            all_user_id = cur.execute(f'SELECT user_id FROM authorization WHERE family_name == ?',
                                      (str(family_name),)).fetchall()
            return all_user_id

        async def get_all_user_id_in_family_name(self, family_name):
            all_user_id = cur.execute(f'SELECT user_id FROM authorization WHERE family_name == ?',
                                      (str(family_name),)).fetchall()
            return all_user_id
