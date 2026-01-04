import yt_dlp
import os
import uuid
from config import DOWNLOAD_DIR

async def download_media(url):
    """
    Downloads media from a given URL using yt-dlp.
    Returns a dictionary with file path and info.
    """
    file_id = str(uuid.uuid4())
    # Note: we use a generic template and fix extension after download
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    
    ydl_opts = {
        # Strategiya: 
        # FAQAT bitta fayldan iborat formatlarni tanlash (ffmpeg birlashtirishni talab qilmasligi uchun)
        'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4][height<=480]/best[ext=mp4][height<=360]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Find the actual downloaded file
            filename = ydl.prepare_filename(info)
            
            # Sometimes extension changes during download, let's verify
            actual_filename = filename
            ext = info.get("ext", "mp4")
            
            # YouTube often returns 'm4a' or 'webm' for audio, or 'mp4' for best video
            return {
                "success": True,
                "file_path": actual_filename,
                "title": info.get("title", "No Title"),
                "ext": ext,
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", ""),
            }
    except Exception as e:
        return {"success": False, "error": f"Yuklashda xatolik: {str(e)}"}

async def search_music(query):
    """
    Searches for music based on query and downloads the best audio.
    """
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    
    ydl_opts = {
        # Specifically pick a single audio file format to avoid merging
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        search_query = query if query.startswith("http") else f"ytsearch1:{query}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            
            # If it's a search result, it will have 'entries'. 
            # If it's a direct link, info is the entry itself.
            if 'entries' in info:
                entry = info['entries'][0]
            else:
                entry = info

            if entry:
                filename = ydl.prepare_filename(entry)
                
                return {
                    "success": True,
                    "file_path": filename,
                    "title": entry.get("track") or entry.get("title", "No Title"),
                    "performer": entry.get("artist") or entry.get("uploader", "Unknown Artist"),
                    "ext": entry.get("ext", "m4a"),
                    "duration": entry.get("duration", 0),
                    "thumbnail": entry.get("thumbnail", ""),
                }
            return {"success": False, "error": "Musiqa topilmadi."}
    except Exception as e:
        return {"success": False, "error": f"Qidiruvda xatolik: {str(e)}"}

def cleanup_file(file_path):
    """Removes a file from the disk."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass
