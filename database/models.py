from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Player:
    user_id: int
    full_name: str
    player_number: int
    team: str
    username: Optional[str] = None
    location: str = "площадь"
    tasks_solved: int = 0
    is_zombie: bool = False

@dataclass
class GameState:
    round: int = 0
    is_active: bool = False
    round_end_time: Optional[datetime] = None

@dataclass
class Task:
    id: int
    question: str
    answer: str
    round: int

@dataclass
class Action:
    id: int
    player_id: int
    action_type: str  # 'shoot' или 'heal'
    target_id: Optional[int] = None
    task_id: Optional[int] = None
    round: int = 0