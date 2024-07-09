import os  
# مكتبة للوصول إلى وظائف النظام مثل التعامل مع الملفات والمجلدات
from rembg import remove  
# مكتبة لإزالة الخلفيات من الصور تلقائيًا باستخدام الذكاء الاصطناعي
from PIL import Image  
# مكتبة لتحرير الصور وفتحها وحفظها ومعالجتها
from telegram import Update  
# مكتبة لتحديثات التلغرام وإدارة الرسائل والمستخدمين
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters  
# مكتبة لبناء تطبيقات التلغرام، وإدارة الأوامر والرسائل والفلاتر

# توكن البوت الخاص بالتلغرام للمصادقة والوصول
TOKEN = "yor_token"

# تعريف دالة لمعالجة أمر /help التي ترسل رسالة ترحيبية
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="مرحباً بك في بوت الذكاء الإصطناعي لحذف الخلفية من الصورة , للبدأ إضغط على  /start")

# تعريف دالة لمعالجة أمر /start التي تطلب من المستخدم إرسال الصورة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="من فضلك قم بإرسال الصورة التي تريد أن تحذف الخلفية منها")

# دالة لمعالجة الصورة بإزالة الخلفية
async def process_image(photo_name: str):
    # تقسيم اسم الملف والامتداد
    name, _ = os.path.splitext(photo_name)
    # تعريف مسار الإخراج للصورة المعالجة
    output_photo_path = f'./processed/{name}.png'
    # فتح الصورة المدخلة من المجلد المؤقت
    input = Image.open(f'./temp/{photo_name}')
    # إزالة الخلفية باستخدام دالة remove من مكتبة rembg
    output = remove(input)
    # حفظ الصورة المعالجة في مسار الإخراج
    output.save(output_photo_path)
    # إزالة الصورة الأصلية من المجلد المؤقت
    os.remove(f'./temp/{photo_name}')
    # إرجاع مسار الصورة المعالجة
    return output_photo_path

# دالة لمعالجة الرسائل الواردة التي تحتوي على صور
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التحقق مما إذا كانت الرسالة تحتوي على صورة
    if filters.PHOTO.check_update(update):
        # الحصول على معرّف الملف ومعرّف الملف الفريد للصورة
        file_id = update.message.photo[-1].file_id
        unique_file_id = update.message.photo[-1].file_unique_id
        # تعريف اسم الصورة باستخدام معرّف الملف الفريد وامتداد .jpg
        photo_name = f"{unique_file_id}.jpg"
    # التحقق مما إذا كانت الرسالة تحتوي على وثيقة صورة
    elif filters.Document.IMAGE:
        # الحصول على معرّف الملف ومعرّف الملف الفريد للوثيقة
        file_id = update.message.document.file_id
        # الحصول على امتداد الملف للوثيقة
        _, f_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        # تعريف اسم الصورة باستخدام معرّف الملف الفريد وامتداد الملف الأصلي
        photo_name = f'{unique_file_id}.{f_ext}'

    # تنزيل الصورة إلى المجلد المؤقت
    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive(custom_path=f'./temp/{photo_name}')
    # إرسال رسالة للمستخدم تشير إلى أن المعالجة جارية
    await context.bot.send_message(chat_id=update.effective_chat.id, text=" جار ِ المعالجة ...")
    # معالجة الصورة لإزالة الخلفية
    processed_image = await process_image(photo_name)
    # إرسال الصورة المعالجة مرة أخرى للمستخدم
    await context.bot.send_document(chat_id=update.effective_chat.id, document=processed_image)
    # إزالة الصورة المعالجة من الخادم
    os.remove(processed_image)

# الدالة الرئيسية لبدء تشغيل البوت
if __name__ == '__main__':
    # إنشاء مثيل للتطبيق باستخدام توكن البوت
    application = ApplicationBuilder().token(TOKEN).build()

    # إنشاء معالجات الأوامر لأوامر /help و /start
    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    # إنشاء معالج الرسائل للصور ووثائق الصور
    message_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_message)

    # تسجيل معالجات الأوامر مع التطبيق
    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(message_handler)

    # تشغيل البوت باستخدام الاستطلاع الطويل
    application.run_polling()


