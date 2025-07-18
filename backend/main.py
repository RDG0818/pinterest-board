from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random
from urllib.parse import urlparse
import os
from typing import List
from backend import create_connection
import chromadb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    client = chromadb.PersistentClient(path="backend/chroma_db")
    collection = client.get_collection(name="fantasy_vibes")
    print("ChromaDB client connected successfully.")
except Exception as e:
    collection = None
    print(f"Failed to connect to ChromaDB: {e}")

app.mount("/static/images", StaticFiles(directory="backend/image_dataset"), name="images")
app.mount("/static/audio", StaticFiles(directory="backend/audio_dataset"), name="audio")

@app.get("/api/v1/images")
def get_image_list():
    """Returns a list of all image URLs."""
    image_dir = "backend/image_dataset"
    base_url = "http://127.0.0.1:8000"
    
    if not os.path.exists(image_dir):
        return []

    image_files = os.listdir(image_dir)

    image_urls = [f"{base_url}/static/images/{filename}" for filename in image_files]
    
    return image_urls


@app.get("/get-tags/")
def get_tags(filename: str):
    """Gets tags for an image by its filename."""
    conn = create_connection()
    row = conn.execute("SELECT tags FROM images WHERE filename = ?", (filename,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Image not found by that filename")

    tags_list = row["tags"].split(',') if row["tags"] else []
    
    return {
        "filename": filename,
        "tags": tags_list
    }

class ImageList(BaseModel):
    image_sources: List[str]


@app.post("/get-chart-data/")
def get_chart_data(image_list: ImageList):
    """
    Generates chart data for a specific list of favorite images.
    """
    conn = create_connection()
    chart_data = []
    base_url = "http://127.0.0.1:8000"

    for src in image_list.image_sources:
        filename = src.split('/')[-1]
        
        row = conn.execute("SELECT * FROM images WHERE filename = ?", (filename,)).fetchone()

        first_color = "red" 

        if row:
            if row["dominant_colors"]: first_color = row["dominant_colors"].split(',')[0]
            data_point = {
                "x": row["mood_score"] or 5, 
                "y": row["magic_score"] or 5,
                "r": row["scale_score"] or 5,
                "style": row["art_style"],
                "label": row["title"],
                "imageSrc": src,
                "color": first_color,
                "id": f"/static/images/{row['filename']}"
            }
            chart_data.append(data_point)
            
    conn.close()
    return chart_data

@app.get("/match-music/")
def match_music(image_id: str):
    """
    Finds the 3 best-matching songs for a given image using vector similarity search.
    The image_id should be the unique hash of the image.
    """
    if not collection:
        raise HTTPException(status_code=503, detail="Vector database is not available.")

    try:
        image_path = urlparse(image_id).path
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image_id format.")

    # 1. Get the image's embedding from ChromaDB using its path
    image_vector_data = collection.get(ids=[image_path], include=["embeddings"])
    if not image_vector_data or not image_vector_data.get('ids'):
        raise HTTPException(status_code=404, detail=f"Image path not found in vector DB: {image_path}")
    
    image_embedding = image_vector_data['embeddings'][0]

    # 2. Query for the 3 most similar audio files
    results = collection.query(
        query_embeddings=[image_embedding],
        n_results=3,
        where={"type": "audio"}
    )
    
    song_filenames = results['ids'][0] if results and results['ids'] else []

    if not song_filenames:
        return []

    # 3. Get song details from SQLite and format the response
    conn = create_connection()
    response_songs = []
    for filename in song_filenames:
        row = conn.execute("SELECT title, mood FROM audio WHERE filename = ?", (filename,)).fetchone()
        if row:
            response_songs.append({
                "song_title": row["title"],
                "audio_url": f"/static/audio/{filename}",
                "mood": row["mood"],
                "matched_image_id": image_id
            })
    conn.close()

    return response_songs