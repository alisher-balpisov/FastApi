from fastapi import FastAPI, Query, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

###---
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = 'postgresql://localhost/postgres'
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class NickName_sql(Base):
    __tablename__ = "nicknames"

    id = Column(Integer, primary_key=True)
    name = Column(String)


Base.metadata.create_all(engine)
###---
app = FastAPI()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='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'
)

LANGUAGE_NAMES = {
    "ru": "русском",
    "en": "английском"
}


class NickName_pydantic(BaseModel):
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
        - не нумеруй никнеймы.
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

        temporary_db = {}
        counter_temporary_db = 0
        clean = completion.choices[0].message.content.replace("**", "").replace("\n", "")
        for names in clean.split("$"):
            if len(names.strip()) > 0:
                session.add(NickName_sql(name=names))
                session.commit()
                temporary_db[counter_temporary_db] = names
                counter_temporary_db += 1
        return {"nicknames": temporary_db}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка в generate_nickname: {e}")


@app.post("/nicknames")
def create_nickname(nickname: NickName_pydantic):
    new_nickname = NickName_sql(name=nickname.value)
    session.add(new_nickname)
    session.commit()
    return {"id": new_nickname.id, "name": new_nickname.name}


@app.get("/nicknames")
def get_nicknames():
    nicknames = session.query(NickName_sql)
    return [{'id': n.id, 'name': n.name} for n in nicknames]


@app.put("/nicknames/{nickname_id}")
def update_nickname(nickname_id: int, nickname: NickName_pydantic):
    record = session.query(NickName_sql).filter(NickName_sql.id == nickname_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Никнейм не найден")

    record.name = nickname.value

    session.commit()

    return {"id": nickname_id, "nickname": nickname.value}


@app.delete("/nicknames/{nickname_id}")
def delete_nickname(nickname_id: int):
    record = session.query(NickName_sql).filter(NickName_sql.id == nickname_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Никнейм не найден")

    session.delete(record)
    session.commit()

    return {"message": f"Никнейм с id={nickname_id} удалён"}
