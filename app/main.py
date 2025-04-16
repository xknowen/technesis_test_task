import os
import telebot

from telebot import types
from dotenv import load_dotenv

from parser import file_parser, price_parser

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

DIR = os.getenv('UPLOAD_DIR')
os.makedirs(DIR, exist_ok=True)


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📂 Загрузить файл"))
    markup.add(types.KeyboardButton("💰 Показать среднюю цену"))
    bot.send_message(message.chat.id, "Привет! Выбери действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "📂 Загрузить файл")
def ask_file(message):
    bot.send_message(message.chat.id, "Пожалуйста, прикрепи Excel-файл (.xlsx)")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    bot.send_message(message.chat.id, f"Файл получен: {message.document.file_name}")

    try:
        response = file_parser(bot=bot, message=message)
        bot.send_message(message.chat.id, response, parse_mode="HTML")
        bot.send_message(message.chat.id, "✅ Данные сохранены в базу данных!")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при обработке файла: {e}")


@bot.message_handler(func=lambda message: message.text == "💰 Показать среднюю цену")
def handle_parse_prices(message):
    response = price_parser()
    if response:
        bot.send_message(message.chat.id, response, parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, f"❌ Не удалось загрузить данные из БД")


if __name__ == "__main__":
    bot.infinity_polling(timeout=30, long_polling_timeout=25)
