import telebot
from telebot import types
import sqlite3
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- إعداد السيرفر الوهمي (لإبقاء Render حياً) ---
app = Flask('')
@app.route('/')
def home(): return "قهرمان بوت يعمل بنجاح!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت وقاعدة البيانات ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
DB_NAME = "kahraman_factory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # جدول المنتجات
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, code TEXT, color TEXT, quantity INTEGER, cost REAL, price REAL)''')
    # جدول المبيعات
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY, product_id INTEGER, qty INTEGER, total_price REAL, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- المتغيرات المؤقتة للجلسة ---
user_steps = {}
ADMIN_ID = 6719487107 # تأكد من أن هذا هو رقمك

# --- القوائم الرئيسية ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🏭 قسم التصنيع', '📦 قسم المخزون')
    markup.add('🛒 قسم المبيعات', '💰 قسم الحسابات')
    markup.add('📊 التقارير')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "مرحباً بك في منظومة قهرمان (النسخة الاحترافية) 🚀\nالبيانات الآن تُحفظ في قاعدة بيانات دائمة.", 
                     reply_markup=main_menu())

# --- قسم المخزون ---
@bot.message_handler(func=lambda m: m.text == '📦 قسم المخزون')
def view_stock(message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, code, color, quantity FROM products")
    items = c.fetchall()
    conn.close()
    
    if not items:
        bot.send_message(message.chat.id, "المخزن فارغ حالياً.")
    else:
        res = "📦 حالة المخزن الحالية:\n\n"
        for i in items:
            res += f"🔹 {i[0]} ({i[1]}) | اللون: {i[2]} | الكمية: {i[3]}\n"
        bot.send_message(message.chat.id, res)

# --- قسم التصنيع (إضافة منتج جديد) ---
@bot.message_handler(func=lambda m: m.text == '🏭 قسم التصنيع')
def start_production(message):
    bot.send_message(message.chat.id, "أرسل اسم المنتج الجديد (مثال: عباية نص كم):")
    user_steps[message.from_user.id] = {'step': 'name'}

@bot.message_handler(func=lambda m: user_steps.get(m.from_user.id, {}).get('step') == 'name')
def get_name(message):
    user_steps[message.from_user.id].update({'name': message.text, 'step': 'qty'})
    bot.send_message(message.chat.id, f"كم الكمية التي تم تصنيعها من {message.text}؟")

@bot.message_handler(func=lambda m: user_steps.get(m.from_user.id, {}).get('step') == 'qty')
def get_qty(message):
    if not message.text.isdigit():
        return bot.send_message(message.chat.id, "الرجاء إدخال رقم صحيح.")
    user_steps[message.from_user.id].update({'qty': int(message.text), 'step': 'price'})
    bot.send_message(message.chat.id, "سعر البيع المقترح للقطعة الواحدة؟")

@bot.message_handler(func=lambda m: user_steps.get(m.from_user.id, {}).get('step') == 'price')
def save_product(message):
    try:
        data = user_steps[message.from_user.id]
        price = float(message.text)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                  (data['name'], data['qty'], price))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "✅ تم إضافة الإنتاج للمخزن بنجاح!", reply_markup=main_menu())
        del user_steps[message.from_user.id]
    except:
        bot.send_message(message.chat.id, "حدث خطأ، تأكد من إدخال السعر بالأرقام.")

# --- تشغيل البوت ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
