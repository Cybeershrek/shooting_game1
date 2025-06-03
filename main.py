import asyncio
import signal
from aiogram import Bot, Dispatcher
from config import BotConfig
from handlers import commands, game_logic
from database import init_db


async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await BotConfig.bot.session.close()


async def main():
    init_db()
    bot = Bot(token=BotConfig.TOKEN)
    dp = Dispatcher()
    BotConfig.bot = bot
    dp.include_router(commands.router)
    dp.shutdown.register(on_shutdown)

    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print("Бот корректно завершает работу...")
    finally:
        await on_shutdown(dp)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        print("Работа бота завершена")