"""
Download and resize bird images and sounds for Anki cards (mobile-friendly)
"""
import os
import sqlite3
import requests
from PIL import Image
from io import BytesIO
import time

DB_FILE = "birds.sqlite3"
MEDIA_ROOT = "media"
IMG_MAX_SIZE = (400, 400)  # Mobile-friendly size
TIMEOUT = 2

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_and_resize_image(url, save_path):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content))
            img.thumbnail(IMG_MAX_SIZE)
            img.save(save_path, format=img.format or 'JPEG', quality=85)
            return True
    except Exception as e:
        print(f"Failed to download/resize {url}: {e}")
    return False

def download_sound(url, save_path):
    # The API provides only a sound ID, not a direct URL. You may need to adjust this for real downloads.
    # Placeholder: just save the ID as a text file for now.
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(url)
        return True
    except Exception as e:
        print(f"Failed to save sound {url}: {e}")
    return False

def main():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, family, latin_name FROM species")
    species_list = cur.fetchall()
    for species_id, family, latin_name in species_list:
        family_dir = family if family else "UnknownFamily"
        species_dir = latin_name if latin_name else f"species_{species_id}"
        base_dir = os.path.join(MEDIA_ROOT, family_dir, species_dir)
        ensure_dir(base_dir)
        # Images
        cur.execute("SELECT id, url FROM images WHERE species_id=?", (species_id,))
        for img_id, url in cur.fetchall():
            ext = os.path.splitext(url)[-1] or ".jpg"
            img_name = f"img_{img_id}{ext}"
            img_path = os.path.join(base_dir, img_name)
            if download_and_resize_image(url, img_path):
                conn.execute("UPDATE images SET file_path=? WHERE id=?", (img_path, img_id))
                print(f"Saved image: {img_path}")
            time.sleep(TIMEOUT)
        # Sounds
        cur.execute("SELECT id, url FROM sounds WHERE species_id=?", (species_id,))
        for snd_id, url in cur.fetchall():
            snd_name = f"sound_{snd_id}.txt"
            snd_path = os.path.join(base_dir, snd_name)
            if download_sound(url, snd_path):
                conn.execute("UPDATE sounds SET file_path=? WHERE id=?", (snd_path, snd_id))
                print(f"Saved sound: {snd_path}")
            time.sleep(TIMEOUT)
        conn.commit()
    conn.close()
    print("Done downloading and resizing media.")

if __name__ == "__main__":
    main()
