import asyncio
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import (Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup,
                           InlineKeyboardButton)
from aiogram.utils.callback_data import CallbackData

from utils.db_api.database import DBCommands, Purchase, User, Item
from states import states
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
    if str(chat_id) in admins:
        text += _("/n"
                  "Добавить новый товар: /add_item")
    await bot.send_message(chat_id, text, reply_markup=language_markup)


@dp.callback_query_handler(text_contains="lang")
async def change_language(call: CallbackQuery):
    await call.message.edit_reply_markup()
    lang = call.data[-2:]
    await db.set_language(lang)

    await call.message.answer(_("Ваш язык был изменен", locale=lang))


@dp.message_handler(commands=["referrals"])
async def check_referrals(message: Message):
    referrals = await db.check_referrals()
    text = _("Ваши рефералы: \n{referrals}").format(referrals=referrals)
    await message.answer(text)


@dp.message_handler(commands=["items"])
async def show_items(message: Message):
    all_items = await db.show_items()
    for num, item in enumerate(all_items):
        text = _("<b>Товар</b> \t№{id}: <u>{name}</u>\n"
                 "<b>Цена:</b> \t{price:,}\n")
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=_("Купить"), callback_data=buy_item.new(item_id=item.id))
                ],
            ]
        )
        await message.answer_photo(
            photo=item.photo,
            caption=text.format(
                id=item.id,
                name=item.name,
                price=item.price / 100
            ), reply_markup=markup
        )
        await asyncio.sleep(0.3)


@dp.callback_query_handler(buy_item.filter())
async def buying_item(call: CallbackQuery, callback_data: dict, state: FSMContext):
    item_id = int(callback_data.get("item_id"))
    await call.message.edit_reply_markup()
    item = await Item.get(item_id)
    if not item:
        await call.message.answer(_("Такого товара не существует"))
        return
    text = _("Вы хотите купить товар \"<b>{name}</b>\" по цене: <i>{price:,}/шт.</i>\n"
             "Введите количество или нажмите отмену").format(name=item.name, price=item.price / 100)
    await call.message.answer(text)
    await states.Purchase.EnterQuantity.set()

    await state.update_data(
        item=item,
        purchase=Purchase(
            item_id=item.id,
            purchase_time=datetime.datetime.now(),
            buyer=call.from_user.id
        )
    )


@dp.message_handler(regexp=r"^(\d+)$", state=states.Purchase.EnterQuantity)
async def enter_quantity(message: Message, state: FSMContext):
    quantity = int(message.text)
    async with state.proxy() as data:
        data["purchase"].quantity = quantity
        item = data["item"]
        amount = item.price * quantity
        data["purchase"].amount = amount

        agree_button = InlineKeyboardButton(
            text=_("Согласен"),
            callback_data="agree"
        )
        change_button = InlineKeyboardButton(
            text=_("Ввести количество заново"),
            callback_data="change"
        )
        cancel_button = InlineKeyboardButton(
            text=_("Отменить покупку"),
            callback_data="cancel"
        )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [agree_button],
            [change_button],
            [cancel_button]
        ]
    )
    await message.answer(
        _("Хорошо, вы хотите купить <i>{quantity}</i> {name} по цене <b>{price:,}/шт.</b>\n\n"
          "Получится <b>{amount:,}</b>. Подтверждаете?").format(
            quantity=quantity,
            name=item.name,
            price=item.price / 100,
            amount=amount / 100,
        ), reply_markup=markup
    )
    await states.Purchase.Approval.set()


@dp.message_handler(state=states.Purchase.EnterQuantity)
async def not_quantity(message: Message):
    await message.answer(_("Неверное значение введите число"))


@dp.callback_query_handler(text_contains="cancel", state=states.Purchase)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer(_("Вы отменили покупку"))
    await state.reset_state()


@dp.callback_query_handler(text_contains="change", state=states.Purchase.Approval)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer(_("Введите количество товара заново"))
    await states.Purchase.EnterQuantity.set()


@dp.callback_query_handler(text_contains="agree", state=states.Purchase.Approval)
async def approval(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    purchase: Purchase = data.get("purchase")
    item: Item = data.get("item")
    await purchase.create()
    await bot.send_message(chat_id=call.from_user.id,
                           text=_("Хорошо. Оплатите <b>{amount:,}</b>по методу указанному ниже и нажмите"
                                  "на кнопку ниже").format(amount=purchase.amount))

    currency = "RUB"
    need_name = True
    need_phone_number = False
    need_email = False
    need_shipping_address = True

    await bot.send_invoice(chat_id=call.from_user.id,
                           title=item.name,
                           description=item.name,
                           payload=str(purchase.id),
                           start_parameter=str(purchase.id),
                           currency=currency,
                           prices=[
                               LabeledPrice(label=item.name, amount=purchase.amount)
                           ],
                           provider_token=LIQPAY_TOKEN,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )
    await state.update_data(purchase=purchase)
    await states.Purchase.Payment.set()


@dp.pre_checkout_query_handler(state=states.Purchase.Payment)
async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)
    data = await state.get_data()
    purchase: Purchase = data.get("purchase")
    success = await check_payment(purchase)

    if success:
        await purchase.update(
            successful=True,
            shiping_address=query.order_info.shipping_address.to_python()
            if query.order_info.shipping_address else None,
            phone_number=query.order_info.phone_number,
            receiver=query.order_info.name,
            email=query.order_info.email
        ).apply()
        await state.reset_state()
        await bot.send_message(query.from_user.id, _("Спасибо за покупку"))
    else:
        await bot.send_message(query.from_user.id, _("Покупка не была подтвержденаб попробуйте позже..."))


async def check_payment(purchase: Purchase):
    pass
