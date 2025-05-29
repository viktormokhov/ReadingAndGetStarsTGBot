from dataclasses import dataclass
from typing import Dict


@dataclass
class UserStats:
    name: str
    stars: int
    streak: int
    q_ok: int
    q_tot: int
    themes: Dict[str, int]
    total_questions: int
    card_count: int
