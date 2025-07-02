from typing import Union

from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from services.db import set_channel_enabled, get_active_channels, get_connection
from states.add_channel import AddChannel


from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

router = Router()



@router.callback_query(F.func(lambda c: c.data == 'list_channels'))
@router.message(Command(commands=["list_channels"]))
async def list_channels(event: Union[types.Message, types.CallbackQuery]):
    channels = get_active_channels()
    print(channels)
    if not channels:
        text = "Каналы не найдены"
        if isinstance(event, types.Message):
            await event.answer(text)
        elif isinstance(event, types.CallbackQuery):
            await event.message.answer(text)
            await event.answer()
        return

    for channel in channels:
        status = "✅ Включена" if channel["forwarding_enabled"] == 1 else "🚫 Выключена"
        text = f"<b>{channel['title']}</b>\nПересылка: {status}"
        btn_text = "Отключить" if channel["forwarding_enabled"] == 1 else "Включить"
        btn_action = "disable" if channel["forwarding_enabled"] == 1 else "enable"

        keyboard_channels = InlineKeyboardBuilder()
        keyboard_channels.add(InlineKeyboardButton(text=btn_text, callback_data=f"{btn_action}:{channel['chat_id']}"))

        if isinstance(event, types.Message):
            await event.answer(text, reply_markup=keyboard_channels.as_markup(), parse_mode="HTML")
        else:
            await event.message.answer(text, reply_markup=keyboard_channels.as_markup(), parse_mode="HTML")

        if isinstance(event, types.CallbackQuery):
            await event.answer()


@router.callback_query(F.data.startswith("enable:") | F.data.startswith("disable:"))
async def toggle_channel_status(callback: types.CallbackQuery):
    action, channel_id_str = callback.data.split(":")
    channel_id = int(channel_id_str)

    # Здесь должна быть логика обновления статуса в БД
    if action == "enable":
        set_channel_enabled(channel_id, 1)
        await callback.answer("Пересылка включена ✅")


    else:
        set_channel_enabled(channel_id, 0)
        await callback.answer("Пересылка выключена 🚫")
