"""
Fetch and parse bird species data from birds.org.il API and store in SQLite
"""

import requests
import sqlite3
import json
import os
import time
import concurrent.futures

API_URL = "https://api.birds.org.il/api/species/byid/he/{}"
VALID_IDS_FILE = "valid_species_ids.txt"
DB_FILE = "birds.sqlite3"
TIMEOUT = 2
REQUEST_TIMEOUT = 30

CREATE_SPECIES_TABLE = """
CREATE TABLE IF NOT EXISTS species (
    id INTEGER PRIMARY KEY,
    hebrew_name TEXT,
    latin_name TEXT,
    family TEXT,
    description TEXT,
    conservation TEXT
);
"""
CREATE_IMAGES_TABLE = """
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id INTEGER,
    url TEXT,
    file_path TEXT,
    FOREIGN KEY(species_id) REFERENCES species(id)
);
"""
CREATE_SOUNDS_TABLE = """
CREATE TABLE IF NOT EXISTS sounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species_id INTEGER,
    url TEXT,
    file_path TEXT,
    FOREIGN KEY(species_id) REFERENCES species(id)
);
"""

def fetch_species_data(species_id):
    try:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6",
            "Referer": "https://www.birds.org.il/",
            "Origin": "https://www.birds.org.il",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }
        resp = requests.get(API_URL.format(species_id), headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            try:
                return resp.json()
            except Exception as e:
                print(f"  Error parsing JSON for {species_id}: {e}")
        else:
            print(f"  HTTP error {resp.status_code} for {species_id}")
    except Exception as e:
        print(f"  Exception for {species_id}: {e}")
    return None

def parse_and_store(data):
    species_id = data.get("id")
    hebrew_name = data.get("name")
    latin_name = data.get("latinName")
    family = data.get("speciesFamilyName")
    description = data.get("description")
    conservation = data.get("conservationLevelIL")
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT OR IGNORE INTO species (id, hebrew_name, latin_name, family, description, conservation) VALUES (?, ?, ?, ?, ?, ?)",
                 (species_id, hebrew_name, latin_name, family, description, conservation))
    # Images
    for img in data.get("images", []):
        url = img.get("path")
        conn.execute("INSERT INTO images (species_id, url, file_path) VALUES (?, ?, ?)" , (species_id, url, None))
    for img in data.get("largeImage", []):
        url = img.get("path")
        conn.execute("INSERT INTO images (species_id, url, file_path) VALUES (?, ?, ?)" , (species_id, url, None))
    # Sounds
    for snd in data.get("sounds", []):
        url = snd.get("path")
        conn.execute("INSERT INTO sounds (species_id, url, file_path) VALUES (?, ?, ?)" , (species_id, url, None))
    conn.commit()
    conn.close()
    if not os.path.exists(VALID_IDS_FILE):
        print(f"Missing {VALID_IDS_FILE}. Run discover_species_ids.py first.")
        return
    else:
        print(f"{VALID_IDS_FILE} already exists. Skipping species ID discovery.")

    with open(VALID_IDS_FILE, encoding="utf-8") as f:
        ids = [int(line.strip()) for line in f if line.strip().isdigit()]

    # Create tables once before threading and enable WAL mode
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute(CREATE_SPECIES_TABLE)
    conn.execute(CREATE_IMAGES_TABLE)
    conn.execute(CREATE_SOUNDS_TABLE)
    conn.close()
def fetch_and_store_one(species_id):
        # Open a single connection per thread
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM species WHERE id=?", (species_id,))
        if cur.fetchone():
            print(f"Skipping already-fetched species: {species_id}")
            conn.close()
            return
        data = fetch_species_data(species_id)
        if data:
            hebrew_name = data.get("name", "")
            print(f"Fetched {species_id} - {hebrew_name}")
            parse_and_store(data)
        else:
            print(f"  Failed to fetch {species_id}")
        conn.close()


def main():
    if not os.path.exists(VALID_IDS_FILE):
        print(f"Missing {VALID_IDS_FILE}. Run discover_species_ids.py first.")
        return
    else:
        print(f"{VALID_IDS_FILE} already exists. Skipping species ID discovery.")

    with open(VALID_IDS_FILE, encoding="utf-8") as f:
        ids = [int(line.strip()) for line in f if line.strip().isdigit()]

    # Create tables once before threading and enable WAL mode
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute(CREATE_SPECIES_TABLE)
    conn.execute(CREATE_IMAGES_TABLE)
    conn.execute(CREATE_SOUNDS_TABLE)
    conn.close()

    print(f"Fetching species data concurrently...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(fetch_and_store_one, ids))
    print(f"Done. Data saved to {DB_FILE}")

if __name__ == "__main__":
    main()
