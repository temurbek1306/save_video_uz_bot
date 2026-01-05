import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import PLATFORMS, API_ID, API_HASH, BOT_TOKEN
from utils.downloader import download_media, cleanup_file, search_music
from utils.shazam_tool import recognize_music
from pyrogram import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client for large file uploads (>50MB)
pg_app = None
if API_ID and API_HASH:
    try:
        pg_app = Client(
            "save_video_bot_large_uploader",
            api_id=int(API_ID),
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            in_memory=True
        )
        logger.info("Pyrogram client initialized for large uploads.")
    except Exception as e:
        logger.error(f"Failed to initialize Pyrogram: {e}")

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
        "Shunchaki havolani (link) yuboring yoki musiqa nomini yozing."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming text messages (links or search)."""
    text = update.message.text
    if not text:
        return

    logger.info(f"Received message: {text}")

    # Check if text is a link to supported platforms
    is_supported = False
    platform_name = None
    for platform, patterns in PLATFORMS.items():
        if any(pattern in text for pattern in patterns):
            is_supported = True
            platform_name = platform
            logger.info(f"Link matched platform: {platform}")
            break
    
    if is_supported:
        # Special handling for YouTube to show buttons
        if platform_name == "youtube":
            keyboard = [
                [
                    InlineKeyboardButton("Video 🎥", callback_data=f"video|{text}"),
                    InlineKeyboardButton("Musiqa (MP3) 🎵", callback_data=f"audio|{text}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("YouTube'dan nima yuklamoqchisiz? 🤔", reply_markup=reply_markup)
            return

        status_msg = await update.message.reply_text("Yuklanmoqda... ⏳")
        result = await download_media(text)
        await process_download_result(update.message, status_msg, result)
    else:
        logger.info(f"Searching for music: {text}")
        status_msg = await update.message.reply_text("Musiqa qidirilmoqda... 🔍")
        result = await search_music(text)
        await process_download_result(update.message, status_msg, result)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles inline button clicks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("|")
    type = data[0]
    url = data[1]
    
    status_msg = await query.message.reply_text(f"{'Video' if type == 'video' else 'Musiqa'} yuklanmoqda... ⏳")
    
    if type == "audio":
        # We can use search_music or a specialized download_audio
        # For simplicity, let's use search_music as it's already optimized for audio
        result = await search_music(url)
    else:
        result = await download_media(url)
        
    await process_download_result(query.message, status_msg, result)

async def process_download_result(message, status_msg, result):
    """Sends the downloaded file to the user."""
    if result["success"]:
        try:
            # Handle Instagram carousel (multiple files)
            if result.get("is_carousel", False):
                files = result.get("files", [])
                if not files:
                    await status_msg.edit_text("❌ Carousel fayllarini yuborib bo'lmadi.")
                    return
                
                caption = f"✅ Yuklandi: {result['title']}\n\n@save_video_uz_bot"
                
                # Send as media group if multiple files
                if len(files) > 1:
                    from telegram import InputMediaPhoto, InputMediaVideo
                    media_group = []
                    
                    for idx, file_info in enumerate(files[:10]):  # Telegram limit: 10 items per media group
                        file_path = file_info["file_path"]
                        ext = file_info["ext"]
                        
                        with open(file_path, 'rb') as f:
                            if ext in ["jpg", "jpeg", "png", "webp"]:
                                media_group.append(InputMediaPhoto(
                                    media=f.read(),
                                    caption=caption if idx == 0 else None
                                ))
                            else:
                                media_group.append(InputMediaVideo(
                                    media=f.read(),
                                    caption=caption if idx == 0 else None
                                ))
                    
                    await message.reply_media_group(media=media_group)
                    
                    # Cleanup all files
                    for file_info in files:
                        cleanup_file(file_info["file_path"])
                else:
                    # Single file from carousel
                    file_info = files[0]
                    file_path = file_info["file_path"]
                    ext = file_info["ext"]
                    
                    with open(file_path, 'rb') as f:
                        if ext in ["jpg", "jpeg", "png", "webp"]:
                            await message.reply_photo(photo=f, caption=caption)
                        else:
                            await message.reply_video(video=f, caption=caption)
                    
                    cleanup_file(file_path)
                
                try:
                    await status_msg.delete()
                except:
                    pass
                return
            
            # Handle single file (original logic)
            file_path = result["file_path"]
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            logger.info(f"Processing file: {file_path} ({file_size:.2f}MB)")
            
            if file_size > 50:
                if not pg_app:
                    logger.warning(f"File too large ({file_size:.2f}MB) and API_ID/API_HASH not set.")
                    await status_msg.edit_text(
                        f"❌ Fayl juda katta ({file_size:.1f}MB).\n\n"
                        "Telegram Botlar ochiq API orqali faqat 50MB gacha fayl yubora oladi.\n"
                        "2GB gacha fayllarni yuborish uchun botni sozlash kerak (.env fayliga API_ID va API_HASH qo'shing)."
                    )
                    cleanup_file(file_path)
                    return
                
                logger.info(f"File size {file_size:.2f}MB > 50MB. Using Pyrogram for upload...")
                await status_msg.edit_text(f"Katta fayl yuklanmoqda... ({file_size:.1f}MB) 📤")
                
                # Define caption before using it
                caption = f"✅ Yuklandi: {result['title']}\n\n@save_video_uz_bot"
                
                try:
                    if not pg_app.is_connected:
                        await pg_app.start()
                    
                    if result["ext"] in ["mp3", "m4a", "webm", "ogg", "wav"]:
                        await pg_app.send_audio(
                            chat_id=message.chat.id,
                            audio=file_path,
                            caption=caption,
                            title=result.get("title"),
                            performer=result.get("performer")
                        )
                    else:
                        await pg_app.send_video(
                            chat_id=message.chat.id,
                            video=file_path,
                            caption=caption,
                            duration=int(result.get("duration", 0)),
                            supports_streaming=True
                        )
                    logger.info("Sent large file via Pyrogram")
                    try:
                        await status_msg.delete()
                    except:
                        pass
                    cleanup_file(file_path)
                    return
                except Exception as pg_e:
                    logger.error(f"Pyrogram upload error: {pg_e}")
                    await status_msg.edit_text(f"❌ Faylni yuborishda xatolik (Pyrogram): {pg_e}")
                    cleanup_file(file_path)
                    return

            caption = f"✅ Yuklandi: {result['title']}\n\n@save_video_uz_bot"
            
            with open(file_path, 'rb') as f:
                if result["ext"] in ["mp3", "m4a", "webm", "ogg", "wav"]:
                    logger.info("Sending as audio...")
                    await message.reply_audio(
                        audio=f, 
                        caption=caption,
                        title=result.get("title"),
                        performer=result.get("performer"),
                        read_timeout=120,
                        write_timeout=120,
                        connect_timeout=120
                    )
                elif result["ext"] in ["jpg", "jpeg", "png", "webp"]:
                    logger.info("Sending as photo...")
                    await message.reply_photo(
                        photo=f,
                        caption=caption
                    )
                else:
                    logger.info("Sending as video...")
                    await message.reply_video(
                        video=f, 
                        caption=caption,
                        read_timeout=120,
                        write_timeout=120,
                        connect_timeout=120
                    )
            
            logger.info("File sent successfully")
            try:
                await status_msg.delete()
            except:
                pass
            cleanup_file(file_path)
        except Exception as e:
            logger.error(f"Error sending file: {e}")
            try:
                await status_msg.edit_text(f"Xatolik yuz berdi: Faylni yuborib bo'lmadi.")
            except:
                pass
    else:
        logger.error(f"Download failed: {result['error']}")
        try:
            await status_msg.edit_text(f"Xatolik: {result['error']}")
        except:
            pass

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
