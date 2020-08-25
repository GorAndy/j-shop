from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def keyboard_template(buttons: list):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for but in buttons:
        markup.insert(KeyboardButton(but))
    return markup


def inline_add_to_db():
    markup = InlineKeyboardMarkup()
    one_but = InlineKeyboardButton("Да", callback_data="yes")
    two_but = InlineKeyboardButton("Нет", callback_data="no")
    markup.add(one_but, two_but)
    return markup
