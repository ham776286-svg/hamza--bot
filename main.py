import os
import threading
from flask import Flask
import telebot
from groq import Groq

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
client = Groq(api_key=GROQ_KEY)

memory = {}

SYSTEM_PROMPT = """انت بوت اسمه بوت حمزة، صديق يمني مرح، تتكلم باللهجة اليمنية - العدني.
ردودك قصيرة، خفيفة، مضحكة شوية، وطبيعية زي البشر.
لا تكرر نفس الجملة ابدا.
اذا حد قال الو قله هلا واسأله ايش اخباره بطريقة مختلفة كل مرة.
اذا حد سألك عن حمزة قله هذا صاحبي وصانعني.
لا تقول انك ذكاء اصطناعي الا اذا سألوك.
"""

@app.route('/')
def home():
    return "الروبوت يعمل!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "هلا والله نورت، انا بوت حمزة الجديد، صرت اذكى الحين 😎 اسألني اي شي")

@bot.message_handler(func=lambda m: True)
def chat(message):
    if not message.text:
        return
    text = message.text
    key = f"{message.chat.id}_{message.from_user.id}"
    if key not in memory:
        memory[key] = []
    memory[key].append({"role": "user", "content": text})
    memory[key] = memory[key][-10:]
    try:
        resp = client.chat.completions.create(
            openai/gpt-oss-20b
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + memory[key],
            temperature=0.8,
            max_tokens=300
        )
        reply = resp.choices[0].message.content
        memory[key].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "ايوه معك، بس النت عندي ثقيل شوية، عيد كلامك 😅")

def run_bot():
    print("Bot is running - smart mode")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
