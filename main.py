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

SYSTEM_PROMPT = """انت تتكلم باللهجة اليمنية - العدنية
ردودك قصيرة، خفيفة، مضحكة شوية، وطبيعية زي البشر
لا تكرر نفس الجملة ابدا
اذا حد قال الو قله هلا واسأله ايش اخباره بطريقة مختلفة كل مرة
اذا احد سألك عن حمزة قله هذا صاحبي وصانعني
لا تقول انك ذكاء اصطناعي الا اذا سألوك
"""

@app.route('/')
def home():
    return "Bot is running!"

def ask_groq(user_id, text):
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append({"role": "user", "content": text})
    # نخلي الذاكرة اخر 10 رسايل بس
    memory[user_id] = memory[user_id][-10:]
    
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + memory[user_id],
        temperature=0.8
    )
    reply = resp.choices[0].message.content
    memory[user_id].append({"role": "assistant", "content": reply})
    return reply

# 1. هذا حق البوت نفسه - لما حد يراسل البوت
@bot.message_handler(func=lambda message: True)
def handle_normal(message):
    try:
        reply = ask_groq(message.chat.id, message.text)
        bot.reply_to(message, reply)
    except Exception as e:
        print(e)

# 2. هذا الجديد - حق حسابك الشخصي - لما حد يراسلك انت
@bot.business_message_handler(func=lambda message: True)
def handle_business(message):
    try:
        # لا ترد على رسايلك انت
        if message.from_user.id == bot.get_me().id:
            return
        chat_id = message.chat.id
        conn_id = message.business_connection_id
        reply = ask_groq(chat_id, message.text)
        # نرسل الرد باسم حسابك
        bot.send_message(chat_id, reply, business_connection_id=conn_id)
    except Exception as e:
        print("business error:", e)

@bot.business_connection_handler(func=lambda c: True)
def handle_business_conn(connection):
    print("Business connected:", connection.id)

def run_bot():
    print("Bot started...")
    bot.infinity_polling()

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
