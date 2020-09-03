import asyncio
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup,
                           InlineKeyboardButton)
from aiogram.utils.callback_data import CallbackData

from utils.db_api.database import DBCommands, Purchase
import states.states
from data.config import LIQPAY_TOKEN, admins
from loader import dp, bot, _

db = DBCommands()

buy_item = CallbackData("buy", "item_id")


@dp.message_handler(CommandStart())
async def register_user(message: Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    user = await db.add_new_user(referral=referral)
    id = user.id
    count_users = await db.count_users()

    language_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Русский", callback_data='lang_ru')],
            [InlineKeyboardButton(text="Украиньска", callback_data='lang_uk')],
            [InlineKeyboardButton(text="English", callback_data='lang_en')]
        ]
    )
    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?satrt={id}"

    text = _(
        "Приветствую вас!!\n"
        "Сейчас в базе {count_users} человек!\n"
        "/n"
        "Ваша реферальная ссылка {bot_link}\n"
        "Проверить рефералов можно командой /referrals\n"
        "Посмотреть товары: /items").format(count_users=count_users,
                                            bot_link=bot_link
                                            )
    if message.from_user.id in admins:
        text += _("/n"
                  "Добавить новый товар: /add_item")
    await bot.send_message(chat_id, text, reply_markup=language_markup)


@dp.callback_query_handler(text_contains="lang")
async def change_language(call: CallbackQuery):
    await call.message.edit_reply_markup()
    lang = call.data[-2:]
    await db.set_language(lang)

    await call.message.answer(_("Ваш язык был изменен", locale=lang))





