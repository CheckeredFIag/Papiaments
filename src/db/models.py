from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    name:       str
    avatar:     str = '🧒'
    niveau:     str = '4-6'
    id:         int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WordScore:
    user_id:    int
    word:       str
    skill:      str   # 'lezen' | 'schrijven' | 'spreken'
    correct:    bool
    niveau:     str
    session_id: int | None = None


@dataclass
class SkillTotal:
    user_id:       int
    skill:         str
    niveau:        str
    correct_total: int = 0
    wrong_total:   int = 0
    streak:        int = 0
