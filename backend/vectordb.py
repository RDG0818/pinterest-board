# backend/populate_vectordb.py
import chromadb
import sqlite3
import json
import os
import google.generativeai as genai
from tqdm import tqdm

DATABASE_FILE = "backend/fantasy_board.db"
CHROMA_PATH = "backend/chroma_db"
# Ensure the API key is set in your environment
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_text_embedding(text):
    """Generates a vector embedding for a given text."""
    try:
        result = genai.embed_content(model="models/text-embedding-004", content=text, task_type="RETRIEVAL_QUERY")
        return result['embedding']
    except Exception as e:
        print(f"  -> Embedding generation failed: {e}")
        return None

# --- Setup ChromaDB ---
client = chromadb.PersistentClient(path=CHROMA_PATH)
if "fantasy_vibes" in [c.name for c in client.list_collections()]:
    print("Collection 'fantasy_vibes' already exists. Deleting to repopulate.")
    client.delete_collection(name="fantasy_vibes")

collection = client.create_collection(name="fantasy_vibes")
conn = sqlite3.connect(DATABASE_FILE)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# --- Process and Add Images ---
print("Processing images...")
cursor.execute("SELECT * FROM images")
images = cursor.fetchall()
for image in tqdm(images, desc="Adding Images to Chroma"):
    text_to_embed = f"""
    Art piece titled '{image['title']}'.
    Style: {image['art_style']}, {image['fantasy_mood']}, {image['fantasy_scale']}, {image['magic_level']}.
    Tags: {image['tags']}.
    Description: {image['caption']}
    """
    embedding = get_text_embedding(text_to_embed)
    
    if embedding:
        # --- MODIFICATION ---
        # Use the static URL path as the unique ID for the image
        image_id = f"/static/images/{image['filename']}"
        
        collection.add(
            embeddings=[embedding],
            metadatas=[{"type": "image", "filename": image['filename']}],
            ids=[image_id] # Use the path as the ID instead of the hash
        )

# --- Process and Add Audio ---
print("\nProcessing audio...")
cursor.execute("SELECT * FROM audio")
audios = cursor.fetchall()
for audio in tqdm(audios, desc="Adding Audio to Chroma"):
    embedding = json.loads(audio['embedding'])
    collection.add(
        embeddings=[embedding],
        metadatas=[{"type": "audio", "title": audio['title']}],
        ids=[audio['filename']]
    )

conn.close()
print(f"\n✅ ChromaDB populated with {collection.count()} items.")