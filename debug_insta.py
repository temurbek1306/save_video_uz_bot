import asyncio
from utils.downloader import download_media, cleanup_file

async def debug_link():
    url = "https://www.instagram.com/reel/DRgyVeLjnrL/?igsh=aHlqbGRvbnlvMzhn"
    print(f"Debugging URL: {url}")
    result = await download_media(url)
    print(f"Result: {result}")
    if result["success"]:
        cleanup_file(result["file_path"])

if __name__ == "__main__":
    asyncio.run(debug_link())
