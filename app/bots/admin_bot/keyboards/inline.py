from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

main_keyboards = InlineKeyboardBuilder()
main_keyboards.add(InlineKeyboardButton(text='Добавить канал', callback_data='add_channel'))
main_keyboards.add(InlineKeyboardButton(text='Список каналов', callback_data='list_channels'))