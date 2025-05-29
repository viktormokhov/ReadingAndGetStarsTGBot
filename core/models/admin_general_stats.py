from dataclasses import dataclass

@dataclass
class GeneralStats:
    total_users: int
    approved_users: int
    avg_accuracy: float  # fraction 0..1
    total_stars: int
    avg_active_hours: int
    avg_active_minutes: int
    total_questions: int
    total_cards: int
