from flask import Flask
from threading import Thread

web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is running!"

def run():
    web_app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp
import os

BOT_TOKEN = os.getenv("bot_tokens")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send /play <song name>")

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Give a song name")
        return

    await update.message.reply_text("Searching...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'quiet': True,

        # ✅ Node.js runtime
        'js_runtimes': {
            'node': {}
        },

        # ✅ Correct format
        'remote_components': ['ejs:github'],
        
        # ✅ Helps avoid some YouTube issues
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)

    file = "song.mp3"  # ✅ correct final file

    await update.message.reply_audio(
        audio=open(file, 'rb'),
        title=info['entries'][0]['title'],
        performer=info['entries'][0]['uploader']
    )

    os.remove(file)

app = ApplicationBuilder().token(BOT_TOKEN)\
    .connect_timeout(30)\
    .read_timeout(60)\
    .write_timeout(60)\
    .build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))

keep_alive()
app.run_polling()
