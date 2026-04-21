from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    avatar: str = '🧒'
    niveau: str = '4-6'


class UserOut(BaseModel):
    id: int
    name: str
    avatar: str
    niveau: str
    created_at: str


class ScoreIn(BaseModel):
    user_id: int
    word: str
    skill: str   # 'lezen' | 'schrijven' | 'spreken'
    correct: bool
    niveau: str
    session_id: Optional[int] = None


class SessionStart(BaseModel):
    user_id: int


class SessionEnd(BaseModel):
    session_id: int
    exercises_done: int = 0


class SkillTotalOut(BaseModel):
    skill: str
    niveau: str
    correct_total: int
    wrong_total: int
    streak: int
    ratio: float


class WeakWordOut(BaseModel):
    word: str
    skill: str
    wrong_total: int
    niveau: str


class NiveauProgressOut(BaseModel):
    niveau: str
    correct: int
    total: int
    ratio: float


class DashboardOut(BaseModel):
    user: UserOut
    skill_totals: list[SkillTotalOut]
    weak_words: list[WeakWordOut]
    niveau_progress: list[NiveauProgressOut]
    total_correct: int
    total_attempts: int
