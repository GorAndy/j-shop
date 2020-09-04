from aiogram import executor

from data.config import admins
from loader import bot
from utils.db_api.database import create_db


async def on_shutdown(dp):

    await bot.send_message(admins, "Бот остановлен")
    await bot.close()


async def on_startup(dp):
    await create_db()
    await bot.send_message(admins, "Бот запущен")

# async def on_shutdown(dp):
#     for admin in admins:
#         await bot.send_message(admin, "Бот остановлен")
#     await bot.close()
#
#
# async def on_startup(dp):
#     for admin in admins:
#         await bot.send_message(admin, "Бот запущен")


if __name__ == '__main__':
    from handlers.users.admin_panel import dp
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

# async def on_startup(dp):
#     import filters
#     import middlewares
#     filters.setup(dp)
#     middlewares.setup(dp)
#
#     from utils.notify_admins import on_startup_notify
#     await on_startup_notify(dp)
#
#
# if __name__ == '__main__':
#     from aiogram import executor
#     from handlers import dp
#
#     executor.start_polling(dp, on_startup=on_startup)
