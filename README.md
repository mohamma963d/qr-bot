# QR Telegram Bot

بوت تلغرام لإنشاء رموز QR بشكل تلقائي حسب اختيار اللون، مع إمكانية إضافة شعار PNG.

## 📦 المتطلبات
- Python 3.10+
- مكتبات:
  - python-telegram-bot
  - qrcode
  - Pillow

## 🚀 خطوات التشغيل على Railway

1. ارفع هذه الملفات إلى مستودع GitHub جديد:
   - bot.py
   - requirements.txt

2. اذهب إلى [https://railway.app](https://railway.app) وسجّل الدخول باستخدام GitHub.

3. أنشئ مشروع جديد عبر "Deploy from GitHub Repo".

4. أضف متغير البيئة التالي من لوحة التحكم:
   - `TOKEN` = توكن البوت من BotFather

5. Railway سيبدأ التثبيت والتشغيل تلقائيًا.

## ✅ ملاحظات
- تأكد أن ملف `bot.py` يحتوي في نهايته على:

```python
if __name__ == "__main__":
    main()
```

- لا تنسَ تعديل `TOKEN = os.environ.get("TOKEN")` داخل `bot.py`.
