import uuid
from datetime import timedelta

from minio import Minio
from io import BytesIO

class MinioImageStorage:
    def __init__(self, minio_client: Minio, bucket_name: str, url_prefix: str):
        self.client = minio_client
        self.bucket = bucket_name
        self.url_prefix = url_prefix

    async def save(self, image_bytes: bytes, object_name: str, ext: str = "png") -> str:
        from asyncio import get_running_loop
        await get_running_loop().run_in_executor(
            None,
            lambda: self.client.put_object(
                self.bucket,
                object_name,
                BytesIO(image_bytes),
                length=len(image_bytes),
                content_type=f"image/{ext}",
            )
        )
        return object_name

    def get_presigned_url(self, object_name: str, expires_minutes: int = 60) -> str:
        """Генерирует временную публичную ссылку на файл."""
        url = self.client.presigned_get_object(
            self.bucket,
            object_name,
            expires=timedelta(minutes=expires_minutes)
        )
        return url