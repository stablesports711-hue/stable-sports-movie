import requests
from bs4 import BeautifulSoup

# টার্গেট ওয়েবসাইট
target_url = "https://cinearenafancode.pages.dev/"
proxy_base = "https://cinexcricket.com/proxy/universal.php/?url="

try:
    # ওয়েবসাইট থেকে ডেটা ফেচ করা
    response = requests.get(target_url, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # M3U প্লেলিস্ট ফাইলের হেডার লেখা
    playlist_content = "#EXTM3U\n"
    
    found_links = 0
    
    # ওয়েবসাইট থেকে m3u8 বা স্ট্রিম লিঙ্কগুলো খোঁজা (আপনার সাইটের স্ট্রাকচার অনুযায়ী ট্যাগ বদলাতে হতে পারে)
    # সাধারণত a ট্যাগ অথবা iframe/source ট্যাগ থাকতে পারে
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if 'm3u8' in href or 'index.m3u8' in href:
            title = a_tag.get_text(strip=True) or "Live Stream"
            
            # যদি লিঙ্কটি পূর্ণাঙ্গ না হয়
            if href.startswith('/'):
                # ডোমেইন যুক্ত করা যদি প্রয়োজন হয়
                pass
            
            # প্রক্সি ফরম্যাটে রূপান্তর
            final_link = f"{proxy_base}{href}"
            
            playlist_content += f"#EXTINF:-1,{title}\n{final_link}\n"
            found_links += 1

    # যদি a ট্যাগে না পেয়ে সরাসরি স্ক্রিপ্টের ভেতরে বা অন্য কোনো এলিমেন্টে থাকে
    if found_links == 0:
        # বিকল্প হিসেবে পেজে থাকা সমস্ত টেক্সট বা স্ক్రిপ্ট থেকে m3u8 লিঙ্ক খোঁজা
        import re
        m3u8_links = re.findall(r'https?://[^\s<>"]+?index\.m3u8[^\s<>"]*', response.text)
        for idx, link in enumerate(m3u8_links, start=1):
            final_link = f"{proxy_base}{link}"
            playlist_content += f"#EXTINF:-1,Channel {idx}\n{final_link}\n"
            found_links += 1

    # playlist.m3u ফাইল সেভ করা
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(playlist_content)
        
    print(f"Successfully generated playlist.m3u with {found_links} links.")

except Exception as e:
    print(f"Error occurred: {e}")
    exit(1)
