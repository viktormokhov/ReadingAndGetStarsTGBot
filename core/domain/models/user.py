from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True)
class User:
    id: int
    name: str
    age: Optional[int] = None
    is_approved: bool
    has_requested_access: Optional[bool] = None
    is_admin: Optional[bool] = None
    q_ok: Optional[int] = None
    q_tot: Optional[int] = None
    streak: Optional[int] = None
    last: Optional[datetime] = None
    first_active: Optional[datetime] = None
    last_active: Optional[datetime] = None
