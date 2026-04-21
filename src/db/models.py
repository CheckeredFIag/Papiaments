from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    nickname:   str
    avatar:     str = '🧒'
    id:         int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen:  str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Score:
    user_id:  int
    skill:    str   # 'lezen' | 'schrijven' | 'spreken'
    niveau:   str   # '4-6' | '6-8' | '8-10' | '10' | 'all'
    stars:    int = 0
    correct:  int = 0
    attempts: int = 0


@dataclass
class Session:
    user_id:  int
    word:     str
    skill:    str
    result:   str   # 'correct' | 'fout'
    heard_as: str = ''
