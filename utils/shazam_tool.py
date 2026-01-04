try:
    from shazamio import Shazam
    SHAZAM_AVAILABLE = True
except ImportError:
    SHAZAM_AVAILABLE = False

import os

async def recognize_music(file_path):
    """
    Recognizes music from an audio file using ShazamIO.
    Returns recognition results.
    """
    if not SHAZAM_AVAILABLE:
        return {"success": False, "error": "Shazam kutubxonasi o'rnatilmagan (Rust compiler talab qilinadi)."}
    
    shazam = Shazam()
    try:
        out = await shazam.recognize_song(file_path)
        if out and 'track' in out:
            track = out['track']
            return {
                "success": True,
                "title": track.get('title'),
                "subtitle": track.get('subtitle'),
                "url": track.get('url'),
                "images": track.get('images', {}),
                "genres": track.get('genres', {}),
            }
        return {"success": False, "error": "Music not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}
