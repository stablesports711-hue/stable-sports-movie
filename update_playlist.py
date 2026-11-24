import os
import re
from urllib.parse import unquote

MAC_ADDRESS = "00:1A:79:1D:12:35"
BASE_URL = f"http://main.light-ott.net/play/live.php?mac={MAC_ADDRESS}&stream={{}}&extension=m3u8"

# ==================== সহজে ফোল্ডার বদলানোর জায়গা ====================
BASE_DIR = "IPTV"
SUBFOLDER = "ASIA-TV"  # অন্য ফোল্ডারে রাখতে চাইলে শুধু এই নামটি বদলান
# =====================================================================

TARGET_DIR = os.path.join(BASE_DIR, SUBFOLDER) if SUBFOLDER else BASE_DIR
GITHUB_RAW_BASE = (
    f"https://raw.githubusercontent.com/stablesports711-hue/stable-sports-movie/refs/heads/main/IPTV/ASIA-TV/"
)


def extract_stream_id(url: str) -> str | None:
    """
    টোকেনযুক্ত বা ffmpeg এনকোডেড লিংক থেকেও আসল stream ID বের করে আনে।
    উদাহরণ: ...&stream=ffmpeg+http%3A%2F%2F...%26stream%3D1025537%26extension%3Dts%26play_token%3D...
    এখান থেকে সবার শেষের/আসল stream=1025537 -> '1025537' বের করবে।
    """
    decoded = unquote(url)

    # ডিকোড করা লিংকের ভেতরে যতগুলো stream=<digits> আছে সবগুলো খোঁজা হয়
    # সাধারণত ffmpeg লিংকের ভেতরের শেষ stream=<id> আসল চ্যানেল ID হয়
    all_ids = re.findall(r"(?:[?&]|%26)stream=(\d+)", decoded, flags=re.IGNORECASE)
    if all_ids:
        return all_ids[-1]

    # যদি ডিকোড না করেই সরাসরি stream=<digits> পাওয়া যায়
    raw_ids = re.findall(r"[?&]stream=(\d+)", url, flags=re.IGNORECASE)
    if raw_ids:
        return raw_ids[-1]

    return None


def process_playlist(input_m3u_path, target_dir=TARGET_DIR, raw_base=GITHUB_RAW_BASE):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    if not os.path.exists(input_m3u_path):
        print(f"Error: {input_m3u_path} file not found!")
        return

    with open(input_m3u_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # #EXTINF লাইনের পর যেকোনো http/https লিংক (টোকেন ও প্যারামিটারসহ) ধরবে
    entries = re.findall(r'(#EXTINF:-.*?\r?\n)(https?://[^\r\n]+)', content)
    updated_content = content
    created_files = 0
    skipped_links = 0

    for extinf, old_url in entries:
        clean_old_url = old_url.strip()
        stream_id = extract_stream_id(clean_old_url)
        if not stream_id:
            skipped_links += 1
            print(f"[SKIP] Stream ID পাওয়া যায়নি: {clean_old_url}")
            continue

        safe_filename = f"{stream_id}.m3u8"
        file_path = os.path.join(target_dir, safe_filename)

        # সাবফোল্ডারের ভেতরের ফাইলের স্ট্রাকচার
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

        # মেইন প্লেলিস্টে টোকেন লিংক বাদ দিয়ে raw লিংক বসানো
        raw_link = f"{raw_base}{safe_filename}"
        updated_content = updated_content.replace(clean_old_url, raw_link)

    with open(input_m3u_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(
        f"সম্পন্ন: {created_files} টি চ্যানেল '{target_dir}/' ফোল্ডারে সেভ হয়েছে"
        + (f" ({skipped_links} টি লিংক স্কিপ করা হয়েছে)" if skipped_links else "")
        + "।"
    )


if __name__ == "__main__":
    process_playlist("playlist.m3u")
