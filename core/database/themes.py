from datetime import date

from sqlalchemy import select, func

from core.database.models import ThemeStat, Card, ThemeSetting
from core.database.init_db import AsyncSessionLocal


async def inc_theme(uid: int, theme: str):
    async with AsyncSessionLocal.begin() as s:
        ts = await s.get(ThemeStat, {"user_id": uid, "theme": theme})
        if ts:
            ts.texts += 1
        else:
            s.add(ThemeStat(user_id=uid, theme=theme, texts=1))


async def all_cards(uid: int) -> dict[str, list[dict]]:
    async with AsyncSessionLocal() as s:
        rows = await s.scalars(select(Card).where(Card.user_id == uid))
        d: dict[str, list[dict]] = {}
        for c in rows:
            d.setdefault(c.theme, []).append({"title": c.title, "url": c.url})
        return d


async def get_min_len(theme: str, default: int) -> int:
    async with AsyncSessionLocal() as s:
        row = await s.get(ThemeSetting, theme)
        return row.min_len if row else default


async def set_min_len(theme: str, new_len: int):
    async with AsyncSessionLocal.begin() as s:
        row = await s.get(ThemeSetting, theme)
        if row:
            row.min_len = new_len
        else:
            s.add(ThemeSetting(theme=theme, min_len=new_len))

