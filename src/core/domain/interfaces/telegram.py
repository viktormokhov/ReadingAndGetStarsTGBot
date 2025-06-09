from typing import Optional

class TelegramGateway:
    async def send_message(self, chat_id: int, text: str, reply_markup: Optional[dict] = None) -> bool:
        raise NotImplementedError

    async def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Optional[dict] = None) -> bool:
        raise NotImplementedError