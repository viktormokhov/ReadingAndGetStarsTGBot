import json
import re

import dirtyjson


def normalize_llm_chatgpt_response(llm_response: str) -> dict | None:
    """
    Парсит строку ответа модели LLM, сначала очищая её с помощью внутренней функции _clean_llm_json,
    а затем пытаясь загрузить как JSON с помощью dirtyjson.
    Возвращает распарсенный объект, либо вызывает исключение, если парсинг не удался.
    """
    cleaned = _clean_llm_json(llm_response)
    try:
        raw = dirtyjson.loads(cleaned)
        if paragraphs := split_into_paragraphs(raw.get('text')):
            raw['text'] = paragraphs
        return raw
    except Exception as e:
        raise RuntimeError(f"Ошибка парсинга LLM-JSON Open AI: {llm_response}")


def escape_control_characters(text: str) -> str:
    # Заменяем невалидные управляющие символы на их escape-последовательности
    return text.replace('\r\n', '\\n').replace('\n', '\\n').replace('\r', '\\n')


def normalize_llm_gemini_response(llm_response: str) -> dict | None:
    if not llm_response or not isinstance(llm_response, str):
        raise ValueError("Входная строка отсутствует или не является строкой.")

    response = llm_response.strip()
    response = re.sub(r"^```(?:json)?\s*", "", response, flags=re.IGNORECASE)
    response = re.sub(r"\s*```$", "", response)
    response = response.strip()
    if not response:
        raise ValueError("Пустой ответ после удаления маркеров.")

    # ВАЖНО: экранируем только управляющие символы в тексте (желательно только внутри значений!)
    response = escape_control_characters(response)

    try:
        return json.loads(response)
    except Exception as e:
        raise ValueError(f"Не удалось преобразовать строку в JSON: {e}\nСтрока: {response}")


def _clean_llm_json(raw: str) -> str:
    """
    Очищает исходную строку, содержащую JSON-данные, для последующего парсинга.
    Выполняет следующие действия:
    - Вырезает только часть строки, содержащую JSON (от первой открывающейся до последней закрывающейся скобки).
    - Заменяет одинарные кавычки ' на двойные ", чтобы соответствовать стандарту JSON.
    - Удаляет запятые, расположенные перед закрывающими скобками ] или }, что делает JSON синтаксис корректным.
    """
    match = re.search(r'(\{[\s\S]*\})', raw)
    if match:
        raw = match.group(1)
    raw = raw.replace("'", '"')
    raw = re.sub(r',(\s*[\]\}])', r'\1', raw)
    return raw


def split_into_paragraphs(text, sentences_per_paragraph=3):
    # Разбить на предложения (учитываем точку, воскл. и вопросит. знаки)
    sentences = re.findall(r'[^.!?]+[.!?]', text, flags=re.U)
    paragraphs = []
    for i in range(0, len(sentences), sentences_per_paragraph):
        paragraph = ''.join(sentences[i:i+sentences_per_paragraph]).strip()
        if paragraph:
            paragraphs.append(paragraph)
    # Собрать абзацы в одну строку, используя \n\n
    return '\n\n'.join(paragraphs)


def validate_generated_data(data: dict[str, object]) -> None:
    """
    Проверяет структуру сгенерированных данных.
    Если структура некорректна — выбрасывает исключение ValueError.
    """
    qa = data.get("qa")
    if not isinstance(qa, list) or len(qa) != 3:
        raise ValueError("Поле 'qa' должно быть списком из 3 элементов.")
    for idx, item in enumerate(qa, 1):
        if not (
                isinstance(item, dict)
                and "question" in item
                and isinstance(item.get("options"), list)
                and len(item["options"]) == 3
        ):
            raise ValueError(f"Элемент №{idx} в 'qa' некорректен или не содержит 3 варианта ответа.")
