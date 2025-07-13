from PIL import Image, ImageDraw
import os
from pathlib import Path
import math

class CharacterGenerator:
    def __init__(self, sprite_size=32):
        self.sprite_size = sprite_size
        self.base_path = Path(__file__).parent.parent / 'assets' / 'images' / 'characters'
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_character_spritesheet(self, colors, gender='male'):
        """Create a character spritesheet with all animations."""
        sheet = Image.new('RGBA', (self.sprite_size * 4, self.sprite_size * 6), (0, 0, 0, 0))
        
        animations = [
            self._create_walk_down_frames(colors, gender),
            self._create_walk_left_frames(colors, gender),
            self._create_walk_right_frames(colors, gender),
            self._create_walk_up_frames(colors, gender),
            self._create_idle_frames(colors, gender),
            self._create_attack_frames(colors, gender)
        ]

        for row, frames in enumerate(animations):
            for col, frame in enumerate(frames):
                sheet.paste(frame, (col * self.sprite_size, row * self.sprite_size))

        return sheet

    def _draw_body(self, draw, x, y, colors, gender, bounce=0):
        """Draw body with gender-specific features"""
        if gender == 'female':
            # Slightly slimmer torso for female character
            draw.rectangle([x+1, y, x+5, y+8], colors['shirt'])
            # Add dress or feminine clothing detail
            if colors.get('dress'):
                draw.rectangle([x, y+6, x+6, y+12], colors['dress'])
        else:
            # Regular torso for male character
            draw.rectangle([x, y, x+6, y+8], colors['shirt'])

    def _draw_hair(self, draw, x, y, colors, gender, wind=0):
        """Draw gender-specific hairstyles"""
        if gender == 'female':
            # Longer hair for female character
            draw.ellipse([x-1, y, x+9, y+10], colors['hair'])
            # Long flowing hair
            draw.rectangle([x+1+wind, y+6, x+7+wind, y+14], colors['hair'])
            # Hair highlights
            highlight_color = self._lighten_color(colors['hair'])
            draw.ellipse([x+2, y+2, x+4, y+4], highlight_color)
        else:
            # Shorter hair for male character
            draw.ellipse([x-1, y, x+9, y+8], colors['hair'])
            # Side locks
            draw.ellipse([x-1+wind, y+2, x+2+wind, y+8], colors['hair'])
            draw.ellipse([x+6+wind, y+2, x+9+wind, y+8], colors['hair'])
            # Highlights
            highlight_color = self._lighten_color(colors['hair'])
            draw.ellipse([x+2, y+1, x+4, y+3], highlight_color)

    def generate_characters(self):
        """Generate both male and female character spritesheets."""
        # Male character colors
        male_colors = {
            'skin': (255, 218, 185, 255),     # Peach skin tone
            'hair': (139, 69, 19, 255),       # Brown hair
            'shirt': (70, 130, 180, 255),     # Steel blue shirt
            'pants': (47, 79, 79, 255),       # Dark slate gray pants
            'boots': (101, 67, 33, 255),      # Brown boots
            'belt': (139, 69, 19, 255),       # Brown belt
            'eyes': (0, 0, 0, 255),           # Black eyes
            'cape': (128, 0, 0, 255)          # Dark red cape
        }
        
        # Female character colors
        female_colors = {
            'skin': (255, 224, 189, 255),     # Lighter peach skin tone
            'hair': (218, 165, 32, 255),      # Golden hair
            'shirt': (147, 112, 219, 255),    # Medium purple shirt
            'dress': (186, 85, 211, 255),     # Medium orchid dress
            'boots': (139, 69, 19, 255),      # Brown boots
            'belt': (218, 165, 32, 255),      # Golden belt
            'eyes': (0, 0, 0, 255),           # Black eyes
            'cape': (153, 50, 204, 255)       # Dark orchid cape
        }
        
        # Generate male character
        male_sheet = self.create_character_spritesheet(male_colors, 'male')
        male_sheet.save(self.base_path / 'player_male.png')
        print("Generated male character spritesheet!")
        
        # Generate female character
        female_sheet = self.create_character_spritesheet(female_colors, 'female')
        female_sheet.save(self.base_path / 'player_female.png')
        print("Generated female character spritesheet!")

    # [Previous animation methods remain the same, just add gender parameter and use it in _draw_body and _draw_hair calls]

if __name__ == "__main__":
    generator = CharacterGenerator()
    generator.generate_characters()