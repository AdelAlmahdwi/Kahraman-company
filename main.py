import telebot
from telebot import types
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- إعداد سيرفر وهمي لإبقاء البوت حياً على Render ---
app = Flask('')

@app.route('/')
def home():
    return "قهرمان بوت يعمل بنجاح!"

def run():
    # Render يعطي المنفذ تلقائياً عبر متغير البيئة PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
# سيقوم البوت بجلب التوكن من Environment Variables في Render
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- نظام الصلاحيات والقواعد (نفس المنطق السابق) ---
ADMIN_ID = 6719487107
MGR_PRODUCTION = [6719487107]
products_db = [] 
orders_db = []
user_steps = {}

# دالة فحص الإلغاء
def is_cancelled(message):
    if message.text in ['🔙 العودة', 'إلغاء']:
        user_steps.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "🛑 تم إلغاء العملية.", reply_markup=main_menu(message.from_user.id))
        return True
    return False

# القائمة الرئيسية
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if uid in MGR_PRODUCTION or uid == ADMIN_ID:
        markup.add('🏭 قسم التصنيع')
    markup.add('📦 قسم المخزون', '🛒 قسم المبيعات')
    markup.add('💰 قسم الحسابات', '📊 التقارير')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "مرحباً بك في منظومة قهرمان على سيرفر Render 🚀", 
                     reply_markup=main_menu(message.from_user.id))

# --- (هنا تضع باقي دوال التصنيع والمخزن والمبيعات التي كتبناها سابقاً) ---
# ملاحظة: الكود طويل جداً لذا اختصرت الدوال المتكررة، تأكد من دمجها هنا.

# --- تشغيل البوت والسيرفر معاً ---
if __name__ == "__main__":
    keep_alive()  # تشغيل سيرفر الويب في الخلفية
    print("البوت بدأ العمل...")
    bot.infinity_polling() # نظام بولينج لا يتوقف
