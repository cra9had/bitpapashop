from aiogram.types import Message
from django.conf import settings
import os


def _get_file_dest(file_name: str) -> str:
    return os.path.join(settings.MEDIA_DIR, file_name)


async def download_file(message: Message) -> str:
    path = _get_file_dest(message.document.file_name)
    await message.bot.download(message.document, path)
    return path
