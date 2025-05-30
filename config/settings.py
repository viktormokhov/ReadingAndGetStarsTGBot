from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, SecretStr, field_validator, BaseModel
from pydantic_settings import BaseSettings

load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
DATA_DIR = BASE_DIR / "data"
CARD_DIR = DATA_DIR / "card"
DATA_DIR.mkdir(exist_ok=True)

WEBAPP_URL = "https://v0-quiz-dx.vercel.app"

class ProjectBaseSettings(BaseSettings):
    class Config:
        env_file = ENV_FILE
        case_sensitive = False
        extra = "ignore"


class TextModelConfig(BaseModel):
    model_name: str

class ImageModelConfig(BaseModel):
    model_name: str


class TelegramSettings(ProjectBaseSettings):
    tg_admin_ids: list[int]
    tg_bot_token: SecretStr

    @field_validator("tg_admin_ids", mode="before")
    def parse_admin_ids(cls, v):
        if isinstance(v, int):
            return [v]
        if isinstance(v, str):
            return [int(uid.strip()) for uid in v.split(",") if uid.strip()]
        return v


class OpenAISettings(ProjectBaseSettings):
    openai_api_key: SecretStr
    text: Optional[TextModelConfig] = TextModelConfig(model_name="gpt-4.1-nano-2025-04-14")
    image: Optional[ImageModelConfig] = ImageModelConfig(model_name="dall-e-3")


class GeminiSettings(ProjectBaseSettings):
    google_gemini_api_key: SecretStr
    google_gemini_proxy_url: str
    text: Optional[TextModelConfig] = TextModelConfig(model_name="gemini-2.0-flash-001:generateContent")
    image: Optional[ImageModelConfig] = None


class CloudflareSettings(ProjectBaseSettings):
    cloudflare_api_key: SecretStr
    cloudflare_account_id: str
    text: Optional[TextModelConfig] = None
    image: Optional[ImageModelConfig] = ImageModelConfig(model_name="bytedance/stable-diffusion-xl-lightning")

    @property
    def cloudflare_worker_image_url(self) -> str:
        return (
            f'https://api.cloudflare.com/client/v4/accounts/'
            f'{self.cloudflare_account_id}/ai/run/@cf/{self.image.model_name}'
        )


class DeepSeekSettings(ProjectBaseSettings):
    openrouter_api_key: SecretStr
    openrouter_url: str = 'https://openrouter.ai/api/v1'
    text: Optional[TextModelConfig] = TextModelConfig(model_name="deepseek/deepseek-r1:free")
    image: Optional[ImageModelConfig] = None


class AISettings:
    def __init__(self, **providers):
        for name, provider in providers.items():
            setattr(self, name, provider)

    def get_all_text_models(self) -> dict:
        result = {}
        for k, v in vars(self).items():
            if hasattr(v, "text") and v.text is not None:
                provider_dict = v.model_dump() if hasattr(v, "model_dump") else v.dict()
                # Удаляем ключ 'image', если он есть
                provider_dict.pop('image', None)
                result[k] = provider_dict
        return result

    def get_all_image_models(self) -> dict:
        result = {}
        for k, v in vars(self).items():
            if hasattr(v, "image") and v.image is not None:
                provider_dict = v.model_dump() if hasattr(v, "model_dump") else v.dict()
                # Удаляем ключ 'text', если он есть
                provider_dict.pop('text', None)
                result[k] = provider_dict
        return result


class DBSettings(ProjectBaseSettings):
    db_url: str = Field(default_factory=lambda: f"sqlite+aiosqlite:///{DATA_DIR / 'bot.database'}")
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_name: str = "telegram_bot"

class ImgBBSettings(ProjectBaseSettings):
    imgbb_api_key: SecretStr


class BackendSettings(ProjectBaseSettings):
    backend_api_key: SecretStr

# === Инициализация ===
tg_settings = TelegramSettings()
openai_settings = OpenAISettings()
gemini_settings = GeminiSettings()
cloudflare_settings = CloudflareSettings()
deepseek_settings = DeepSeekSettings()

ai_settings = AISettings(
    openai=openai_settings,
    gemini=gemini_settings,
    cloudflare=cloudflare_settings,
    deepseek=deepseek_settings,
)

db_settings = DBSettings()
imgbb_settings = ImgBBSettings()
backend_settings = BackendSettings()
