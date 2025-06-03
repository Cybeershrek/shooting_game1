from datetime import datetime, timedelta
from typing import List, Optional
from .db_connection import get_db
from .models import Player, GameState, Task, Action
from pathlib import Path

import pandas as pd
from shooting_game.config import QUESTIONS_PATH, LOCATIONS, ROUND_DURATION, MAX_TASKS_PER_ROUND


def create_player(user_id: int, full_name: str, username: str = None) -> Player:
    with get_db() as conn:
        cursor = conn.cursor()

        team_counts = cursor.execute(
            "SELECT team, COUNT(*) as count FROM players GROUP BY team"
        ).fetchall()

        team = "Team 1"
        if team_counts:
            team1_count = next((t['count'] for t in team_counts if t['team'] == 'Team 1'), 0)
            team2_count = next((t['count'] for t in team_counts if t['team'] == 'Team 2'), 0)
            team = "Team 1" if team1_count <= team2_count else "Team 2"

        player_number = cursor.execute("SELECT COALESCE(MAX(player_number), 0) + 1 FROM players").fetchone()[0]

        cursor.execute(
            """INSERT INTO players 
            (user_id, username, full_name, player_number, team) 
            VALUES (?, ?, ?, ?, ?)""",
            (user_id, username, full_name, player_number, team)
        )
        return Player(user_id, full_name, player_number, team, username)


def get_player(user_id: int) -> Optional[Player]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM players WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        return Player(**row) if row else None


def get_game_state() -> GameState:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM game_state").fetchone()
        if not row:
            return GameState()
        return GameState(
            round=row['round'],
            is_active=bool(row['is_active']),
            round_end_time=datetime.fromisoformat(row['round_end_time']) if row['round_end_time'] else None
        )


def start_new_round() -> GameState:
    with get_db() as conn:
        current_state = get_game_state()
        new_round = current_state.round + 1
        round_end = datetime.now() + timedelta(seconds=ROUND_DURATION)

        conn.execute(
            """UPDATE game_state 
            SET round = ?, is_active = 1, round_end_time = ?""",
            (new_round, round_end.isoformat())
        )
        return GameState(new_round, True, round_end)


def generate_tasks(round_num: int) -> list:
    """Генерация задач для раунда"""
    try:
        if not Path(QUESTIONS_PATH).exists():
            raise FileNotFoundError(f"Файл {QUESTIONS_PATH} не найден")
        questions = pd.read_csv(
            QUESTIONS_PATH,
            sep=';',
            header=None,
            names=['question', 'answer'],
            on_bad_lines='skip'
        )
        if len(questions) == 0:
            raise ValueError("Файл с вопросами пуст")

        task_count = min(3, len(questions))
        tasks = questions.sample(task_count).to_dict('records')
        saved_tasks = []
        with get_db() as conn:
            for task in tasks:
                cursor = conn.execute(
                    """INSERT INTO tasks (question, answer, round)
                    VALUES (?, ?, ?) RETURNING id""",
                    (task['question'], task['answer'], round_num)
                )
                task_id = cursor.fetchone()['id']
                saved_tasks.append({
                    'id': task_id,
                    'question': task['question'],
                    'answer': task['answer']
                })

        return saved_tasks

    except Exception as e:
        print(f"Ошибка генерации задач: {e}")
        return [
            {'question': 'Сколько будет 2+2?', 'answer': '4'},
            {'question': 'Столица России?', 'answer': 'Москва'}
        ]


def get_round_tasks(round_num: int) -> List[Task]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE round = ?",
            (round_num,)
        ).fetchall()
        return [Task(**row) for row in rows]

def end_current_round(round_num: int):
    with get_db() as conn:
        conn.execute(
            "UPDATE game_state SET is_active = 0 WHERE round = ?",
            (round_num,)
        )
        conn.commit()


def process_round_actions(round_num: int):
    """Обрабатывает все действия раунда и возвращает победителей"""
    with get_db() as conn:
        conn.execute("""
            UPDATE players SET location = 
            CASE 
                WHEN location = 'больница' THEN 'площадь'
                WHEN location = 'реанимация' THEN 'больница' 
                WHEN location = 'морг' THEN 'реанимация'
                ELSE location
            END
            WHERE user_id IN (
                SELECT player_id FROM actions 
                WHERE action_type = 'heal' AND round = ?
            )
        """, (round_num,))
        conn.execute("""
            UPDATE players SET location = 
            CASE 
                WHEN location = 'площадь' AND RANDOM() % 2 = 0 THEN 'больница'
                WHEN location = 'больница' AND RANDOM() % 2 = 0 THEN 'реанимация'
                WHEN location = 'реанимация' AND RANDOM() % 2 = 0 THEN 'морг'
                WHEN location = 'морг' AND RANDOM() % 2 = 0 THEN 'кладбище'
                ELSE location
            END
            WHERE user_id IN (
                SELECT target_id FROM actions 
                WHERE action_type = 'shoot' AND round = ?
            )
        """, (round_num,))
        conn.execute("""
            UPDATE players SET is_zombie = 1 
            WHERE location = 'кладбище'
        """)
        winners = conn.execute("""
            SELECT * FROM players 
            WHERE location = 'площадь' AND is_zombie = 0
        """).fetchall()

        return winners