import aiohttp
import uuid
from PIL import Image
from io import BytesIO

class ImageTools:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def compress_to_png(self, url: str, size=(256, 256)) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes))
        image = image.convert("RGBA")
        image = image.resize(size, Image.LANCZOS)
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

    async def compress_and_store_in_redis(self, url: str, user_id: int) -> str:
        png_bytes = await self.compress_to_png(url)
        avatar_uuid = str(uuid.uuid4())
        await self.redis.set(f"avatar:{user_id}:{avatar_uuid}", png_bytes, ex=3600)  # TTL 1 час
        return avatar_uuid

    async def get_png_from_redis(self, user_id: int, avatar_uuid: str) -> bytes:
        data = await self.redis.get(f"avatar:{user_id}:{avatar_uuid}")
        if data is None:
            raise Exception("Аватар не найден или истек срок действия")
        return data

    async def delete_png_from_redis(self, user_id: int, avatar_uuid: str):
        await self.redis.delete(f"avatar:{user_id}:{avatar_uuid}")

    async def increment_avatar_attempts(self, user_id: int) -> tuple[int, str]:
        """
        Increment the number of avatar generation attempts for a user.
        Returns a tuple of (attempt_number, key).
        """
        attempt_uuid = str(uuid.uuid4())
        key = f"user:avatar:attempts:{user_id}:{attempt_uuid}"
        # Store 1 as the value to indicate this is a single attempt
        await self.redis.set(key, 1, ex=86400)  # TTL 24 hours
        # Count the total number of attempts
        total_attempts = await self.count_avatar_attempts(user_id)
        return total_attempts, key

    async def count_avatar_attempts(self, user_id: int) -> int:
        """Count the number of avatar generation attempts for a user."""
        pattern = f"user:avatar:attempts:{user_id}:*"
        count = 0
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            count += len(keys)
            if cursor == 0:
                break
        return count

    async def get_avatar_attempts(self, user_id: int) -> int:
        """Get the number of avatar generation attempts for a user."""
        return await self.count_avatar_attempts(user_id)
