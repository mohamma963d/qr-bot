import logging
import qrcode
import time
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from PIL import Image
import qrcode.constants

# التوكن
TOKEN = "8111253594:AAHMfy7IZEMem8_G8QRhMDY9jF5FXZ9JUo8"

# حالات المحادثة
SELECT_COLOR, GET_LOGO, GET_TEXT = range(3)

# خيارات الألوان
COLOR_OPTIONS = {
    "رمادي": ("#444444", "white"),
    "أسود": ("black", "white"),
}

# تهيئة السجل
logging.basicConfig(level=logging.INFO)
open("user_logs.txt", "a", encoding="utf-8").close()

def log_user_message(update):
    user = update.effective_user
    text = update.callback_query.data if update.callback_query else update.message.text
    with open("user_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"{user.username or user.id}: {text}\n")

def start(update: Update, context: CallbackContext):
    log_user_message(update)
    keyboard = [[InlineKeyboardButton(color, callback_data=color)] for color in COLOR_OPTIONS]
    update.message.reply_text(
        "👋 أهلاً بك!\n\n"
        "1. اختر لون رمز QR:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_COLOR

def select_color(update: Update, context: CallbackContext):
    log_user_message(update)
    color = update.callback_query.data
    context.user_data['color'] = color
    # نطلب شعار أو تخطي
    keyboard = [[
        InlineKeyboardButton("🖼️ أرسل شعار PNG", callback_data="send_logo"),
        InlineKeyboardButton("⏭️ تخطي الشعار", callback_data="skip_logo")
    ]]
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        f"✅ اخترت اللون «{color}». الآن:\n\n"
        "2. أرسل صورة PNG للشعار أو اضغط تخطي:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GET_LOGO

def get_logo(update: Update, context: CallbackContext):
    log_user_message(update)
    query = update.callback_query
    choice = query.data
    query.answer()

    if choice == "skip_logo":
        context.user_data['logo_path'] = None
        # اطلب النص
        query.edit_message_text("✅ تم تخطي الشعار.\n\n3. أرسل الآن النص أو الرابط:")
        return GET_TEXT

    # المستخدم يريد إرسال شعار: نوّجه لإرسال صورة
    query.edit_message_text("📤 أرسل الآن صورة PNG للشعار:")
    return GET_LOGO

def handle_logo_file(update: Update, context: CallbackContext):
    log_user_message(update)
    # نتلقى صورة
    photo = update.message.photo[-1].get_file()
    logo_path = f"logo_{update.effective_user.id}.png"
    photo.download(logo_path)
    context.user_data['logo_path'] = logo_path
    # اطلب النص
    update.message.reply_text("✅ استلمت الشعار.\n\n3. أرسل الآن النص أو الرابط:")
    return GET_TEXT

def get_text(update: Update, context: CallbackContext):
    
    log_user_message(update)
    text = update.message.text
    color = context.user_data.get('color', 'أسود')
    fill, back = COLOR_OPTIONS.get(color, ("black","white"))
    logo_path = context.user_data.get('logo_path')
    


    # توليد QR
    qr = qrcode.QRCode(
    version=None,          # ← اسمح للمكتبة باختيار أنسب حجم تلقائي
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=4,
    
    )          

    try:
        qr.add_data(text)
        qr.make(fit=True)       # ← اجعل المكتبة تختار الحجم المناسب تلقائياً
    except Exception as e:
        update.message.reply_text(f"❌ لا يمكن توليد الرمز لان عدد الاحرف تجاوز المسموح به:\n"
                                  
                                  "✅ ارسال النص مرة اخرى:\n"
                                  )
        return GET_TEXT
    
    
    img = qr.make_image(fill_color=fill, back_color=back).convert("RGB")

    # دمج الشعار إذا موجود
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path)
        size = img.size[0] // 4
        logo = logo.resize((size, size), Image.LANCZOS)
        pos = ((img.size[0]-size)//2, (img.size[1]-size)//2)
        img.paste(logo, pos, mask=logo if logo.mode=='RGBA' else None)
        os.remove(logo_path)

    # إرسال الصورة
    path = "qr.png"
    img.save(path)
    update.message.reply_photo(open(path, "rb"), caption="✅ هذا هو رمز QR الخاص بك.")

    # نبدأ دورة جديدة مباشرةً
    keyboard = [[InlineKeyboardButton(color, callback_data=color)] for color in COLOR_OPTIONS]
    update.message.reply_text(
        "🔁 تريد رمزًا جديدًا؟\n1. اختر لون الرمز:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_COLOR

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ تم إلغاء العملية. أرسل /start للبدء من جديد.")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_COLOR: [CallbackQueryHandler(select_color)],
            GET_LOGO: [
                CallbackQueryHandler(get_logo, pattern="^(send_logo|skip_logo)$"),
                MessageHandler(Filters.photo, handle_logo_file)
            ],
            GET_TEXT: [MessageHandler(Filters.text & ~Filters.command, get_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    dp.add_handler(conv)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
