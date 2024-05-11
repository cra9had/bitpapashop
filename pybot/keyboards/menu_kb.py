import math

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from main.models import Product
from pybot.utils import db

PRODUCTS_PER_PAGE = 5


def menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="Каталог товаров")
    )
    builder.row(
        KeyboardButton(text="Поддержка"), KeyboardButton(text="Личный кабинет")
    )
    return builder.as_markup(resize_keyboard=True)


async def catalog() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for button in await db.get_categories():
        builder.add(InlineKeyboardButton(text=button.name, callback_data=f"catalog/{button.pk}"))

    builder.adjust(2)
    return builder.as_markup()


async def get_products(catalog_pk: int, page: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    products = await db.get_products(catalog_pk)

    for button in (await db.get_products(catalog_pk))[(page - 1) * PRODUCTS_PER_PAGE: page * PRODUCTS_PER_PAGE]:
        if button.in_stock() > 0:
            builder.row(
            InlineKeyboardButton(text=f"{button.name} | {button.price_rub}р | {button.in_stock()}шт.", callback_data=f"product/{button.pk}"))

    if len(products) > PRODUCTS_PER_PAGE:
        builder.row(
            InlineKeyboardButton(text="<", callback_data=f"products/left/{products[0].pk}"),
            InlineKeyboardButton(text=f"{page}/{math.ceil(len(products) / PRODUCTS_PER_PAGE)}",
                                 callback_data="empty"),
            InlineKeyboardButton(text=">", callback_data=f"products/right/{products[0].pk}"),
        )

    builder.row(InlineKeyboardButton(text="В каталог", callback_data="back_to_calatog"))

    return builder.as_markup()


def product_buy_button(product: Product) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="К оплате", callback_data=f"payform/{product.pk}"),
                InlineKeyboardButton(text="Назад", callback_data=f"back_to_products"))

    return builder.as_markup()
