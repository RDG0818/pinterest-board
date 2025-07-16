import praw
import requests
import os
from dotenv import load_dotenv

load_dotenv()
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.webp')

TARGET_SUBREDDIT = "ImaginaryBestOf"
POST_LIMIT = 100
IMAGE_DIR = "backend/image_sorter/to_process"
other_dir = "backend/image_sorter"
REVIEW_FILE = os.path.join(other_dir, "links_to_review.txt")

try:
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT'),
        username=os.getenv('REDDIT_USERNAME'),
        password=os.getenv('REDDIT_PASSWORD')
    )
    print("Authenticated as:", reddit.user.me())
except Exception as e:
    print(f"Authentication failed. Error: {e}")
    exit()

SAVE_PATH = IMAGE_DIR
os.makedirs(SAVE_PATH, exist_ok=True)

if os.path.exists(REVIEW_FILE):
    os.remove(REVIEW_FILE)

print(f"Downloading top {POST_LIMIT} image posts from r/{TARGET_SUBREDDIT}...")
print(f"Skipped posts will be saved to '{REVIEW_FILE}' for manual review.")

subreddit = reddit.subreddit(TARGET_SUBREDDIT)
downloaded_count = 0
review_count = 0

for submission in subreddit.hot(limit=POST_LIMIT):
    if submission.stickied:
        continue

    safe_title = "".join([c for c in submission.title if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()[:80]
    was_downloaded = False

    if hasattr(submission, 'is_gallery') and submission.is_gallery:
        gallery_count = 1
        for item in submission.gallery_data['items']:
            media_id = item['media_id']
            meta = submission.media_metadata.get(media_id)
            if meta and meta.get('e') == 'Image':
                source_url = meta['s']['u']
                file_ext = os.path.splitext(source_url)[1].split('?')[0]
                if file_ext in IMAGE_FORMATS:
                    filename = os.path.join(SAVE_PATH, f"{safe_title}_{gallery_count}{file_ext}")
                    try:
                        response = requests.get(source_url, headers=HEADERS)
                        response.raise_for_status()
                        with open(filename, 'wb') as f: f.write(response.content)
                        print(f"Downloaded gallery image: {filename}")
                        downloaded_count += 1
                        was_downloaded = True
                        gallery_count += 1
                    except requests.exceptions.RequestException as e:
                        print(f"❌ Failed gallery download for {source_url}: {e}")
        if was_downloaded:
            continue

    url = submission.url
    if any(url.endswith(ext) for ext in IMAGE_FORMATS):
        file_extension = os.path.splitext(url)[1]
        filename = os.path.join(SAVE_PATH, f"{safe_title}{file_extension}")
        
        if not os.path.exists(filename):
            try:
                response = requests.get(url, headers=HEADERS)
                response.raise_for_status()
                with open(filename, 'wb') as f: f.write(response.content)
                print(f"Downloaded direct image: {filename}")
                downloaded_count += 1
                was_downloaded = True
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to download {url}: {e}")
        else:
            was_downloaded = True 

    if not was_downloaded:
        with open(REVIEW_FILE, "a", encoding="utf-8") as f:
            f.write(f"Title: {submission.title}\n")
            f.write(f"Link: https://www.reddit.com{submission.permalink}\n")
            f.write("-" * 30 + "\n")
        print(f"--> Saved for review: {submission.title}")
        review_count += 1


print(f"\nFinished. Downloaded {downloaded_count} new images.")
print(f"Saved {review_count} posts to '{REVIEW_FILE}' for manual review.")