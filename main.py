###--- fastapi
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

###--- sqlalchemy
from Sqlalchemy import session, NickName

from Generate_nickname import generate_nickname
import asyncio
from aiogram import Bot, Dispatcher
from keys import tg_token
from aiogramClient import router

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main_aiogram())


bot = Bot(token=tg_token)
dp = Dispatcher()
dp.include_router(router)


async def main_aiogram():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error_in_Main: {e}")


class NickNameModel(BaseModel):
    value: str = Field(min_length=3, max_length=20)


@app.get("/generate-nickname")
async def Generate_nickname(
        language: str = Query("ru", enum=["ru", "en"]),
        count: int = Query(10, ge=1, le=100),
        length: str = Query("long", enum=["short", "medium", "long"]),
):
    cleaned = generate_nickname(language, count, length)
    temporary_db = {}
    counter_temporary_db = 0
    for names in cleaned.split("$"):
        if len(names.strip()) > 0:
            session.add(NickName(name=names))
            temporary_db[counter_temporary_db] = names
            counter_temporary_db += 1
    session.commit()
    return {"nicknames": temporary_db}


@app.post("/nicknames")
def create_nickname(nickname: NickNameModel):
    new_nickname = NickName(name=nickname.value)
    session.add(new_nickname)
    session.commit()
    return {"id": new_nickname.id, "name": new_nickname.name}


@app.get("/nicknames")
def get_nicknames():
    nicknames = session.query(NickName)
    return [{'id': n.id, 'name': n.name} for n in nicknames]


@app.put("/nicknames/{nickname_id}")
def update_nickname(nickname_id: int, nickname: NickNameModel):
    replaced_nickname = session.query(NickName).filter(NickName.id == nickname_id).first()

    if not replaced_nickname:
        raise HTTPException(status_code=404, detail="Никнейм не найден")

    replaced_nickname.name = nickname.value

    session.commit()

    return {"id": nickname_id, "nickname": nickname.value}


@app.delete("/nicknames/{nickname_id}")
def delete_nickname(nickname_id: int):
    deleted_nickname = session.query(NickName).filter(NickName.id == nickname_id).first()

    if not deleted_nickname:
        raise HTTPException(status_code=404, detail="Никнейм не найден")

    session.delete(deleted_nickname)
    session.commit()

    return {"message": f"Никнейм с id={nickname_id} удалён"}
