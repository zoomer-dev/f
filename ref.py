import telebot
from telebot import types
import json
import os
import time

# === Настройки ===
TOKEN = '7549972063:AAH_ueDQxT8-K2D5EVm-M_jLFG1_c3wA9pc'
SPONSOR_CHANNELS = ['@lemon_wh', '@limonchat_777','@bet_gram1', '@jet_bio']
DATA_FILE = 'data.json'

bot = telebot.TeleBot(TOKEN)
bot_username = bot.get_me().username or "UnknownBot"

# === Работа с файлами ===
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# === Проверка подписки ===
def check_subscription(user_id):
    for channel in SPONSOR_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# === Обработка /start ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or f"user_{user_id}"
    language = message.from_user.language_code or "неизвестно"

    if not check_subscription(message.from_user.id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for ch in SPONSOR_CHANNELS:
            markup.add(types.InlineKeyboardButton(f"🔗 Перейти: {ch}", url=f"https://t.me/{ch[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check_subs"))
        bot.send_message(message.chat.id, "📛 Подпишитесь на все каналы ниже, чтобы продолжить:", reply_markup=markup)
        return

    data = load_data()
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None

    if user_id in data:
        bot.send_message(message.chat.id, "✅ Вы уже зарегистрированы.")
    else:
        data[user_id] = {
            "username": username,
            "language": language,
            "referrer": referrer_id if referrer_id != user_id else None,
            "referrals": [],
            "balance": 0
        }

        if referrer_id and referrer_id in data:
            data[referrer_id]["referrals"].append(user_id)
            data[referrer_id]["balance"] += 1000
            try:
                bot.send_message(
                    int(referrer_id),
                    "🎉 По вашей ссылке зарегистрировался новый пользователь!\n+1000 грам 🪙"
                )
            except:
                pass

        save_data(data)
        bot.send_message(message.chat.id, "🛠 Создание аккаунта...")
        time.sleep(1)
        bot.send_message(message.chat.id, "✅ Аккаунт создан!")
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEOcBVoHgI5xEh18LRdGsggm6P35WRj_wAC_QwAAgZQQEtJOAmxTRuvtDYE')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Профиль🧛‍♀️", "Помощь🩺", "Вывод🎁", "Реф.ссылка📰")
    bot.send_message(message.chat.id, "📋 Главное меню", reply_markup=markup)

# === Обработка inline-кнопки проверки подписки ===
@bot.callback_query_handler(func=lambda call: call.data == "check_subs")
def callback_check_subs(call):
    if check_subscription(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    else:
        bot.answer_callback_query(call.id, "🚫 Вы не подписались на все каналы!", show_alert=True)

# === Обработка сообщений ===
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = str(message.from_user.id)
    data = load_data()
    user = data.get(user_id, {})

    if message.text == "Профиль🧛‍♀️":
        ref_count = len(user.get("referrals", []))
        bot.send_message(message.chat.id, f"""🧛‍♀️ Ваш профиль:
ID: {user_id}
Имя пользователя: @{user.get("username", f"user_{user_id}")}
Язык: {user.get("language", "неизвестно")}
Рефералов: {ref_count}
Баланс: {user.get("balance", 0)} грам
""")

    elif message.text == "Помощь🩺":
        bot.send_message(message.chat.id, "Если нужна помощь — пиши сюда: @test")

    elif message.text == "Вывод🎁":
        bot.send_message(message.chat.id, "💳 Минимальный вывод — 1000 грам.\nОтправьте скрин профиля сюда: @test")

    elif message.text == "Реф.ссылка📰":
        bot.send_message(message.chat.id, f"Ваша реферальная ссылка:\nhttps://t.me/{bot_username}?start={user_id}")

    else:
        bot.send_message(message.chat.id, "🤖 Неизвестная команда. Используй кнопки меню.")

# === Запуск бота ===
if __name__ == '__main__':
    bot.polling(none_stop=True)
