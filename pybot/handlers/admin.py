from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from pybot.states import AdminStateGroup
from aiogram.filters import Command
from pybot.keyboards import admin_kb
from pybot.filters import IsAdmin

import pathlib


router = Router()


@router.message(Command("admin"), IsAdmin())
async def admin_menu(message: Message):
    await message.answer("Меню администратора", reply_markup=admin_kb.admin_menu())


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel_callback(call: CallbackQuery):
    await call.message.delete()
    await admin_menu(call.message)


@router.callback_query(F.data == "admin_add_account")
async def add_account(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Пришлите сессию в формате .session", reply_markup=admin_kb.admin_cancel_keyboard())
    await state.set_state(AdminStateGroup.sending_telethon_session)


@router.message(AdminStateGroup.sending_telethon_session, F.document)
async def telethon_session_sent(message: Message):
    if pathlib.Path(message.document.file_name).suffix != ".session":
        await message.answer("Формат должен быть Telethon .session")
