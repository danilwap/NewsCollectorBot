from aiogram import Router, types
from aiogram.filters import Command
from keyboards.inline import main_keyboards

router = Router()

@router.message(Command(commands=['start']))
async def start(message: types.Message):
    await message.answer("Привет! Я админ-бот. Что вы хотите сделать?", reply_markup=main_keyboards.as_markup())
