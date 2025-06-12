from fastapi import HTTPException
from openai import OpenAI, api_key
from keys import key_api

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=key_api
)

LANGUAGE_NAMES = {
    "ru": "русском",
    "en": "английском"
}



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
            return cleaned
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"OpenAI API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка в generate_nickname: {e}")
