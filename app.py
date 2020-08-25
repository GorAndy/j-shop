from utils.set_bot_commands import set_fefault_commands


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)

    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)
    await set_fefault_commands(dp)


if __name__ == '__main__':
    from aiogram import executor, Dispatcher
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)


# async def on_startup(dp: Dispatcher):
#     setup_logger()
#     setup_filters(dp)
#     logger.info("Установка обработчиков...")
#
#     import handlers
#     setup_middlewares(dp)
#
#     await on_startup_notify(dp)
#     await set_default_commands(dp)
#     logger.info("Бот успешно запущен...")