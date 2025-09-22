"""
Bird species ID discovery script for birds.org.il API
"""
import requests
import time

API_URL = "https://www.birds.org.il/api/{}"
START_ID = 1
END_ID = 1000  # Adjust as needed
TIMEOUT = 2  # seconds between requests

VALID_IDS_FILE = "valid_species_ids.txt"

def is_valid_species(species_id):
    try:
        resp = requests.get(API_URL.format(species_id), timeout=10)
        if resp.status_code == 200 and resp.headers.get('Content-Type', '').startswith('application/json'):
            data = resp.json()
            # Basic check: must have a Hebrew name and Latin name
            if data.get("name") and data.get("latinName"):
                return data.get("name")
        return False
    except Exception:
        return False

def discover_species_ids(start=START_ID, end=END_ID):
    valid_ids = []
    for species_id in range(start, end + 1):
        print(f"Checking species ID {species_id}...")
        name = is_valid_species(species_id)
        if name:
            print(f"  Valid: {species_id} - {name}")
            valid_ids.append(species_id)
        else:
            print(f"  Invalid: {species_id}")
        time.sleep(TIMEOUT)
    with open(VALID_IDS_FILE, "w", encoding="utf-8") as f:
        for sid in valid_ids:
            f.write(f"{sid}\n")
    print(f"Done. {len(valid_ids)} valid species IDs saved to {VALID_IDS_FILE}")

if __name__ == "__main__":
    discover_species_ids()
