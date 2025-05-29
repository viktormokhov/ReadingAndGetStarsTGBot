# Limits and Paging
DEFAULT_PROMPT_LENGTH: int = 150
DAILY_LIMIT_PER_THEME: int = 5
MAX_ATTEMPTS: int = 3
MAX_RETRIES: int = 5
BACKOFF_BASE_SECONDS: int = 1
PAGE_SIZE: int = 5
CARDS_PER_PAGE: int = 4
CARDS_ROW_WIDTH: int = 2

KIND_TO_MESSAGE = {
    "text": "❗Пожалуйста, дождись завершения генерации текста!",
    "card": "❗Пожалуйста, дождись завершения генерации карточки!",
    "read": "❗Пожалуйста, прочитай текст и ответь на вопрос!",
}

# Redis keys
BLOCK_MSG_KEY = "user:{user_id}:block_message_id"
ACTIVE_QUESTION_KEY = "user:{user_id}:has_active_question"