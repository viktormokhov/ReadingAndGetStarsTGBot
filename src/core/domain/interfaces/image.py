from typing import Protocol

class ImageGenerator(Protocol):
    async def generate(self, prompt: str) -> str:
        """Генерирует изображение по prompt и возвращает URL."""
        pass

class ImageStorage(Protocol):
    async def save(self, image_bytes: bytes, ext: str = "png") -> str:
        """Сохраняет изображение, возвращает URL (или путь)."""
        pass
