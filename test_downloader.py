import asyncio
from utils.downloader import download_media, cleanup_file

async def test_download():
    # Test with a known stable YouTube link
    test_url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    print(f"Testing download for: {test_url}")
    
    result = await download_media(test_url)
    
    if result["success"]:
        print(f"Success! File saved at: {result['file_path']}")
        print(f"Title: {result['title']}")
        cleanup_file(result['file_path'])
        print("Cleanup successful.")
    else:
        print(f"Failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_download())
