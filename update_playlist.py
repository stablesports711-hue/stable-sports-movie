import os
import re

MAC_ADDRESS = "00:1B:77:36:26:BD"
BASE_URL = f"http://liee.tivi..net/play/live.php?mac={MAC_ADDRESS}&stream={{}}&extension=m3u8"
GITHUB_RAW_BASE = "https://github.com/stablesports711-hue/stable-sports-movie/tree/main/IPTV/LALIGA"

def process_playlist(input_m3u_path, target_dir="IPTV"):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if not os.path.exists(input_m3u_path):
        print(f"Error: {input_m3u_path} file not found!")
        return

    with open(input_m3u_path, "r", encoding="utf-8") as f:
        content = f.read()

    entries = re.findall(r'(#EXTINF:-.*?\n)(https?://[^\s]+)', content)
    updated_content = content
    created_files = 0

    for extinf, old_url in entries:
        stream_match = re.search(r'stream=(\d+)', old_url)
        if not stream_match:
            continue
        
        stream_id = stream_match.group(1)
        safe_filename = f"{stream_id}.m3u8"
        file_path = os.path.join(target_dir, safe_filename)

        # ফাইলের ভেতরের স্ট্রাকচার
        new_stream_url = BASE_URL.format(stream_id)
        file_content = (
            "#EXTM3U\n"
            "#EXT-X-VERSION:3\n"
            f"#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=5550000\n"
            f"{new_stream_url}\n"
        )

        with open(file_path, "w", encoding="utf-8") as out_f:
            out_f.write(file_content)
        
        created_files += 1

        # মেইন প্লেলিস্টে র-লিংক বসানো
        raw_link = f"{GITHUB_RAW_BASE}{safe_filename}"
        updated_content = updated_content.replace(old_url, raw_link)

    with open(input_m3u_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Successfully processed {created_files} channels into IPTV/ folder.")

if __name__ == "__main__":
    process_playlist("playlist.m3u")
