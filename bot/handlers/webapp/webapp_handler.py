# from aiogram import Router, F
# from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from aiogram.utils.web_app import safe_parse_webapp_init_data
#
# from core.config import WEBAPP_URL
#
# router = Router()
#
#
# @router.callback_query(F.data == "webapp")
# async def open_webapp(callback: CallbackQuery):
#     """Handler for the open_webapp callback - sends a button to open the WebApp"""
#     await callback.answer()
#
#     webapp_button = InlineKeyboardButton(
#         text="Открыть WebApp",
#         web_app=WebAppInfo(url=WEBAPP_URL)
#     )
#
#     markup = InlineKeyboardMarkup(inline_keyboard=[[webapp_button]])
#
#     await callback.message.answer(
#         "Нажмите кнопку ниже, чтобы открыть WebApp с 3D персонажем:",
#         reply_markup=markup
#     )


# @router.message(F.web_app_data)
# async def web_app_handler(message: Message):
#     """Handler for data received from the WebApp"""
#     try:
#         # Parse the data from the WebApp
#         web_app_data = safe_parse_webapp_init_data(token=message.bot.token, init_data=message.web_app_data.data)
#
#         # Process the data (in a real app, you would save this to your database)
#         user_id = web_app_data.get("users", {}).get("id")
#         category = web_app_data.get("category")
#         topic = web_app_data.get("topic")
#         result = web_app_data.get("result")
#
#         # In a real implementation, you would use the AI service to generate content
#         # from core.ai.prompt.prompt import READING_PROMPT
#         # from core._services.ai_service import generate_content
#
#         # Generate content using AI (this would be the actual implementation)
#         # ai_content = await generate_content(
#         #     prompt=READING_PROMPT,
#         #     topic=topic,
#         #     category=category,
#         #     user_id=user_id
#         # )
#
#         # Send a confirmation message
#         await message.answer(
#             f"✅ Данные получены:\n"
#             f"📚 Категория: {category}\n"
#             f"📖 Тема: {topic}\n"
#             f"🏆 Результат: {result}\n\n"
#             f"Ваш прогресс сохранен! Продолжайте изучение в WebApp или в боте."
#         )
#
#     except Exception as e:
#         # Handle any errors
#         await message.answer(f"❌ Произошла ошибка при обработке данных: {str(e)}")

# # Add this to your main menu or other appropriate handlers
# async def add_webapp_button_to_menu(message: Message):
#     """Helper function to add a WebApp button to menus"""
#     webapp_button = InlineKeyboardButton(
#         text="3D WebApp",
#         callback_data="open_webapp"
#     )
#
#     # Return the button to be added to an existing keyboard
#     return webapp_button
