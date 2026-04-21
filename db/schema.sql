-- Kinderen
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    avatar     TEXT    DEFAULT '🧒',
    niveau     TEXT    DEFAULT '4-6',
    created_at TEXT    DEFAULT (datetime('now'))
);

-- Oefensessies
CREATE TABLE IF NOT EXISTS sessions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL REFERENCES users(id),
    started_at     TEXT    DEFAULT (datetime('now')),
    ended_at       TEXT,
    exercises_done INTEGER DEFAULT 0
);

-- Individuele antwoorden (goed/fout per woord per vaardigheid)
CREATE TABLE IF NOT EXISTS word_scores (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    session_id INTEGER REFERENCES sessions(id),
    word       TEXT    NOT NULL,
    skill      TEXT    NOT NULL CHECK(skill IN ('lezen','schrijven','spreken')),
    correct    INTEGER NOT NULL CHECK(correct IN (0,1)),
    niveau     TEXT    NOT NULL,
    last_seen  TEXT    DEFAULT (datetime('now'))
);

-- Lopende totalen per gebruiker × vaardigheid × niveau
CREATE TABLE IF NOT EXISTS skill_totals (
    user_id       INTEGER NOT NULL REFERENCES users(id),
    skill         TEXT    NOT NULL CHECK(skill IN ('lezen','schrijven','spreken')),
    niveau        TEXT    NOT NULL,
    correct_total INTEGER DEFAULT 0,
    wrong_total   INTEGER DEFAULT 0,
    streak        INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, skill, niveau)
);
