import os
from pathlib import Path
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from tqdm import tqdm

# --- 1. Configuration ---

# Define the text prompts that describe your categories.
# Be descriptive! The more detail, the better.
GOOD_PROMPTS = [
    "A high-resolution, atmospheric digital painting of a fantasy landscape.",
    "Cinematic lighting, epic scale, and high detail fantasy art.",
    "A beautiful, awe-inspiring, and cohesive fantasy illustration.",
    "A moody and atmospheric painting of a haunted forest at dusk, with ethereal light filtering through ancient trees.",
    "A dramatic and cinematic fantasy scene with volumetric lighting and a sense of epic scale.",
    "An enchanting and magical landscape painting with vibrant, glowing flora and a serene mood.",
    "A dark, foreboding, and grim illustration of a lich's tomb, with visible textures of cold stone and decay.",
    "A photorealistic, detailed portrait of a stoic dwarf warrior with a braided beard and intricate, worn armor.",
    "A majestic and powerful dragon with iridescent scales, perched on a mountain peak against a stormy sky.",
    "An elegant and ethereal elf archer with glowing magical arrows, rendered in a realistic style.",
    "A horrifying and grotesque demon with leathery wings and molten eyes, painted in a dark fantasy style.",
    "Dynamic digital art of a massive medieval battle, with smoke and magical energy filling the air.",
    "A beautifully rendered fantasy city with towering spires and intricate architecture, reminiscent of Tolkien.",
    "A painting of a powerful magic spell being cast, with glowing runes and explosive elemental effects.",
    "A cohesive digital painting with a clear focal point and professional-level rendering.",
    "Artwork with a masterful use of color theory and composition.",
    "A detailed fantasy illustration in the style of Frank Frazetta or Brom.",
    "A texture-heavy digital painting emphasizing the grit and grime of medieval life, with visible rust on armor and dirt on clothing.",
    "A lone, weary knight in dented, mud-spattered plate armor, resting by a meager campfire.",
    "Artwork with a dark, grounded, and realistic tone, reminiscent of historical concept art.",
    "A mercenary with a scarred face and functional, worn leather gear, depicted with realistic anatomy.",
    "A castle under siege, focusing on the chaos and destruction, with dramatic chiaroscuro lighting.",
    "A cinematic illustration of a colossal dragon, its shadow blanketing the valley below.",
    "An epic digital painting capturing the immense scale of a kraken attacking a fleet of ships.",
    "A painting of a gargantuan titan or giant striding over a mountain range.",
    "Artwork depicting a massive world serpent coiling around a castle.",
    "A dramatic scene showing a tiny figure on a cliff looking up at a titanic, awe-inspiring beast.",
    "An ancient, monolithic stone elemental so large it is mistaken for a walking mountain."
]

BAD_PROMPTS = [
    "A blurry, low-resolution, or pixelated image.",
    "A photo of a person, a meme, or a screenshot.",
    "An image with a large, ugly watermark or distracting text.",
    "A sketch, line art, or unfinished-looking artwork.",
    "A 3D model with flat, unnatural, plastic-like textures and poor lighting.",
    "An image with muddy colors, poor composition, or an unclear subject.",
    "A digitally compressed image with noticeable JPEG artifacts, pixelation, or blurriness.",
    "Artwork with disproportionate anatomy or amateurish perspective.",
    "A photograph of a person in cosplay, not a digital or traditional painting.",
    "An abstract or overly surreal painting with unrecognizable forms.",
    "A character sheet with multiple views of the same character.",
    "An orthographic character turnaround or model sheet on a plain white background.",
    "Concept art showing front, side, and back views of a character.",
    "A reference sheet with text annotations, color swatches, or callout lines.",
    "Multiple separate drawings or sketches of one character on a single image.",
    "Images that look like the came from a comic book or contain text bubbles",
    "Black and white concept art images.",
    "A character or object on a plain white, gray, or transparent background.",
    "A black and white, grayscale, or monochrome illustration.",
    "A pencil sketch, ink line art, or charcoal drawing without color.",
    "A hand-drawn fantasy map, a regional diagram, or a blueprint.",
    "An inventory screen, an item chart, or a UI design element.",
    "A stylized cartoon with simple shapes and exaggerated features.",
    "Artwork with a cel-shaded or comic book art style with thick outlines.",
    "A posed group shot of multiple characters, like a movie poster or book cover.",
    "An image with a prominent logo or stylized title text overlaying the artwork.",
    "A character lineup or promotional splash art for a game or series."
]

