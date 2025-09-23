"""
Generate an Anki deck (APKG) from the bird species database and images.
"""
import os
import sqlite3
import genanki

DB_FILE = "birds.sqlite3"
DECK_ID = 2059400110  # Random, but must be consistent for updates
DECK_NAME = "Birds of Israel"
MODEL_ID = 1607392319  # Random, must be unique
MEDIA_ROOT = "media"
OUTPUT_FILE = "Birds_of_Israel.apkg"

# Define the card model (template) for Anki
my_model = genanki.Model(
    MODEL_ID,
    'Bird Card',
    fields=[
        {'name': 'Image'},
        {'name': 'HebrewName'},
        {'name': 'LatinName'},
        {'name': 'Family'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '<div style="text-align:center;">{{Image}}</div>',
            'afmt': '''
                <div style="text-align:center;">{{Image}}</div>
                <hr>
                <b>{{HebrewName}}</b><br>
                <i>{{LatinName}}</i><br>
                <span>{{Family}}</span>
            ''',
        },
    ],
    css='''
        .card {
            font-family: Arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        img {
            max-width: 100%;
            height: auto;
        }
    '''
)

def main():
    """
    Generate an Anki deck from the SQLite database and images.
    Each card will have an image on the front, and bird names/family on the back.
    All images are included as media in the APKG file.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    deck = genanki.Deck(DECK_ID, DECK_NAME)
    media_files = []

    # Query all images and their species info
    cur.execute("""
        SELECT images.file_path, species.hebrew_name, species.latin_name, species.family
        FROM images
        JOIN species ON images.species_id = species.id
        WHERE images.file_path IS NOT NULL AND images.file_path != ''
    """)
    rows = cur.fetchall()
    print(f"Found {len(rows)} images for Anki deck generation.")

    for img_path, hebrew_name, latin_name, family in rows:
        if not os.path.exists(img_path):
            print(f"Warning: Image file missing: {img_path}")
            continue
        # Anki expects just the filename in the <img> tag, not the full path
        img_filename = os.path.basename(img_path)
        media_files.append(img_path)
        note = genanki.Note(
            model=my_model,
            fields=[
                f'<img src="{img_filename}">',  # Image field
                hebrew_name or '',
                latin_name or '',
                family or '',
            ]
        )
        deck.add_note(note)

    # Package the deck with media
    print(f"Packaging deck with {len(media_files)} images...")
    genanki.Package(deck, media_files).write_to_file(OUTPUT_FILE)
    print(f"Anki deck generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
