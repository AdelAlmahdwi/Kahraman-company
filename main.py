import telebot
from telebot import types
from datetime import datetime

# --- إعدادات التوكن ---
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

# --- نظام الصلاحيات ---
ADMIN_ID = 6719487107
MGR_PRODUCTION = [6719487107]
MGR_STOCK = [6719487107]
# أضف هنا IDs موظفي المبيعات لكل متجر
STAFF_STORE_1 = [] 
STAFF_STORE_2 = []

# --- قواعد البيانات المؤقتة ---
products_db = [] 
orders_db = []   
user_steps = {}  

# --- ثوابت حالات الطلبيات ---
STATUS_WAITING_PREP = "🟡 في انتظار التجهيز"
STATUS_WAITING_PICKUP = "🚛 في انتظار الإرسال"
STATUS_OUT_OF_STOCK = "🔴 انتهت من المخزون"
STATUS_IN_DELIVERY = "🛣️ قيد التوصيل"
STATUS_DELIVERED_UNPAID = "💰 تم التوصيل ولم تحصل"
STATUS_RETURNING = "🔄 قيد الإرجاع"
STATUS_ARCHIVED = "✅ الأرشيف"

# --- دالة فحص الإلغاء (المفتاح السحري) ---
def is_cancelled(message):
    if message.text == '🔙 العودة' or message.text == 'إلغاء':
        user_steps.pop(message.from_user.id, None)
        bot.send_message(message.chat.id, "🛑 تم إلغاء العملية والعودة للقائمة.", 
                         reply_markup=main_menu(message.from_user.id))
        return True
    return False

# --- القائمة الرئيسية ---
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if uid in MGR_PRODUCTION or uid == ADMIN_ID:
        markup.add('🏭 قسم التصنيع')
    markup.add('📦 قسم المخزون', '🛒 قسم المبيعات')
    markup.add('💰 قسم الحسابات', '📊 التقارير')
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, "مرحباً بك في منظومة قهرمان المتكاملة 🏭📦🛒", 
                     reply_markup=main_menu(uid))

# ==========================================
# 1. قسم التصنيع (مع ميزة الإلغاء)
# ==========================================
@bot.message_handler(func=lambda m: m.text == '🏭 قسم التصنيع')
def manufacturing_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('➕ إضافة منتج جديد', '🔍 مراجعة منتج تم تصنيعه', '🔙 العودة')
    bot.send_message(message.chat.id, "إدارة التصنيع:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '➕ إضافة منتج جديد')
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
    # التحقق من النص قبل نوع المحتوى للسماح بالعودة
    if message.content_type == 'text' and is_cancelled(message): return
    
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "⚠️ يرجى إرسال صورة أو اضغط عودة.")
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
    try:
        user_steps[message.from_user.id]['qty'] = int(message.text)
        bot.send_message(message.chat.id, "🛠️ خامة المادة المصنعة:")
        bot.register_next_step_handler(message, get_prod_price)
    except:
        bot.send_message(message.chat.id, "⚠️ يرجى إدخال رقم صحيح!")
        bot.register_next_step_handler(message, get_prod_material)

