from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.adjust(2)

    builder.add(InlineKeyboardButton(text="Добавить аккаунт", callback_data="admin_add_account"))

    return builder.as_markup()


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Отменить", callback_data="admin_cancel"))

    return builder.as_markup()

