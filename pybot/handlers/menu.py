import math
import time

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from django.db.models import Sum

from main.services import rub_to_btc
from pybot.states import MainStatesGroup
from pybot.utils import db

from aiogram import Router, F
from aiogram.filters import CommandStart
from pybot.keyboards import menu_kb

router = Router()


@router.message(CommandStart())
async def start_menu(message: Message):
    await db.create_user(message.chat.id, message.chat.username)
    await message.answer("Добро пожаловать в магазин. Меню:", reply_markup=menu_kb.menu())


@router.message(F.text == "Личный кабинет")
async def board(message: Message):
    orders = await db.get_all_user_orders(message.chat.id)
    await message.answer(f"Ваш ID: {message.chat.id}\nВсего покупок: {orders.count()}\nПотрачено: "
                         f"{orders.aggregate(Sum('transaction__amount_rub')).get('transaction__amount_rub__sum') or 0} руб.")


@router.message(F.text == "Каталог товаров")
async def get_categories(message: Message):
    await message.answer("Выберите категорию:", reply_markup=await menu_kb.catalog())


@router.callback_query(F.data.startswith("catalog/"))
async def on_catalog_selected(call: CallbackQuery, state: FSMContext):
    catalog_pk = int(call.data.replace("catalog/", ""))
    await state.set_data({
        "index": 1,
        "catalog": catalog_pk
    })
    await get_products(call, state)


async def get_products(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(f"Список доступных товаров\n➖➖➖➖➖➖➖➖➖➖➖➖",
                              reply_markup=await menu_kb.get_products((await state.get_data()).get("catalog"),
                                                                      (await state.get_data()).get("index")))


@router.callback_query(F.data.startswith("products/right/"))
async def products_right(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    products = await db.get_products(data.get("catalog"))
    pages = math.ceil(len(products) / menu_kb.PRODUCTS_PER_PAGE)
    await state.update_data({
        "index": data.get("index") + 1 if data.get("index") < pages else 1
    })
    await get_products(call, state)


@router.callback_query(F.data.startswith("products/left/"))
async def products_left(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    products = await db.get_products(data.get("catalog"))
    pages = math.ceil(len(products) / menu_kb.PRODUCTS_PER_PAGE)
    await state.update_data({
        "index": data.get("index") - 1 if data.get("index") > 1 else pages
    })
    await get_products(call, state)


@router.callback_query(F.data == "back_to_calatog")
async def back_to_catalog(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await get_categories(call.message)


@router.callback_query(F.data.startswith("product/"))
async def product_page(call: CallbackQuery, state: FSMContext):
    product_pk = int(call.data.replace("product/", ""))
    await call.message.delete()
    product = await db.get_product(product_pk)
    await call.message.answer(f"Вы выбрали: {product.name}\nСтоимость: {product.price_rub} руб.",
                              reply_markup=menu_kb.product_buy_button(product))


@router.callback_query(F.data == "back_to_products")
async def back_to_products(call: CallbackQuery, state: FSMContext):
    await get_products(call, state)


@router.callback_query(F.data.startswith("payform/"))
async def payform(call: CallbackQuery, state: FSMContext):
    product_pk = int(call.data.replace("payform/", ""))
    await call.message.delete()
    product = await db.get_product(product_pk)
    amount_btc = rub_to_btc(product.price_rub)
    await state.set_data({
        "amount_btc": amount_btc,
        "amount_rub": product.price_rub,
        "product": product,
        "reserve_time": time.time()
    })
    await call.message.answer(f"""
Создайте одноразовый код через @bitpapa_bot строго на сумму <b>{amount_btc} btc</b> и пришлите его, чтобы оплатить товар.
Курс заморожен на <b>10 минут</b>
""")    # TODO: вынести минуты в админку
    await state.set_state(MainStatesGroup.sending_bitpapa_code)


@router.message(MainStatesGroup.sending_bitpapa_code)
async def on_bitpapa_code(message: Message, state: FSMContext):
    data = await state.get_data()
    if time.time() - data["reserve_time"] > 60*10:    # TODO: 10 min
        await message.answer("Курс устарел!")
        return
    if not message.text.startswith("https://t.me/bitpapa_bot?start=papa_code_"):
        await message.answer("Укажите валидный код. Получить его можно здесь: @bitpapabot")
        return

    else:
        trx = await db.create_transaction(message.chat.id, data.get("amount_rub"), data.get("amount_btc"), message.text)
        order = await db.create_order(message.chat.id, data.get("product"), trx)

