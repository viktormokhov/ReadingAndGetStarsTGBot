from core.services.users.user_progress import get_status_by_stars


def format_stats(data: dict) -> str:
    name = data.get("name", "Пользователь")
    stars = data.get("stars", 0)
    streak = data.get("streak", 0)
    q_ok = data.get("q_ok", 0)
    q_tot = data.get("q_tot", 0)
    acc = int(q_ok * 100 / q_tot) if q_tot > 0 else 0
    badge = get_status_by_stars(stars)

    lines = [
        f"<b>{name}</b>, твой прогресс:",
        "────────────────────────────",
        f"⭐  Звёздочки:  {stars}",
        f"🏅  Статус: <b>{badge}</b>",
        f"🃏  Карточки: {data.get('card_count')}",
        f"💬  Вопросы: {data.get('questions_count')}",
        f"🎯  Точность: {acc}% ({q_ok}/{q_tot})",
        f"🔥  Серия:   {streak}",
    ]

    themes = data.get("themes", {})
    if themes:
        lines.append("────────────────────────────")
        lines.append("📚 По темам:")
        # Найдём максимальное значение
        max_count = max(themes.values())
        for theme, count in themes.items():
            if count == max_count:
                lines.append(f"• <b>{theme}: {count}</b>")
            else:
                lines.append(f"• {theme}: {count}")

    return "\n".join(lines)