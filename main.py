import telebot
from telebot import types
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- إعداد السيرفر لـ Render ---
app = Flask('')
@app.route('/')
def home(): return "بوت قهرمان - قسم التصنيع يعمل!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# --- إعدادات البوت ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- الصلاحيات وقاعدة البيانات المؤقتة ---
ADMIN_ID = 6719487107
MANUFACTURING_STAFF = [6719487107] # أضف IDs المساعدين هنا
products_db = [] 
user_steps = {}

# --- دالة فحص الإلغاء ---
def is_cancelled(message):
    if message.text == '🔙 العودة':
        user_steps.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "🛑 تم إلغاء العملية.", reply_markup=main_menu())
        return True
    return False

# --- القوائم ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🏭 قسم التصنيع', '📦 قسم المخزون')
    markup.add('🛒 قسم المبيعات', '💰 قسم الحسابات')
    return markup

def manufacturing_home():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('➕ إضافة منتج جديد', '🔍 مراجعة منتج تم تصنيعه')
    markup.add('🔙 العودة')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "مرحباً بك في منظومة قهرمان 🏭", reply_markup=main_menu())

# ==========================================
# دخول قسم التصنيع
# ==========================================
@bot.message_handler(func=lambda m: m.text == '🏭 قسم التصنيع')
def enter_manuf(message):
    if message.from_user.id in MANUFACTURING_STAFF or message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "إدارة التصنيع - اختر إجراء:", reply_markup=manufacturing_home())
    else:
        bot.send_message(message.chat.id, "⚠️ عذراً، ليس لديك صلاحية دخول هذا القسم.")

# ==========================================
# مسار إضافة منتج جديد
# ==========================================
@bot.message_handler(func=lambda m: m.text == '➕ إضافة منتج جديد')
def start_add(message):
    user_steps[message.from_user.id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add('🔙 العودة')
    bot.send_message(message.chat.id, "📸 1. أرسل صورة المنتج:", reply_markup=markup)
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if message.content_type == 'text' and is_cancelled(message): return
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "⚠️ يرجى إرسال صورة!")
        bot.register_next_step_handler(message, get_photo)
        return
    user_steps[message.from_user.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "🏷️ 2. الصنف (مثلاً: عباية):")
    bot.register_next_step_handler(message, get_category)

