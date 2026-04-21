from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .models import UserCreate, ScoreIn, SessionStart, SessionEnd
from . import crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title='Papiaments Leeravontuur API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


# ── Users ──────────────────────────────────────────────────────────────────

@app.post('/api/users', status_code=201)
def create_user(body: UserCreate):
    user = crud.create_user(body.name, body.avatar, body.niveau)
    if not user:
        raise HTTPException(409, 'Naam al in gebruik')
    return user


@app.get('/api/users')
def list_users():
    return crud.get_users()


@app.get('/api/users/{user_id}/dashboard')
def get_dashboard(user_id: int):
    d = crud.get_dashboard(user_id)
    if not d:
        raise HTTPException(404, 'Gebruiker niet gevonden')
    return d


@app.get('/api/users/{user_id}/weaknesses')
def get_weaknesses(user_id: int, limit: int = 5):
    if not crud.get_user(user_id):
        raise HTTPException(404, 'Gebruiker niet gevonden')
    return crud.get_weaknesses(user_id, limit)


@app.get('/api/users/{user_id}/niveau-progress')
def get_niveau_progress(user_id: int):
    d = crud.get_dashboard(user_id)
    if not d:
        raise HTTPException(404, 'Gebruiker niet gevonden')
    return d.niveau_progress


# ── Scores ─────────────────────────────────────────────────────────────────

@app.post('/api/score', status_code=201)
def post_score(body: ScoreIn):
    if not crud.get_user(body.user_id):
        raise HTTPException(404, 'Gebruiker niet gevonden')
    crud.post_score(
        body.user_id, body.word, body.skill, body.correct,
        body.niveau, body.session_id,
    )
    return {'ok': True}


# ── Sessies ────────────────────────────────────────────────────────────────

@app.post('/api/session/start', status_code=201)
def start_session(body: SessionStart):
    if not crud.get_user(body.user_id):
        raise HTTPException(404, 'Gebruiker niet gevonden')
    return {'session_id': crud.start_session(body.user_id)}


@app.post('/api/session/end')
def end_session(body: SessionEnd):
    crud.end_session(body.session_id, body.exercises_done)
    return {'ok': True}


# ── Static files (altijd als laatste!) ────────────────────────────────────

_DOCS = Path(__file__).parent.parent / 'docs'
if _DOCS.exists():
    app.mount('/', StaticFiles(directory=_DOCS, html=True), name='static')
