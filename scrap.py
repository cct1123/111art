# scrap.py
# Download all audio (MP3) and thumbnails from a YouTube channel.
# Dependencies:
#     pip install yt-dlp requests
#     ffmpeg on your PATH

import os

import requests
from yt_dlp import YoutubeDL

# ─────── CONFIGURE HERE ───────
CHANNEL_URL = "https://www.youtube.com/@tori.segura/videos"
OUTPUT_DIR = "tori_segura_media"
# ──────────────────────────────


def sanitize_filename(s: str) -> str:
    return "".join(c if c.isalnum() or c in " ._-" else "_" for c in s).strip()


def download_channel_media(url: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    thumbs_dir = os.path.join(outdir, "thumbnails")
    os.makedirs(thumbs_dir, exist_ok=True)

    # 1) Extract list of video entries (flat)
    with YoutubeDL({"extract_flat": True}) as ydl:
        playlist = ydl.extract_info(url, download=False)

    # 2) Prepare downloader for audio
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(outdir, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "download_archive": os.path.join(outdir, "downloaded.txt"),
        "quiet": True,
    }
    ydl_audio = YoutubeDL(ydl_opts)

    # 3) Loop through each video entry
    for entry in playlist.get("entries", []):
        vid_id = entry.get("id")
        # some extract_flat entries may include full URL; normalize to ID if needed
        if vid_id and vid_id.startswith("http"):
            full_url = vid_id
        else:
            full_url = f"https://www.youtube.com/watch?v={vid_id}"

        # a) get full info to find title & thumbnail
        try:
            info = ydl_audio.extract_info(full_url, download=False)
        except Exception as e:
            print(f"[!] Skipping metadata for {full_url}: {e}")
            continue
        title = sanitize_filename(info.get("title", vid_id))
        thumb_url = info.get("thumbnail")
        if thumb_url:
            ext = os.path.splitext(thumb_url)[1].split("?")[0] or ".jpg"
            thumb_path = os.path.join(thumbs_dir, f"{title}{ext}")
            if not os.path.exists(thumb_path):
                try:
                    resp = requests.get(thumb_url, timeout=10)
                    resp.raise_for_status()
                    with open(thumb_path, "wb") as f:
                        f.write(resp.content)
                    print(f"[✓] Thumbnail: {title}{ext}")
                except Exception as e:
                    print(f"[!] Thumb failed for {title}: {e}")

        # b) download audio
        try:
            print(f"[→] Audio: {title}.mp3")
            ydl_audio.download([full_url])
        except Exception as e:
            print(f"[!] Audio failed for {title}: {e}")


if __name__ == "__main__":
    print(f"Fetching audio + thumbnails from {CHANNEL_URL}")
    download_channel_media(CHANNEL_URL, OUTPUT_DIR)
    print("All done!")
