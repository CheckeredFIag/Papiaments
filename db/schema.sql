-- Gebruikers
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname    TEXT    NOT NULL UNIQUE,
    avatar      TEXT    DEFAULT '🧒',
    created_at  TEXT    DEFAULT (datetime('now')),
    last_seen   TEXT    DEFAULT (datetime('now'))
);

-- Scores per vaardigheid per niveau
CREATE TABLE IF NOT EXISTS scores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    skill       TEXT    NOT NULL CHECK(skill IN ('lezen','schrijven','spreken')),
    niveau      TEXT    NOT NULL,
    stars       INTEGER DEFAULT 0,
    correct     INTEGER DEFAULT 0,
    attempts    INTEGER DEFAULT 0,
    updated_at  TEXT    DEFAULT (datetime('now')),
    UNIQUE(user_id, skill, niveau)
);

-- Individuele oefensessies (voor voortgang per woord)
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    word        TEXT    NOT NULL,
    skill       TEXT    NOT NULL,
    result      TEXT    NOT NULL CHECK(result IN ('correct','fout')),
    heard_as    TEXT,
    played_at   TEXT    DEFAULT (datetime('now'))
);

-- Woorden die een kind moeilijk vindt (voor herhaling)
CREATE TABLE IF NOT EXISTS weak_words (
    user_id     INTEGER NOT NULL REFERENCES users(id),
    word        TEXT    NOT NULL,
    miss_count  INTEGER DEFAULT 1,
    last_missed TEXT    DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, word)
);
