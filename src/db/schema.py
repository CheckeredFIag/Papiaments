import sqlite3
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
DB_PATH     = _ROOT / 'db' / 'papiaments.db'
SCHEMA_PATH = _ROOT / 'db' / 'schema.sql'


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))
    print(f"✅ Database klaar: {DB_PATH}")
