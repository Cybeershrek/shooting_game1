from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from shooting_game.database import get_db

from shooting_game.database.crud import (
    create_player,
    get_player,
    get_game_state,
    start_new_round,
    end_current_round
)
from shooting_game.database.models import Player, GameState
from shooting_game.utils.keyboards import game_keyboard
from shooting_game.config import LOCATIONS

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    player = get_player(user.id)

    if player:
        await message.answer(
            f"Вы уже зарегистрированы! Ваш номер: {player.player_number}",
            reply_markup=game_keyboard()
        )
        return

    try:
        player = create_player(user.id, user.full_name, user.username)
        await message.answer(
            f"Вы зарегистрированы в игре! Ваш номер: {player.player_number}",
            reply_markup=game_keyboard()
        )
    except Exception as e:
        await message.answer("Ошибка регистрации. Попробуйте позже.")
        print(f"Error registering player: {e}")


@router.message(Command("status"))
async def cmd_status(message: types.Message):
    try:
        with get_db() as conn:
            state = conn.execute("SELECT * FROM game_state").fetchone()
            players = conn.execute("""
                SELECT player_number, team, location 
                FROM players 
                ORDER BY player_number
            """).fetchall()

            status_msg = [
                f"Раунд: {state['round']} | {'Активен' if state['is_active'] else 'Не активен'}"
            ]
            status_msg.extend(
                f"#{p['player_number']} ({p['team']}): {p['location']}"
                for p in players
            )

            await message.answer("\n".join(status_msg))

    except Exception as e:
        await message.answer(f"Ошибка получения статуса: {str(e)}")
        print(f"Error in cmd_status: {e}")


@router.message(Command("begin"))
async def cmd_begin(message: types.Message):
    state = get_game_state()
    if state.is_active:
        await message.answer("Игра уже начата!")
        return

    with get_db() as conn:
        player_count = conn.execute("SELECT COUNT(*) FROM players").fetchone()[0]
        if player_count < 2:
            await message.answer("Недостаточно игроков (минимум 2)")
            return

    new_state = start_new_round()
    tasks = generate_tasks(new_state.round)

    await message.answer(
        f"Раунд {new_state.round} начался!\n"
        f"Задачи:\n" + "\n".join(f"{i + 1}. {t.question}" for i, t in enumerate(tasks)),
        reply_markup=game_keyboard()
    )