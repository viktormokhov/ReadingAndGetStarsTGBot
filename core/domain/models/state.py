from dataclasses import dataclass, field
from typing import Dict, Optional


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

@dataclass
class ReadingState:
    uid: int
    theme: str
    qa: list[dict]
    asked: set[str]
    correct: str
    wrong: int
    card_title: str
    word_count: int
    full_text: str
    age_prompt_id: int = field(default=None)
    feedback_msg_id: Optional[int] = None  # ID предыдущего мотивационного сообщения