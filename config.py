import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8507784193:AAEj2tMBQniB9wJ5cjOY-Sq6bKLZs-PLEy4")

# Paths
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Supported platforms patterns
PLATFORMS = {
    "instagram": ["instagram.com/reels/", "instagram.com/reel/", "instagram.com/p/", "instagram.com/stories/", "instagr.am/"],
    "youtube": ["youtube.com/", "youtu.be/"],
    "tiktok": ["tiktok.com/"],
    "pinterest": ["pinterest.com/pin/", "pin.it/"],
    "likee": ["likee.video/"],
}
