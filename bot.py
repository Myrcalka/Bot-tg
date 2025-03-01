import os
import json
import random
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")  # Отримуємо токен з ENV змінної

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "users_data.json"  # Один файл для зберігання всіх даних

# Завантаження даних
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
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

# Головне меню
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/start"), KeyboardButton("/status"))
    keyboard.add(KeyboardButton("/boost"))
    keyboard.add(KeyboardButton("/farm"))
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

    if user_id not in data:
        await message.reply("❌ Ты еще не начал игру! Напиши /start, чтобы начать.", reply_markup=get_main_menu())
        return

    # Перевірка часу фармлення
    last_farm_time = data.get(user_id, {}).get("last_farm_time", 0)
    current_time = int(time.time())

    if current_time - last_farm_time < 300:  # 5 хвилин
        remaining_time = 300 - (current_time - last_farm_time)
        await message.reply(f"❌ Ты можешь фармить зефирки только раз в 5 минут. Попробуй еще через {remaining_time} секунд.", reply_markup=get_main_menu())
        return

    # Запит на введення числа
    await message.reply(f"💬 Напиши число от 1 до 10 для фарма зефирок.", reply_markup=get_main_menu())

    # Зберігаємо число для фармлення
    data[user_id]["farm_number"] = random.randint(1, 10)  # Генерація числа для фармлення
    save_data(data)

# Перевірка відповіді на фармлення
@dp.message_handler(lambda message: message.text.isdigit())
async def check_farm_answer(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()

    if user_id in data and "farm_number" in data[user_id]:
        # Користувач може використати введене число
        user_number = int(message.text)

        # Перевіряємо, чи правильне число
        correct_number = data[user_id]["farm_number"]

        if user_number == correct_number:
            # Додаємо зефірки в залежності від введеного числа
            earned_marshmallows = user_number * 5  # Кількість зефірок за введене число
            data[user_id]["marshmallows"] += earned_marshmallows
            data[user_id]["last_farm_time"] = int(time.time())  # Оновлюємо час фармлення
            del data[user_id]["farm_number"]  # Видаляємо збережене число
            save_data(data)

            await message.reply(f"🎉 Ты использовал правильное число {user_number}! Ты получил {earned_marshmallows} зефирок. Теперь у тебя {data[user_id]['marshmallows']} зефирок.", reply_markup=get_main_menu())
        else:
            await message.reply(f"❌ Неправильное число! Попробуй еще раз.", reply_markup=get_main_menu())

# Статистика
@dp.message_handler(commands=['stats'])
async def stats_cmd(message: Message):
    data = load_data()
    stats = "📊 Статистика:\n"
    
    # Відображаємо всіх користувачів і їх зефірки
    for user_id, user_data in data.items():
        stats += f"{user_id}: {user_data['marshmallows']} 🍬 зефирок, Уровень {user_data['level']}\n"

    await message.reply(stats, reply_markup=get_main_menu())

# Меню
@dp.message_handler(commands=['menu'])
async def menu_cmd(message: Message):
    await message.reply(
        "🔹 Доступные команды:\n"
        "/start — Начать игру (если ты еще не начал)\n"
        "/status — Проверить свой статус (количество зефирок и уровень)\n"
        "/stats — Посмотреть общую статистику всех игроков\n"
        "/boost — Повысить уровень (снимает 10 зефирок)\n"
        "/farm — Фармите зефирки (каждые 5 минут)\n"
        "/menu — Показать это меню",
        reply_markup=get_main_menu()
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
