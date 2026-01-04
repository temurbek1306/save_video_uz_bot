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
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We use extract_info with download=True as yt-dlp's YouTubeDL is synchronous
            # In a real async environment, we might use run_in_executor
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            return {
                "success": True,
                "file_path": filename,
                "title": info.get("title", "No Title"),
                "ext": info.get("ext", "mp4"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail", ""),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

async def search_music(query):
    """
    Searches for music based on query and downloads the best audio.
    """
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # Search using ytsearch: prefix
        search_query = f"ytsearch1:{query}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            # ytsearch returns a list of entries
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                filename = ydl.prepare_filename(entry)
                
                return {
                    "success": True,
                    "file_path": filename,
                    "title": entry.get("track") or entry.get("title", "No Title"),
                    "performer": entry.get("artist") or entry.get("uploader", "Unknown Artist"),
                    "ext": entry.get("ext", "mp3"),
                    "duration": entry.get("duration", 0),
                    "thumbnail": entry.get("thumbnail", ""),
                }
            return {"success": False, "error": "Musiqa topilmadi."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def cleanup_file(file_path):
    """Removes a file from the disk."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass
