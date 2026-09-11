import json, uuid, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8412811751:AAE92Q3TM4uWZi-bwyOBqutO2jzD4-IsOH0"
GPLINKS_API = "1825da784476d2c6eed6db3ba46ab3b2e76dd677"
BOT_USERNAME = "my_earning_store_bot"

DB_FILE = "files.json"

def load_db():
    try:
        with open(DB_FILE, 'r') as f: return json.load(f)
    except: return {}
def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    if context.args:
        code = context.args[0]
        if code in db:
            d = db[code]
            if d['type'] == 'document': await update.message.reply_document(d['id'], caption=f"Join @{BOT_USERNAME}")
            elif d['type'] == 'photo': await update.message.reply_photo(d['id'])
            elif d['type'] == 'video': await update.message.reply_video(d['id'])
        else:
            await update.message.reply_text("❌ Link expire!")
    else:
        await update.message.reply_text("Hi! File ke liye admin ka earning link use karo.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id, file_type = None, None
    if update.message.document: file_id, file_type = update.message.document.file_id, 'document'
    elif update.message.photo: file_id, file_type = update.message.photo[-1].file_id, 'photo'
    elif update.message.video: file_id, file_type = update.message.video.file_id, 'video'
    if not file_id: return

    code = uuid.uuid4().hex[:8]
    db = load_db(); db[code] = {"id": file_id, "type": file_type}; save_db(db)

    long_url = f"https://t.me/{BOT_USERNAME}?start={code}"
    try:
        api_url = f"https://api.gplinks.com/st?api={GPLINKS_API}&url={long_url}&format=text"
        short_url = requests.get(api_url, timeout=15).text.strip()
        if "http" not in short_url: short_url = long_url
    except:
        short_url = long_url

    await update.message.reply_text(f"✅ DONE!\n\n💰 Earning Link (Share this):\n{short_url}\n\nDirect Link:\n{long_url}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, handle_file))
    print("Bot Running @my_earning_store_bot")
    app.run_polling()

if __name__ == "__main__":
    main()
