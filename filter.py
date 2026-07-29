import urllib.request
import re

# ১. মূল M3U প্লেলিস্ট লিংক
SOURCE_URL = "https://raw.githubusercontent.com/srhady/Fancode-bd/refs/heads/main/main_playlist.m3u"

# ২. আপনার ফিল্টার করার টার্গেট নাম (যেমন: LPL, Lanka Premier League, Cricket ইত্যাদি)
TARGET_NAME = "Lanka Premier League"

# ৩. আউটপুট ফাইলের নাম
OUTPUT_FILE = "LPL.m3u8"

def fetch_data(url):
    """অনলাইন থেকে ডাটা ফেচ করার ফাংশন"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def main():
    print(f"Downloading main playlist...")
    main_playlist = fetch_data(SOURCE_URL)
    
    if not main_playlist:
        print("Main playlist could not be downloaded!")
        return

    lines = main_playlist.splitlines()
    stream_url = None

    # ৪. টার্গেট নাম দিয়ে M3U এর ভেতর লিংক খোঁজা
    for i, line in enumerate(lines):
        # লাইনটিতে #EXTINF আছে কিনা এবং টার্গেট নামটি কেস-ইনসেনসিটিভ ভাবে মেলে কিনা
        if line.startswith("#EXTINF") and TARGET_NAME.lower() in line.lower():
            # টার্গেট লাইনের ঠিক নিচের লাইনে ভিডিও লিংকটি থাকে
            if i + 1 < len(lines):
                potential_link = lines[i + 1].strip()
                if potential_link.startswith("http"):
                    stream_url = potential_link
                    print(f"Found target stream URL: {stream_url}")
                    break

    # ৫. টার্গেট লিংক পেলে তার ভেতরে ঢুকে পুরো স্ট্রিম ডাটা নিয়ে আসা
    if stream_url:
        print(f"Fetching stream content from target link...")
        stream_content = fetch_data(stream_url)
        
        if stream_content:
            # LPL.m3u8 ফাইলের মধ্যে কোডটি সেভ করা
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(stream_content)
            print(f"Successfully created '{OUTPUT_FILE}' with nested stream content!")
        else:
            print("Failed to fetch stream content from the found URL.")
    else:
        print(f"Target '{TARGET_NAME}' not found in the main playlist.")

if __name__ == "__main__":
    main()
