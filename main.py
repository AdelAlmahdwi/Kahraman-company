import telebot
from telebot import types
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- إعداد السيرفر لـ Render ---
app = Flask('')
@app.route('/')
def home(): return "بوت قهرمان - قسم التصنيع يعمل بدقة!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- قاعدة البيانات والصلاحيات ---
ADMIN_ID = 6719487107
MANUFACTURING_STAFF = [6719487107] 
products_db = [] 
user_data = {} # لتخزين الخطوات لكل مستخدم

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🏭 قسم التصنيع', '📦 قسم المخزون')
    markup.add('🛒 قسم المبيعات', '💰 قسم الحسابات')
    return markup

def manufacturing_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('➕ إضافة منتج جديد', '🔍 مراجعة منتج تم تصنيعه')
    markup.add('🔙 العودة للقائمة الرئيسية')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحباً بك في منظومة قهرمان 🏭", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == '🏭 قسم التصنيع')
def manufacturing_section(message):
    if message.from_user.id in MANUFACTURING_STAFF or message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "إدارة التصني Cervices:", reply_markup=manufacturing_menu())
    else:
        bot.send_message(message.chat.id, "⚠️ لا تملك صلاحية.")

# --- بداية عملية إضافة منتج (خطوة بخطوة) ---
@bot.message_handler(func=lambda m: m.text == '➕ إضافة منتج جديد')
def start_adding(message):
    user_data[message.from_user.id] = {}
    bot.send_message(message.chat.id, "1️⃣ أرسل صورة المنتج:")
    bot.register_next_step_handler(message, process_photo)

def process_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "⚠️ يرجى إرسال صورة!")
        bot.register_next_step_handler(message, process_photo)
        return
    user_data[message.from_user.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "2️⃣ أدخل (الصنف):")
    bot.register_next_step_handler(message, process_category)

def process_category(message):
    user_data[message.from_user.id]['category'] = message.text
    bot.send_message(message.chat.id, "3️⃣ أدخل (كود المنتج):")
    bot.register_next_step_handler(message, process_code)

def process_code(message):
    user_data[message.from_user.id]['code'] = message.text
    bot.send_message(message.chat.id, "4️⃣ أدخل (عدد القطع):")
    bot.register_next_step_handler(message, process_qty)

def process_qty(message):
    user_data[message.from_user.id]['qty'] = int(message.text)
    bot.send_message(message.chat.id, "5️⃣ تكلفة القماش:")
    bot.register_next_step_handler(message, process_c1)

def process_c1(message):
    user_data[message.from_user.id]['c1'] = float(message.text)
    bot.send_message(message.chat.id, "6️⃣ تكلفة الفازليين:")
    bot.register_next_step_handler(message, process_c2)

def process_c2(message):
    user_data[message.from_user.id]['c2'] = float(message.text)
    bot.send_message(message.chat.id, "7️⃣ تكلفة الأزرار:")
    bot.register_next_step_handler(message, process_c3)

def process_c3(message):
    user_data[message.from_user.id]['c3'] = float(message.text)
    bot.send_message(message.chat.id, "8️⃣ تكلفة الخياطة:")
    bot.register_next_step_handler(message, process_c4)

def process_c4(message):
    user_data[message.from_user.id]['c4'] = float(message.text)
    bot.send_message(message.chat.id, "9️⃣ تكلفة التطريز:")
    bot.register_next_step_handler(message, process_c5)

def process_c5(message):
    user_data[message.from_user.id]['c5'] = float(message.text)
    bot.send_message(message.chat.id, "🔟 تكلفة الملحقات:")
    bot.register_next_step_handler(message, process_c6)

def process_c6(message):
    user_data[message.from_user.id]['c6'] = float(message.text)
    bot.send_message(message.chat.id, "1️⃣1️⃣ تكلفة التصوير:")
    bot.register_next_step_handler(message, process_c7)

def process_c7(message):
    user_data[message.from_user.id]['c7'] = float(message.text)
    bot.send_message(message.chat.id, "1️⃣2️⃣ تاريخ التصنيع:")
    bot.register_next_step_handler(message, process_date)

def process_date(message):
    user_data[message.from_user.id]['date'] = message.text
    bot.send_message(message.chat.id, "1️⃣3️⃣ اسم المتجر:")
    bot.register_next_step_handler(message, process_store)

def process_store(message):
    user_data[message.from_user.id]['store'] = message.text
    bot.send_message(message.chat.id, "1️⃣4️⃣ خامة المادة المصنعة:")
    bot.register_next_step_handler(message, process_material)

