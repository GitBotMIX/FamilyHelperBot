from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/Вход')
b2 = KeyboardButton('/Регистрация')


kb_authorization = ReplyKeyboardMarkup(resize_keyboard=True)

kb_authorization.add(b1).add(b2)