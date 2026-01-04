import asyncio
from utils.downloader import search_music, cleanup_file

async def debug_search():
    query = "Kaptiva"
    print(f"Searching for: {query}")
    result = await search_music(query)
    print(f"Result: {result}")
    if result["success"]:
        cleanup_file(result["file_path"])

if __name__ == "__main__":
    asyncio.run(debug_search())
