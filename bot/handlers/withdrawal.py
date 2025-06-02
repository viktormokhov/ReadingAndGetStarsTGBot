# from telegram import Update, ReplyKeyboardRemove
# from telegram.ext import ContextTypes
#
# from bot.routers.state import ensure_name
#
#
# async def cmd_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if await ensure_name(update, context):
#         return
#     await update.message.reply_text(
#         f"В процессе разработки",
#         reply_markup=ReplyKeyboardRemove()
#     )
