import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # حط TOKEN ديالك هنا أو في environment variable

# مسار الفايل اللي يحفظو البوت
DATA_FILE = "data.txt"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\n\n"
        "📁 بعثلي text file وأنا نحفظو عندي.\n"
        "🔍 بعدها بعثلي أي كلمة وأنا نجيب ليك جميع الليني فيها.\n\n"
        "جرب دابا!"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    # تحقق أنو text file
    if not (doc.file_name.endswith(".txt") or doc.mime_type == "text/plain"):
        await update.message.reply_text("❌ بعثلي غير text file (.txt) من فضلك.")
        return

    await update.message.reply_text("⏳ كنحمل الفايل... صبر شوية.")

    file = await context.bot.get_file(doc.file_id)
    await file.download_to_drive(DATA_FILE)

    # عد عدد الليني
    with open(DATA_FILE, "r", encoding="utf-8", errors="ignore") as f:
        line_count = sum(1 for _ in f)

    await update.message.reply_text(
        f"✅ الفايل تحفظ!\n"
        f"📊 عدد الليني: {line_count:,}\n\n"
        f"دابا بعثلي أي كلمة باش نبحث فيها."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text.strip()

    if not os.path.exists(DATA_FILE):
        await update.message.reply_text("❌ ما عندي فايل محفوظ. بعثلي text file أولاً.")
        return

    await update.message.reply_text(f"🔍 كنبحث على: **{keyword}**...", parse_mode="Markdown")

    results = []
    try:
        with open(DATA_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if keyword.lower() in line.lower():
                    results.append(line.rstrip("\n"))
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")
        return

    if not results:
        await update.message.reply_text(f"😕 ما لقيت والو على '{keyword}'.")
        return

    # كتب النتائج ف resultat.txt
    result_file = "resultat.txt"
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(f"نتائج البحث على: {keyword}\n")
        f.write(f"عدد النتائج: {len(results)}\n")
        f.write("=" * 50 + "\n\n")
        for line in results:
            f.write(line + "\n")

    # بعث الفايل
    await update.message.reply_document(
        document=open(result_file, "rb"),
        filename="resultat.txt",
        caption=f"✅ لقيت **{len(results):,}** نتيجة على '{keyword}'",
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("البوت شغال! ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
