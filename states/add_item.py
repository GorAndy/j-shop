from aiogram.dispatcher.filters.state import StatesGroup, State


class AddItem(StatesGroup):
    item_name = State()
    item_description = State()
    item_price = State()
    item_photo = State()
