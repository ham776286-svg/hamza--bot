import os
import threading
import telebot
from flask import Flask
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def ask_groq(text):
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are Hamza, a helpful friendly assistant. Reply in the same language as the user, in Yemeni dialect if they speak Yemeni."},
            {"role": "user", "content": text},
        ],
        temperature=0.8,
        max_tokens=800,
    )
    return resp.choices[0].message.content

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "هلا والله 🔥 انا حمزة، ارسل لي اي شي وبرد عليك.")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    try:
        if not message.text:
            return
        reply = ask_groq(message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "صار عندي خطأ بسيط، جرب مرة ثانية.")

@bot.business_message_handler(func=lambda m: True)
def handle_business(message):
    try:
        if not message.text:
            return
        reply = ask_groq(message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Business Error: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    while True:
        try:
            print("Bot started...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"BOT DIED, retry in 10s: {e}")
            import time
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    run_bot()
{"role": "system", "content": "You are Hamza, a helpful friendly assistant..."},
