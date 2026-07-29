import urllib.request

# Raw M3U Link
url = "https://raw.githubusercontent.com/srhady/Fancode-bd/refs/heads/main/main_playlist.m3u"

# আপনার টার্গেট চ্যানেল নাম
TARGET_NAME = "Lanka Premier League"

# আউটপুট ফাইলের নাম
OUTPUT_FILE = "LPL_playlist.m3u8"

# চ্যানেল না পাওয়া গেলে ডিফল্ট লিংক
DEFAULT_OFFLINE_LINK = "https://res.cloudinary.com/qleik3si/video/upload/v1785235285/VN20260728_161756_ev6pow.mp4"

def fetch_content(link_url):
    """লিংক থেকে কনটেন্ট রিড করার ফাংশন"""
    try:
        req = urllib.request.Request(link_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {link_url}: {e}")
        return None

try:
    content = fetch_content(url)

    if content:
        lines = content.splitlines()
        filtered_output = [
            "#EXTM3U\n",
            "#EXT-X-VERSION:3\n"
        ]
        
        found_channel = False
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # টার্গেট চ্যানেল ম্যাচ করলে
            if line.startswith("#EXTINF") and TARGET_NAME.lower() in line.lower():
                if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                    extinf_line = line
                    stream_link = lines[i + 1].strip()
                    
                    # লিঙ্কটি গিটহাবের M3U/M3U8 হলে সেটির ভিতরে ঢুকে সম্পূর্ণ কনটেন্ট নিয়ে আসবে
                    if "github" in stream_link.lower() and stream_link.endswith((".m3u", ".m3u8")):
                        sub_content = fetch_content(stream_link)
                        if sub_content:
                            sub_lines = sub_content.splitlines()
                            for sub_line in sub_lines:
                                # সাব-ফাইলের হেডার লাইন বাদ দিয়ে বাকিসব হুবহু যুক্ত করা হবে
                                if sub_line.strip() and not sub_line.startswith("#EXTM3U") and not sub_line.startswith("#EXT-X-VERSION"):
                                    filtered_output.append(sub_line + "\n")
                            found_channel = True
                    else:
                        # যদি গিটহাবের ফাইল না হয়, তবে মেইন ফাইলের আসল #EXTINF এবং লিঙ্ক দুটিই যুক্ত হবে
                        filtered_output.append(extinf_line + "\n")
                        filtered_output.append(stream_link + "\n")
                        found_channel = True
                        
                    i += 1
            i += 1

        # চ্যানেল না পাওয়া গেলে ডিফল্ট অফলাইন ভিডিও দেখাবে
        if not found_channel:
            filtered_output.append(f'#EXTINF:-1 tvg-logo="" group-title="Offline", {TARGET_NAME} (Offline)\n')
            filtered_output.append(DEFAULT_OFFLINE_LINK + "\n")

        # ফাইল সেভ করা
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.writelines(filtered_output)
            
        print(f"Successfully generated {OUTPUT_FILE}")

except Exception as e:
    print(f"Error occurred: {e}")
