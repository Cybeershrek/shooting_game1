import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database" / "game.db"
QUESTIONS_PATH = BASE_DIR / "questions.csv"

ROUND_DURATION = 300
MAX_TASKS_PER_ROUND = 3
LOCATIONS = ["площадь", "больница", "реанимация", "морг", "кладбище"]

class BotConfig:
    TOKEN = "8003794444:AAGV-oHUkiDq2bDkDrBGR7gH9mszyVrRjBg"
    ADMIN_IDS = [123456789]
    bot: 'Bot' = None