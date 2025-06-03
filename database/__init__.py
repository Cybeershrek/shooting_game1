import sqlite3
from pathlib import Path
from .crud import *
from .models import *
from shooting_game.config import DB_PATH



DB_PATH = Path(__file__).parent / "game.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

from .crud import (
    create_player,
    get_player,
    get_game_state,
    start_new_round,
    end_current_round,
    process_round_actions,
    generate_tasks
)

__all__ = [
    'get_db',
    'create_player',
    'get_player',
    'get_game_state',
    'start_new_round',
    'end_current_round',
    'process_round_actions',
    'generate_tasks',
    'DB_PATH'
]


def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT NOT NULL,
            player_number INTEGER NOT NULL,
            team TEXT CHECK(team IN ('Team 1', 'Team 2')),
            location TEXT NOT NULL DEFAULT 'площадь',
            tasks_solved INTEGER NOT NULL DEFAULT 0,
            is_zombie INTEGER NOT NULL DEFAULT 0,
            UNIQUE(player_number)
        );

        CREATE TABLE IF NOT EXISTS game_state (
            round INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 0,
            round_end_time TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            round INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            target_id INTEGER,
            action_type TEXT NOT NULL,
            task_id INTEGER,
            round INTEGER NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (user_id),
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        );

        INSERT OR IGNORE INTO game_state DEFAULT VALUES;
        """)