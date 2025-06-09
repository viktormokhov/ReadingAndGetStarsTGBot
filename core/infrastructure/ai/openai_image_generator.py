import openai


class OpenAIImageGenerator:
    def __init__(self, api_key):
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str) -> str | None:
        try:
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard",
                response_format="url",
            )
            return response.data[0].url

        except Exception as e:
            print(f"[generate_avatar] Ошибка генерации аватара через OpenAI: {e}")
            return None
