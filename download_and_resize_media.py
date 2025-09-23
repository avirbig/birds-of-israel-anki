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

def download_sound(sound_id, save_path):
    """
    Download the actual .mp3 file from xeno-canto.org using the sound ID.
    """
    # The download URL is https://xeno-canto.org/{sound_id}/download
    sound_url = f"https://xeno-canto.org/{sound_id}/download"
    try:
        resp = requests.get(sound_url, timeout=15)
        if resp.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(resp.content)
            return True
        else:
            print(f"Failed to download sound {sound_url}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"Failed to download sound {sound_url}: {e}")
    return False

def main():
    # Clean up old .mp3 and .txt files from media directory
    print("Cleaning up old .mp3 and .txt files from media directory...")
    for root, dirs, files in os.walk(MEDIA_ROOT):
        for file in files:
            if file.endswith('.mp3') or file.endswith('.txt'):
                try:
                    os.remove(os.path.join(root, file))
                except Exception as e:
                    print(f"Failed to remove {file}: {e}")
    import concurrent.futures
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, family, latin_name FROM species")
    species_list = cur.fetchall()
    download_tasks = []
    for species_id, family, latin_name in species_list:
        family_dir = family.strip() if family else "UnknownFamily"
        species_dir = latin_name.strip() if latin_name else f"species_{species_id}"
        base_dir = os.path.join(MEDIA_ROOT, family_dir, species_dir)
        ensure_dir(base_dir)
        # Images
        cur.execute("SELECT id, url FROM images WHERE species_id=?", (species_id,))
        for img_id, url in cur.fetchall():
            ext = os.path.splitext(url)[-1] or ".jpg"
            img_name = f"img_{img_id}{ext}"
            img_path = os.path.join(base_dir, img_name)
            if os.path.exists(img_path):
                print(f"Skipping existing image: {img_path}")
                continue
            download_tasks.append(("image", img_id, url, img_path))
        # Sounds
        cur.execute("SELECT id, url FROM sounds WHERE species_id=?", (species_id,))
        for snd_id, url in cur.fetchall():
            # url is actually the sound ID as a string
            snd_name = f"sound_{snd_id}.mp3"
            snd_path = os.path.join(base_dir, snd_name)
            if os.path.exists(snd_path):
                print(f"Skipping existing sound: {snd_path}")
                continue
            download_tasks.append(("sound", snd_id, url, snd_path))

    def process_task(task):
        typ, file_id, url, path = task
        if typ == "image":
            if download_and_resize_image(url, path):
                # Open a new connection for thread safety
                conn2 = sqlite3.connect(DB_FILE)
                conn2.execute("UPDATE images SET file_path=? WHERE id=?", (path, file_id))
                conn2.commit()
                conn2.close()
                print(f"Saved image: {path}")
        elif typ == "sound":
            # url is actually the sound ID
            if download_sound(url, path):
                conn2 = sqlite3.connect(DB_FILE)
                conn2.execute("UPDATE sounds SET file_path=? WHERE id=?", (path, file_id))
                conn2.commit()
                conn2.close()
                print(f"Saved sound: {path}")

    print(f"Starting media downloads with multithreading...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(process_task, download_tasks))
    conn.close()
    print("Done downloading and resizing media.")

if __name__ == "__main__":
    main()
