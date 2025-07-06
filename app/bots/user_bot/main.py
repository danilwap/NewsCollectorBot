import asyncio
from telethon.tl.functions.channels import GetForumTopicsRequest, CreateForumTopicRequest

from config import api_id, api_hash, phone, target_forum_id
from telethon.tl.types import Channel, Chat
from logging_config import logger
from services.db import get_active_channels, save_channels_to_db, init_db
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest

client = TelegramClient(session=f"{str(phone)}.session", api_id=api_id, api_hash=api_hash, phone=str(phone))


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


async def get_all_channels(client: TelegramClient):
    dialogs = await client.get_dialogs()

    chat_list = []
    for dialog in dialogs:
        entity = dialog.entity

        if isinstance(entity, Channel):
            chat_type = 'channel' if not entity.megagroup else 'supergroup'
            chat_list.append({
                'id': entity.id,
                'title': entity.title or 'No Title',
                'chat_type': chat_type
            })

        elif isinstance(entity, Chat):
            chat_list.append({
                'id': entity.id,
                'title': entity.title or 'No Title',
                'chat_type': 'group'
            })

    logger.info(f"📋 Список чатов обновлён: {chat_list}")
    save_channels_to_db(chat_list)


# === Обработка сообщений ===  в работе
@client.on(events.NewMessage())
async def watch_sources(event):

    try:
        if str(event.chat_id) == '7732659130':
            if event.message.text == '/update_channels':
                await get_all_channels(client)

            else:
                text = event.message.text.strip()
                logger.info(text)
                await client(JoinChannelRequest(text))


        else:
            active_channels = [i['chat_id'] for i in get_active_channels()]  # заменить на API
            if not active_channels:
                return
            entity = await event.get_chat()
            title = getattr(entity, "title", None)

            str_chat_id = str(getattr(entity, "id", None)
)
            if str_chat_id[:4] == '-100':
                str_chat_id = str_chat_id[4:]

            if isinstance(entity, (Channel, Chat)):
                if str_chat_id in active_channels:
                    logger.info(f'[✅] Получено сообщение из активного канала: {title}, ID: {str_chat_id}')
                    await forward_to_forum(event.message, title)

    except Exception as e:
        logger.error(f"[❗] Ошибка в обработчике сообщений: {e}")


async def get_my_id(client):
    my_id = await client.get_me()
    logger.info(f"👤 ID user_bot: {my_id.id}", )


# === Запуск клиента ===
async def main():
    await client.start()
    init_db()
    logger.info("Бот запущен и следит за каналами...")
    await get_all_channels(client)
    await get_my_id(client)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
