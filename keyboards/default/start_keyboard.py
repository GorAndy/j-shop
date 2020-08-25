from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

one_but = KeyboardButton(text="Первая")
sec_but = KeyboardButton("Вторая")

markup.add(one_but, sec_but)