import os
import re
import requests
from bs4 import BeautifulSoup

# Target URL
TARGET_URL = "https://socolivei.tv/"
M3U_FILE = "playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": TARGET_URL
}

def fetch_live_matches():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching website: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    matches = []

    # 1. HTML Element Scrape (Page links and match titles)
    links = soup.find_all("a", href=True)
    for link in links:
        href = link['href']
        title = link.get_text(strip=True)
        
        # 'VS' বা ম্যাচের ফরম্যাট অনুযায়ী টাইটেল ফিল্টার করা
        if "vs" in title.lower() or "v/s" in title.lower() or " - " in title:
            full_url = href if href.startswith("http") else f"{TARGET_URL.rstrip('/')}/{href.lstrip('/')}"
            matches.append({"title": title, "link": full_url})

    # 2. Extract m3u8 / Direct Stream Links using Regex
    stream_urls = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', response.text)
    
    # Process extracted streams into match details
    results = []
    if stream_urls:
        for idx, stream in enumerate(set(stream_urls), 1):
            results.append({
                "title": f"Live Match Stream {idx}",
                "stream_url": stream
            })
    else:
        # If no direct m3u8 found on main page, map page links
        for m in matches:
            results.append({
                "title": m["title"],
                "stream_url": m["link"]
            })

    return results

def generate_m3u(matches):
    m3u_content = "#EXTM3U\n"
    m3u_content += "#EXT-X-VERSION:3\n\n"

    if not matches:
        # Fallback element if no matches currently active
        m3u_content += "#EXTINF:-1 tvg-name=\"No Matches Available\", No Live Matches Right Now\n"
        m3u_content += "https://0.0.0.0/offline.m3u8\n"
    else:
        for idx, match in enumerate(matches, 1):
            title = match['title']
            url = match['stream_url']
            m3u_content += f'#EXTINF:-1 tvg-id="{idx}" tvg-name="{title}", {title}\n'
            m3u_content += f'{url}\n\n'

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Successfully updated {M3U_FILE} with {len(matches)} streams.")

if __name__ == "__main__":
    live_data = fetch_live_matches()
    generate_m3u(live_data)