def get_prod_price(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['material'] = message.text
    bot.send_message(message.chat.id, "💵 سعر بيع القطعة (دينار):")
    bot.register_next_step_handler(message, get_prod_store)

def get_prod_store(message):
    if is_cancelled(message): return
    try:
        user_steps[message.from_user.id]['sell_price'] = float(message.text)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add('متجر 1', 'متجر 2', '🔙 العودة')
        bot.send_message(message.chat.id, "🏪 توجيه المنتج إلى:", reply_markup=markup)
        bot.register_next_step_handler(message, save_product_final)
    except:
        bot.send_message(message.chat.id, "⚠️ يرجى إدخال سعر صحيح!")
        bot.register_next_step_handler(message, get_prod_store)

def save_product_final(message):
    if is_cancelled(message): return
    data = user_steps[message.from_user.id]
    data.update({
        'store': message.text,
        'sold': 0, 'returned': 0, 'delivery': 0, 'returning': 0,
        'date': datetime.now().strftime("%Y-%m-%d")
    })
    products_db.append(data)
    bot.send_message(message.chat.id, "✅ تم حفظ المنتج وتوزيعه للمخازن.", reply_markup=main_menu(message.from_user.id))

# ==========================================
# 2. قسم المخزون
# ==========================================
@bot.message_handler(func=lambda m: m.text == '📦 قسم المخزون')
def stock_menu(message):
    uid = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if uid == ADMIN_ID or uid in MGR_STOCK:
        markup.add('المخزن الرئيسي', 'مخزن متجر 1', 'مخزن متجر 2')
    elif uid in STAFF_STORE_1: markup.add('مخزن متجر 1')
    markup.add('🔙 العودة')
    bot.send_message(message.chat.id, "اختر المخزن:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['المخزن الرئيسي', 'مخزن متجر 1', 'مخزن متجر 2'])
def view_stock(message):
    store_name = message.text.replace('مخزن ', '')
    items = products_db if store_name == 'المخزن الرئيسي' else [p for p in products_db if p['store'] == store_name]
    
    if not items:
        bot.send_message(message.chat.id, "📦 المخزن فارغ حالياً.")
        return

    for p in items:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"📄 تفاصيل الكود: {p['code']}", callback_data=f"stk_{p['code']}"))
        bot.send_photo(message.chat.id, p['photo'], caption=f"📸 كود: {p['code']}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stk_'))
def show_stock_details(call):
    code = call.data.split('_')[1]
    p = next((i for i in products_db if i['code'] == code), None)
    if p:
        text = (f"📊 **بيانات المنتج ({p['code']}):**\n\n"
                f"3️⃣ الاسم: {p['category']}\n4️⃣ المقاس: {p['size']}\n5️⃣ سعر البيع: {p['sell_price']} د.ل\n"
                f"6️⃣ الخامة: {p['material']}\n7️⃣ اللون: {p['color']}\n8️⃣ المتوفر: {p['qty']}\n"
                f"9️⃣ المباع: {p['sold']}\n🔟 المرجوع: {p['returned']}\n"
                f"1️⃣1️⃣ قيد التوصيل: {p['delivery']}\n1️⃣2️⃣ قيد الإرجاع: {p['returning']}")
        bot.send_message(call.message.chat.id, text)

# ==========================================
# 3. قسم المبيعات
# ==========================================
@bot.message_handler(func=lambda m: m.text == '🛒 قسم المبيعات')
def sales_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('➕ إضافة طلب جديد', '📦 مراجعة حالة الطلبيات', '🔍 البحث عن طلبية', '🔙 العودة')
    bot.send_message(message.chat.id, "إدارة المبيعات:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '➕ إضافة طلب جديد')
def new_order_start(message):
    user_steps[message.from_user.id] = {
        'order_id': len(orders_db) + 1,
        'status': STATUS_WAITING_PREP,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add('🔙 العودة')
    bot.send_message(message.chat.id, "📸 أرسل سكرين الحجز:", reply_markup=markup)
    bot.register_next_step_handler(message, get_order_screenshot)

def get_order_screenshot(message):
    if message.content_type == 'text' and is_cancelled(message): return
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "⚠️ يرجى إرسال صورة السكرين أو عودة.")
        bot.register_next_step_handler(message, get_order_screenshot)
        return
    user_steps[message.from_user.id]['screenshot'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "👤 اسم الزبون:")
    bot.register_next_step_handler(message, get_order_cust)

def get_order_cust(message):
    if is_cancelled(message): return
    user_steps[message.from_user.id]['customer'] = message.text
    bot.send_message(message.chat.id, "🔢 كود القطعة:")
    bot.register_next_step_handler(message, get_order_item)

def get_order_item(message):
    if is_cancelled(message): return
    code = message.text
    item = next((p for p in products_db if p['code'] == code), None)
    if item:
        user_steps[message.from_user.id]['item_code'] = code
        user_steps[message.from_user.id]['price'] = item['sell_price']
        user_steps[message.from_user.id]['store'] = item['store']
        
        # تحديث فوري للمخزن
        item['qty'] -= 1
        item['delivery'] += 1
        
        orders_db.append(user_steps[message.from_user.id])
        bot.send_message(message.chat.id, f"✅ تم الحجز بنجاح. رقم الطلبية: {user_steps[message.from_user.id]['order_id']}")
        
        if item['qty'] <= 3:
            bot.send_message(ADMIN_ID, f"⚠️ تنبيه: المنتج {code} قارب على النفاد! المتبقي: {item['qty']}")
    else:
        bot.send_message(message.chat.id, "⚠️ الكود غير موجود! حاول مرة أخرى أو اضغط عودة.")
        bot.register_next_step_handler(message, get_order_item)

@bot.message_handler(func=lambda m: m.text == '🔙 العودة')
def back_home(message):
    bot.send_message(message.chat.id, "الرئيسية:", reply_markup=main_menu(message.from_user.id))

bot.polling(none_stop=True)
