import os
import re
import requests
from bs4 import BeautifulSoup
from googletrans import Translator

TARGET_URL = "https://socolivei.tv/"
M3U_FILE = "playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": TARGET_URL
}

translator = Translator()

def clean_title(raw_title):
    """
    টাইটেল থেকে অতিরিক্ত লেখা মুছে ফেলে শুধু Team1 VS Team2 অংশ বের করে এবং ইংরেজিতে অনুবাদ করে।
    """
    try:
        # ভিয়েতনামিজ বা অন্যান্য ভাষা থেকে ইংরেজিতে অনুবাদ
        translated = translator.translate(raw_title, dest='en').text
        
        # 'VS' বা 'V/S' অংশ খুঁজে বের করার চেষ্টা
        match = re.search(r'([A-Za-z0-9\s]+)\s+(?:VS|v/s|vs|-)\s+([A-Za-z0-9\s]+)', translated, re.IGNORECASE)
        if match:
            team1 = match.group(1).strip()
            team2 = match.group(2).strip()
            # অপ্রয়োজনীয় ছোট শব্দ বাদ দেওয়া
            team1 = re.sub(r'^(Prediction|Match|Review|Analysis)\s+', '', team1, flags=re.IGNORECASE)
            return f"{team1} VS {team2}"
        
        return translated
    except Exception:
        return raw_title

def get_actual_stream_url(page_url):
    """
    ম্যাচ পেজের ভেতরে গিয়ে আসল m3u8 স্ট্রিম লিংক বের করে।
    """
    try:
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            # HTML-এর ভেতরে m3u8 লিংক খোঁজা
            m3u8_matches = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', res.text)
            if m3u8_matches:
                return m3u8_matches[0]
            
            # iframe-এর ভেতরে m3u8 খোঁজা
            soup = BeautifulSoup(res.text, 'html.parser')
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if src:
                    if not src.startswith('http'):
                        src = 'https:' + src if src.startswith('//') else TARGET_URL + src
                    iframe_res = requests.get(src, headers=HEADERS, timeout=5)
                    iframe_m3u8 = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', iframe_res.text)
                    if iframe_m3u8:
                        return iframe_m3u8[0]
    except Exception as e:
        print(f"Error extracting stream from {page_url}: {e}")
    return None

def fetch_live_matches():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching main site: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    processed_links = set()

    links = soup.find_all("a", href=True)
    for link in links:
        href = link['href']
        raw_title = link.get_text(strip=True)

        if "vs" in raw_title.lower() or "v/s" in raw_title.lower() or " - " in raw_title:
            full_page_url = href if href.startswith("http") else f"{TARGET_URL.rstrip('/')}/{href.lstrip('/')}"
            
            if full_page_url in processed_links:
                continue
            processed_links.add(full_page_url)

            print(f"Processing: {raw_title}")
            clean_name = clean_title(raw_title)
            stream_url = get_actual_stream_url(full_page_url)

            # যদি m3u8 পাওয়া যায়, তবেই কেবল প্লেলিস্টে যোগ করবে
            if stream_url:
                results.append({
                    "title": clean_name,
                    "stream_url": stream_url
                })

    return results

def generate_m3u(matches):
    m3u_content = "#EXTM3U\n"
    m3u_content += "#EXT-X-VERSION:3\n\n"

    if not matches:
        m3u_content += "#EXTINF:-1 tvg-name=\"No Stream Available\", No Active Live Stream Found\n"
        m3u_content += "https://0.0.0.0/offline.m3u8\n"
    else:
        for idx, match in enumerate(matches, 1):
            title = match['title']
            url = match['stream_url']
            m3u_content += f'#EXTINF:-1 tvg-id="{idx}" tvg-name="{title}", {title}\n'
            m3u_content += f'{url}\n\n'

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"Successfully saved {len(matches)} valid streams.")

if __name__ == "__main__":
    live_data = fetch_live_matches()
    generate_m3u(live_data)
