from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp, bot


@dp.message_handler(Command('info'))
async def get_bot_info(mes: types.Message):
    botname = mes.via_bot
    botdesc = mes.chat.description
    bottitle = (await bot.get_chat(chat_id=1350497656))
    bot_name = (await bot.get_me()).first_name
    await mes.answer(f"Этого бота звать {botname}\n"
                     f"{bot_name}\n"
                     f"{bottitle}\n"
                     f"{botname}")