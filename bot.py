import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")  # Отримуємо токен з ENV змінної

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "users_data.json"

# Завантаження даних
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Збереження даних
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Головна команда
@dp.message_handler(commands=['start'])
async def start_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    if user_id not in data:
        data[user_id] = {"marshmallows": 1}  # Новий користувач отримує 1 зефір
    else:
        data[user_id]["marshmallows"] += 1  # Додаємо зефір

    save_data(data)
    await message.reply(f"🎉 Ти почав гру та отримав зефір! У тебе вже {data[user_id]['marshmallows']} 🍬")

# Перевірка кількості зефірів
@dp.message_handler(commands=['status'])
async def status_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    count = data.get(user_id, {}).get("marshmallows", 0)
    await message.reply(f"📊 У тебе {count} зефірів 🍬")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
