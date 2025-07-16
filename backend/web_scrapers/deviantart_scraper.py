import requests
import os
from dotenv import load_dotenv
import webbrowser
import time

load_dotenv()
CLIENT_ID = os.getenv("DEVIANTART_CLIENT_ID")
CLIENT_SECRET = os.getenv("DEVIANTART_CLIENT_SECRET")
REDIRECT_URI = "https://www.google.com/"
IMAGE_DIR = "backend/image_sorter/to_process"
query = "magic"
limit = 50

def get_access_token():
    """Guides the user through the one-time authentication process."""
    auth_url = (f"https://www.deviantart.com/oauth2/authorize?"
                f"response_type=code&client_id={CLIENT_ID}&"
                f"redirect_uri={REDIRECT_URI}&scope=browse")

    print("="*50)
    print("One-Time Authentication Needed")
    print(f"Copy this link and paste it in your browser: {auth_url}")
    print("Click 'Authorize' to grant your script access.")
    print("You will be redirected to a blank page. Copy the ENTIRE URL from your browser's address bar.")
    print("="*50)
    time.sleep(0.5)
    webbrowser.open(auth_url)

    redirected_url = input("Paste the full redirected URL here and press Enter:\n> ")

    # Extract the authorization code from the URL
    try:
        code = redirected_url.split('code=')[1].split('&')[0]
    except IndexError:
        print("\n❌ Error: Could not find the authorization code in the URL.")
        print("Please make sure you copied the full URL after being redirected.")
        return None

    # Exchange the code for an access token
    token_url = "https://www.deviantart.com/oauth2/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code,
    }
    
    response = requests.post(token_url, data=token_data)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print("\n✅ Successfully obtained access token!")
        return access_token
    else:
        print(f"\n❌ Error getting access token: {response.text}")
        return None

def download_deviations(access_token, query="fantasy", limit=50):
    """Downloads images from DeviantArt based on a search query."""
    if not access_token:
        print("Cannot download without a valid access token.")
        return

    os.makedirs(IMAGE_DIR, exist_ok=True)
    print(f"\nSearching for '{query}' on DeviantArt...")
    
    # Use the /browse/tags endpoint
    browse_url = "https://www.deviantart.com/api/v1/oauth2/browse/tags"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'tag': query, 'limit': limit, 'mature_content': 'true'}
    
    try:
        response = requests.get(browse_url, headers=headers, params=params)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}")
        return

    data = response.json()
    downloaded_count = 0
    
    if not data.get('results'):
        print("API returned no results for this query. Try a different search term.")
        return

    for deviation in data.get('results', []):
        # First, check if there is a public image URL available
        image_url = deviation.get('content', {}).get('src')
        if not image_url:
            print(f"--> Skipping post with no direct image content: {deviation['title']}")
            continue

        title = deviation['title']
        deviation_id = deviation['deviationid']
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()[:50]
        
        filename = os.path.join(IMAGE_DIR, f"{safe_title}_{deviation_id}.jpg")
        
        if os.path.exists(filename):
            continue

        try:
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(img_response.content)
            print(f"Downloaded: {filename}")
            downloaded_count += 1
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {image_url}: {e}")
    
    print(f"\nFinished. Downloaded {downloaded_count} new images.")

if __name__ == "__main__":
    if not os.path.exists("deviantart_token.txt"):
        token = get_access_token()
        if token:
            with open("deviantart_token.txt", "w") as f:
                f.write(token)
    else:
        with open("deviantart_token.txt", "r") as f:
            token = f.read().strip()

    download_deviations(token, query=query, limit=limit)