def get_category(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['category'] = message.text
    bot.send_message(message.chat.id, "🔢 3. كود المنتج:")
    bot.register_next_step_handler(message, get_code)

def get_code(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['code'] = message.text
    bot.send_message(message.chat.id, "📦 4. عدد القطع:")
    bot.register_next_step_handler(message, get_qty)

def get_qty(message):
    if is_cancelled(message): return
    try:
        user_steps[message.from_user.id]['qty'] = int(message.text)
        bot.send_message(message.chat.id, "💵 5. تكلفة القماش (للقطعة):")
        bot.register_next_step_handler(message, get_fabric_cost)
    except:
        bot.send_message(message.chat.id, "⚠️ يرجى إدخال رقم!")
        bot.register_next_step_handler(message, get_qty)

def get_fabric_cost(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['c1'] = float(message.text)
    bot.send_message(message.chat.id, "💵 6. تكلفة الفازلين:")
    bot.register_next_step_handler(message, get_cost2)

def get_cost2(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['c2'] = float(message.text)
    bot.send_message(message.chat.id, "💵 7. تكلفة الأزرار:")
    bot.register_next_step_handler(message, get_cost3)

def get_cost3(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['c3'] = float(message.text)
    bot.send_message(message.chat.id, "💵 8. تكلفة الخياطة:")
    bot.register_next_step_handler(message, get_cost4)

def get_cost4(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['c4'] = float(message.text)
    bot.send_message(message.chat.id, "💵 9. تكلفة التطريز:")
    bot.register_next_step_handler(message, get_cost5)

def get_cost5(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['c5'] = float(message.text)
    bot.send_message(message.chat.id, "💵 10. تكلفة الملحقات:")
    bot.register_next_step_handler(message, get_cost6)

def get_cost6(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['c6'] = float(message.text)
    bot.send_message(message.chat.id, "💵 11. تكلفة التصوير:")
    bot.register_next_step_handler(message, get_cost7)

def get_cost7(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['c7'] = float(message.text)
    bot.send_message(message.chat.id, "📅 12. تاريخ التصنيع (مثلاً: 2026-04-27):")
    bot.register_next_step_handler(message, get_date)

def get_date(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['date'] = message.text
    bot.send_message(message.chat.id, "🏪 13. اسم المتجر:")
    bot.register_next_step_handler(message, get_store)

def get_store(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['store'] = message.text
    bot.send_message(message.chat.id, "🧵 14. خامة المادة:")
    bot.register_next_step_handler(message, get_material)

def get_material(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['material'] = message.text
    bot.send_message(message.chat.id, "💰 15. سعر بيع القطعة يدوياً (بالدينار):")
    bot.register_next_step_handler(message, calculate_and_save)

def calculate_and_save(message):
    if is_cancelled(message): return
    try:
        data = user_steps[message.from_user.id]
        sell_p = float(message.text)
        
        # الحسابات الرياضية
        unit_cost = data['c1'] + data['c2'] + data['c3'] + data['c4'] + data['c5'] + data['c6'] + data['c7']
        total_cost = unit_cost * data['qty']
        total_sell = sell_p * data['qty']
        unit_profit = sell_p - unit_cost
        total_profit = unit_profit * data['qty']
        
        data.update({
            'unit_cost': unit_cost, 'total_cost': total_cost,
            'sell_p': sell_p, 'total_sell': total_sell,
            'unit_profit': unit_profit, 'total_profit': total_profit
        })
        
        products_db.append(data)
        bot.send_message(message.chat.id, f"✅ تم حفظ المنتج بنجاح!\nكود: {data['code']}\nتكلفة القطعة: {unit_cost:.2f} د.ل", reply_markup=manufacturing_home())
        del user_steps[message.from_user.id]
    except:
        bot.send_message(message.chat.id, "⚠️ خطأ في السعر، حاول مرة أخرى.")
        bot.register_next_step_handler(message, calculate_and_save)

# ==========================================
# مراجعة المنتجات (بحث وحذف)
# ==========================================
@bot.message_handler(func=lambda m: m.text == '🔍 مراجعة منتج تم تصنيعه')
def search_start(message):
    bot.send_message(message.chat.id, "أدخل (الكود) أو (الصنف) أو (التاريخ) للبحث:")
    bot.register_next_step_handler(message, search_result)

def search_result(message):
    query = message.text
    results = [p for p in products_db if query in [p['code'], p['category'], p['date']]]
    
    if not results:
        bot.send_message(message.chat.id, "❌ لم يتم العثور على نتائج.")
        return

    for p in results:
        text = (f"📋 **بيانات المنتج:**\n"
                f"الصنف: {p['category']}\nالكود: {p['code']}\nالتاريخ: {p['date']}\n"
                f"المتجر: {p['store']}\nالخامة: {p['material']}\nالعدد: {p['qty']}\n"
                f"------------------\n"
                f"💰 تكلفة القطعة: {p['unit_cost']:.2f} د.ل\n📈 إجمالي الربح: {p['total_profit']:.2f} د.ل")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📄 عرض التفاصيل", callback_data=f"det_{p['code']}"))
        markup.add(types.InlineKeyboardButton("🗑️ حذف الصنف", callback_data=f"confdel_{p['code']}"))
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    code = call.data.split('_')[1]
    p = next((i for i in products_db if i['code'] == code), None)
    
    if call.data.startswith("det_") and p:
        details = (f"📸 **التفاصيل الكاملة لـ {p['code']}:**\n\n"
                   f"توليفة التكاليف:\n"
                   f"- قماش: {p['c1']} | فازلين: {p['c2']}\n- أزرار: {p['c3']} | خياطة: {p['c4']}\n"
                   f"- تطريز: {p['c5']} | ملحقات: {p['c6']}\n- تصوير: {p['c7']}\n"
                   f"------------------\n"
                   f"💵 سعر البيع: {p['sell_p']:.2f}\n💰 إجمالي التكلفة: {p['total_cost']:.2f}\n"
                   f"📊 ربح القطعة: {p['unit_profit']:.2f}")
        bot.send_photo(call.message.chat.id, p['photo'], caption=details)

    elif call.data.startswith("confdel_"):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("نعم، متأكد", callback_data=f"delete_{code}"),
                   types.InlineKeyboardButton("لا، إلغاء", callback_data="cancel_del"))
        bot.send_message(call.message.chat.id, f"⚠️ هل أنت متأكد من حذف كود {code}؟", reply_markup=markup)

    elif call.data.startswith("delete_"):
        global products_db
        products_db = [i for i in products_db if i['code'] != code]
        bot.edit_message_text("✅ تم حذف الصنف بنجاح.", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == '🔙 العودة')
def back(message):
    bot.send_message(message.chat.id, "الرئيسية:", reply_markup=main_menu())

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
