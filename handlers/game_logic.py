from aiogram import Bot
from datetime import datetime, timedelta
import asyncio
from typing import List

from shooting_game.database.crud import (
    get_game_state,
    start_new_round,
    generate_tasks,
    end_current_round,
    process_round_actions
)
from shooting_game.database.models import GameState, Player
from shooting_game.config import ROUND_DURATION, LOCATIONS

bot: Bot = None


async def start_round():
    state = get_game_state()
    if state.is_active:
        return
    new_state = start_new_round()
    tasks = generate_tasks(new_state.round)
    with get_db() as conn:
        players = conn.execute("SELECT user_id FROM players").fetchall()
        tasks_text = "\n".join(f"{i + 1}. {t.question}" for i, t in enumerate(tasks))

        for player in players:
            try:
                await bot.send_message(
                    chat_id=player['user_id'],
                    text=f"🔔 Раунд {new_state.round} начался!\nЗадачи:\n{tasks_text}",
                    reply_markup=game_keyboard()
                )
            except Exception as e:
                print(f"Error sending message to {player['user_id']}: {e}")
    asyncio.create_task(round_timer(new_state.round))


async def round_timer(round_num: int):
    await asyncio.sleep(ROUND_DURATION)
    current_state = get_game_state()
    if current_state.round != round_num or not current_state.is_active:
        return
    winners = process_round_actions(round_num)

    winners = process_round_actions(round_num)
    if winners:
        for winner in winners:
            await bot.send_message(
                chat_id=winner['user_id'],
                text="🎉 Вы победили!"
            )
        return
    else:
        await start_round()