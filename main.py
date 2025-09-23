"""
Main entry point for birding project: runs all steps in order
"""
import subprocess
import sys

import os


# List of scripts to run in order (excluding discover_species_ids.py, which is conditional)
SCRIPTS = [
    "fetch_and_store_species.py",
    "download_and_resize_media.py",
    "generate_anki_deck.py"
]


if not os.path.exists("valid_species_ids.txt"):
    print("\n=== Running discover_species_ids.py ===")
    result = subprocess.run([sys.executable, "discover_species_ids.py"])
    if result.returncode != 0:
        print(f"Error running discover_species_ids.py. Stopping.")
        sys.exit(result.returncode)
else:
    print("valid_species_ids.txt already exists. Skipping discover_species_ids.py.")

# Run the rest of the scripts in order
for script in SCRIPTS:
    print(f"\n=== Running {script} ===")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"Error running {script}. Stopping.")
        sys.exit(result.returncode)
print("\nAll steps completed successfully.")
