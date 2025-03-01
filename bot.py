import os
import json
import random
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
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
            print("Ошибка: Неверный формат JSON в файле users_data.json")
            return {}
    return {}

# Збереження даних
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

# Рівень користувача та кількість зефірів залежно від рівня
def get_marshmallows(level):
    return random.randint(1, level * 3)  # Рандомна кількість зефірів в залежності від рівня

# Головне меню
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/start"), KeyboardButton("/status"))
    keyboard.add(KeyboardButton("/stats"), KeyboardButton("/menu"))
    keyboard.add(KeyboardButton("/boost"))  # Додаємо кнопку для підвищення рівня
    return keyboard

# Головна команда
@dp.message_handler(commands=['start'])
async def start_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    if user_id not in data:
        data[user_id] = {"marshmallows": 0, "level": 1}  # Новий користувач, рівень 1
    else:
        data[user_id]["level"] += 1  # Збільшуємо рівень після кожного запуску

    level = data[user_id]["level"]
    marshmallows = get_marshmallows(level)
    data[user_id]["marshmallows"] += marshmallows  # Додаємо зефірки

    save_data(data)
    await message.reply(f"🎉 Ты начал игру! У тебя уровень: {level}. Ты получил {marshmallows} зефирок. В твоем аккаунте теперь {data[user_id]['marshmallows']} 🍬", reply_markup=get_main_menu())

# Перевірка кількості зефірів
@dp.message_handler(commands=['status'])
async def status_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    count = data.get(user_id, {}).get("marshmallows", 0)
    level = data.get(user_id, {}).get("level", 1)
    await message.reply(f"📊 Статус: У тебя {count} зефирок 🍬 на уровне {level}.", reply_markup=get_main_menu())

# Статистика
@dp.message_handler(commands=['stats'])
async def stats_cmd(message: Message):
    data = load_data()
    total_users = len(data)
    total_marshmallows = sum(user_data["marshmallows"] for user_data in data.values())
    total_levels = sum(user_data["level"] for user_data in data.values())
    
    await message.reply(f"📊 Статистика:\n" 
                        f"🔹 Общее количество пользователей: {total_users}\n"
                        f"🔹 Общая количество зефирок: {total_marshmallows} 🍬\n"
                        f"🔹 Сумма всех уровней: {total_levels}", reply_markup=get_main_menu())

# Підвищення рівня
@dp.message_handler(commands=['boost'])
async def boost_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    if user_id in data:
        # Підвищуємо рівень
        data[user_id]["level"] += 1
        save_data(data)
        await message.reply(f"🎉 Твой уровень увеличен на 1! Сейчас твой уровень: {data[user_id]['level']}.", reply_markup=get_main_menu())
    else:
        await message.reply("❌ Ты еще не начал игру! Напиши /start, чтобы начать.", reply_markup=get_main_menu())

# Привітання
@dp.message_handler(commands=['hello'])
async def hello_cmd(message: Message):
    await message.reply("👋 Привет! Рад тебя видеть в нашей игре! Напиши /start, чтобы начать игру!", reply_markup=get_main_menu())

# Генерація випадкового числа
@dp.message_handler(commands=['random'])
async def random_cmd(message: Message):
    rand_num = random.randint(1, 100)
    await message.reply(f"🎲 Твое случайное число: {rand_num}", reply_markup=get_main_menu())

# Додавання зефірів
@dp.message_handler(commands=['add_marshmallow'])
async def add_marshmallow_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    if user_id in data:
        data[user_id]["marshmallows"] += 5  # Додаємо 5 зефірів користувачу
        save_data(data)
        await message.reply(f"🎉 Ты получил 5 зефирок! У тебя теперь {data[user_id]['marshmallows']} 🍬", reply_markup=get_main_menu())
    else:
        await message.reply("❌ Ты еще не начал игру! Напиши /start, чтобы начать!", reply_markup=get_main_menu())

# Покажемо меню з усіма командами
@dp.message_handler(commands=['menu'])
async def menu_cmd(message: Message):
    await message.reply(
        "🔹 Доступные команды:\n"
        "/start — Начать игру\n"
        "/status — Проверить свой статус\n"
        "/stats — Посмотреть общую статистику\n"
        "/boost — Повысить уровень\n"
        "/random — Сгенерировать случайное число\n"
        "/add_marshmallow — Добавить зефир\n"
        "/hello — Приветствие\n"
        "/menu — Показать это меню",
        reply_markup=get_main_menu()
    )

# Перевірка повідомлення на український текст
@dp.message_handler(content_types=['text'])
async def check_message(message: Message):
    if contains_ukrainian(message.text):
        await message.reply("❌ Извините, украинский текст не поддерживается. Пожалуйста, используйте русский.")
        return

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
