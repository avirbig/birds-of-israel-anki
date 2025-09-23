
# 🐦 Bird Recognition Flashcard Tool

This project collects bird data from birds.org.il, stores it in a SQLite database, downloads and resizes images for mobile Anki flashcards, and generates a fully operational Anki deck (APKG) for use on AnkiDroid or Anki Desktop.

## Features
- Discovers valid bird species IDs from birds.org.il API
- Fetches and parses species data (Hebrew name, Latin name, family, images, sounds)
- Downloads and resizes images for mobile-friendly Anki cards
- Stores all data in a SQLite database
- **Generates a ready-to-use Anki deck (APKG) with images and bird info**

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
   - **Generate an Anki deck (Birds_of_Israel.apkg) with all images and info**

## Output
- `birds.sqlite3`: SQLite database with all species, images, and sounds
- `media/`: Folder with resized images and sounds, organized by family/species
- `valid_species_ids.txt`: List of valid bird species IDs
- `Birds_of_Israel.apkg`: Anki deck file ready for import into AnkiDroid or Anki Desktop

## Anki Deck Details
- Each card shows a bird image on the front, and the Hebrew name, Latin name, and family on the back.
- All images are included in the APKG file for offline use on mobile.
- The deck is generated using the [genanki](https://github.com/kerrickstaley/genanki) library.

## Notes
- Images are resized to max 400x400px for mobile performance
- Hebrew names are handled with UTF-8 encoding
- Sound support is planned for a future update

## License
MIT
