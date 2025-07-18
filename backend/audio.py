# backend/audio.py
import os
import google.generativeai as genai
import sqlite3
from tqdm import tqdm
import json
from backend import create_audio_table
import time

AUDIO_DIR = "backend/audio_dataset"
DATABASE_FILE = "backend/fantasy_board.db"

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')
embedding_model = genai.GenerativeModel('models/text-embedding-004')


def get_audio_analysis(audio_file_path, title):
    """Analyzes an audio file given its title and returns a structured JSON description."""
    prompt = f"""
    You are a music analysis expert for fantasy worlds. The provided audio track is titled "{title}".
    Listen to the audio and return a single, valid JSON object that analyzes its "vibe", taking the title into account.

    The JSON object must have the following keys:
    - "mood": The primary emotion (e.g., "Epic Battle," "Mysterious Forest," "Somber Journey," "Triumphant Celebration").
    - "genre": The musical style (e.g., "Orchestral," "Ambient," "Cinematic," "Folk").
    - "instruments": A comma-separated list of the 3-5 most prominent instruments (e.g., "Strings,Horns,Timpani Drums,Choir").
    - "description": A short paragraph describing the overall feeling and a scene this music would fit, informed by both the audio and its title.

    Return ONLY the raw JSON object.
    """
    try:
        audio_file = genai.upload_file(path=audio_file_path)
        response = vision_model.generate_content(
            [prompt, audio_file],
            generation_config={"response_mime_type": "application/json"}
        )
        genai.delete_file(audio_file.name)
        return json.loads(response.text)
    except Exception as e:
        print(f"  -> Audio analysis failed for {os.path.basename(audio_file_path)}: {e}")
        return None

def get_text_embedding(text):
    """Generates a vector embedding for a given text."""
    try:
        result = genai.embed_content(model="models/text-embedding-004", content=text)
        return json.dumps(result['embedding']) # Store as JSON string
    except Exception as e:
        print(f"  -> Embedding generation failed: {e}")
        return None

def process_all_audio():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    audio_files = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(('.mp3', '.wav'))]

    for filename in tqdm(audio_files, desc="Processing Audio Files"):
        time.sleep(5) 
        # Check if already processed
        cursor.execute("SELECT filename FROM audio WHERE filename = ?", (filename,))
        if cursor.fetchone():
            continue

        print(f"\nProcessing new audio: {filename}")
        file_path = os.path.join(AUDIO_DIR, filename)
        audio_title = os.path.splitext(filename)[0].replace('_', ' ')
        
        analysis = get_audio_analysis(file_path, audio_title)
        if not analysis:
            continue

        full_description = f"Title: {audio_title}. Mood: {analysis.get('mood')}. Genre: {analysis.get('genre')}. {analysis.get('description')}"
        
        embedding = get_text_embedding(full_description)
        if not embedding:
            continue

        cursor.execute("""
            INSERT INTO audio (filename, title, mood, genre, instruments, description, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            filename,
            audio_title, 
            analysis.get('mood'),
            analysis.get('genre'),
            analysis.get('instruments'),
            analysis.get('description'),
            embedding
        ))
        conn.commit()

    conn.close()
    print("\n✅ Audio processing complete.")

if __name__ == "__main__":
    process_all_audio()