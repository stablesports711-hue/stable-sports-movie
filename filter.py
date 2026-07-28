import urllib.request

# Raw M3U Link
url = "https://raw.githubusercontent.com/srhady/Fancode-bd/refs/heads/main/main_playlist.m3u"

# আপনার টার্গেট চ্যানেল নাম
TARGET_NAME = "Global Super"

# আউটপুট ফাইলের নাম
OUTPUT_FILE = "gsl_playlist.m3u8"

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
                    stream_link = lines[i + 1].strip()
                    
                    # যদি পাওয়া লিংকটি গিটহাবের আরেকটা M3U8 প্লেলিস্ট হয়, তবে তার ভেতর ঢুকে আসল লিংক বের করা
                    if "raw.githubusercontent.com" in stream_link and stream_link.endswith((".m3u", ".m3u8")):
                        sub_content = fetch_content(stream_link)
                        if sub_content:
                            sub_lines = [l.strip() for l in sub_content.splitlines() if l.strip() and not l.startswith("#")]
                            if sub_lines:
                                stream_link = sub_lines[-1] # আসল ডাইরেক্ট ভিডিও লিংকটি নেয়া হলো
                    
                    filtered_output.append("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2200000\n")
                    filtered_output.append(stream_link + "\n\n")
                    found_channel = True
                    i += 1
            i += 1

        # না পাওয়া গেলে
        if not found_channel:
            filtered_output.append("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2200000\n")
            filtered_output.append(DEFAULT_OFFLINE_LINK + "\n")

        # ফাইল সেভ করা
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.writelines(filtered_output)
            
        print(f"Successfully generated {OUTPUT_FILE}")

except Exception as e:
    print(f"Error occurred: {e}")
