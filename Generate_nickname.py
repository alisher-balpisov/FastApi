from fastapi import HTTPException
from openai import OpenAI, api_key
from keys import key_api
from Sqlalchemy import session, NickName
from pydantic import BaseModel, Field

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=key_api
)

LANGUAGE_NAMES = {
    "ru": "русском",
    "en": "английском"
}


class NickNameModel(BaseModel):
    value: str = Field(min_length=3, max_length=20)


def generate_nickname(language: str, count: int, length: str):
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
            cleaned = completion.choices[0].message.content.replace("**", "").replace("\n", "")
            for names in cleaned.split("$"):
                if len(names.strip()) > 0:
                    session.add(NickName(name=names))
            session.commit()
            return cleaned
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"OpenAI API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка в generate_nickname: {e}")


def create_nickname(nickname: str | NickNameModel, indicator: str):
    try:
        if indicator == 'fastapi':
            validated = nickname
        elif indicator == 'aiogram':
            validated = NickNameModel(value=nickname)
    except Exception as e:
        if indicator == 'fastapi':
            raise HTTPException(status_code=500, detail=f"Ошибка в create_nickname: {e}")
        elif indicator == 'aiogram':
            return {f"error: {e} Oшибка в create_nickname"}
    new_nickname = NickName(name=validated.value)
    session.add(new_nickname)
    session.commit()
    return {"id": new_nickname.id, "name": new_nickname.name}


def update_nickname(nickname_id: int, nickname: str | NickNameModel, indicator: str):
    replaced_nickname = session.query(NickName).filter(NickName.id == nickname_id).first()

    if not replaced_nickname:
        raise HTTPException(status_code=404, detail="Никнейм не найден")

    try:
        if indicator == 'fastapi':
            replaced_nickname.name = nickname.value
        elif indicator == 'aiogram':
            replaced_nickname.name = NickNameModel(value=nickname)
    except Exception as e:
        if indicator == 'fastapi':
            raise HTTPException(status_code=500, detail=f"Ошибка в update_nickname: {e}")
        elif indicator == 'aiogram':
            return {f"error: {e} Oшибка в update_nickname"}

    session.commit()

    return {
        "id": nickname_id,
        "nickname": nickname.value if indicator == 'fastapi' else nickname
    }
