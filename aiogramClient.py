from aiogram.types import Message
from aiogram.filters import Command
from Generate_nickname import generate_nickname
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router

router = Router()
reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить'), KeyboardButton(text='Изменить'), KeyboardButton(text='Удалить'),
         KeyboardButton(text='Вывести')]
    ],
    resize_keyboard=True
)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Привет! Я бот для работы с никнеймами")


@router.message()
async def Generate_Nickname(message: Message):
    cleaned = generate_nickname()
    for i in range(0, len(cleaned), 4096):
        await message.answer(cleaned[i:i + 4096])