# --- 2. File Paths ---
# Use Path for robust file system operations.
# The script assumes it's running in the 'image_sorter' directory.
script_dir = Path(__file__).resolve().parent

# All other paths are now correctly based off the script's location.
process_dir = script_dir / "to_process"
reference_dir = script_dir / "reference_images"
output_dir = script_dir / "classified_output"

# Define reference image paths
good_ref_dir = reference_dir / "good"
bad_ref_dir = reference_dir / "bad"

# Define output paths
good_output_dir = output_dir / "good"
bad_output_dir = output_dir / "bad"
not_sure_output_dir = output_dir / "not_sure"
    

# Create output directories if they don't exist
good_output_dir.mkdir(parents=True, exist_ok=True)
bad_output_dir.mkdir(parents=True, exist_ok=True)
not_sure_output_dir.mkdir(parents=True, exist_ok=True)

# --- 3. The Core Logic ---

def get_image_paths(directory):
    """Returns a list of all image file paths in a directory."""
    return [p for p in directory.glob('*') if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')]

def create_category_prototype(model, image_paths, text_prompts):
    """
    Creates a single "prototype" vector for a category by averaging the
    embeddings of its reference images and text prompts.
    """
    # Encode all text prompts
    text_embeddings = model.encode(text_prompts, convert_to_tensor=True)
    
    # Encode all reference images
    image_embeddings = []
    if image_paths:
        for img_path in image_paths:
            img = Image.open(img_path)
            # Handle images with alpha channels (RGBA)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            emb = model.encode(img, convert_to_tensor=True)
            image_embeddings.append(emb)
    
    # Combine all embeddings into one list
    all_embeddings = text_embeddings.tolist() + [emb.tolist() for emb in image_embeddings]
    
    if not all_embeddings:
        raise ValueError(f"No reference images or text prompts provided for a category.")

    # Calculate the average embedding
    prototype_vector = np.mean(all_embeddings, axis=0).astype(np.float32)
    return prototype_vector


def main():
    """Main function to run the classification process."""
    print("🚀 Starting image classification process...")

    # --- 1. Configuration for Thresholds ---
    # The image must have at least this score to be considered a confident match.
    CONFIDENCE_THRESHOLD = 0.26 
    # If the good and bad scores are closer than this, the model is "not sure".
    SCORE_DIFFERENCE_THRESHOLD = 0.02

    print("Loading CLIP model... (This might take a moment on first run)")
    model = SentenceTransformer('clip-ViT-L-14')

    # --- Create Prototypes (No changes to this part) ---
    print("Analyzing reference images and text prompts to create prototypes...")
    # ... (rest of the prototype creation logic is the same) ...
    good_ref_paths = get_image_paths(good_ref_dir)
    bad_ref_paths = get_image_paths(bad_ref_dir)
    good_prototype = create_category_prototype(model, good_ref_paths, GOOD_PROMPTS)
    bad_prototype = create_category_prototype(model, bad_ref_paths, BAD_PROMPTS)


    # --- Classify New Images with Updated Logic ---
    images_to_process = get_image_paths(process_dir)
    if not images_to_process:
        print("No images found in the 'to_process' folder. Exiting.")
        return
        
    print(f"Found {len(images_to_process)} images to classify. Starting...")
    
    for img_path in tqdm(images_to_process, desc="Classifying Images"):
        try:
            img = Image.open(img_path)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            img_embedding = model.encode(img).astype(np.float32)
            
            good_sim = cos_sim(img_embedding, good_prototype)[0][0].item()
            bad_sim = cos_sim(img_embedding, bad_prototype)[0][0].item()

            # --- 3. New Classification Logic ---
            highest_score = max(good_sim, bad_sim)
            score_difference = abs(good_sim - bad_sim)

            destination = None
            if highest_score < CONFIDENCE_THRESHOLD:
                # If the model isn't confident about any category, it's "not sure".
                destination = not_sure_output_dir / img_path.name
            elif score_difference < SCORE_DIFFERENCE_THRESHOLD:
                # If the scores are too close, the model is ambivalent, so it's "not sure".
                destination = not_sure_output_dir / img_path.name
            elif good_sim > bad_sim:
                # If it passes the checks and "good" is higher, it's a confident "good".
                destination = good_output_dir / img_path.name
            else:
                destination = bad_output_dir / img_path.name
            
            img_path.rename(destination)
            
        except Exception as e:
            print(f"Could not process {img_path.name}. Error: {e}")

    print("\n✅ Classification complete!")
    print(f"Sorted images can be found in '{output_dir}'.")

if __name__ == "__main__":
    main()