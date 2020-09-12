import os
import calendar

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import CommandStart
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton,\
    Message

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
admins = [admin.strip() for admin in os.getenv("ADMINS_ID").split(',')]

bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


async def on_startup(dp):
    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)

# Отсюда начнем экспериментировать
@dp.message_handler(CommandStart())
async def start(message: Message):
    await message.answer(text="Привет")

# Где-то здесь закончим ))


if __name__ == '__main__':
    executor.start_polling(dp)
