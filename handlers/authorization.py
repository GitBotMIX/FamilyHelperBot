from aiogram import types, Dispatcher
from keyboards.authorization_kb import kb_authorization
from keyboards.shopping_kb import kb_shopping
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base.sqlite_db import Database


class SignInStates(StatesGroup):
    FAMILY_NAME = State()
    FAMILY_PASSWORD = State()
    FAMILY_FINISH = State()


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == None:
        return
    await state.finish()
    await message.reply('*Действие отменено*', parse_mode='markdown')

class SignIn:
    @staticmethod
    async def family_name(message: types.Message):
        if await authorization_check(message):
            return
        await message.answer('Введи название семьи:')
        await SignInStates.FAMILY_NAME.set()
        await SignInStates.next()

    @staticmethod
    async def family_password(message: types.Message, state: FSMContext):
        #if await Database().sql_check_login(message.text):
        async with state.proxy() as data:
            data['family_name'] = message.text
        await message.answer('Введи пароль:')
        await SignInStates.next()
        #else:
        #    await message.answer('Такого названия семьи нету.')
        #    await state.finish()

    @staticmethod
    async def finish(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['family_password'] = message.text
        if await Database().sql_sign_in(state, message):
            await message.answer('Успешно вошел!', reply_markup=kb_shopping)
        else:
            await message.answer('Введено неверное название семьи или пароль!')
        await state.finish()


class RegistrationStates(StatesGroup):
    FAMILY_NAME = State()
    FAMILY_PASSWORD = State()
    FAMILY_FINISH = State()


class Registration:
    @staticmethod
    async def family_name(message: types.Message):
        if await authorization_check(message):
            return
        await message.answer('Придумай название семьи:')
        await RegistrationStates.FAMILY_NAME.set()
        await RegistrationStates.next()


    @staticmethod
    async def family_password(message: types.Message, state: FSMContext):
        if await Database().sql_check_login(message.text) == False:
            async with state.proxy() as data:
                data['family_name'] = message.text
            await message.answer('Придумай пароль:')
            await RegistrationStates.next()
        else:
            await message.answer('Такое название семьи уже существует.')
            await state.finish()

    @staticmethod
    async def finish(message: types.Message, state: FSMContext):
        if len(message.text) >= 5:
            async with state.proxy() as data:
                data['family_password'] = message.text
            await Database().sql_registration(state, message)
            await message.answer('Регистрация прошла успешно!', reply_markup=kb_shopping)
            await state.finish()
        else:
            await message.answer('Пароль должен содержать минимум 5 символов.\n\nПридумай пароль:')
            await RegistrationStates.FAMILY_PASSWORD.set()
            await RegistrationStates.next()

async def authorization_check(message: types.Message):
    if await Database().sql_check_user_id(str(message.from_user.id)):
        await message.answer('Для начала необходимо выйти из текущего аккаунта.\n'
                             'Что-бы выйти из аккаунта, используй комманду /signout', reply_markup=kb_shopping)
        return True
    return False

class SignUpStates(StatesGroup):
    SIGN_UP_ALERT = State()
    SIGN_UP_FINISH = State()

async def sign_out(message: types.Message):
    await message.answer('При выходе из аккаунта все записи будут удалены!\nДля выхода из аккаунта необходимо '
                         'подтверждение. \n\nНапиши "*ОТМЕНА*" чтобы '
                         'отменить выход из аккаунта.\n\nНапиши "*ПОДТВЕРЖДАЮ*" чтобы выйти из аккаунта.', parse_mode='markdown')
    await SignUpStates.SIGN_UP_ALERT.set()
    await SignUpStates.next()

async def sign_out_finish(message: types.Message, state: FSMContext):
    if message.text == 'ПОДТВЕРЖДАЮ':
        await Database().sql_delete_user(str(message.from_user.id))
        await message.answer('Успешно вышел из аккаунта, все записи удалены', reply_markup=kb_authorization)
    else:
        await message.answer('Выход из аккаунта отменен')
    await state.finish()



async def start(message: types.Message):
    await message.answer('Добро пожаловать в бота FamilyHelper.\n\n'
                         'Здесь можно всей семьей:\n'
                         '  *·Делать записи о покупках.*\n'
                         '  *·Просматривать записи о покупках.*\n'
                         '  *·Редактировать записи о покупках.*\n'
                         '  *·Получать уведомления о добавлении записей.*\n'
                         '  *·Получать уведомления о актуальных записях.*\n\n'
                         'Для того что-бы начать, необходимо зарегестрироваться, после '
                         'регистрации сообщи "*название семьи*" и "*пароль*" людям с которыми хочешь '
                         'разделить пользование этим ботом.\n'
                         'Они смогут присоедениться к тебе нажав на кнопку */вход* и введя '
                         'данные которые *вводил ты* при регистрации.\n'
                         'Так же можешь использовать этого бота только для себя, в таком случае '
                         'не сообщай никому свой логин и пароль от аккаута.\n', reply_markup=kb_authorization,
                         parse_mode='markdown')

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cancel_handler, commands=['отмена'], state='*')

    dp.register_message_handler(SignIn.family_name, commands=['Вход'])
    dp.register_message_handler(SignIn.family_password, state=SignInStates.FAMILY_PASSWORD)
    dp.register_message_handler(SignIn.finish, state=SignInStates.FAMILY_FINISH)

    dp.register_message_handler(Registration.family_name, commands=['Регистрация'])
    dp.register_message_handler(Registration.family_password, state=RegistrationStates.FAMILY_PASSWORD)
    dp.register_message_handler(Registration.finish, state=RegistrationStates.FAMILY_FINISH)

    dp.register_message_handler(sign_out, commands=['Выйти', 'signout'])
    dp.register_message_handler(sign_out_finish, state=SignUpStates.SIGN_UP_FINISH)

    dp.register_message_handler(start, commands=['start'])
