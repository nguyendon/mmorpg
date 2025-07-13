from PIL import Image, ImageDraw
import os
from pathlib import Path

def generate_item_icons():
    base_path = Path(__file__).parent.parent / 'assets' / 'images' / 'items'
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Weapon icons
    _generate_sword_icon(base_path / 'iron_sword.png', (192, 192, 192))  # Silver color
    _generate_sword_icon(base_path / 'steel_sword.png', (128, 128, 128))  # Gray color
    _generate_staff_icon(base_path / 'magic_staff.png', (148, 0, 211))   # Purple color
    
    # Armor icons
    _generate_armor_icon(base_path / 'leather_armor.png', (139, 69, 19))  # Brown color
    _generate_armor_icon(base_path / 'steel_armor.png', (128, 128, 128))  # Gray color
    _generate_robe_icon(base_path / 'mage_robe.png', (148, 0, 211))      # Purple color
    
    # Potion icons
    _generate_potion_icon(base_path / 'health_potion.png', (255, 0, 0))   # Red color
    _generate_potion_icon(base_path / 'mana_potion.png', (0, 0, 255))     # Blue color
    _generate_potion_icon(base_path / 'strength_potion.png', (255, 165, 0))  # Orange color
    
    # Material icons
    _generate_ore_icon(base_path / 'iron_ore.png', (192, 192, 192))       # Silver color
    _generate_crystal_icon(base_path / 'magic_crystal.png', (148, 0, 211))  # Purple color
    
    # Quest item icons
    _generate_relic_icon(base_path / 'ancient_relic.png', (255, 215, 0))   # Gold color
    
    print("Generated all item icons!")

def _generate_sword_icon(path, color):
    """Generate a sword icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Blade
    draw.polygon([(16, 4), (20, 8), (16, 28), (12, 28)], color)
    # Handle
    draw.rectangle([14, 24, 18, 30], (139, 69, 19))  # Brown handle
    # Guard
    draw.rectangle([10, 23, 22, 25], (*color, 255))
    
    img.save(path)

def _generate_staff_icon(path, color):
    """Generate a magic staff icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Staff pole
    draw.rectangle([14, 8, 18, 30], (139, 69, 19))  # Brown staff
    # Crystal top
    draw.ellipse([12, 4, 20, 12], color)
    # Glow effect
    draw.ellipse([13, 5, 19, 11], (255, 255, 255, 128))
    
    img.save(path)

def _generate_armor_icon(path, color):
    """Generate armor icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Main armor piece
    draw.polygon([
        (16, 4), (28, 12), (28, 24),
        (16, 28), (4, 24), (4, 12)
    ], color)
    
    # Highlight
    highlight_color = tuple(min(255, c + 50) for c in color)
    draw.line([(16, 4), (28, 12)], highlight_color, 2)
    
    img.save(path)

def _generate_robe_icon(path, color):
    """Generate robe icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Main robe
    draw.polygon([
        (16, 4), (24, 8), (24, 28),
        (8, 28), (8, 8)
    ], color)
    
    # Hood
    draw.ellipse([12, 2, 20, 10], color)
    
    img.save(path)

def _generate_potion_icon(path, color):
    """Generate potion icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Bottle
    draw.polygon([
        (12, 12), (20, 12), (18, 28),
        (14, 28)
    ], (200, 200, 200, 200))  # Glass color
    
    # Liquid
    draw.polygon([
        (14, 16), (18, 16), (17, 27),
        (15, 27)
    ], color)
    
    # Bottle neck
    draw.rectangle([14, 8, 18, 12], (200, 200, 200, 200))
    # Cork
    draw.rectangle([14, 6, 18, 8], (139, 69, 19))  # Brown cork
    
    img.save(path)

def _generate_ore_icon(path, color):
    """Generate ore icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rock shape
    draw.polygon([
        (16, 8), (24, 12), (24, 20),
        (16, 24), (8, 20), (8, 12)
    ], (128, 128, 128))  # Gray rock
    
    # Ore veins
    draw.line([(12, 14), (20, 18)], color, 2)
    draw.line([(14, 20), (18, 16)], color, 2)
    
    img.save(path)

def _generate_crystal_icon(path, color):
    """Generate crystal icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Crystal shape
    draw.polygon([
        (16, 4), (24, 12), (20, 28),
        (12, 28), (8, 12)
    ], color)
    
    # Highlight
    highlight_color = tuple(min(255, c + 50) for c in color)
    draw.polygon([
        (16, 4), (24, 12), (20, 16),
        (12, 16), (8, 12)
    ], highlight_color)
    
    img.save(path)

def _generate_relic_icon(path, color):
    """Generate relic icon"""
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Relic base
    draw.ellipse([8, 16, 24, 28], color)
    
    # Relic top
    draw.polygon([
        (16, 4), (20, 8), (20, 16),
        (12, 16), (12, 8)
    ], color)
    
    # Gem
    draw.ellipse([14, 12, 18, 16], (255, 0, 0))  # Red gem
    
    img.save(path)

if __name__ == "__main__":
    generate_item_icons()