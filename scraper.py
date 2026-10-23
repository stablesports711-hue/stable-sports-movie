import re
import requests

# সোর্স সাইট এবং প্রক্সি প্রিক্সURL
SOURCE_URL = "https://cinearenafancode.pages.dev/"
PROXY_PREFIX = "https://cinexcricket.com/proxy/universal.php/?url="
OUTPUT_FILE = "playlist.m3u"

def fetch_and_generate_playlist():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(SOURCE_URL, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Error fetching source: {e}")
        return

    # m3u8 লিঙ্ক এবং সম্ভাব্য টাইটেল খুঁজে বের করার Regex নিয়ম
    # প্রয়োজনীয়তা অনুযায়ী এই রুল পরিবর্তন করা যেতে পারে
    m3u8_links = re.findall(r'https?://[^\s\'"]+\.m3u8', html_content)
    
    # ডুপ্লিকেট লিঙ্ক সরানো
    unique_links = list(set(m3u8_links))

    playlist_content = "#EXTM3U\n"
    
    for count, original_link in enumerate(unique_links, start=1):
        # প্রক্সি ফরম্যাটে পরিবর্তন
        proxied_link = f"{PROXY_PREFIX}{original_link}"
        
        # M3U ফরম্যাট সংযোজন
        playlist_content += f'#EXTINF:-1 tvg-id="fancode_{count}" group-title="Sports", FanCode Stream {count}\n'
        playlist_content += f'{proxied_link}\n\n'

    # ফাইল সেভ করা
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"Successfully generated {OUTPUT_FILE} with {len(unique_links)} streams.")

if __name__ == "__main__":
    fetch_and_generate_playlist()
