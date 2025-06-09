import asyncio


class AvatarService:
    def __init__(self, image_generator, image_storage, image_tools):
        self.image_generator = image_generator
        self.image_storage = image_storage
        self.image_tools = image_tools

    async def generate_avatar_and_cache(self, prompt: str, user_id: int) -> tuple[str | None, str | None]:
        img_url = await self.image_generator.generate(prompt)
        avatar_uuid = None
        if img_url is not None:
            avatar_uuid = await self.image_tools.compress_and_store_in_redis(img_url, user_id)
        return img_url, avatar_uuid

    async def confirm_and_store_avatar(self, user_id: int, avatar_uuid: str) -> str:
        img_bytes = await self.image_tools.get_png_from_redis(user_id, avatar_uuid)
        object_name = await self.image_storage.save(img_bytes, ext="png")
        await self.image_tools.delete_png_from_redis(user_id, avatar_uuid)
        avatar_url = self.image_storage.get_presigned_url(object_name, expires_minutes=60)
        return avatar_url

    async def get_avatar_attempts(self, user_id: int) -> int:
        """Get the number of avatar generation attempts for a user."""
        return await self.image_tools.get_avatar_attempts(user_id)

    async def increment_avatar_attempts(self, user_id: int) -> tuple[int, str]:
        """
        Increment the number of avatar generation attempts for a user and return the new count and key.
        Returns a tuple of (attempt_number, key).
        """
        return await self.image_tools.increment_avatar_attempts(user_id)
