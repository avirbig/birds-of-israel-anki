"""
Main entry point for birding project: runs all steps in order
"""
import subprocess
import sys

SCRIPTS = [
    "discover_species_ids.py",
    "fetch_and_store_species.py",
    "download_and_resize_media.py"
]

for script in SCRIPTS:
    print(f"\n=== Running {script} ===")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"Error running {script}. Stopping.")
        sys.exit(result.returncode)
print("\nAll steps completed successfully.")
