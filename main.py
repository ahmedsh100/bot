from keep_alive import keep_alive
import asyncio
import subprocess
from pyrogram import Client, filters
import os
import datetime
import pytz
import yt_dlp

# 🔹 Bot Credentials (يجب إضافتها كمتغيرات بيئية عند الرفع إلى Koyeb)
API_ID = int(os.getenv("19906987"))
API_HASH = os.getenv("4353d7341a3e6017f9d9026b897703c0")
BOT_TOKEN = os.getenv("7431379275:AAFP-2Khf9McBWmRIQdNIo3mnslX9YCFUrY")

# 🔹 تشغيل البوت
app = Client("media_bot",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN)

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


# 📌 إظهار الوقت الحالي بتوقيت القاهرة ومكة
@app.on_message(filters.command("time"))
async def get_time(_, message):
    cairo_tz = pytz.timezone("Africa/Cairo")
    mecca_tz = pytz.timezone("Asia/Riyadh")

    cairo_time = datetime.datetime.now(cairo_tz).strftime("%Y-%m-%d %H:%M:%S")
    mecca_time = datetime.datetime.now(mecca_tz).strftime("%Y-%m-%d %H:%M:%S")

    await message.reply(f"🕒 **الوقت الحالي:**\n"
                        f"🇪🇬 القاهرة: `{cairo_time}`\n"
                        f"🇸🇦 مكة المكرمة: `{mecca_time}`")


# 📌 تحميل الفيديوهات من YouTube
@app.on_message(filters.command("download"))
async def download_video(_, message):
    if len(message.command) < 2:
        await message.reply("🔗 **يرجى إرسال رابط فيديو YouTube بعد الأمر!**")
        return

    url = message.command[1]
    
    ydl_opts = {
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
    }

    await message.reply("⏳ **جارٍ تحميل الفيديو...**")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info)

    await message.reply_document(video_path, caption="🎥 **تم تحميل الفيديو بنجاح!**")


# 🔹 تشغيل Flask لإبقاء البوت نشطًا
keep_alive()

# 🔹 تشغيل البوت
app.run()
