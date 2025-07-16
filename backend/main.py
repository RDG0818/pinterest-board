from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random
import os
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/images", StaticFiles(directory="backend/image_dataset"), name="images")

@app.get("/api/v1/images")
def get_image_list():
    """Returns a list of all image URLs."""
    image_dir = "backend/image_dataset"
    base_url = "http://127.0.0.1:8000"
    
    # Check if the directory exists to prevent a server error
    if not os.path.exists(image_dir):
        return []

    image_files = os.listdir(image_dir)
    
    # CORRECTED: The URL path now matches the app.mount path
    image_urls = [f"{base_url}/static/images/{filename}" for filename in image_files]
    
    return image_urls


@app.get("/get-tags/")
def get_tags(image_id: str):
    # TODO: Replace with actual ML model logic later
    # For now, return a few random/fixed tags
    return {
        "image_id": image_id,
        "tags": ["castle", "dragon", "armor", "fog"]
    }

class ImageList(BaseModel):
    image_sources: List[str]

@app.post("/get-chart-data/")
def get_chart_data(image_list: ImageList):
    """
    Generates placeholder chart data for a specific list of images.
    """
    styles = ['watercolor', 'digital', 'oil', 'sketch', 'pixel']
    chart_data = []
    
    # Use the list of images provided by the frontend
    for src in image_list.image_sources:
        label = src.split('/')[-1].split('.')[0]
        
        data_point = {
            "x": random.randint(-100, 100),
            "y": random.randint(0, 100),
            "r": random.randint(5, 15),
            "style": random.choice(styles),
            "label": label,
            "imageSrc": src
        }
        chart_data.append(data_point)
        
    return chart_data

@app.get("/match-music/")
def match_music(image_id: str):
    # TODO: Replace with ML-based logic
    return [
        {
            "song_title": "Battle Hymn of the Elf Lords",
            "audio_url": "/audio/mystic-river.mp3",
            "mood": "epic war",
            "matched_image_id": image_id
        },
        {
            "song_title": "Mystic Riverwalk",
            "audio_url": "/audio/mystic-river.mp3",
            "mood": "peaceful exploration",
            "matched_image_id": image_id
        },
        {
            "song_title": "Ancient Spellcast",
            "audio_url": "/audio/mystic-river.mp3",
            "mood": "magical ritual",
            "matched_image_id": image_id
        }
    ]