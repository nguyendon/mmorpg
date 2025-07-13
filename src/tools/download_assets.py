import os
import requests
from pathlib import Path

def download_file(url, filepath):
    """Download a file from URL to the specified filepath."""
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return True
    return False

# Asset URLs (using some free RPG assets)
ASSETS = {
    # Terrain/tiles
    'tiles/grass.png': 'https://raw.githubusercontent.com/silveira/openpixels/master/grass.png',
    'tiles/water.png': 'https://raw.githubusercontent.com/silveira/openpixels/master/water.png',
    'tiles/dirt.png': 'https://raw.githubusercontent.com/silveira/openpixels/master/dirt.png',
    'tiles/stone.png': 'https://raw.githubusercontent.com/silveira/openpixels/master/stone.png',
    
    # Character sprites (placeholder URLs - we'll need to find actual free assets)
    'characters/player.png': 'https://raw.githubusercontent.com/silveira/openpixels/master/char_hero.png',
}

def download_assets():
    """Download all game assets."""
    base_path = Path(__file__).parent.parent / 'assets' / 'images'
    
    for rel_path, url in ASSETS.items():
        filepath = base_path / rel_path
        print(f"Downloading {rel_path}...")
        if download_file(url, filepath):
            print(f"Successfully downloaded {rel_path}")
        else:
            print(f"Failed to download {rel_path}")

if __name__ == "__main__":
    download_assets()