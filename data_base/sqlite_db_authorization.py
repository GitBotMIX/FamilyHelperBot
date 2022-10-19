import sqlite3 as sq
from create_bot import bot
from keyboards.authorization_kb import kb_authorization



class DatabaseAuthorization:
    async def get_family_name(self, user_id):
        try:
            family_name = self.cur.execute(f'SELECT family_name FROM authorization WHERE user_id == ?',
                        (str(user_id),)).fetchone()[0]
            return family_name
        except TypeError:
            #await bot.send_message(user_id, 'Необходимо войти в аккаунт!', reply_markup=kb_authorization)
            #raise TypeError
            pass





    async def true_or_false_check(self, data):
        if data == None:
            return False
        return True
    async def existance_check_user_id(self, data):
        check = self.cur.execute('SELECT user_id FROM authorization WHERE user_id == ?',
                                 (str(data),)).fetchone()
        return await self.true_or_false_check(check)
    async def existence_check_password(self, tuple_data):
        check = self.cur.execute('SELECT user_id FROM authorization WHERE family_name == ? AND password == ?',
                                 (str(tuple_data[0]), str(tuple_data[1]),)).fetchone()
        return await self.true_or_false_check(check)


    async def existence_check_login(self, data):
        check = self.cur.execute('SELECT user_id FROM authorization WHERE family_name == ?',
                                 (str(data),)).fetchone()
        return await self.true_or_false_check(check)


    async def sign_in_user_exist(self, tuple_data):
        check = self.cur.execute('SELECT user_id FROM authorization WHERE family_name == ? AND password == ?', (tuple_data[0], tuple_data[1],)).fetchone()
        return await self.true_or_false_check(check)


    async def execute_sign_in(self):
        pass


    async def execute_registration(self, tupleData):
        self.cur.execute(f'INSERT INTO authorization VALUES (?, ?, ?)', tupleData)
        self.base.commit()

    def __init__(self, cur, base):
        self.cur, self.base = cur, base

