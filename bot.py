import os
import json
import re
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
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # Якщо файл пошкоджений, створюємо новий порожній словник
            print("Помилка: Невірний формат JSON в файлі users_data.json")
            return {}
    return {}

# Збереження даних
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Помилка під час збереження даних: {e}")

# Функція для перевірки українського тексту
def contains_ukrainian(text):
    # Перевіряємо, чи містить текст українські символи
    return bool(re.search('[а-яА-Яіїєґ]', text)) and not bool(re.search('[ёЁ]', text))

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
    await message.reply(f"🎉 Ты начал игру и получил зефир! У тебя уже {data[user_id]['marshmallows']} 🍬")

# Перевірка кількості зефірів
@dp.message_handler(commands=['status'])
async def status_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    count = data.get(user_id, {}).get("marshmallows", 0)
    await message.reply(f"📊 У тебя {count} зефиров 🍬")

# Перевірка повідомлення на український текст
@dp.message_handler(content_types=['text'])
async def check_message(message: Message):
    if contains_ukrainian(message.text):
        await message.reply("❌ Извините, украинский текст не поддерживается. Пожалуйста, используйте русский.")
        return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
