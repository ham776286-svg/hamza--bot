import os
import threading
from flask import Flask
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(func=lambda message: True)
def reply(message):
    text = message.text.lower() if message.text else ""
    if "هلا" in text or "سلام" in text or "hello" in text or "hi" in text:
        bot.reply_to(message, "هلا والله نورت")
    else:
        bot.reply_to(message, "هلا والله نورت، كيف اقدر اخدمك؟")

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
