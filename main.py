import asyncio
import subprocess
from pyrogram import Client, filters
import os
import pytz
from datetime import datetime
import yt_dlp
from flask import Flask
from threading import Thread

# 🔹 بيانات البوت
API_ID = int(os.getenv("API_ID", "19906987"))  # استبدل بالقيم الخاصة بك
API_HASH = os.getenv("API_HASH", "4353d7341a3e6017f9d9026b897703c0")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7431379275:AAFP-2Khf9McBWmRIQdNIo3mnslX9YCFUrY")

# 🔹 تشغيل البوت
app = Client("media_bot",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN)

# 📌 إرسال الوقت بتوقيت القاهرة ومكة
@app.on_message(filters.command("time"))
async def send_time(_, message):
    cairo_time = datetime.now(pytz.timezone("Africa/Cairo")).strftime("%Y-%m-%d %H:%M:%S")
    mecca_time = datetime.now(pytz.timezone("Asia/Riyadh")).strftime("%Y-%m-%d %H:%M:%S")
    await message.reply(f"🕒 **التوقيت الحالي:**\n🇪🇬 القاهرة: `{cairo_time}`\n🇸🇦 مكة المكرمة: `{mecca_time}`")

# 📌 تشغيل أي ملف صوتي أو فيديو عند الرد عليه
@app.on_message(filters.command("play"))
async def play_media(_, message):
    if not message.reply_to_message or not (message.reply_to_message.audio or message.reply_to_message.video or message.reply_to_message.voice):
        await message.reply("🎵 **يجب الرد على ملف صوتي أو فيديو لتشغيله!**")
        return

    media_file = await message.reply_to_message.download()
    
    # تشغيل الصوت أو الفيديو باستخدام FFmpeg
    process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", media_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    await message.reply("🎶 **تم تشغيل الملف بنجاح!**")

# 📌 إيقاف التشغيل مؤقتًا
@app.on_message(filters.command("pause"))
async def pause_media(_, message):
    subprocess.run(["pkill", "-STOP", "ffplay"])
    await message.reply("⏸ **تم إيقاف التشغيل مؤقتًا!**")

# 📌 استئناف التشغيل
@app.on_message(filters.command("resume"))
async def resume_media(_, message):
    subprocess.run(["pkill", "-CONT", "ffplay"])
    await message.reply("▶ **تم استئناف التشغيل!**")

# 📌 إيقاف التشغيل نهائيًا
@app.on_message(filters.command("stop"))
async def stop_media(_, message):
    subprocess.run(["pkill", "ffplay"])
    await message.reply("🛑 **تم إيقاف التشغيل نهائيًا!**")

# 📌 تحميل فيديو من يوتيوب
@app.on_message(filters.command("download"))
async def download_video(_, message):
    if len(message.command) < 2:
        await message.reply("❌ **يرجى إرسال رابط فيديو يوتيوب بعد الأمر!**")
        return
    
    url = message.command[1]
    await message.reply("🔄 **جاري تحميل الفيديو...**")
    
    options = {
        "format": "best",
        "outtmpl": "downloaded_video.mp4"
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    await message.reply_video("downloaded_video.mp4", caption="📥 **تم تحميل الفيديو!**")
    os.remove("downloaded_video.mp4")

# 🔹 تشغيل Flask لإبقاء البوت نشطًا
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

def run():
    flask_app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# 🔹 تشغيل البوت
app.run()
