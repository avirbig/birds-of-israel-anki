"""
Fetch and parse bird species data from birds.org.il API and store in SQLite
"""
import requests
import sqlite3
import json
import os
import time

API_URL = "https://www.birds.org.il/api/{}"
VALID_IDS_FILE = "valid_species_ids.txt"
DB_FILE = "birds.sqlite3"
TIMEOUT = 2

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
        resp = requests.get(API_URL.format(species_id), timeout=10)
        if resp.status_code == 200 and resp.headers.get('Content-Type', '').startswith('application/json'):
            return resp.json()
    except Exception:
        pass
    return None

def parse_and_store(conn, data):
    species_id = data.get("id")
    hebrew_name = data.get("name")
    latin_name = data.get("latinName")
    family = data.get("speciesFamilyName")
    description = data.get("description")
    conservation = data.get("conservationLevelIL")
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

def main():
    if not os.path.exists(VALID_IDS_FILE):
        print(f"Missing {VALID_IDS_FILE}. Run discover_species_ids.py first.")
        return
    conn = sqlite3.connect(DB_FILE)
    conn.execute(CREATE_SPECIES_TABLE)
    conn.execute(CREATE_IMAGES_TABLE)
    conn.execute(CREATE_SOUNDS_TABLE)
    with open(VALID_IDS_FILE, encoding="utf-8") as f:
        ids = [int(line.strip()) for line in f if line.strip().isdigit()]
    for species_id in ids:
        print(f"Fetching species {species_id}...")
        data = fetch_species_data(species_id)
        if data:
            parse_and_store(conn, data)
        else:
            print(f"  Failed to fetch {species_id}")
        time.sleep(TIMEOUT)
    conn.close()
    print(f"Done. Data saved to {DB_FILE}")

if __name__ == "__main__":
    main()
