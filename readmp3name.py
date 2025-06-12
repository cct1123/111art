#!/usr/bin/env python3
import os

# ← Change this to the folder you want to scan:
root_dir = "tori_segura_media"

mp3_files = []
for dirpath, _, filenames in os.walk(root_dir):
    for fname in filenames:
        if fname.lower().endswith(".mp3"):
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, root_dir)
            mp3_files.append(rel_path)

# Write results to a text file next to the script
with open("mp3_list.txt", "w", encoding="utf-8") as out:
    for p in sorted(mp3_files):
        out.write(f'"{root_dir}/{p}", ')

print(f"Found {len(mp3_files)} MP3 file(s).")
print("See mp3_list.txt for the list of relative paths.")
