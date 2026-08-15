import urllib.request

# Raw M3U Link
url = "https://raw.githubusercontent.com/srhady/SonyLiv/refs/heads/main/sonyliv_playlist.m3u"

# আপনার টার্গেট চ্যানেল নাম
TARGET_NAME = "India Tour of Sri Lanka"

# আউটপুট ফাইলের নাম
OUTPUT_FILE = "Fancode1.m3u8"

# চ্যানেল না পাওয়া গেলে ডিফল্ট ভিডিও
DEFAULT_OFFLINE_LINK = "https://res.cloudinary.com/qleik3si/video/upload/v1785235285/VN20260728_161756_ev6pow.mp4"


def fetch_content(link_url):
    """লিংক থেকে কনটেন্ট আনে"""
    try:
        req = urllib.request.Request(
            link_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"Error fetching {link_url}: {e}")
        return None


try:
    content = fetch_content(url)

    if not content:
        raise Exception("Playlist download failed!")

    lines = content.splitlines()

    filtered_output = [
        "#EXTM3U\n"
    ]

    found_channel = False

    i = 0
    while i < len(lines):

        line = lines[i].strip()

        # টার্গেট চ্যানেল খুঁজবে
        if line.startswith("#EXTINF") and TARGET_NAME.lower() in line.lower():

            found_channel = True

            j = i

            # পরবর্তী EXTINF আসা পর্যন্ত সব লাইন কপি করবে
            while j < len(lines):

                current_line = lines[j].rstrip()

                if j != i and current_line.startswith("#EXTINF"):
                    break

                filtered_output.append(current_line + "\n")

                j += 1

            break

        i += 1

    # না পেলে অফলাইন ভিডিও
    if not found_channel:
        filtered_output = [
            "#EXTM3U\n",
            '#EXTINF:-1 tvg-name="Offline",Offline\n',
            DEFAULT_OFFLINE_LINK + "\n"
        ]

    # ফাইল সেভ
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(filtered_output)

    print(f"Successfully generated {OUTPUT_FILE}")

except Exception as e:
    print(f"Error occurred: {e}")
