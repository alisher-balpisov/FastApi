###--- fastapi
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field

###--- sqlalchemy
from Sqlalchemy import session, NickName

from Generate_nickname import generate_nickname, create_nickname
import asyncio
from aiogram import Bot, Dispatcher
from keys import tg_token
from aiogramClient import router
import uvicorn

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main_aiogram())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

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
            temporary_db[counter_temporary_db] = names
            counter_temporary_db += 1
    return {"nicknames": temporary_db}


@app.post("/nicknames")
def Create_nickname(nickname: NickNameModel):
    return create_nickname(nickname, indicator="fastapi")


@app.get("/nicknames")
def get_nicknames():
    nicknames = session.query(NickName)
    if not nicknames:
        raise HTTPException(status_code=404, detail="Список пуст")
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
