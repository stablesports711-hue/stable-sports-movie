import os
import re
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

TARGET_URL = "https://socolivei.tv/"
M3U_FILE = "playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": TARGET_URL
}

def clean_title(raw_title):
    try:
        # ভিয়েতনামিজ থেকে ইংরেজি অনুবাদ
        translated = GoogleTranslator(source='auto', target='en').translate(raw_title)
        
        # 'VS' টিম ফিল্টার করা
        match = re.search(r'([A-Za-z0-9\s]+)\s+(?:VS|v/s|vs|-)\s+([A-Za-z0-9\s]+)', translated, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            team1 = re.sub(r'^(Prediction|Match|Review|Analysis)\s+', '', team1, flags=re.IGNORECASE)
            return f"{team1} VS {team2}"
        
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return raw_title

def get_actual_stream_url(page_url):
    try:
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            m3u8_matches = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', res.text)
            if m3u8_matches:
                return m3u8_matches[0]
            
            soup = BeautifulSoup(res.text, 'html.parser')
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                if src:
                    if not src.startswith('http'):
                        src = 'https:' + src if src.startswith('//') else TARGET_URL.rstrip('/') + '/' + src.lstrip('/')
                    iframe_res = requests.get(src, headers=HEADERS, timeout=5)
                    iframe_m3u8 = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', iframe_res.text)
                    if iframe_m3u8:
                        return iframe_m3u8[0]
    except Exception as e:
        print(f"Stream extract error: {e}")
    return None

def fetch_live_matches():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching site: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    processed = set()

    for link in soup.find_all("a", href=True):
        href = link['href']
        raw_title = link.get_text(strip=True)

        if "vs" in raw_title.lower() or "v/s" in raw_title.lower() or " - " in raw_title:
            full_page_url = href if href.startswith("http") else f"{TARGET_URL.rstrip('/')}/{href.lstrip('/')}"
            
            if full_page_url in processed:
                continue
            processed.add(full_page_url)

            clean_name = clean_title(raw_title)
            stream_url = get_actual_stream_url(full_page_url)

            if stream_url:
                results.append({"title": clean_name, "stream_url": stream_url})

    return results

def generate_m3u(matches):
    m3u_content = "#EXTM3U\n#EXT-X-VERSION:3\n\n"

    if not matches:
        m3u_content += '#EXTINF:-1 tvg-name="No Stream Available", No Active Live Stream Found\nhttps://0.0.0.0/offline.m3u8\n'
    else:
        for idx, match in enumerate(matches, 1):
            title = match['title']
            url = match['stream_url']
            m3u_content += f'#EXTINF:-1 tvg-id="{idx}" tvg-name="{title}", {title}\n{url}\n\n'

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

if __name__ == "__main__":
    live_data = fetch_live_matches()
    generate_m3u(live_data)
