from logging import basicConfig, INFO

from src.settings import bot, dp
from bot.handlers import start


if __name__ == '__main__':
    # basicConfig(level=INFO)
    dp.include_router(router=start.router)
    dp.run_polling(bot)