def process_material(message):
    user_data[message.from_user.id]['material'] = message.text
    bot.send_message(message.chat.id, "💰 أخيراً، أدخل سعر بيع القطعة يدوياً:")
    bot.register_next_step_handler(message, process_final_save)

def process_final_save(message):
    try:
        sell_price = float(message.text)
        data = user_data[message.from_user.id]
        
        # --- الحسابات التلقائية ---
        unit_cost = data['c1'] + data['c2'] + data['c3'] + data['c4'] + data['c5'] + data['c6'] + data['c7']
        total_cost = unit_cost * data['qty']
        total_sell = sell_price * data['qty']
        unit_profit = sell_price - unit_cost
        total_profit = unit_profit * data['qty']

        product = {
            **data,
            'sell_price': sell_price,
            'unit_cost': unit_cost,
            'total_cost': total_cost,
            'total_sell': total_sell,
            'unit_profit': unit_profit,
            'total_profit': total_profit
        }
        
        products_db.append(product)
        bot.send_message(message.chat.id, "✅ تم حفظ المنتج وإجراء كافة الحسابات بنجاح!", reply_markup=manufacturing_menu())
    except Exception as e:
        bot.send_message(message.chat.id, "❌ حدث خطأ في البيانات، حاول مرة أخرى.")

# --- مراجعة المنتجات والبحث ---
@bot.message_handler(func=lambda m: m.text == '🔍 مراجعة منتج تم تصنيعه')
def search_product(message):
    bot.send_message(message.chat.id, "🔍 ابحث بـ (الكود أو التاريخ أو الصنف):")
    bot.register_next_step_handler(message, show_search_results)

def show_search_results(message):
    query = message.text
    results = [p for p in products_db if query in [p['code'], p['date'], p['category']]]
    
    if not results:
        bot.send_message(message.chat.id, "❌ لم يتم العثور على نتائج.")
        return

    for p in results:
        summary = (f"📋 **بيانات المنتج:**\n"
                   f"الصنف: {p['category']}\n"
                   f"الكود: {p['code']}\n"
                   f"التاريخ: {p['date']}\n"
                   f"المتجر: {p['store']}\n"
                   f"الخامة: {p['material']}\n"
                   f"العدد: {p['qty']}\n"
                   f"------------------\n"
                   f"💰 تكلفة القطعة: {p['unit_cost']:.2f} د.ل\n"
                   f"📈 إجمالي الربح: {p['total_profit']:.2f} د.ل")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📄 عرض باقي التفاصيل", callback_data=f"details_{p['code']}"))
        markup.add(types.InlineKeyboardButton("🗑️ حذف الصنف", callback_data=f"delete_{p['code']}"))
        bot.send_message(message.chat.id, summary, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    code = call.data.split('_')[1]
    product = next((p for p in products_db if p['code'] == code), None)

    if call.data.startswith("details_") and product:
        details = (f"📸 **بيانات المنتج الكاملة:**\n"
                   f"الصنف: {product['category']}\nالكود: {product['code']}\nالعدد: {product['qty']}\n"
                   f"قماش: {product['c1']} | فازلين: {product['c2']} | أزرار: {product['c3']}\n"
                   f"خياطة: {product['c4']} | تطريز: {product['c5']} | ملحقات: {product['c6']}\n"
                   f"تصوير: {product['c7']}\nالتاريخ: {product['date']}\nالمتجر: {product['store']}\n"
                   f"الخامة: {product['material']}\n"
                   f"------------------\n"
                   f"💰 تكلفة القطعة: {product['unit_cost']:.2f}\n"
                   f"💵 إجمالي التكلفة: {product['total_cost']:.2f}\n"
                   f"🏷️ سعر بيع القطعة: {product['sell_price']:.2f}\n"
                   f"📊 سعر بيع إجمالي القطع: {product['total_sell']:.2f}\n"
                   f"📉 الربح للقطعة: {product['unit_profit']:.2f}\n"
                   f"📈 إجمالي الربح: {product['total_profit']:.2f}")
        bot.send_photo(call.message.chat.id, product['photo'], caption=details)

    elif call.data.startswith("delete_"):
        global products_db
        products_db = [p for p in products_db if p['code'] != code]
        bot.answer_callback_query(call.id, "✅ تم الحذف")
        bot.edit_message_text("❌ تم حذف هذا المنتج من السجلات.", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == '🔙 العودة للقائمة الرئيسية')
def back_home(message):
    bot.send_message(message.chat.id, "القائمة الرئيسية:", reply_markup=main_menu())

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
