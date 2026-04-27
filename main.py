import telebot
from telebot import types
import sqlite3
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- إعداد السيرفر الوهمي لـ Render ---
app = Flask('')
@app.route('/')
def home(): return "كهرمان بوت يعمل بنجاح!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت وقاعدة البيانات ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
DB_NAME = "ghahraman_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # جدول المنتجات (بكل تفاصيل كود أمس)
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, photo TEXT, code TEXT, 
                  color TEXT, size TEXT, qty INTEGER, material TEXT, sell_price REAL, store TEXT,
                  sold INTEGER DEFAULT 0, returned INTEGER DEFAULT 0, delivery INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

# --- نظام الصلاحيات ---
ADMIN_ID = 6719487107
user_steps = {}

# --- دالة فحص الإلغاء ---
def is_cancelled(message):
    if message.text in ['🔙 العودة', 'إلغاء']:
        user_steps.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "🛑 تم إلغاء العملية.", reply_markup=main_menu(message.from_user.id))
        return True
    return False

# --- القائمة الرئيسية ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🏭 قسم التصنيع', '📦 قسم المخزون')
    markup.add('🛒 قسم المبيعات', '💰 قسم الحسابات')
    markup.add('📊 التقارير')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "مرحباً بك في منظومة قهرمان (النسخة الدائمة) 🏭📦", 
                     reply_markup=main_menu(message.from_user.id))

# ==========================================
# 1. قسم التصنيع (نفس تسلسل أمس تماماً)
# ==========================================
@bot.message_handler(func=lambda m: m.text == '🏭 قسم التصنيع')
def add_prod_start(message):
    user_steps[message.from_user.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add('🔙 العودة')
    bot.send_message(message.chat.id, "🏷️ الصنف (اسم المنتج):", reply_markup=markup)
    bot.register_next_step_handler(message, get_prod_photo)

def get_prod_photo(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['category'] = message.text
    bot.send_message(message.chat.id, "📸 أرسل صورة المنتج:")
    bot.register_next_step_handler(message, get_prod_code)

def get_prod_code(message):
    if message.content_type == 'text' and is_cancelled(message): return
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "⚠️ يرجى إرسال صورة!")
        bot.register_next_step_handler(message, get_prod_code)
        return
    user_steps[message.from_user.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "🔢 كود المنتج:")
    bot.register_next_step_handler(message, get_prod_color)

def get_prod_color(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['code'] = message.text
    bot.send_message(message.chat.id, "🎨 لون المنتج:")
    bot.register_next_step_handler(message, get_prod_size)

def get_prod_size(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['color'] = message.text
    bot.send_message(message.chat.id, "📏 مقاس المنتج:")
    bot.register_next_step_handler(message, get_prod_qty)

def get_prod_qty(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['size'] = message.text
    bot.send_message(message.chat.id, "📦 عدد القطع:")
    bot.register_next_step_handler(message, get_prod_material)

def get_prod_material(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['qty'] = int(message.text)
    bot.send_message(message.chat.id, "🛠️ خامة المادة:")
    bot.register_next_step_handler(message, get_prod_price)

def get_prod_price(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['material'] = message.text
    bot.send_message(message.chat.id, "💵 سعر البيع:")
    bot.register_next_step_handler(message, get_prod_store)

def get_prod_store(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['price'] = float(message.text)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add('متجر 1', 'متجر 2', '🔙 العودة')
    bot.send_message(message.chat.id, "🏪 توجيه إلى:", reply_markup=markup)
    bot.register_next_step_handler(message, save_final)

def save_final(message):
    if is_cancelled(message): return
    d = user_steps[message.from_user.id]
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO products (category, photo, code, color, size, qty, material, sell_price, store) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (d['category'], d['photo'], d['code'], d['color'], d['size'], d['qty'], d['material'], d['price'], message.text))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, "✅ تم حفظ المنتج في قاعدة البيانات بنجاح!", reply_markup=main_menu(message.from_user.id))
    del user_steps[message.from_user.id]

# ==========================================
# 2. قسم المخزون (استدعاء من قاعدة البيانات)
# ==========================================
@bot.message_handler(func=lambda m: m.text == '📦 قسم المخزون')
def view_stock(message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT photo, code, category, qty FROM products")
    items = c.fetchall()
    conn.close()
    if not items:
        bot.send_message(message.chat.id, "المخزن فارغ.")
    for item in items:
        bot.send_photo(message.chat.id, item[0], caption=f"📸 كود: {item[1]}\nالصنف: {item[2]}\nالمتوفر: {item[3]}")

# --- التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
