from aiogram import Dispatcher
from . import start, channels

def register_handlers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(channels.router)
