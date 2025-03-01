import os
import json
import random
import re
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")  # Отримуємо токен з ENV змінної

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "users_data.json"
TIME_FILE = "farm_time.json"  # Файл для збереження часу фармлення

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

# Завантаження часу фармлення
def load_farm_time():
    if os.path.exists(TIME_FILE):
        with open(TIME_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Збереження даних
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")

# Збереження часу фармлення
def save_farm_time(farm_time):
    with open(TIME_FILE, "w", encoding="utf-8") as file:
        json.dump(farm_time, file, indent=4)

# Головне меню
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/start"), KeyboardButton("/status"))
    keyboard.add(KeyboardButton("/boost"))  # Додаємо кнопку для підвищення рівня
    return keyboard

# Головна команда
@dp.message_handler(commands=['start'])
async def start_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"marshmallows": 0, "level": 1}  # Новий користувач, рівень 1

        marshmallows = 10  # Кількість зефірок, що отримує користувач при старті
        data[user_id]["marshmallows"] += marshmallows  # Додаємо зефірки
        save_data(data)

        level = data[user_id]["level"]
        await message.reply(f"🎉 Ты начал игру! У тебя уровень: {level}. Ты получил {marshmallows} зефирок. Теперь у тебя {data[user_id]['marshmallows']} 🍬", reply_markup=get_main_menu())
    else:
        # Якщо користувач вже в грі, не потрібно відправляти повідомлення про старт
        await message.reply(f"📝 Ты уже в игре. Твой уровень: {data[user_id]['level']}. У тебя {data[user_id]['marshmallows']} зефирок 🍬.", reply_markup=get_main_menu())

# Перевірка кількості зефірок
@dp.message_handler(commands=['status'])
async def status_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    count = data.get(user_id, {}).get("marshmallows", 0)
    level = data.get(user_id, {}).get("level", 1)
    await message.reply(f"📊 Статус: У тебя {count} зефирок 🍬 на уровне {level}.", reply_markup=get_main_menu())

# Підвищення рівня
@dp.message_handler(commands=['boost'])
async def boost_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    if user_id in data:
        if data[user_id]["marshmallows"] >= 10:  # Плата за підвищення рівня
            data[user_id]["marshmallows"] -= 10  # Знімаємо 10 зефірок
            data[user_id]["level"] += 1  # Підвищуємо рівень
            save_data(data)
            await message.reply(f"🎉 Твой уровень увеличен на 1! Теперь твой уровень: {data[user_id]['level']}. Ты потратил 10 зефирок. Теперь у тебя {data[user_id]['marshmallows']} зефирок.", reply_markup=get_main_menu())
        else:
            await message.reply("❌ У тебя недостаточно зефирок для повышения уровня. Нужно 10 зефирок.", reply_markup=get_main_menu())
    else:
        await message.reply("❌ Ты еще не начал игру! Напиши /start, чтобы начать.", reply_markup=get_main_menu())

# Функція фармлення зефірок
@dp.message_handler(commands=['farm'])
async def farm_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()
    farm_time = load_farm_time()

    if user_id not in data:
        await message.reply("❌ Ты еще не начал игру! Напиши /start, чтобы начать.", reply_markup=get_main_menu())
        return

    # Перевірка часу фармлення
    last_farm_time = farm_time.get(user_id, 0)
    current_time = int(time.time())

    if current_time - last_farm_time < 300:  # 5 хвилин
        await message.reply(f"❌ Ты можешь фармить зефирки только раз в 5 минут. Попробуй еще через {300 - (current_time - last_farm_time)} секунд.", reply_markup=get_main_menu())
        return

    # Генерація випадкового числа, яке користувач має вгадати
    random_number = random.randint(1, 10)
    farm_time[user_id] = current_time
    save_farm_time(farm_time)

    # Просимо користувача ввести число
    await message.reply(f"💬 Напиши число от 1 до 10, чтобы получить зефирки.", reply_markup=get_main_menu())

    # Зберігаємо правильну відповідь для перевірки
    farm_time[user_id] = {"number": random_number}

# Перевірка відповіді на фармлення
@dp.message_handler()
async def check_farm_answer(message: Message):
    user_id = str(message.from_user.id)
    farm_time = load_farm_time()

    if user_id in farm_time and "number" in farm_time[user_id]:
        correct_number = farm_time[user_id]["number"]
        if message.text.isdigit() and int(message.text) == correct_number:
            # Додаємо зефірки
            data = load_data()
            data[user_id]["marshmallows"] += random.randint(5, 20)  # Випадкове значення зефірок
            save_data(data)
            await message.reply(f"🎉 Ты правильно угадал число! Ты получил зефирки! Теперь у тебя {data[user_id]['marshmallows']} зефирок.", reply_markup=get_main_menu())
        else:
            await message.reply(f"❌ Ты не угадал число. Правильный ответ был {correct_number}. Попробуй снова через 5 минут.", reply_markup=get_main_menu())

# Статистика
@dp.message_handler(commands=['stats'])
async def stats_cmd(message: Message):
    data = load_data()
    stats = "\n".join([f"{i+1}. {user}: {data[user]['marshmallows']} 🍬 зефирок" for i, user in enumerate(data)])
    await message.reply(f"📊 Статистика:\n{stats}", reply_markup=get_main_menu())

# Меню
@dp.message_handler(commands=['menu'])
async def menu_cmd(message: Message):
    await message.reply(
        "🔹 Доступные команды:\n"
        "/start — Начать игру\n"
        "/status — Проверить свой статус\n"
        "/stats — Посмотреть общую статистику\n"
        "/boost — Повысить уровень (снимает 10 зефирок)\n"
        "/farm — Фармите зефирки\n"
        "/menu — Показать это меню",
        reply_markup=get_main_menu()
    )

# Перевірка повідомлення на український текст
@dp.message_handler(content_types=['text'])
async def check_message(message: Message):
    # Тут нічого не змінюється, ми не будемо блокувати український текст
    # Всі тексти, написані українською мовою, також обробляються нормально
    pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
