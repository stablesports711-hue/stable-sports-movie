import urllib.request

# Raw M3U Link
url = "https://raw.githubusercontent.com/srhady/Fancode-bd/refs/heads/main/main_playlist.m3u"

# আপনার টার্গেট চ্যানেল নাম
TARGET_NAME = "GSL"

# আউটপুট ফাইলের নাম
OUTPUT_FILE = "gsl_playlist.m3u8"

# চ্যানেল না পাওয়া গেলে যে ডিফল্ট লিংক বসাতে চান (ইচ্ছা হলে পরিবর্তন করতে পারেন)
DEFAULT_OFFLINE_LINK = "http://example.com/offline.m3u8"

try:
    # M3U ডাটা ডাউনলোড
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')

    lines = content.splitlines()
    filtered_output = [
        "#EXTM3U\n",
        "#EXT-X-VERSION:3\n"
    ]
    
    found_channel = False
    
    # M3U ফাইল ফিল্টার করা
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # যদি EXTINF লাইনে GSL ম্যাচ করে
        if line.startswith("#EXTINF") and TARGET_NAME.lower() in line.lower():
            # STREAM-INF হেডার যোগ করা
            filtered_output.append("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2200000\n")
            
            # সরাসরি নিচের লিংকটি নেয়া
            if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                filtered_output.append(lines[i + 1] + "\n\n")
                found_channel = True
                i += 1
        i += 1

    # যদি GSL নামে কিছু না পাওয়া যায়, তবে ডিফল্ট লিংক বসবে
    if not found_channel:
        filtered_output.append("#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2200000\n")
        filtered_output.append(DEFAULT_OFFLINE_LINK + "\n")

    # ফাইল সেভ করা
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(filtered_output)
        
    print(f"Successfully generated {OUTPUT_FILE}")

except Exception as e:
    print(f"Error occurred: {e}")
