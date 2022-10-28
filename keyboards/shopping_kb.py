from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


b1 = KeyboardButton('/Добавить запись     ➕')
b2 = KeyboardButton('/Посмотреть записи   👀')
b4 = KeyboardButton('/Удалить запись        ➖')
b5 = KeyboardButton('/Удалить все записи  ✖')
b6 = KeyboardButton('/Выйти из аккаунта🚪')


kb_shopping = ReplyKeyboardMarkup(resize_keyboard=True)

kb_shopping.row(b1,b2).row(b4,b5).add(b6)