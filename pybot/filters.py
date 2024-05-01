from aiogram.filters import BaseFilter
from aiogram.types import Message

admin_ids = [1140197457,]


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admin_ids
