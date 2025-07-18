import os
import sqlite3
import json
import numpy as np
from mutagen.mp3 import MP3

# --- CONFIG ---
IMAGE_DIR = "backend/image_dataset"
AUDIO_DIR = "backend/audio_dataset"
DB_PATH = "backend/db.sqlite"

# --- HELPER: Dummy embedding (for now) ---
def dummy_embedding(dim=128):
    return np.random.rand(dim).astype(np.float32).tobytes()

# --- SETUP DB ---
def create_tables(conn):
    cur = conn.cursor()

    # Images table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        filename TEXT UNIQUE,
        title TEXT,
        tags TEXT,
        mood TEXT,
        style TEXT,
        chart_x REAL,
        chart_y REAL,
        chart_r REAL,
        embedding BLOB
    )""")

    # Audio table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audio_tracks (
        id INTEGER PRIMARY KEY,
        filename TEXT UNIQUE,
        title TEXT,
        mood TEXT,
        duration REAL,
        filepath TEXT
    )""")

    # Image-Audio matching table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS image_audio_matches (
        id INTEGER PRIMARY KEY,
        image_id INTEGER,
        audio_id INTEGER,
        FOREIGN KEY (image_id) REFERENCES images(id),
        FOREIGN KEY (audio_id) REFERENCES audio_tracks(id)
    )""")

    # Optional similarity table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS image_similarity (
        id INTEGER PRIMARY KEY,
        image_id_a INTEGER,
        image_id_b INTEGER,
        similarity_score REAL,
        FOREIGN KEY (image_id_a) REFERENCES images(id),
        FOREIGN KEY (image_id_b) REFERENCES images(id)
    )""")

    conn.commit()

# --- POPULATE AUDIO TABLE ---
def populate_audio(conn):
    cur = conn.cursor()

    for fname in os.listdir(AUDIO_DIR):
        if not fname.lower().endswith(".mp3"):
            continue

        filepath = os.path.join(AUDIO_DIR, fname)
        relpath = os.path.relpath(filepath, start="backend")
        try:
            audio = MP3(filepath)
            duration = audio.info.length
        except:
            duration = None

        title = os.path.splitext(fname)[0]  # Keep exact title from cleaned filename

        cur.execute("""
        INSERT OR IGNORE INTO audio_tracks (filename, title, mood, duration, filepath)
        VALUES (?, ?, ?, ?, ?)
        """, (fname, title, None, duration, relpath))

    conn.commit()

# --- POPULATE IMAGE TABLE ---
def populate_images(conn):
    cur = conn.cursor()
    for fname in os.listdir(IMAGE_DIR):
        if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue

        title = os.path.splitext(fname)[0]  # Already cleaned, use as-is

        cur.execute("""
        INSERT OR IGNORE INTO images (filename, title, tags, mood, style, chart_x, chart_y, chart_r, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fname,
            title,
            json.dumps(["placeholder"]),
            "placeholder",
            "placeholder",
            np.random.uniform(-100, 100),
            np.random.uniform(0, 100),
            np.random.uniform(5, 15),
            dummy_embedding()
        ))

    conn.commit()

# --- MAIN ---
def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    populate_audio(conn)
    populate_images(conn)
    conn.close()
    print(f"✅ Database created and populated at {DB_PATH}")


if __name__ == "__main__":
    main()
