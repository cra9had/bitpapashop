from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from pybot.states import AdminStateGroup
from aiogram.filters import Command
from pybot.keyboards import admin_kb
from pybot.filters import IsAdmin
import pathlib

from pybot.utils import db
from pybot.utils.services import download_file

router = Router()


@router.message(Command("admin"), IsAdmin())
async def admin_menu(message: Message, state: FSMContext):
    await state.clear()
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
async def telethon_session_sent(message: Message, state: FSMContext):
    if pathlib.Path(message.document.file_name).suffix != ".session":
        await message.answer("Формат должен быть Telethon .session")

    path = await download_file(message)
    await state.update_data({
        "telethon_session": path,
    })
    await state.set_state(AdminStateGroup.sending_json_session)
    await message.answer("Пришлите сессию в формате .json", reply_markup=admin_kb.admin_cancel_keyboard())


@router.message(AdminStateGroup.sending_json_session, F.document)
async def session_json_sent(message: Message, state: FSMContext):
    if pathlib.Path(message.document.file_name).suffix != ".json":
        await message.answer("Формат файла должен быть .json")

    json_path = await download_file(message)
    await db.create_telegram_account(
        (await state.get_data()).get("telethon_session"),
        json_path
    )
    await message.answer("Аккаунт добавлен!")
    await admin_menu(message, state)
