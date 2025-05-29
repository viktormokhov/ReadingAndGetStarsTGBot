READING_PROMPT = """
Ты — опытный автор и эксперт. Напиши информативный, хорошо структурированный, содержательный и увлекательный текст на тему
«%s» с контекстом «%s» для %s-летнего читателя (максимальное количество символов: %s). Текст должен быть хорошо связанным. 
Руководствуйся только проверенными источниками, энциклопедиями, научными журналами.
Структура:
Выбери один интересный факт или пример, вопрос, проблему или парадокс из этой темы.
Расскажи об этом.
Краткое сравнение с похожими явлениями, ситуациями в других странах, эпохах или областях.
Язык и стиль:
До 12 лет: понятно, дружелюбно, с простыми примерами, образами и небольшими историями.
13–17: живо, с элементами анализа, ссылками на современные интересы, без морализаторства.
Взрослые: нейтрально или профессионально, с аналитикой и актуальными вопросами.
Дополнительно:
Не давай описания темы.
Не используй клишированные фразы.
Объясняй сложные термины простыми словами или аналогиями.
Добавь 1–2 живых примера из жизни при необходимости.
После текста создай ровно 3 вопроса, ответы на которые можно найти только в самом тексте.
У каждого вопроса — три варианта ответа: первый всегда правильный, два других правдоподобные, но неверные. Каждый вариант не длиннее четырех слов.
Ответ верни только в виде валидного JSON-объекта, без каких-либо пояснений, комментариев или форматирования.
Формат ответа:
{
"text": "<весь текст одной строкой, абзацы разделены двумя символами \n\n>",
"card": "<одно слово из текста>",
"qa": [
{"question": "<строка>", "options": ["<строка>", "<строка>", "<строка>"]},
{"question": "<строка>", "options": ["<строка>", "<строка>", "<строка>"]},
{"question": "<строка>", "options": ["<строка>", "<строка>", "<строка>"]}
]
}
Правила:
Все строки и ключи — только в двойных кавычках.
В массиве qa — ровно три вопроса.
В каждом options — ровно три варианта.
Ключ card — словосочетание, которое встречается в text.
Не добавляй никаких пояснений, комментариев или markdown.
Проверь JSON на валидность перед отправкой.
В значении "text" не должно быть настоящих переводов строки (Enter)
"""
SCHOOL_PROMPT = """
Ты — опытный педагог. Задай вопрос из школьной программы по предмету
%s для %s-летнего школьника (максимальное количество символов: %s). Учитывай возраст и класс
Руководствуйся только проверенными источниками, энциклопедиями, научными журналами, школьными учебниками.
Язык и стиль:
До 12 лет: понятно, дружелюбно
Дополнительно:
- Не давай описание темы
- Не использовать клишированные фразы
После текста дай 3 вопроса строго по содержанию этого текста (было упоминание в тексте) и у каждого 3 варианта ответа, каждый не больше 4 слов"
где <первый> вариант должен быть правильным, а два других — правдоподобными, но неверными."
Отвечай только валидным JSON-объектом.
Формат:
{
  "text": "<строка>",
  "card": "<ключевое слово или словосочетание из текста>",
  "qa": [
    {"question": "<строка>", "options": ["<строка>","<строка>","<строка>"]},
    ...
    (ровно 3 элемента)
  ]
}
Правила:
- Все строки и ключи — только в двойных кавычках.
- В массиве qa — ровно три вопроса.
- В каждом options — ровно три варианта.
- Ключ card — словосочетание, которое встречается в text.
- Не добавляй никаких комментариев, пояснений и markdown. Только чистый JSON.
"""

CARD_PROMPT = """
Create a high-resolution image on the theme of “%s” for an audience aged %s years.
Format: %s.
Art style: %s.
Requirements and preferences:
Artistic approach with an emotional atmosphere, detailed elements, and thoughtful composition.
Select a color palette, visual imagery, and stylistic techniques that will spark interest and provide aesthetic pleasure specifically for this age group. Harmoniously combine colors, avoiding overload or imbalance.
Convey the main ideas and emotions of the theme through expressive details, original symbols, compositional choices, and typographic accents. Strive to reveal meaning not only directly, but also through associations, contrasts, and playful viewer perception.
Ensure high-quality rendering, clarity, and depth of details.
Demonstrate maximum originality and creativity: avoid clichés, stereotypes, or overused artistic techniques. Aim to surprise and engage the audience with an unexpected artistic approach or a fresh perspective on the theme.
If needed, carefully add the theme title as text, ensuring it is seamlessly integrated into the composition, does not compete with main visual elements, and reinforces the overall message.
"""

# - Заверши вопросом для размышления или небольшим заданием.
