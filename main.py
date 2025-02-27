from keep_alive import keep_alive
import asyncio
import subprocess
import os
import yt_dlp
from datetime import datetime
import pytz
from telethon import TelegramClient, events
from telethon.tl.functions.phone import CreateGroupCallRequest
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream

# 🔹 Bot Credentials
API_ID = 19906987  # Replace with your API ID
API_HASH = "4353d7341a3e6017f9d9026b897703c0"  # Replace with your API HASH
BOT_TOKEN = "7431379275:AAFP-2Khf9McBWmRIQdNIo3mnslX9YCFUrY"  # Replace with your bot token

# 🔹 تشغيل البوت مع Telethon
app = TelegramClient("media_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# 🔹 إعداد PyTgCalls
tgcalls = PyTgCalls(app)
tgcalls.start()

# 📌 إنشاء بث صوتي
async def create_voice_chat(chat_id):
    try:
        await app(CreateGroupCallRequest(chat_id=chat_id))
        return True
    except Exception as e:
        await app.send_message(chat_id, f"❌ **خطأ أثناء إنشاء البث: {str(e)}**")
        print(f"Error creating voice chat: {e}")
        return False

# 📌 تشغيل ملف صوتي أو فيديو في البث المباشر
@app.on(events.NewMessage(pattern=r"^/play"))
async def play_media(event):
    if not event.is_reply or not (event.reply_to_msg.audio or event.reply_to_msg.video or event.reply_to_msg.voice):
        await event.reply("🎵 **يجب الرد على ملف صوتي أو فيديو لتشغيله!**")
        return

    media_file = await event.reply_to_msg.download_media()
    
    chat_id = event.chat_id
    if not await create_voice_chat(chat_id):
        await event.reply("❌ **تعذر إنشاء بث صوتي! تأكد من صلاحيات البوت.**")
        return

    output_file = "live_stream.mp3"
    process = subprocess.run(["ffmpeg", "-i", media_file, "-vn", "-acodec", "mp3", output_file, "-y"], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        await event.reply(f"❌ **خطأ أثناء تحويل الملف: {process.stderr.decode()}**")
        return

    try:
        await tgcalls.join_group_call(chat_id, InputAudioStream(output_file))
        await event.reply("🎶 **تم بدء البث المباشر بنجاح!**")
    except Exception as e:
        await event.reply(f"❌ **خطأ أثناء البث: {str(e)}**")
        print(f"Streaming error: {e}")

# 📌 إيقاف التشغيل مؤقتًا
@app.on(events.NewMessage(pattern=r"^/pause"))
async def pause_media(event):
    try:
        await tgcalls.pause_stream(event.chat_id)
        await event.reply("⏸ **تم إيقاف البث مؤقتًا!**")
    except Exception as e:
        await event.reply(f"❌ **خطأ: {str(e)}**")

# 📌 استئناف التشغيل
@app.on(events.NewMessage(pattern=r"^/resume"))
async def resume_media(event):
    try:
        await tgcalls.resume_stream(event.chat_id)
        await event.reply("▶ **تم استئناف البث!**")
    except Exception as e:
        await event.reply(f"❌ **خطأ: {str(e)}**")

# 📌 إيقاف التشغيل نهائيًا
@app.on(events.NewMessage(pattern=r"^/stop"))
async def stop_media(event):
    try:
        await tgcalls.leave_group_call(event.chat_id)
        await event.reply("🛑 **تم إيقاف البث نهائيًا!**")
        if os.path.exists("live_stream.mp3"):
            os.remove("live_stream.mp3")
    except Exception as e:
        await event.reply(f"❌ **خطأ: {str(e)}**")

# 📌 عرض الوقت الحالي بتوقيت القاهرة ومكة
@app.on(events.NewMessage(pattern=r"^/time"))
async def send_time(event):
    cairo_tz = pytz.timezone("Africa/Cairo")
    mecca_tz = pytz.timezone("Asia/Riyadh")
    cairo_time = datetime.now(cairo_tz).strftime("%Y-%m-%d %H:%M:%S")
    mecca_time = datetime.now(mecca_tz).strftime("%Y-%m-%d %H:%M:%S")
    await event.reply(f"🕰 **الوقت الحالي:**\n"
                      f"🇪🇬 القاهرة: `{cairo_time}`\n"
                      f"🇸🇦 مكة المكرمة: `{mecca_time}`")

# 📌 تحميل الفيديوهات من يوتيوب
@app.on(events.NewMessage(pattern=r"^/yt"))
async def download_youtube(event):
    args = event.raw_text.split(maxsplit=1)
    if len(args) < 2:
        await event.reply("📽 **يرجى إرسال رابط فيديو من يوتيوب!**")
        return

    url = args[1]
    ydl_opts = {"format": "bestaudio/best", "outtmpl": "downloads/%(title)s.%(ext)s", "noplaylist": True}
    
    await event.reply("⏳ **جاري تحميل الفيديو...**")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
    
    await event.reply(file=file_path, caption="✅ **تم تحميل الفيديو بنجاح!**")
    if os.path.exists(file_path):
        os.remove(file_path)

# 📌 بدء بث صوتي فارغ
@app.on(events.NewMessage(pattern=r"^/startvc"))
async def start_voice_chat(event):
    if await create_voice_chat(event.chat_id):
        await event.reply("🎤 **تم بدء البث الصوتي بنجاح!**")
    else:
        await event.reply("❌ **تعذر بدء البث الصوتي! تأكد من صلاحيات البوت.**")

# 🔹 تشغيل Flask لإبقاء البوت نشطًا
keep_alive()

# 🔹 تشغيل البوت
print("Bot is running...")
app.run_loop()
