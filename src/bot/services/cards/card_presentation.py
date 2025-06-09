from aiogram.types import CallbackQuery, InputMediaPhoto

from config.constants import CARDS_PER_PAGE
from bot.handlers.ui.ui_cards import cards_pagination_kb


async def send_card_page(query: CallbackQuery, cards: list, page: int):
    total_pages = (len(cards) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
    start = (page - 1) * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    page_cards = cards[start:end]

    text = f"Страница {page} из {total_pages}"

    # Удаляем старое сообщение, если хотим чтобы было всегда только одно "окно"
    try:
        await query.message.delete()
    except Exception:
        pass

    # Отправляем карточки (группой или по одной)
    media = []
    for c in page_cards:
        media.append(InputMediaPhoto(media=c["url"], caption=c["title"]))

    # Нет смысла показывать навигацию тем — показывай навигацию по страницам карточек!
    nav_kb = cards_pagination_kb(page, total_pages)  # сделай отдельную функцию для этого

    if len(media) == 1:
        await query.message.answer_photo(media[0].media, caption=media[0].caption,
                                         reply_markup=nav_kb)
    else:
        await query.message.answer(text, reply_markup=nav_kb)
        for m in media:
            await query.message.answer_photo(m.media, caption=m.caption)
