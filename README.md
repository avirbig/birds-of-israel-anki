# 🐦 Bird Recognition Flashcard Tool

This project collects bird data from birds.org.il, stores it in a SQLite database, downloads and resizes images for mobile Anki flashcards, and prepares media for further deck generation.

## Features
- Discovers valid bird species IDs from birds.org.il API
- Fetches and parses species data (Hebrew name, Latin name, family, images, sounds)
- Downloads and resizes images for mobile-friendly Anki cards
- Stores all data in a SQLite database

## Usage
1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
2. **Run the full workflow**
   ```
   python main.py
   ```
   This will:
   - Discover valid species IDs
   - Fetch and store species data in SQLite
   - Download and resize images and sounds

## Output
- `birds.sqlite3`: SQLite database with all species, images, and sounds
- `media/`: Folder with resized images and sounds, organized by family/species
- `valid_species_ids.txt`: List of valid bird species IDs

## Next Steps
- Generate Anki deck (APKG or CSV) using the processed data and media

## Notes
- Images are resized to max 400x400px for mobile performance
- Hebrew names are handled with UTF-8 encoding

## License
MIT
