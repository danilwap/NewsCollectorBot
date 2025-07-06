from config import api_id, api_hash, phone, target_forum_id

from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetForumTopicsRequest, CreateForumTopicRequest
import asyncio
from logging_config import logger
from services.db import get_active_channels

from telethon.tl.types import Channel, Chat

# === Инициализация клиента ===
client = TelegramClient(phone, api_id, api_hash)


async def get_forum_topic(input_channel, title):
    try:
        list_topics = await client(GetForumTopicsRequest(
            channel=input_channel,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        for topic in list_topics.topics:
            if topic.title == title:
                logger.info(f"[🔁] Найден существующий топик '{title}'")
                return topic
        return
    except Exception as e:
        logger.error(f'[❗] Ошибка при получении списка топиков: {e}')
        raise


async def get_or_create_topic_entity(title):
    try:
        input_channel = await client.get_input_entity(target_forum_id)  # Получаем InputChannel группы

        # Получаем список всех топиков (до 100)
        topic = await get_forum_topic(input_channel, title)
        if topic:
            return topic

        # # Если не найден — создаём
        await client(CreateForumTopicRequest(channel=input_channel, title=title))
        topic = await get_forum_topic(input_channel, title)
        logger.info(f"[🆕] Создан новый топик '{title}' {topic.id}")
        return topic

    except Exception as e:
        logger.error(f"[❗] Ошибка при получении/создании топика '{title}': {e}")
        raise


async def forward_to_forum(message, title):
    try:
        input_topic = await get_or_create_topic_entity(title)

        await client.send_message(
            entity=target_forum_id,
            message=message,
            comment_to=input_topic.id
        )

        logger.info(f"[➡] Сообщение переслано в топик '{title}'")

    except Exception as e:
        logger.error(f"[❗] Ошибка при пересылке в топик '{title}': {e}")


async def get_all_topic(client: TelegramClient):
    input_channel = await client.get_input_entity(target_forum_id)

    result = await client(GetForumTopicsRequest(
        channel=input_channel,
        offset_date=None,
        offset_id=0,
        offset_topic=0,
        limit=100
    ))

    for topic in result.topics:
        print(f"🟢 Тема: {topic.title} | ID: {topic.id}")
        if topic.id == 1:
            await client.send_message(
                entity=input_channel,  # 👈 отправка напрямую в топик
                message="Привет из нужной темы",
                comment_to=7
            )


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
    logger.info("Бот запущен и следит за каналами...")
    await client.run_until_disconnected()


asyncio.run(main())
