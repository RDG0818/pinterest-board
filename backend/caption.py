import os
import json
from hashlib import md5
from collections import defaultdict
from PIL import Image
from tqdm import tqdm
import time
import google.generativeai as genai
from backend import create_connection, create_table

MIN_WIDTH = 512
MIN_HEIGHT = 512
INPUT_DIR = "backend/image_dataset"
CACHE_PATH = "backend/cache.json"
TAG_VOCABULARY = [
    "Dragon", "Griffin", "Undead", "Demon", "Angel", "Monster", "Goblin", "Elf", "Dwarf", "Human",
    "Castle", "Forest", "Mountain", "Ruins", "City", "Dungeon", "Ocean", "Swamp", "Cave", "Sky",
    "Knight", "Wizard", "Sorceress", "Rogue", "King", "Queen", "Warrior",
    "Epic", "Dark", "Mysterious", "Peaceful", "Magical", "Battle", "War",
    "Sword", "Armor", "Magic", "Spell", "Fire", "Ice", "Lightning"
]

def get_analysis_prompt(vocabulary):
    """Constructs the full prompt with the tag vocabulary embedded."""
    allowed_tags = ", ".join(f'"{tag}"' for tag in vocabulary) # Enclose in quotes for clarity
    
    return f"""
You are a meticulous visual analyst AI specializing in fantasy art. Your task is to analyze the provided image and return a single, valid JSON object. Do not include any other text or explanations.

The JSON object must contain two top-level keys: "caption" and "analysis".

1.  The "caption" key should contain a detailed and vivid paragraph of at least 100 words describing the image, grounded in visual evidence.

2.  The "analysis" key should contain a nested JSON object with the following seven keys, based on the provided definitions:

    - "fantasy_scale": Choose ONE of the following strings: ["Small Scale", "Medium Scale", "Large Scale"].
        - "Small Scale": Focus on 1-2 subjects.
        - "Medium Scale": 3-6 subjects or a moderately-sized environment.
        - "Large Scale": 7+ subjects, vast landscapes, or massive structures.

    - "fantasy_mood": Choose ONE of the following strings: ["Light Fantasy", "Medium Fantasy", "Dark Fantasy"].
        - "Light Fantasy": Bright, happy, peaceful themes.
        - "Medium Fantasy": Standard adventure or neutral themes.
        - "Dark Fantasy": Grim, horror, or unsettling elements.

    - "magic_level": Choose ONE of the following strings: ["Low Magic", "Medium Magic", "High Magic"].
        - "Low Magic": No obvious magic; realistic scenes.
        - "Medium Magic": Subtle or ambiguous magical elements.
        - "High Magic": Overt spells, fantastical creatures, or impossible landscapes.

    - "art_style": Choose the ONE best-fitting string from this list: ["Photorealistic", "Stylized Realism", "Painterly", "Illustration with Line Art", "Anime/Manga Style", "Concept Art Sketch"].

    - "tags": An array of strings, choosing the most relevant tags for the artwork. You MUST only choose from this allowed list: [{allowed_tags}]

    - "dominant_colors": An array of 3-5 strings describing the most prominent colors by name (e.g., "Crimson Red", "Forest Green", "Royal Gold").
    
    - "detail_score": An integer from 1 to 10, where 1 is a very simple sketch and 10 is a highly detailed, complex scene.

    - "mood_score": An integer from 1 to 10, where 1 is pure dark fantasy and 10 is pure light fantasy.

    - "magic_score": An integer from 1 to 10, where 1 is absolute low magic and 10 is overwhelming high magic.

    - "scale_score": An integer from 1 to 10, where 1 is a tight Small Scale close-up and 10 is a vast large scale scene.

Your entire output must be ONLY the raw JSON object.
"""

