from PIL import Image, ImageDraw
import os
from pathlib import Path

def create_sprite(size, color, filename, border_color=None):
    """Create a simple sprite with the given color and optional border."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if border_color:
        draw.rectangle([0, 0, size-1, size-1], fill=color, outline=border_color)
    else:
        draw.rectangle([0, 0, size-1, size-1], fill=color)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, 'PNG')

def create_character_sprite(size, colors, filename):
    """Create a simple character sprite with multiple frames for animation."""
    # Create a spritesheet with 4 frames (for walking animation)
    img = Image.new('RGBA', (size * 4, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    for i in range(4):
        x = i * size
        # Body
        draw.rectangle([x+4, 4, x+size-5, size-5], fill=colors['body'])
        # Head
        draw.ellipse([x+8, 2, x+size-9, size//2], fill=colors['head'])
        # Add simple animation effect (slight up/down movement)
        offset = 2 if i % 2 == 0 else 0
        draw.rectangle([x+4, size-8-offset, x+8, size-4-offset], fill=colors['feet'])
        draw.rectangle([x+size-9, size-8-offset, x+size-5, size-4-offset], fill=colors['feet'])
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, 'PNG')

def generate_assets():
    """Generate all game assets."""
    base_path = Path(__file__).parent.parent / 'assets' / 'images'
    
    # Generate terrain sprites (32x32)
    sprites = {
        'grass.png': ((34, 139, 34), (25, 100, 25)),      # Green with darker border
        'water.png': ((0, 0, 139), (0, 0, 100)),          # Blue with darker border
        'stone.png': ((169, 169, 169), (120, 120, 120)),  # Gray with darker border
        'wall.png': ((128, 128, 128), (90, 90, 90)),      # Dark gray with darker border
        'sand.png': ((238, 214, 175), (200, 180, 150)),   # Tan with darker border
    }
    
    for filename, (color, border) in sprites.items():
        filepath = base_path / 'tiles' / filename
        create_sprite(32, color, filepath, border)
        print(f"Created {filename}")
    
    # Generate character sprite (32x32)
    character_colors = {
        'body': (255, 0, 0),    # Red body
        'head': (255, 218, 185),  # Peach head
        'feet': (139, 69, 19)     # Brown feet
    }
    
    filepath = base_path / 'characters' / 'player.png'
    create_character_sprite(32, character_colors, filepath)
    print("Created player.png")

if __name__ == "__main__":
    generate_assets()