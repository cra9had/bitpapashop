from typing import List

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"
django.setup()
from main.models import TelegramAccount, Order, TelegramUser, Catalog, Product, Transaction


async def create_telegram_account(telethon_session: str, json_session: str) -> None:
    TelegramAccount(session=telethon_session, json=json_session).save()


async def create_user(telegram_id: int, username: str) -> None:
    TelegramUser.objects.get_or_create(telegram_id=telegram_id, telegram_username=username)


async def get_all_user_orders(telegram_id: int) -> Order:
    return Order.objects.filter(order_status="success", buyer__telegram_id=telegram_id)


async def get_categories() -> List[Catalog]:
    return Catalog.objects.all()


async def get_products(catalog_pk: int) -> List[Product]:
    return Product.objects.filter(catalog=catalog_pk)


async def get_product(pk: int) -> Product:
    return Product.objects.get(pk=pk)


async def create_transaction(pk: int) -> Transaction:
    return Transaction.objects.filter()
