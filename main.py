from fastapi import FastAPI, Query, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

app = FastAPI()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='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'
)

LANGUAGE_NAMES = {
    "ru": "русском",
    "en": "английском"
}

db = {}


class NickName(BaseModel):
    value: str = Field(min_length=3, max_length=20)


@app.get("/generate-nickname")
def generate_nickname(
        language: str = Query("ru", enum=["ru", "en"]),
        count: int = Query(10, ge=1, le=100),
        length: str = Query("long", enum=["short", "medium", "long"])
):
    try:
        prompt = f"""
        Сгенерируй {count} уникальных никнеймов на {language} языке.

        Формат каждого никнейма:
        [Прилагательное][Существительное][Число]

        Требования:
        - Прилагательное описывает тему.
        - Существительное — объект из этой темы.
        - Число: случайное число ({{
                "long": "1000-9999",
                "medium": "100-999",
                "short": "10-99"
            }}["{length}"]).
        - Все никнеймы должны быть разными.
        - Не используй символы, кроме букв и цифр.
        - Не добавляй пояснений, только список никнеймов построчно.
        - разделяй никнеймы вот таким знаком $
        """
        try:
            completion = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324:free",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"OpenAI API error: {e}")
        global db
        temporary_db = {}
        counter_temporary_db = 0
        clean = completion.choices[0].message.content.replace("**", "").replace("\n", "")
        for name in clean.split("$"):
            if len(name.strip()) > 0:
                db[len(db)] = name
                temporary_db[counter_temporary_db] = name
                counter_temporary_db += 1
        return {"nicknames": temporary_db}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка в generate_nickname: {e}")


@app.post("/nicknames")
def create_nickname(nickname: NickName):
    new_id = len(db)
    db[new_id] = nickname.value
    return {"id": new_id, "nickname": nickname.value}


@app.get("/nicknames")
def get_nicknames():
    if len(db) == 0:
        raise HTTPException(status_code=404, detail="Словарь пуст!")
    return db


@app.put("/nicknames/{nickname_id}")
def update_nickname(nickname_id: int, nickname: NickName):
    if nickname_id not in db:
        raise HTTPException(status_code=404, detail="Никнейм не найден")
    db[nickname_id] = nickname.value
    return {"id": nickname_id, "nickname": nickname.value}


@app.delete("/nicknames/{nickname_id}")
def delete_nickname(nickname_id: int):
    global db
    if nickname_id not in db:
        raise HTTPException(status_code=404, detail="Никнейм не найден")
    deleted = db.pop(nickname_id)

    new_db = {}
    for id, value in enumerate(db.values()):
        new_db[id] = value
    db = new_db
    return {"message": f"Никнейм '{deleted}' удалён"}
