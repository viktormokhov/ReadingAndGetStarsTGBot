# from telegram import Update
# from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler
#
# from core import ui
# from core.db import session, user_ops
# from core.ai.entry import get_question_from_openai
#
# TEST_ANSWER = 0
# user_tests = {}
#
#
# async def cmd_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     questions = [await get_question_from_openai("random") for _ in range(5)]
#     user_tests[user_id] = {"questions": questions, "index": 0, "score": 0}
#
#     return await send_question(update, context)
#
#
# async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     data = user_tests[user_id]
#     idx = data["index"]
#     q = data["questions"][idx]
#
#     keyboard = ui.reading(q["options"])
#     await update.message.reply_text(q["question"], reply_markup=keyboard)
#     return TEST_ANSWER
#
#
# async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     data = user_tests[user_id]
#     idx = data["index"]
#     q = data["questions"][idx]
#
#     selected = update.callback_query.data.split("|")[1]
#     if selected == q["answer"]:
#         data["score"] += 1
#
#     data["index"] += 1
#     if data["index"] < 5:
#         return await send_question(update, context)
#
#     stars = data["score"] * 10
#     async with session.Session() as s:
#         await user_ops.add_stars(user_id, stars, s)
#
#     await update.callback_query.edit_message_text(
#         f"Тест завершён! ✅ Правильных ответов: {data['score']}/5\n⭐ Вы получаете {stars} звёзд!"
#     )
#     return ConversationHandler.END
#
#
# def get_test_handler():
#     return ConversationHandler(
#         entry_points=[CommandHandler("test", cmd_test)],
#         states={TEST_ANSWER: [CallbackQueryHandler(handle_answer, pattern="^OPT\\|")]},
#         fallbacks=[],
#         name="test_quiz",
#         persistent=False,
#     )
