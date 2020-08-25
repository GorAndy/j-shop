import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ContentType, ContentTypes
from keyboards.default.admin_keyboard import keyboard_template, inline_add_to_db

from loader import dp, bot
from data.config import admins
from states.add_item import AddItem


@dp.message_handler(Command('admin'), user_id=admins)
async def admin_page(message: Message):
    buttons = ["Товары", "Покупатели"]
    await message.answer("выберите объект администрирования", reply_markup=keyboard_template(buttons=buttons))


@dp.message_handler(text="Товары", user_id=admins)
async def admin_item_choice(message: Message):
    buttons = ["Добавить товар", "Список товаров", "Редактировать товар"]
    await message.answer("Выберите:", reply_markup=keyboard_template(buttons=buttons))


@dp.message_handler(text="Добавить товар", user_id=admins)
async def add_item(message: Message):
    await message.answer("Введите\n"
                         "Наименование товара:")
    await AddItem.item_name.set()


@dp.message_handler(state=AddItem.item_name, user_id=admins)
async def add_name_item(message: Message, state: FSMContext):
    item_name = message.text
    await state.update_data({"item_name": item_name})

    await message.answer("Добавьте\n"
                         "Описание товара:")
    await AddItem.item_description.set()


@dp.message_handler(state=AddItem.item_description, user_id=admins)
async def add_description_item(message: Message, state: FSMContext):
    item_description = message.text
    await state.update_data({"item_description": item_description})

    await message.answer("Укажите\n"
                         "Цену товара (рубли.копейки): ")
    await AddItem.item_price.set()


@dp.message_handler(state=AddItem.item_price, user_id=admins)
async def add_price_item(message: Message, state: FSMContext):
    item_price = float(message.text)
    await state.update_data({"item_price": item_price})

    await message.answer("Отправьте\n"
                         "фотографию с изображением товара:")

    await AddItem.item_photo.set()


@dp.message_handler(content_types=ContentTypes.PHOTO | ContentTypes.DOCUMENT, state=AddItem.item_photo, user_id=admins)
async def add_photo_item(message: Message, state: FSMContext):
    item_photo = message.photo[-1].file_id
    await state.update_data({"item_photo": item_photo})
    data = await state.get_data()
    item_name = data.get("item_name")
    item_description = data.get("item_description")
    item_price = data.get("item_price")
    item_photo = data.get("item_photo")
    caption = f"""
            Наименование товара:     <b>{item_name}</b>
            Описание:                <i>{item_description}</i>
            Цена товара:             <b>{item_price} руб </b>"""
    await state.finish()
    await bot.send_photo(message.chat.id, photo=item_photo, caption=caption, reply_markup=inline_add_to_db())
    return data



