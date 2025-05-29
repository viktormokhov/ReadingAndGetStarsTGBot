from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional


@dataclass
class ReadingState:
    uid: int
    theme: str
    qa: List[dict]
    asked: Set[str]
    correct: str
    wrong: int
    card_title: str
    word_count: int
    full_text: str
    age_prompt_id: int = field(default=None)
    feedback_msg_id: Optional[int] = None  # ID предыдущего мотивационного сообщения
