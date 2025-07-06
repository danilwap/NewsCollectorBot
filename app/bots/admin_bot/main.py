import asyncio
from handlers import register_handlers
from services.logging_config import logger
from loader import dp, bot
from services.db import init_db

async def main():
    me = await bot.get_me()
    logger.info(me.id)
    register_handlers(dp)
    init_db()
    logger.info('Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
