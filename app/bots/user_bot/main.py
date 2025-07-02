import asyncio
from telethon import TelegramClient
from config import api_id, api_hash, phone
from telethon.tl.types import Channel, Chat
from logging_config import logger
from services.db import get_active_channels
from telethon import TelegramClient, events

client = TelegramClient(phone, api_id, api_hash)


# === Обработка сообщений ===
@client.on(events.NewMessage())
async def watch_sources(event):
    try:
        active_channels = [i['chat_id'] for i in get_active_channels()]  # заменить на API
        if not active_channels:
            return
        entity = await event.get_chat()
        title = getattr(entity, "title", None)
        str_chat_id = str(event.chat_id)
        if not title:
            logger.warning(f"[⚠] У источника {str_chat_id} нет названия (title=None)")
            title = str_chat_id
        if isinstance(entity, (Channel, Chat)):
            if str_chat_id in active_channels:
                logger.info(f'[✅] Получено сообщение из активного канала: {title}, ID: {str_chat_id}')
                await forward_to_forum(event.message, title)

    except Exception as e:
        logger.error(f"[❗] Ошибка в обработчике сообщений: {e}")


async def main():
    await client.start()
    logger.info("Бот запущен и следит за каналами...")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
