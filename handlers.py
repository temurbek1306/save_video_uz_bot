import os
import logging
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from config import PLATFORMS
from utils.downloader import download_media, cleanup_file
from utils.shazam_tool import recognize_music

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "Xush kelibsiz! 👋\n\n"
        "Men orqali quyidagi ijtimoiy tarmoqlardan media yuklab olishingiz mumkin:\n"
        "• Instagram (Post, Stories, Reels)\n"
        "• YouTube (Video, Shorts, Audio)\n"
        "• TikTok (Suv belgisiz)\n"
        "• Pinterest (Video, Rasm)\n"
        "• Likee (Suv belgisiz)\n"
        "• Shazam (Musiqa tanish)\n\n"
        "Shunchaki havolani (link) yuboring yoki musiqa faylini yuboring."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming text messages (links)."""
    text = update.message.text
    if not text:
        return

    logger.info(f"Received message: {text}")

    # Check if text is a link to supported platforms
    is_supported = False
    for platform, patterns in PLATFORMS.items():
        if any(pattern in text for pattern in patterns):
            is_supported = True
            logger.info(f"Link matched platform: {platform}")
            break
    
    if is_supported:
        status_msg = await update.message.reply_text("Yuklanmoqda... ⏳")
        result = await download_media(text)
        
        if result["success"]:
            try:
                file_path = result["file_path"]
                logger.info(f"Download success: {file_path}")
                caption = f"✅ Yuklandi: {result['title']}\n\n@save_video_uz_bot"
                
                with open(file_path, 'rb') as f:
                    # Treat mp3, m4a, webm, etc., as audio if extracted as such
                    if result["ext"] in ["mp3", "m4a", "webm", "ogg", "wav"]:
                        await update.message.reply_audio(
                            audio=f, 
                            caption=caption,
                            title=result.get("title"),
                            performer=result.get("performer")
                        )
                    else:
                        await update.message.reply_video(video=f, caption=caption)
                
                await status_msg.delete()
                cleanup_file(file_path)
            except Exception as e:
                logger.error(f"Error sending file: {e}")
                await status_msg.edit_text(f"Xatolik yuz berdi: Faylni yuborib bo'lmadi. (Fayl juda katta bo'lishi mumkin)")
        else:
            logger.error(f"Download failed: {result['error']}")
            await status_msg.edit_text(f"Xatolik: {result['error']}")
    else:
        logger.info(f"Searching for music: {text}")
        status_msg = await update.message.reply_text("Musiqa qidirilmoqda... 🔍")
        
        from utils.downloader import search_music
        result = await search_music(text)
        
        if result["success"]:
            try:
                file_path = result["file_path"]
                caption = f"✅ Topildi: {result['title']}\n\n@save_video_uz_bot"
                
                with open(file_path, 'rb') as f:
                    await update.message.reply_audio(
                        audio=f, 
                        caption=caption,
                        title=result.get("title"),
                        performer=result.get("performer")
                    )
                
                await status_msg.delete()
                cleanup_file(file_path)
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
                await status_msg.edit_text(f"Xatolik yuz berdi: Musiqani yuborib bo'lmadi.")
        else:
            await status_msg.edit_text(f"Afsuski, hech narsa topilmadi.")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles audio messages for music recognition."""
    audio = update.message.audio or update.message.voice
    if not audio:
        return

    status_msg = await update.message.reply_text("Musiqa tanilmoqda... 🎧")
    
    # Download file for recognition
    file_id = audio.file_id
    new_file = await context.bot.get_file(file_id)
    file_path = f"downloads/{file_id}.ogg"
    await new_file.download_to_drive(file_path)
    
    result = await recognize_music(file_path)
    
    if result["success"]:
        text = f"🎵 Topildi!\n\n**Nomi:** {result['title']}\n**Ijrochi:** {result['subtitle']}"
        if result['url']:
            text += f"\n\n[Shazam'da ko'rish]({result['url']})"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Afsuski, musiqani tanib bo'lmadi.")
    
    cleanup_file(file_path)
    await status_msg.delete()
