import aiohttp
import uuid
from PIL import Image
from io import BytesIO

class ImageTools:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def compress_to_png_bytes(self, url: str, size=(256, 256)) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to fetch image: {resp.status}")
                img_bytes = await resp.read()
        image = Image.open(BytesIO(img_bytes)).convert("RGBA")
        image = image.resize(size, Image.LANCZOS)
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()

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
