import os
import re
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

TARGET_URL = "https://socolivei.tv/"
M3U_FILE = "playlist.m3u"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": TARGET_URL,
    "Origin": TARGET_URL.rstrip('/')
}

def clean_title(raw_title):
    try:
        # অনুবাদের মাধ্যমে নাম পরিষ্কার করা
        translated = GoogleTranslator(source='auto', target='en').translate(raw_title)
        
        # Team1 VS Team2 প্যাটার্ন ফিল্টার
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

def extract_stream_from_page(page_url):
    try:
        res = requests.get(page_url, headers=HEADERS, timeout=12)
        if res.status_code != 200:
            return None

        # ১. সরাসরি পেজের জাভাস্ক্রিপ্ট / সোর্সে m3u8 লিংক খোঁজা (যেমন: pull.niues.live বা অন্য সিডিএন)
        m3u8_links = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', res.text)
        if m3u8_links:
            return m3u8_links[0]

        # ২. আইফ্রেম (Iframe) সোর্স চেক করা
        soup = BeautifulSoup(res.text, 'html.parser')
        iframes = soup.find_all(['iframe', 'frame'])
        
        for iframe in iframes:
            src = iframe.get('src') or iframe.get('data-src')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = TARGET_URL.rstrip('/') + src
                
                try:
                    iframe_res = requests.get(src, headers=HEADERS, timeout=8)
                    iframe_m3u8 = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', iframe_res.text)
                    if iframe_m3u8:
                        return iframe_m3u8[0]
                except Exception:
                    continue

        # ৩. ব্যাকএন্ডে কোনো JSON বা কনফিগারেশন এপিআই আছে কি না
        js_vars = re.findall(r'(?:file|source|stream|url)\s*:\s*["\'](https?://[^\'\"]+\.m3u8[^\'\"]*)["\']', res.text, re.IGNORECASE)
        if js_vars:
            return js_vars[0]

    except Exception as e:
        print(f"Error scraping {page_url}: {e}")
    return None

def fetch_live_matches():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error loading target URL: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    processed_urls = set()

    # মূল পাতার সব লিংক পড়া
    links = soup.find_all("a", href=True)
    for link in links:
        href = link['href']
        raw_title = link.get_text(strip=True)

        if not raw_title or len(raw_title) < 3:
            continue

        # লাইভ ম্যাচ পেজ চিহ্নিত করা
        if any(keyword in raw_title.lower() for keyword in ["vs", "v/s", "-", "live"]):
            full_url = href if href.startswith("http") else f"{TARGET_URL.rstrip('/')}/{href.lstrip('/')}"
            
            if full_url in processed_urls:
                continue
            processed_urls.add(full_url)

            clean_name = clean_title(raw_title)
            print(f"Checking stream for: {clean_name}")

            stream_url = extract_stream_from_page(full_url)
            if stream_url:
                results.append({
                    "title": clean_name,
                    "stream_url": stream_url
                })

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
    
    print(f"Successfully generated {len(matches)} streams.")

if __name__ == "__main__":
    live_data = fetch_live_matches()
    generate_m3u(live_data)
