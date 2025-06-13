from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from Generate_nickname import generate_nickname, create_nickname, update_nickname
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardRemove
from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from Sqlalchemy import session, NickName

class Form(StatesGroup):
    language = State()
    count = State()
    length = State()


class NicknameStates(StatesGroup):
    waiting_for_nickname = State()
    waiting_for_id = State()
    waiting_for_NewNickname= State()
router = Router()
reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить'), KeyboardButton(text='Изменить'), KeyboardButton(text='Удалить'),
         KeyboardButton(text='Вывести'), KeyboardButton(text='Сгенерировать')]
    ],
    resize_keyboard=True
)

language_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='ru'), KeyboardButton(text='en')]],
    resize_keyboard=True
)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Привет! Я бот для работы с никнеймами", reply_markup=reply_kb)


@router.message(F.text == "Сгенерировать")
async def start_gen(message: Message, state: FSMContext):
    await state.set_state(Form.language)
    await message.answer("Выберите язык:", reply_markup=language_kb)


@router.message(Form.language)
async def get_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await state.set_state(Form.count)
    await message.answer("Введите количество (count):", reply_markup=ReplyKeyboardRemove())


@router.message(Form.count)
async def get_count(message: Message, state: FSMContext):
    await state.update_data(count=message.text)
    await state.set_state(Form.length)
    await message.answer("Введите длину (length):")


@router.message(Form.length)
async def get_length(message: Message, state: FSMContext):
    await state.update_data(length=message.text)
    data = await state.get_data()

    language = data["language"]
    count = int(data["count"])
    length = (data["length"])

    nicknames = generate_nickname(language, count, length)

    if isinstance(nicknames, list):
        result = "\n".join(nicknames)
    else:
        result = str(nicknames)

    await message.answer(f"Вот твои никнеймы:\n{result}")
    await state.clear()


@router.message(F.text == "Добавить")
async def Create_nickname(message: Message, state: FSMContext):
    await message.answer("Введите никнейм:")
    await state.set_state(NicknameStates.waiting_for_nickname)


@router.message(NicknameStates.waiting_for_nickname)
async def save_nickname(message: Message, state: FSMContext):
    nickname = create_nickname(message.text, indicator='aiogram')
    await message.answer(f"Никнейм добавлен: {nickname}")
    await state.clear()


@router.message(F.text == 'Вывести')
async def get_nicknames(message: Message):
    nicknames = session.query(NickName)

    if not nicknames:
        await message.answer("Список никнеймов пуст.")
        return

    response = "\n".join([f"id:    {n.id}             name:    {n.name}" for n in nicknames])
    await message.answer(response)

id
@router.message(F.text == 'Изменить')
async def Update_nickname(message: Message, state: FSMContext):
    await message.answer("Введите id:")
    await state.set_state(NicknameStates.waiting_for_id)


@router.message(NicknameStates.waiting_for_id)
async def update_Nickname(message: Message, state: FSMContext):
    global id
    id = message.text
    await message.answer("Введите новый никнейм:")
    await state.set_state(NicknameStates.waiting_for_NewNickname)


@router.message(NicknameStates.waiting_for_NewNickname)
async def update_nickName(message: Message, state: FSMContext):
    global id
    new_nickname = message.text
    nickname = update_nickname(id, new_nickname, indicator='aiogram')
    await message.answer(nickname)

