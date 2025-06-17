import uuid


class AvatarService:
    def __init__(self, image_generator, image_storage, image_tools):
        self.image_generator = image_generator
        self.image_storage = image_storage
        self.image_tools = image_tools

    async def generate_avatar_and_cache(self, prompt: str, user_id: int) -> tuple[str | None, str | None]:
        img_url = await self.image_generator.generate(prompt)
        if img_url is None:
            return None, None

        png_bytes = await self.image_tools.compress_to_png_bytes(img_url)
        avatar_uuid = str(uuid.uuid4())
        object_name = f"{user_id}/{avatar_uuid}.png"

        await self.image_storage.save(png_bytes, object_name=object_name, ext="png")
        avatar_url = self.image_storage.get_presigned_url(object_name)
        return avatar_url, avatar_uuid

    async def confirm_and_store_avatar(self, user_id: int, avatar_uuid: str) -> str:
        object_name = f"{user_id}/{avatar_uuid}.png"
        return self.image_storage.get_presigned_url(object_name)

    async def get_avatar_attempts(self, user_id: int) -> int:
        """Get the number of avatar generation attempts for a user."""
        return await self.image_tools.get_avatar_attempts(user_id)

    async def increment_avatar_attempts(self, user_id: int) -> tuple[int, str]:
        """
        Increment the number of avatar generation attempts for a user and return the new count and key.
        Returns a tuple of (attempt_number, key).
        """
        return await self.image_tools.increment_avatar_attempts(user_id)