def analyze_and_caption_image(image_path, model, prompt):
    img = Image.open(image_path)
    try:
        response = model.generate_content(
            [prompt, img],
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except (Exception, json.JSONDecodeError) as e:
        print(f"  -> Gemini analysis/caption failed: {e}")
        return None

def title(caption_text, model):
    prompt = f"""
    You are a fantasy world-builder and a master of naming things. Your task is to create a short, evocative, and imaginative title for a piece of fantasy art based on its description.
    The title should be thematic and hint at a larger story, not just be a literal summary. It should be 2-6 words long.
    Here are examples of the desired style:
    - City of Ruins
    - Monster in the Field
    - Raging Tides
    - The Last Spellcaster
    - Whispers in the Deepwood
    Now, based on the following description, provide only the title itself. Do not include quotes, explanations, or any other text.
    Description:
    \"\"\"{caption_text}\"\"\"
    Imaginative Title:
    """.strip()
    
    try:
        response = model.generate_content(prompt)
        raw_name = response.text.strip().strip('"')
        final_name = ' '.join(word.capitalize() for word in raw_name.split())
        return final_name
    except Exception as e:
        print(f"  -> Gemini title failed: {e}")
        return "Untitled"

def get_file_hash(image_path):
    with open(image_path, "rb") as f:
        return md5(f.read()).hexdigest()

def run_batch_processor():
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("✅ Gemini API configured successfully.")
    except Exception as e:
        print(f"🔥 Failed to configure Gemini API: {e}")
        return

    master_prompt = get_analysis_prompt(TAG_VOCABULARY)

    print("--- Pass 1: Finding and removing duplicate images ---")
    hashes = defaultdict(list)
    initial_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    for filename in tqdm(initial_files, desc="Hashing files"):
        path = os.path.join(INPUT_DIR, filename)
        if os.path.exists(path): hashes[get_file_hash(path)].append(path)
    for paths in hashes.values():
        if len(paths) > 1:
            for duplicate_path in paths[1:]:
                print(f"Removing duplicate: {os.path.basename(duplicate_path)}")
                os.remove(duplicate_path)
    
    print("\n--- Pass 2: Processing, renaming, and generating metadata ---")
    conn = create_connection()
    cursor = conn.cursor()

    remaining_files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
    
    for filename in tqdm(remaining_files, desc="Processing Images"):
        image_path = os.path.join(INPUT_DIR, filename)
        try:
            with Image.open(image_path) as img: width, height = img.size
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                print(f"\nImage {filename} is too small ({width}x{height}). Removing.")
                os.remove(image_path)
                continue
        except Exception as e:
            print(f"\nCould not read image {filename}: {e}. Removing.")
            if os.path.exists(image_path): os.remove(image_path)
            continue
            
        image_hash = get_file_hash(image_path)
        cursor.execute("SELECT hash FROM images WHERE hash = ?", (image_hash,))
        if cursor.fetchone():
            continue

        print(f"\nProcessing new image: {filename}")
        all_data = analyze_and_caption_image(image_path, model, master_prompt)
        time.sleep(5)

        if not all_data:
            print("  -> Skipping image due to analysis failure.")
            continue

        image_caption = all_data.get("caption", "No caption generated.")
        analysis_data = all_data.get("analysis", {})

        image_title = title(image_caption, model)
        time.sleep(5)
        
        # Renaming Logic
        original_extension = os.path.splitext(filename)[1]
        safe_title = image_title.replace(' ', '_').replace("'", "") 
        new_filename = f"{safe_title}{original_extension}"
        new_path = os.path.join(INPUT_DIR, new_filename)
        count = 1
        while os.path.exists(new_path):
            count += 1
            new_filename = f"{safe_title}_{count}{original_extension}"
            new_path = os.path.join(INPUT_DIR, new_filename)
            
        os.rename(image_path, new_path)
        print(f"Renamed '{filename}' to '{new_filename}'")

        tags_list = analysis_data.get("tags", [])
        tags_string = ",".join(tags_list)
        colors_string = ",".join(analysis_data.get("dominant_colors", []))
        
        cursor.execute("""
            INSERT INTO images (
                hash, filename, title, caption, art_style, 
                fantasy_mood, fantasy_scale, magic_level, tags,
                dominant_colors, detail_score, mood_score, magic_score, scale_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image_hash, new_filename, image_title, image_caption,
            analysis_data.get("art_style"),
            analysis_data.get("fantasy_mood"),
            analysis_data.get("fantasy_scale"), # <<< CHANGED >>> Corrected from image_scale
            analysis_data.get("magic_level"),
            tags_string,
            colors_string,
            analysis_data.get("detail_score"),
            analysis_data.get("mood_score"),
            analysis_data.get("magic_score"),
            analysis_data.get("scale_score")
        ))
        conn.commit()
    
    conn.close()
    print("\n✅ Processing complete.")

if __name__ == "__main__":
    create_table()
    run_batch_processor()