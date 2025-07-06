from typing import Union

from aiogram.filters import Command
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from services.db import set_channel_enabled, get_active_channels, get_connection
from states.add_channel import AddChannel
from services.logging_config import logger
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from config import api_id, api_hash, phone, target_forum_id
from telethon.tl.functions.channels import JoinChannelRequest
from loader import bot


ITEMS_PER_PAGE = 5

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

router = Router()



@router.message(Command(commands=["update_channels"]))
async def update_channels(event: types.Message):
    await bot.send_message(6968880389, text='/update_channels')








@router.callback_query(F.data.startswith("list_channels"))
@router.message(Command(commands=["list_channels"]))
async def list_channels(event: Union[types.Message, types.CallbackQuery]):
    if isinstance(event, types.CallbackQuery):
        try:
            page = int(event.data.split(":")[1])
        except (IndexError, ValueError):
            page = 0
    else:
        page = 0


    channels = get_active_channels()
    total = len(channels)
    print(total)

    if total == 0:
        text = "Каналы не найдены"
        await (event.message if isinstance(event, types.CallbackQuery) else event).answer(text)
        if isinstance(event, types.CallbackQuery):
            await event.answer()
        return

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    current_channels = channels[start:end]

    text_lines = []
    keyboard = InlineKeyboardBuilder()

    for channel in current_channels:
        status = f"✅ Включена" if channel["forwarding_enabled"] == 1 else "🚫 Выключена"
        text_lines.append(f"<b>{channel['title']}</b>\nПересылка: {status}\n")

        btn_text = f"Отключить в {channel['title']}" if channel["forwarding_enabled"] == 1 else f"Включить в {channel['title']}"
        btn_action = "disable" if channel["forwarding_enabled"] == 1 else "enable"

        keyboard.row(InlineKeyboardButton(
            text=btn_text,
            callback_data=f"{btn_action}:{channel['chat_id']}"
        ))

    # Навигация по страницам
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"list_channels:{page - 1}"))
    if end < total:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"list_channels:{page + 1}"))
    if nav_buttons:
        keyboard.row(*nav_buttons)

    text = "\n".join(text_lines)

    respond = event.message if isinstance(event, types.CallbackQuery) else event
    await respond.answer(text, reply_markup=keyboard.as_markup(), parse_mode="HTML")

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


@router.message(lambda F: F.text.startswith('@') or 't.me/' in F.text)
async def add_channel(message: types.Message):
    text = message.text.strip()
    if text.startswith('https://t.me/'):
        username = text.split('/')[-1]
    elif text.startswith('@'):
        username = text[1:]
    else:
        await message.answer("❗ Не удалось распознать ссылку.")
        return

    await bot.send_message(6968880389, text=username)







