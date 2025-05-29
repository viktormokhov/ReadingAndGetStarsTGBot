import random
import time

import emoji
import math

from core.ai.prompt.mapping import CATEGORIES_PROMPT
from core.ai.prompt.prompt import SCHOOL_PROMPT, READING_PROMPT


def get_length_by_age(age: int) -> int:
    """
    Вычисляет максимальную длину текста на основе возраста пользователя.

    Для младших пользователей длина текста меньше, для старших — больше.
    Используется экспоненциальная зависимость между min_length и max_length
    в диапазоне возрастов от min_age до max_age.

    Args:
        age (int): Возраст пользователя.

    Returns:
        int: Максимально допустимая длина текста.
    """
    min_length = 150
    max_length = 1000
    min_age = 6
    max_age = 25

    exponent = (age - min_age) / (max_age - min_age)
    value = min_length + (max_length - min_length) * (math.exp(exponent) - 1) / (math.e - 1)
    return int(value)


def build_mapping(category: str, theme: str, age: int) -> dict:
    """
    Находит и возвращает параметры темы по названию среди всех категорий.

    Args:
        category (str): Название категории.
        theme (str): Название темы.
        age (int): Возраст пользователя.

    Returns:
        dict: Словарь с параметрами для генерации текста.

    Raises:
        KeyError: Если категория или тема не найдены.
    """
    emojis = emoji.emoji_list(category)
    if emojis:
        emoji_end = emojis[0]['match_end']
        category = category[emoji_end:].strip()

    if category not in CATEGORIES_PROMPT:
        raise KeyError(f"Категория {category} не найдена.")

    category_dict = CATEGORIES_PROMPT[category]
    if theme not in category_dict:
        raise KeyError(f"Тема {theme} не найдена в категории {category}.")

    instruction = category_dict[theme]
    return {
        "max_length": get_length_by_age(age),
        "instruction": instruction,
        "category": theme
    }


def build_prompt(category: str, theme: str, age: int) -> str:
    """
    Собирает финальный prompt для генерации текста.

    Включает:
      - ограничение по длине и hint,
      - ровно 3 вопроса с 3 вариантами (первый — правильный),
      - блок запрета на использование prev_q,
      - уникальный seed для снижения повторов.

    Args:
        category (str): Категория темы.
        theme (str): Тема генерации.
        age (int): Возраст целевой аудитории.

    Returns:
        str: Готовый prompt для передачи модели.
    """
    seed = f"{random.randint(1000, 9999)}-{int(time.time())}"
    params = build_mapping(category, theme, age)
    max_text_length = params["max_length"]
    instruction = params["instruction"]

    # Определяем шаблон в зависимости от категории
    if "Школа" in category:
        prompt = SCHOOL_PROMPT % (instruction, age, max_text_length)
    else:
        prompt = READING_PROMPT % (theme, instruction, age, max_text_length)

    return f"[SEED:{seed}] {prompt}"
