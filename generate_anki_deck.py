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

# Define the card model (template) for Anki, now with Sounds field.
# IMPORTANT: Field order matters for Anki duplicate detection. We make the
# first field a small unique ID (UID) per image so Anki's duplicate detector
# won't merge cards just because the image binary/tag is identical.
my_model = genanki.Model(
    MODEL_ID,
    'Bird Card',
    fields=[
        {'name': 'UID'},
        {'name': 'Image'},
        {'name': 'HebrewName'},
        {'name': 'LatinName'},
        {'name': 'Family'},
        {'name': 'Sounds'},
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
                <span>{{Family}}</span><br>
                {{Sounds}}
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
        audio {
            margin-top: 10px;
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
        SELECT images.file_path, species.id, species.hebrew_name, species.latin_name, species.family
        FROM images
        JOIN species ON images.species_id = species.id
        WHERE images.file_path IS NOT NULL AND images.file_path != ''
    """)
    rows = cur.fetchall()
    print(f"Found {len(rows)} images for Anki deck generation.")

    for img_path, species_id, hebrew_name, latin_name, family in rows:
        if not os.path.exists(img_path):
            print(f"Warning: Image file missing: {img_path}")
            continue
        # Anki expects just the filename in the <img> tag, not the full path
        img_filename = os.path.basename(img_path)
        media_files.append(img_path)

        # Get all sound files for this species
        cur.execute("SELECT file_path FROM sounds WHERE species_id=? AND file_path IS NOT NULL AND file_path != ''", (species_id,))
        sound_paths = [row[0] for row in cur.fetchall() if os.path.exists(row[0])]
        sound_filenames = [os.path.basename(p) for p in sound_paths]
        # Build the Anki sound field: [sound:filename1.mp3][sound:filename2.mp3] ...
        sounds_field = ''.join([f'[sound:{fname}]' for fname in sound_filenames])
        # Add all sound files to media
        media_files.extend(sound_paths)

        # Use image filename as a short unique ID (Field 1) to avoid Anki
        # merging notes on identical Field 1 checksums. The image HTML is kept
        # in Field 2 so the card shows correctly.
        uid = img_filename
        note = genanki.Note(
            model=my_model,
            fields=[
                uid,
                f'<img src="{img_filename}">',  # Image field
                hebrew_name or '',
                latin_name or '',
                family or '',
                sounds_field,
            ]
        )
        deck.add_note(note)

    # Remove duplicates from media_files
    media_files = list(dict.fromkeys(media_files))

    # Package the deck with media
    print(f"Packaging deck with {len(media_files)} media files (images + sounds)...")
    genanki.Package(deck, media_files).write_to_file(OUTPUT_FILE)
    print(f"Anki deck generated: {OUTPUT_FILE}")

    # --- Create per-family decks ---
    print("Creating per-family decks...")
    # ensure decks directory exists
    decks_dir = "decks"
    os.makedirs(decks_dir, exist_ok=True)
    # Build mapping: family -> list of rows (image_path, species_id, hebrew, latin, family)
    family_map = {}
    for img_path, species_id, hebrew_name, latin_name, family in rows:
        fam_key = family or 'UnknownFamily'
        family_map.setdefault(fam_key, []).append((img_path, species_id, hebrew_name, latin_name, family))

    def sanitize_name(name):
        # Simple filename-safe sanitizer
        return ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')

    import hashlib

    for fam, items in family_map.items():
        # skip small families
        if len(items) < 3:
            print(f"Skipping family '{fam}' with only {len(items)} items (<3)")
            continue
        fam_safe = sanitize_name(fam)
        # Deterministic deck id from family name
        fam_hash = int(hashlib.sha1(fam.encode('utf-8')).hexdigest()[:8], 16)
        fam_deck_id = DECK_ID + fam_hash
        fam_deck_name = f"Birds of Israel - {fam}"
        fam_deck = genanki.Deck(fam_deck_id, fam_deck_name)
        fam_media = []
        for img_path, species_id, hebrew_name, latin_name, family in items:
            if not os.path.exists(img_path):
                continue
            img_filename = os.path.basename(img_path)
            fam_media.append(img_path)
            cur.execute("SELECT file_path FROM sounds WHERE species_id=? AND file_path IS NOT NULL AND file_path != ''", (species_id,))
            sound_paths = [row[0] for row in cur.fetchall() if os.path.exists(row[0])]
            sound_filenames = [os.path.basename(p) for p in sound_paths]
            sounds_field = ''.join([f'[sound:{fname}]' for fname in sound_filenames])
            fam_media.extend(sound_paths)
            uid = img_filename
            note = genanki.Note(
                model=my_model,
                fields=[
                    uid,
                    f'<img src="{img_filename}">',
                    hebrew_name or '',
                    latin_name or '',
                    family or '',
                    sounds_field,
                ]
            )
            fam_deck.add_note(note)
        fam_media = list(dict.fromkeys(fam_media))
        fam_filename = os.path.join(decks_dir, f"Birds_of_Israel_{fam_safe}.apkg")
        print(f"Packaging family deck '{fam_deck_name}' with {len(fam_media)} media files -> {fam_filename}")
        genanki.Package(fam_deck, fam_media).write_to_file(fam_filename)
    print("Per-family decks created.")

if __name__ == "__main__":
    main()
