# 🐦 Bird Recognition Flashcard Tool – Updated LLM Instructions

## 1. Goal
Help me build a tool that:
- Collects structured bird data from **birds.org.il** using its **JSON API**.
- Stores Hebrew name, Latin name, family, images, and audio when available.
- Organizes images so that each image → one Anki flashcard.
- Generates an **Anki deck** (APKG or CSV) with:
  - **Front**: bird image
  - **Back**: Hebrew name + Latin name (and optionally family name, conservation level, etc.)

---

## 2. Data Source (confirmed)
- API endpoint per species:
  ```
  https://www.birds.org.il/api/{species_id}
  ```
  Example: `/api/4` returns the **Black Francolin**.

- Each response includes:
  - `"name"` → Hebrew name
  - `"latinName"` → Latin name
  - `"speciesFamilyName"` → family in Hebrew
  - `"images"` → multiple image URLs
  - `"sounds"` → audio references
  - `"videos"` → YouTube links
  - `"shortDescription"` and `"description"` → Hebrew text
  - `"relatedSpecies"`, `"moreFromFamily"` → navigation
  - `"latestObservations"` → sightings data

---

## 3. Data to Collect
For each species ID:
- Hebrew name
- Latin name
- Family name
- All image URLs (`images[]` and `largeImage[]`)
- Audio (`sounds[]`)
- Optional: description (Hebrew), conservation level, related species

Each image should map to one flashcard entry.

---

## 4. Implementation Plan
1. **Discover species IDs**
   - Either iterate sequential IDs (1 → N) or collect from `/api` endpoints if available.
   - Skip invalid IDs (returning errors).

2. **Fetch JSON** for each valid species ID.

3. **Download media**
   - Save images into structured folders:
     ```
     birds/{family}/{species}/img1.jpg
     ```
   - Optionally download sounds (MP3/WAV if accessible).

4. **Database / Storage**
   - Use **SQLite** or JSON/CSV files.
   - Suggested schema:

     ```sql
     CREATE TABLE species (
       id INTEGER PRIMARY KEY,
       hebrew_name TEXT,
       latin_name TEXT,
       family TEXT,
       description TEXT,
       conservation TEXT
     );

     CREATE TABLE images (
       id INTEGER PRIMARY KEY,
       species_id INTEGER,
       url TEXT,
       file_path TEXT,
       FOREIGN KEY(species_id) REFERENCES species(id)
     );
     ```

5. **Generate Anki deck**
   - Use `genanki` or export CSV.
   - Card front = image.
   - Card back = Hebrew + Latin name (and optionally description, family, sound).

6. **Validation & Testing**
   - Test on a few species first.
   - Check Anki import.
   - Ensure UTF-8 encoding for Hebrew text.

---

## 5. Tools to Use
- **Python 3**
- Libraries:
  - `requests` (API calls)
  - `sqlite3` (database)
  - `genanki` (Anki deck generation)
  - `pydub` (optional: handle audio)

---

## 6. How LLM Should Help Me
When I ask, the LLM should:
- Write Python functions to fetch species JSON by ID.
- Parse and save the relevant fields (name, latin, family, images, sounds).
- Implement retry & error handling for API calls.
- Download and store images locally with proper filenames.
- Build the SQLite DB or CSV.
- Generate an Anki deck with one card per image.
- Suggest improvements (e.g., add sounds to cards, extra fields).

