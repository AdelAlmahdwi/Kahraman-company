import telebot
from telebot import types
from datetime import datetime
import os
from flask import Flask
from threading import Thread

# --- إعداد السيرفر لضمان عمله على Render ---
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
MANUFACTURING_STAFF = [6719487107] 
products_db = [] 
user_steps = {}

# --- دالة فحص الإلغاء ---
def is_cancelled(message):
    if message.text == '🔙 العودة':
        user_steps.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "🛑 تم إلغاء العملية.", reply_markup=main_menu())
        return True
    return False

# --- القوائم الرئيسية ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🏭 قسم التصنيع', '📦 قسم المخزون')
    markup.add('🛒 قسم المبيعات', '💰 قسم الحسابات', '📊 التقارير')
    return markup

def manufacturing_home():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('➕ إضافة منتج جديد', '🔍 مراجعة منتج تم تصنيعه')
    markup.add('🔙 العودة')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "مرحباً بك في منظومة قهرمان المحدثة 🏭", reply_markup=main_menu())

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
# مسار إضافة منتج جديد (تعبئة يدوية)
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
    bot.send_message(message.chat.id, "🏷️ 2. الصنف:")
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
        bot.send_message(message.chat.id, "💵 5. تكلفة القماش:")
        bot.register_next_step_handler(message, get_cost1)
    except:
        bot.send_message(message.chat.id, "⚠️ يرجى إدخال رقم صحيح.")
        bot.register_next_step_handler(message, get_qty)

def get_cost1(message):
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
    bot.send_message(message.chat.id, "📅 12. تاريخ التصنيع (مثال: 2026-04-27):")
    bot.register_next_step_handler(message, get_date)

def get_date(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['date'] = message.text
    bot.send_message(message.chat.id, "🏪 13. اسم المتجر:")
    bot.register_next_step_handler(message, get_store)

def get_store(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['store'] = message.text
    bot.send_message(message.chat.id, "🧵 14. خامة المادة المصنعة:")
    bot.register_next_step_handler(message, get_material)

def get_material(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['material'] = message.text
    bot.send_message(message.chat.id, "💰 15. سعر بيع القطعة يدوياً (دينار):")
    bot.register_next_step_handler(message, final_calc)

def final_calc(message):
    if is_cancelled(message): return
    try:
        sell_p = float(message.text)
        d = user_steps[message.from_user.id]
        
        # الحسابات التلقائية
        unit_cost = d['c1'] + d['c2'] + d['c3'] + d['c4'] + d['c5'] + d['c6'] + d['c7']
        total_cost = unit_cost * d['qty']
        total_sell = sell_p * d['qty']
        unit_profit = sell_p - unit_cost
        total_profit = unit_profit * d['qty']
        
        d.update({
            'sell_p': sell_p, 'unit_cost': unit_cost, 'total_cost': total_cost,
            'total_sell': total_sell, 'unit_profit': unit_profit, 'total_profit': total_profit
        })
        
        products_db.append(d)
        bot.send_message(message.chat.id, f"✅ تم الحفظ! تكلفة القطعة: {unit_cost:.2f} د.ل", reply_markup=manufacturing_home())
        del user_steps[message.from_user.id]
    except:
        bot.send_message(message.chat.id, "⚠️ أدخل سعراً صحيحاً.")
        bot.register_next_step_handler(message, final_calc)

# ==========================================
# مراجعة المنتجات (بحث، تفاصيل، حذف)
# ==========================================
@bot.message_handler(func=lambda m: m.text == '🔍 مراجعة منتج تم تصنيعه')
def search_start(message):
    bot.send_message(message.chat.id, "🔍 ابحث بـ (الكود أو الصنف أو التاريخ):")
    bot.register_next_step_handler(message, search_results)

def search_results(message):
    q = message.text
    res = [p for p in products_db if q in [p['code'], p['category'], p['date']]]
    if not res: return bot.send_message(message.chat.id, "❌ لم يتم العثور على نتائج.")
    
    for p in res:
        txt = (f"📋 **بيانات المنتج:**\nالصنف: {p['category']}\nالكود: {p['code']}\nالتاريخ: {p['date']}\n"
               f"المتجر: {p['store']}\nالخامة: {p['material']}\nالعدد: {p['qty']}\n"
               f"------------------\n💰 تكلفة القطعة: {p['unit_cost']:.2f} د.ل\n📈 إجمالي الربح: {p['total_profit']:.2f} د.ل")
        
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("📄 عرض التفاصيل", callback_data=f"det_{p['code']}"))
        mk.add(types.InlineKeyboardButton("🗑️ حذف الصنف", callback_data=f"askdel_{p['code']}"))
        bot.send_message(message.chat.id, txt, reply_markup=mk, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    code = call.data.split('_')[1]
    p = next((i for i in products_db if i['code'] == code), None)
    
    if call.data.startswith("det_") and p:
        full_info = (f"📸 **تفاصيل شاملة لـ {p['code']}:**\n"
                     f"- قماش: {p['c1']} | فازلين: {p['c2']} | أزرار: {p['c3']}\n"
                     f"- خياطة: {p['c4']} | تطريز: {p['c5']} | ملحقات: {p['c6']}\n"
                     f"- تصوير: {p['c7']}\n------------------\n"
                     f"💵 سعر البيع: {p['sell_p']:.2f}\n💰 إجمالي التكلفة: {p['total_cost']:.2f}\n"
                     f"📊 إجمالي المبيعات: {p['total_sell']:.2f}\n📉 ربح القطعة: {p['unit_profit']:.2f}")
        bot.send_photo(call.message.chat.id, p['photo'], caption=full_info)

    elif call.data.startswith("askdel_"):
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("✅ نعم متأكد", callback_data=f"confirmdel_{code}"),
               types.InlineKeyboardButton("❌ لا، إلغاء", callback_data="cancel_del"))
        bot.send_message(call.message.chat.id, f"⚠️ هل أنت متأكد من حذف {code}؟", reply_markup=mk)

    elif call.data.startswith("confirmdel_"):
        global products_db
        products_db = [i for i in products_db if i['code'] != code]
        bot.edit_message_text("✅ تم حذف الصنف نهائياً.", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == '🔙 العودة')
def go_back(message):
    bot.send_message(message.chat.id, "الرئيسية:", reply_markup=main_menu())

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
