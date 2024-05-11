import asyncio
import json
import time
from typing import Literal

from asgiref.sync import sync_to_async
from loguru import logger
from telethon import TelegramClient

from .models import Order, TelegramAccount


def parse_json_session(json_path: str) -> dict:
    with open(json_path) as f:
        data = json.load(f)
        return data


async def click_button(client: TelegramClient, button_num: int):
    last_message = (await client.get_messages("@bitpapa_bot", 1))[0]
    logger.info(last_message)
    await last_message.click(button_num)
    await asyncio.sleep(1)


async def is_paid(client: TelegramClient, order: Order) -> bool:
    messages = await client.get_messages("@bitpapa_bot", 5)
    amount_matched = False
    code_success = False
    for message in messages:
        if str(order.transaction.amount_btc) in message.message:
            amount_matched = True

        if "✔️" in message.message:
            code_success = True

        if "/start" in message.message:
            continue

        await message.delete()

    if not amount_matched:
        logger.warning(f"Заказ: {order.pk}. Сумма не совпала!")

    elif not code_success:
        logger.warning(f"Заказ: {order.pk}. Код уже активирован!")

    return code_success and amount_matched


@sync_to_async
def change_account_status(account: TelegramAccount, is_free: bool):
    account.is_free = is_free
    account.save()


@sync_to_async
def set_order_status(order: Order, account: TelegramAccount, status: Literal["success", "bad_code"]):
    if status == "success":
        order.transaction.is_confirmed = True
        order.transaction.save()
        logger.warning(f"Заказ {order.pk} выполнен!")
    order.bitpapa_account = account
    order.order_status = status
    order.save()


async def activate_bitpapa_code(account: TelegramAccount, order: Order, code: str):
    await change_account_status(account, False)
    session_json = parse_json_session(account.json.path)
    client = TelegramClient(account.session.path, session_json.get("app_id"), session_json.get("app_hash"),
                            system_version=session_json.get("sdk"), device_model=session_json.get("device"),
                            app_version=session_json.get("app_version"))

    async with client:
        if len(await client.get_messages("@bitpapa_bot")) == 0:
            await client.send_message("@bitpapa_bot", code)
            await asyncio.sleep(1)
            for _ in range(4):
                await click_button(client, 0)
        else:
            await client.send_message("@bitpapa_bot", code)
        await asyncio.sleep(3)
        if await is_paid(client, order):
            await set_order_status(order, account, "success")
        else:
            await set_order_status(order, account, "bad_code")
    await change_account_status(account, True)


def use_bitpapa_code(order: Order):
    if order.transaction.is_confirmed:
        logger.warning("Код bitpapa уже подтверждён!")
        return

    logger.info(order.transaction.bitpapa_code)

    if not order.transaction.bitpapa_code.startswith("https://t.me/bitpapa_bot?start=papa_code_"):
        logger.debug(f"Заказ {order.pk}. Неверный формат кода.")
        return
    else:
        code = f"/start {order.transaction.bitpapa_code.replace('https://t.me/bitpapa_bot?start=', '')}"

    while True:
        account = TelegramAccount.objects.filter(is_banned=False, is_free=True).first()
        if account:
            break

        if not TelegramAccount.objects.filter(is_banned=False).exists():
            ...     # TODO: отправить уведолмние, о нехватки аккаунтов.

        time.sleep(5)

    try:
        asyncio.run(activate_bitpapa_code(account, order, code))
    except Exception as e:
        logger.error(e)
        account.is_banned = True
        account.save()
        use_bitpapa_code(order)
    ...