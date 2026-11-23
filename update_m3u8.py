from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# এখানে নতুন লিংক (base URL) এবং নতুন MAC অ্যাড্রেস দিন
NEW_BASE_URL = "http://new-domain.example.com"
NEW_MAC = "00:1A:2B:3C:4D:5E"

# স্ক্রিপ্ট বা workflow ফোল্ডার বাদে পুরো repo স্ক্যান করার জন্য root হিসেবে বর্তমান ডিরেক্টরি ধরা হয়েছে
ROOT_DIR = Path(".")
SKIP_DIRS = {".git", ".github", "__pycache__", "node_modules"}


def update_stream_url(line: str, new_base_url: str, new_mac: str) -> str:
    raw_url = line.strip()
    if not (raw_url.startswith("http://") or raw_url.startswith("https://")):
        return line

    old_parts = urlsplit(raw_url)
    new_base_parts = urlsplit(new_base_url.strip())

    # নতুন base URL থেকে scheme ও netloc (এবং প্রিফিক্স path থাকলে তা) নেওয়া হচ্ছে
    scheme = new_base_parts.scheme or old_parts.scheme
    netloc = new_base_parts.netloc or old_parts.netloc
    base_path = new_base_parts.path.rstrip("/")
    old_path = old_parts.path
    path = f"{base_path}{old_path}" if base_path else old_path

    # Query string থেকে mac প্যারামিটার আপডেট করা হচ্ছে, বাকি প্যারামিটার ঠিক রেখে
    query_params = parse_qsl(old_parts.query, keep_blank_values=True)
    updated_query = []
    mac_found = False

    for key, value in query_params:
        if key.lower() == "mac":
            updated_query.append((key, new_mac.strip()))
            mac_found = True
        else:
            updated_query.append((key, value))

    if not mac_found and new_mac.strip():
        updated_query.append(("mac", new_mac.strip()))

    new_query = urlencode(updated_query)
    updated_url = urlunsplit((scheme, netloc, path, new_query, old_parts.fragment))

    # মূল লাইনের শেষের newline ধরে রাখা হচ্ছে
    ending = "\r\n" if line.endswith("\r\n") else ("\n" if line.endswith("\n") else "")
    return f"{updated_url}{ending}"


def main() -> None:
    updated_files = 0

    for m3u8_path in ROOT_DIR.rglob("*.m3u8"):
        if any(part in SKIP_DIRS for part in m3u8_path.parts):
            continue

        original_text = m3u8_path.read_text(encoding="utf-8", errors="replace")
        lines = original_text.splitlines(keepends=True)
        new_lines = [update_stream_url(line, NEW_BASE_URL, NEW_MAC) for line in lines]
        new_text = "".join(new_lines)

        if new_text != original_text:
            m3u8_path.write_text(new_text, encoding="utf-8")
            updated_files += 1
            print(f"Updated: {m3u8_path}")

    print(f"Done. Total files updated: {updated_files}")


if __name__ == "__main__":
    main()
