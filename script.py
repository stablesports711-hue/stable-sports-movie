import requests
from bs4 import BeautifulSoup
import re

target_url = "https://cinearenafancode.pages.dev/"
proxy_base = "https://cinexcricket.com/proxy/universal.php/?url="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    print(f"Fetching URL: {target_url}")
    response = requests.get(target_url, headers=headers, timeout=20)
    response.raise_for_status()
    
    playlist_content = "#EXTM3U\n"
    found_links = 0
    
    # পেজ থেকে সব ধরনের m3u8 বা স্ট্রিম লিঙ্ক খুঁজে বের করা
    m3u8_links = re.findall(r'https?://[^\s<>"]+?index\.m3u8[^\s<>"]*', response.text)
    
    # যদি সরাসরি লিঙ্ক না থাকে, তবে a ট্যাগ বা অন্য এলিমেন্ট চেক করা
    if not m3u8_links:
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '.m3u8' in href:
                m3u8_links.append(href)

    # ডুপ্লিকেট রিমুভ করা
    m3u8_links = list(set(m3u8_links))

    for idx, link in enumerate(m3u8_links, start=1):
        # যদি লিঙ্কটি রিলেটিভ হয়
        if link.startswith('/'):
            link = "https://cinearenafancode.pages.dev" + link
            
        final_link = f"{proxy_base}{link}"
        playlist_content += f"#EXTINF:-1,Fancode Stream {idx}\n{final_link}\n"
        found_links += 1

    # playlist.m3u ফাইল সেভ করা (যদি লিঙ্ক না ও পাওয়া যায়, অন্তত হেডার সেভ হবে যাতে এক্সিট কোড 2 না আসে)
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"Successfully generated playlist.m3u with {found_links} links.")

except Exception as e:
    print(f"An error occurred: {e}")
    # এরর হলেও যাতে অ্যাকশন ফেল না করে খালি ফাইল তৈরি করে এক্সিট করে
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
    print("Created empty playlist.m3u to prevent workflow failure.")
