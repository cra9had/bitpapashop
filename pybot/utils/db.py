import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"
django.setup()
from main.models import TelegramAccount


async def create_telegram_account(telethon_session: str, json_session: str):
    TelegramAccount(session=telethon_session, json=json_session).save()
