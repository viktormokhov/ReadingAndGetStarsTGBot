import asyncio
from telegram import Bot
from bot import TOKEN
from bot import session, user_ops

bot = Bot(token=TOKEN)


async def notify_all_users(text: str):
    async with session.Session() as s:
        users = await user_ops.get_all_user_ids(s)

    success = 0
    failed = 0

    for uid in users:
        try:
            await bot.send_message(chat_id=uid, text=text)
            success += 1
        except Exception as e:
            print(f"❌ Не удалось отправить {uid}: {e}")
            failed += 1

    print(f"✅ Отправлено: {success}, ❌ Ошибок: {failed}")


if __name__ == "__main__":
    asyncio.run(notify_all_users("🚀 Новая функция: тест из 5 вопросов! Используй /test"))
