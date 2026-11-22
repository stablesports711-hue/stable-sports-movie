import os
import re
from urllib.request import urlopen, Request

# ==================== কনফিগারেশন ====================
SOURCE_PLAYLIST = "source_playlist.m3u8"  # লোকাল ফাইল অথবা "https://..." URL
IPTV_DIR = "IPTV"                        # ছবির ফোল্ডার পাথ
DRY_RUN = False                          # True দিলে ফাইল না বদলে শুধু কী হবে দেখাবে
# ====================================================

# ছবিতে থাকা ফাইলগুলোর তালিকা (নাম কখনো পরিবর্তন হবে না)
EXISTING_FILES = [
    "FOX501HD.m3u8",
    "FOX505HD.m3u8",
    "LPL1.m3u8",
    "SS-ASports.m3u8",
    "SS-Cricbuzz.m3u8",
    "SS-Cricbuzz1.m3u8",
    "SS-Cricbuzz2.m3u8",
    "SS-GeoSuper.m3u8",
    "SS-PTVSports.m3u8",
    "SS-SonyTen_1.m3u8",
    "SS-SonyTen_2.m3u8",
    "SS-SonyTen_3.m3u8",
    "SS-SonyTen_5.m3u8",
    "SS-StarSS_1.m3u8",
    "SS-StarSS_2.m3u8",
    "SS-StarSports1.m3u8",
    "SS-StarSports2.m3u8",
    "SS-SuperSCric.m3u8",
    "SS-TSports.m3u8",
    "SS-TSports1.m3u8",
    "SS-TSports2.m3u8",
    "SS-Unite8S1.m3u8",
    "SS-Unite8S2.m3u8",
    "SS-Willow1.m3u8",
    "SS-Willow2.m3u8",
    "SkyNZ1.m3u8",
    "SkyNZ2.m3u8",
    "SkyNZ3.m3u8",
    "SkyNZ4.m3u8",
    "SkyNZ5.m3u8",
    "SkyNZ6.m3u8",
    "SkyNZ7.m3u8",
    "SkyNZ8.m3u8",
    "SkyNZ9.m3u8",
    "SkySCric.m3u8",
]

# প্লেলিস্টে নামের ভিন্ন রূপ / অর্থ ম্যাপিং
ALIASES = {
    "sswillow2": ["willow extra", "willow2", "willow 2"],
    "ssstarss1": ["star sports select 1", "star sports select1", "starsportsselect1", "star select 1"],
    "ssstarss2": ["star sports select 2", "star sports select2", "starsportsselect2", "star select 2"], 
    "ssasports": ["asports", "a sports"],
    "ssptvsports": ["ptvsports", "ptv sports"],
    "ssgeosuper": ["geosuper", "geo super"],
    "sstsports": ["tsports", "t sports"],
    "sstsports1": ["tsports1", "tsports 1", "t sports 1"],
    "sstsports2": ["tsports2", "tsports 2", "t sports 2"],
    "sswillow1": ["willow1", "willow 1", "willow hd"],
    "sscricbuzz": ["cricbuzz"],
    "sscricbuzz1": ["cricbuzz1", "cricbuzz 1"],
    "sscricbuzz2": ["cricbuzz2", "cricbuzz 2"],
    "sssuperscric": ["superscric", "super cric", "cric"],
    "skyscric": ["skycric", "sky cric", "sky sports cricket"],
}


def normalize(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"\.m3u8$", "", name)
    name = re.sub(r"\b(hd|fhd|uhd|4k|live|in|uk|us|nz)\b", "", name)
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


def load_playlist_text(source: str) -> str:
    if source.startswith(("http://", "https://")):
        req = Request(source, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    with open(source, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_playlist(content: str) -> dict[str, tuple[str, str]]:
    channels = {}
    current_name = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("#EXTINF:"):
            tvg_match = re.search(r'tvg-name="([^"]*)"', line, re.IGNORECASE)
            comma_name = line.split(",", 1)[1].strip() if "," in line else ""
            current_name = comma_name or (tvg_match.group(1).strip() if tvg_match else "")
        elif not line.startswith("#") and current_name:
            norm = normalize(current_name)
            if norm:
                channels[norm] = (current_name, line)
            current_name = None

    return channels


def find_match(filename: str, parsed_channels: dict[str, tuple[str, str]]):
    base_name = os.path.splitext(filename)[0]
    norm_target = normalize(base_name)

    # ১. Alias তালিকায় সরাসরি ম্যাচ (প্রথমে চেক করা হয় যাতে বিশেষ অর্থ অগ্রাধিকার পায়)
    for alias in ALIASES.get(norm_target, []):
        norm_alias = normalize(alias)
        if norm_alias in parsed_channels:
            return parsed_channels[norm_alias]

    # ২. হুবহু নরমালাইজড নাম ম্যাচ
    if norm_target in parsed_channels:
        return parsed_channels[norm_target]

    # ৩. SS- বা SkyNZ প্রিফিক্স বাদ দিয়ে ম্যাচ
    stripped = re.sub(r"^(ss|skynz)", "", norm_target)
    if stripped in parsed_channels:
        return parsed_channels[stripped]

    # ৪. আংশিক/কন্টেইন ম্যাচ
    for norm_key, value in parsed_channels.items():
        if stripped and (stripped in norm_key or norm_key in stripped):
            return value

    return None


def replace_url_line_only(file_path: str, new_url: str) -> bool:
    """
    শুধুমাত্র লিংক লাইনটি নতুন লিংক দিয়ে বদলায়।
    #EXTM3U, #EXT-X-VERSION, #EXT-X-STREAM-INF এবং ফাইলের নাম অপরিবর্তিত থাকে।
    """
    with open(file_path, "rb") as fb:
        raw_bytes = fb.read()
    had_trailing_newline = raw_bytes.endswith(b"\n")

    lines = raw_bytes.decode("utf-8", errors="ignore").splitlines()
    new_lines = []
    replaced = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("http://", "https://")) or (stripped and not stripped.startswith("#")):
            new_lines.append(new_url)
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        return False

    output = "\n".join(new_lines) + ("\n" if had_trailing_newline else "")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output)

    return True


def main():
    if not os.path.isdir(IPTV_DIR):
        print(f"'{IPTV_DIR}' ফোল্ডারটি পাওয়া যায়নি।")
        return

    content = load_playlist_text(SOURCE_PLAYLIST)
    parsed_channels = parse_playlist(content)

    updated = 0
    kept = 0

    for filename in EXISTING_FILES:
        file_path = os.path.join(IPTV_DIR, filename)
        if not os.path.isfile(file_path):
            print(f"[SKIP]  {filename}  --> ফোল্ডারে নেই")
            continue

        match = find_match(filename, parsed_channels)
        if match:
            ch_name, new_url = match
            print(f"[UPDATE] {filename}  <==  '{ch_name}' | {new_url}")
            if not DRY_RUN and replace_url_line_only(file_path, new_url):
                updated += 1
        else:
            kept += 1
            print(f"[KEPT]   {filename}  --> নাম মেলেনি, আগের লিংকই রাখা হয়েছে")

    print(f"\nসম্পন্ন: {updated} টি আপডেট হয়েছে, {kept} টি আগের লিংকে অপরিবর্তিত আছে।")


if __name__ == "__main__":
    main()
