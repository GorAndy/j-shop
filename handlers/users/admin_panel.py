from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from data.config import admins
from loader import dp, _, bot
from states.states import NewItem, Mailing
from utils.db_api.database import Item, User


@dp.message_handler(user_id = admins, commands=['add_item'])
async def add_item(message: Message):
    await message.answer(_("Введите название товара или нажмите  /cancel"))
    await NewItem.Name.set()


@dp.message_handler(user_id=admins, state=NewItem.Name)
async def enter_name(message: Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name
