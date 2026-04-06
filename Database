import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "streetfifa.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            coins       INTEGER DEFAULT 500,
            wins        INTEGER DEFAULT 0,
            losses      INTEGER DEFAULT 0,
            draws       INTEGER DEFAULT 0,
            last_pack   INTEGER DEFAULT 0,
            created_at  INTEGER DEFAULT (strftime('%s','now'))
        );

        CREATE TABLE IF NOT EXISTS collection (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            player_id   INTEGER NOT NULL,
            obtained_at INTEGER DEFAULT (strftime('%s','now')),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS squads (
            user_id     INTEGER PRIMARY KEY,
            player_ids  TEXT NOT NULL DEFAULT '[]',
            formation   TEXT DEFAULT '4-3-3',
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            mode        TEXT NOT NULL,
            team1_ids   TEXT NOT NULL,
            team2_ids   TEXT NOT NULL,
            team1_score INTEGER DEFAULT 0,
            team2_score INTEGER DEFAULT 0,
            status      TEXT DEFAULT 'pending',
            created_at  INTEGER DEFAULT (strftime('%s','now')),
            chat_id     INTEGER
        );

        CREATE TABLE IF NOT EXISTS quick_drafts (
            match_id    INTEGER PRIMARY KEY,
            pool        TEXT NOT NULL,
            team1_picks TEXT DEFAULT '[]',
            team2_picks TEXT DEFAULT '[]',
            turn        INTEGER DEFAULT 1,
            FOREIGN KEY(match_id) REFERENCES matches(id)
        );
        """)

def get_or_create_user(user_id: int, name: str) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            conn.execute("INSERT INTO users(user_id,name) VALUES(?,?)", (user_id, name))
            conn.commit()
            row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row)

def get_user(user_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None

def add_coins(user_id: int, amount: int):
    with get_conn() as conn:
        conn.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (amount, user_id))
        conn.commit()

def deduct_coins(user_id: int, amount: int) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT coins FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row or row["coins"] < amount:
            return False
        conn.execute("UPDATE users SET coins=coins-? WHERE user_id=?", (amount, user_id))
        conn.commit()
        return True

def get_collection(user_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT player_id FROM collection WHERE user_id=? ORDER BY obtained_at DESC",
            (user_id,)
        ).fetchall()
        return [r["player_id"] for r in rows]

def add_to_collection(user_id: int, player_ids: list):
    with get_conn() as conn:
        conn.executemany(
            "INSERT INTO collection(user_id, player_id) VALUES(?,?)",
            [(user_id, pid) for pid in player_ids]
        )
        conn.commit()

def can_open_free_pack(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    now = int(time.time())
    return (now - user["last_pack"]) >= 86400  # 24h

def mark_pack_opened(user_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE users SET last_pack=? WHERE user_id=?", (int(time.time()), user_id))
        conn.commit()

def get_squad(user_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM squads WHERE user_id=?", (user_id,)).fetchone()
        if row:
            return {"player_ids": json.loads(row["player_ids"]), "formation": row["formation"]}
        return {"player_ids": [], "formation": "4-3-3"}

def set_squad(user_id: int, player_ids: list, formation: str = "4-3-3"):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO squads(user_id, player_ids, formation)
            VALUES(?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET player_ids=excluded.player_ids, formation=excluded.formation
        """, (user_id, json.dumps(player_ids), formation))
        conn.commit()

def record_result(user_id: int, result: str):
    col = {"win": "wins", "loss": "losses", "draw": "draws"}.get(result)
    if col:
        with get_conn() as conn:
            conn.execute(f"UPDATE users SET {col}={col}+1 WHERE user_id=?", (user_id,))
            conn.commit()

def create_match(mode: str, team1_ids: list, team2_ids: list, chat_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO matches(mode,team1_ids,team2_ids,chat_id) VALUES(?,?,?,?)",
            (mode, json.dumps(team1_ids), json.dumps(team2_ids), chat_id)
        )
        conn.commit()
        return cur.lastrowid

def create_quick_draft(match_id: int, pool: list):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO quick_drafts(match_id,pool) VALUES(?,?)",
            (match_id, json.dumps(pool))
        )
        conn.commit()

def get_quick_draft(match_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM quick_drafts WHERE match_id=?", (match_id,)).fetchone()
        if row:
            return {
                "pool": json.loads(row["pool"]),
                "team1_picks": json.loads(row["team1_picks"]),
                "team2_picks": json.loads(row["team2_picks"]),
                "turn": row["turn"],
            }
        return None

def update_quick_draft(match_id: int, team1_picks: list, team2_picks: list, turn: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE quick_drafts SET team1_picks=?,team2_picks=?,turn=? WHERE match_id=?",
            (json.dumps(team1_picks), json.dumps(team2_picks), turn, match_id)
        )
        conn.commit()

def get_leaderboard() -> list:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT name, wins, losses, draws,
                   (wins*3 + draws) AS points
            FROM users
            ORDER BY points DESC, wins DESC
            LIMIT 10
        """).fetchall()
        return [dict(r) for r in rows]
