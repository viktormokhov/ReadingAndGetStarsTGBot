from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.config.content import build_display
from src.core.infrastructure.database import themes
from src.core.application.security.approved_user_only import is_approved_user
from src.bot.services.cards.card_presentation import send_card_page
from src.bot.handlers.ui.ui_cards import card_filter_paged_kb

router = Router()


@router.callback_query(F.data == "cards")
@is_approved_user()
async def cards_handler(message: Message, is_approved: bool, state: FSMContext):
    uid = message.from_user.id
    all_user_themes = list((await themes.all_cards(uid)).keys())
    if not all_user_themes:
        await message.answer("Коллекция пустая.")
        return

    await state.update_data(card_themes=all_user_themes)
    await message.answer(
        "Выбери группу карточек:",
        reply_markup=card_filter_paged_kb(all_user_themes, page=1)
    )


# Фильтр по теме
@router.callback_query(F.data.startswith("CARD_THEME|"))
@is_approved_user()
async def card_filter(query: CallbackQuery, is_approved: bool, state: FSMContext):
    await query.answer()
    _, theme = query.data.split("|", 1)
    uid = query.from_user.id
    all_cards = await themes.all_cards(uid)
    cards = all_cards.get(theme, [])

    if not cards:
        await query.message.answer("Карточек в этой теме нет.")
        return

    # Показать первую страницу (page=1)
    await send_card_page(query, theme, cards, 1)

@router.callback_query(F.data.startswith("CARD_PAGE|"))
@is_approved_user()
async def card_page_callback(query: CallbackQuery, is_approved: bool, state: FSMContext):
    page = int(query.data.split("|")[1])
    data = await state.get_data()
    themes = data.get("card_themes", [])
    if not themes:
        await query.answer("Нет доступных тем.")
        return

    await query.message.edit_reply_markup(reply_markup=card_filter_paged_kb(themes, page))
    await query.answer()


# Кнопка «CARDS»
@is_approved_user()
@router.callback_query(F.data == "CARD_THEME")
async def cards_callback(query: CallbackQuery, is_approved: bool):
    await query.answer()
    await show_all_cards(query.from_user.id, query)


async def show_all_cards(uid: int, query: CallbackQuery):
    cards_by_theme = await themes.all_cards(uid)
    if not cards_by_theme:
        await query.message.answer("📦 Тут будут ваши карточки!")
        return

    for theme, cards in cards_by_theme.items():
        # Отображаем название темы
        display = build_display()
        await query.message.answer(display.get(theme, theme))
        # Отправляем каждую карточку отдельным фото
        for c in cards:
            await query.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=c["url"],
                caption=c["title"]
            )

# async def card_filter(query: CallbackQuery, is_approved):
    # await query.answer()
    # _, theme = query.data.split("|", 1)
    #
    # uid = query.from_user.id
    # all_cards = await themes.all_cards(uid)
    #
    # # Если выбрана не все темы
    # if theme != "ALL":
    #     all_cards = {theme: all_cards.get(theme, [])}
    #
    # # Если в выбранной теме нет карточек
    # if not any(all_cards.values()):
    #     await query.bot.send_message(query.message.chat.id, "Карточек в этой теме нет.")
    #     return
    #
    # # Отправляем карточки «альбомами» — группами по 10
    # for th, cards in all_cards.items():
    #     if not cards:
    #         continue
    #     await query.bot.send_message(
    #         query.message.chat.id,
    #         f"🗂 {config.DISPLAY.get(th, th)}"
    #     )
    #     for chunk in (cards[i: i + 10] for i in range(0, len(cards), 10)):
    #         media = [
    #             InputMediaPhoto(media=c["url"], caption=c["title"])
    #             for c in chunk
    #         ]
    #         await query.bot.send_media_group(query.message.chat.id, media=media)
    #
    # # Снова показываем меню выбора темы
    # topics = list((await themes.all_cards(uid)).keys())
    # await query.bot.send_message(
    #     query.message.chat.id,
    #     "Выбери группу карточек:",
    #     reply_markup=ui.card_filter_kb(topics)
    # )

@router.callback_query(F.data == "CLOSE_CARDS")
async def close_cards_callback(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.delete()
    except Exception:
        pass
