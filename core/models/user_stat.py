from dataclasses import dataclass

from core.services.users.user_progress import get_status_by_stars


@dataclass
class UserStat:
    id: int
    name: str
    is_approved: bool
    stars: int
    cards: int
    q_ok: int
    q_tot: int
    streak: int

    def format_html(self) -> str:
        acc = f"{(self.q_ok/self.q_tot*100):.0f}%" if self.q_tot else "—"
        status = "✅" if self.is_approved else "⏳"
        rank = get_status_by_stars(self.stars)
        return (
            f"{status} <b>{self.name}</b> "
            f"(ID: <code>{self.id}</code>)\n"
            f"{rank}\n"
            f"⭐ {self.stars} | 🃏 {self.cards} | 📖 {self.q_tot} | 🎯 {self.q_ok} | ⚖️ {acc} | 🔥 {self.streak}"
        )
    