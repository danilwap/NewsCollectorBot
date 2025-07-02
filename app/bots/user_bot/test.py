from config import api_id, api_hash, phone

from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.functions.channels import GetFullChannelRequest, GetForumTopicsRequest
from telethon.errors.rpcerrorlist import ChannelPrivateError, ChannelInvalidError, MessageIdInvalidError
import asyncio
from logging_config import logger
from services.db import get_active_channels

from telethon.tl.types import Channel, Chat, User

# === Инициализация клиента ===
client = TelegramClient(phone, api_id, api_hash)


async def get_or_create_topic_id(title):
    pass

async def forward_to_forum(message, title):
    print(message, title)


async def list_user_chats(client: TelegramClient, show_users=False):
    dialogs = await client.get_dialogs()

    result = []

    for dialog in dialogs:
        entity = dialog.entity

        if isinstance(entity, Channel):
            if entity.megagroup:
                chat_type = "Супергруппа"
            elif entity.broadcast:
                chat_type = "Канал"
            else:
                chat_type = "Канал/Группа"
        elif isinstance(entity, Chat):
            chat_type = "Группа"
        elif isinstance(entity, User):
            if not show_users:
                continue
            chat_type = "Пользователь"
        else:
            chat_type = "Другое"
        print(entity)
        result.append({
            "id": entity.id,
            "title": getattr(entity, 'title', None) or getattr(entity, 'first_name', ''),
            "username": getattr(entity, 'username', None),
            "type": chat_type
        })

    return result


async def get_all_topic(client: TelegramClient):
    input_channel = await client.get_input_entity(-1002899127100)

    result = await client(GetForumTopicsRequest(
        channel=input_channel,
        offset_date=None,
        offset_id=0,
        offset_topic=0,
        limit=100
    ))

    for topic in result.topics:
        (f"🟢 Тема: {topic.title} | ID: {topic.id}")









# === Обработка сообщений ===  в работе
@client.on(events.NewMessage())
async def watch_sources(event):
    try:
        active_channels = [i['chat_id'] for i in get_active_channels()]  # заменить на API
        if not active_channels:
            return
        entity = await event.get_chat()
        title = getattr(entity, "title", None)

        str_chat_id = str(event.chat_id)
        if isinstance(entity, (Channel, Chat)):
            if str_chat_id in active_channels:
                logger.info(f'[✅] Получено сообщение из активного канала: {title}, ID: {str_chat_id}')
                await forward_to_forum(event.message, title)

    except Exception as e:
        logger.error(f"[❗] Ошибка в обработчике сообщений: {e}")




# === Запуск клиента ===
async def main():
    await client.start()
    print("Бот запущен и следит за каналами...")
    await get_all_topic(client)

    await client.run_until_disconnected()


asyncio.run(main())
