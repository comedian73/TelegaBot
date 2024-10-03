import asyncio
import logging
import dispatcher, logic
from aiogram import Bot
from aiogram.filters.command import Command

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = '7920615627:AAGswxm1_K9QeMwpkrsYgkInUP6UZgkJzYs'

# Объект бота
bot = Bot(token=API_TOKEN)

async def main():
    # Запускаем создание таблицы базы данных
    await logic.create_table()
    await dispatcher.dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
