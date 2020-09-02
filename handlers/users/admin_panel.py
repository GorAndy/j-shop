from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.parts import paginate

from data.config import admins
from loader import dp, _, bot
from states.states import NewItem, Mailing
from utils.db_api.database import Item, User


@dp.message_handler(user_id=admins, commands=['cancel'], state=NewItem)
async def cancel(message: Message, state: FSMContext):
    await message.answer(_("Вы отменили создание товара"))
    await state.reset_state()


@dp.message_handler(user_id=admins, commands=['add_item'])
async def add_item(message: Message):
    await message.answer(_("Введите название товара или нажмите  /cancel"))
    await NewItem.Name.set()


@dp.message_handler(user_id=admins, state=NewItem.Name)
async def enter_name(message: Message, state: FSMContext):
    name = message.text
    item = Item()
    item.name = name
    await message.answer(_("Название: {name}\n"
                           "Пришлите фотографию товара или нажмите /cancel").format(name=name))
    await state.update_data(item=item)
    await NewItem.Photo.set()


@dp.message_handler(user_id=admins, state=NewItem.Photo, content_types=types.ContentType.PHOTO)
async def add_photo(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    item: Item = data.get("item")
    print("Переменная data", data)
    print("Переменная item", item)
    item.photo = photo

    await message.answer_photo(photo=photo, caption=_("Название: {name}\n"
                                                      "Пришлите мне цену товара в копейках или /cancel"))
    await NewItem.Price.set()


@dp.message_handler(user_id=admins, state=NewItem.Price)
async def add_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer(_("Неверное значение, введите число"))
        return

    data = await state.get_data()
    item: Item = data.get("item")
    item.price = price
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Yes", callback_data="confirm")],
            [InlineKeyboardButton(text=_("Ввести заново"), callback_data="change")]
        ]
    )
    await message.answer(_("Цена: {price:,} \n"
                           "Подтверждаете? Нажмите /cancel чтобы отменить").format(price=price/100),
                         reply_markup=markup)
    await state.update_data(item=item)
    await NewItem.Confirm.set()


@dp.callback_query_handler(user_id=admins, text_contains="change", state=NewItem.Confirm)
async def enter_price(call: CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer(_("Введите заново цену товара в копейках"))
    await NewItem.Price.set()


@dp.callback_query_handler(user_id=admins, text_contains="confirm", state=NewItem.Confirm)
async def enter_price(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    item: Item = data.get("item")
    await item.create()
    await call.message.answer(_("Товар успешно добавлен"))
    await state.reset_state()


# Рассылка по пользователям
@dp.message_handler(user_id=admins, commands=["tell_everyone"])
async def mailing(message: Message):
    await message.answer(_("Пришлите текст рассылки"))
    await Mailing.Text.set()


@dp.message_handler(user_id=admins, state=Mailing.Text)
async def mailing(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Русский", callback_data="ru")],
            [InlineKeyboardButton(text="Украинский", callback_data="uk")],
            [InlineKeyboardButton(text="English", callback_data="en")]
        ]
    )
    await message.answer(_("Пользователям на каком языке разослать это сообщение?\n\n"
                           "Текст: {}\n"
                           "{text}").format(text=text),
                         reply_markup=markup)
    await Mailing.Language.set()


@dp.callback_query_handler(user_id=admins, state=Mailing.Language)
async def mailing_start(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    await state.reset_state()
    await call.message.edit_reply_markup()

    users = await User.query.where(User.language == call.data).gino.all()
    for user in users:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            await sleep(0.3)
        except Exception:
            pass
    await call.message.answer(_("Рассылка выполнена"))






