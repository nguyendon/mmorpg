from PIL import Image, ImageDraw
import os
from pathlib import Path
import math

class CharacterGenerator:
    def __init__(self, sprite_size=32):
        self.sprite_size = sprite_size
        self.base_path = Path(__file__).parent.parent / 'assets' / 'images' / 'characters'
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_character_spritesheet(self, colors):
        """
        Create a character spritesheet with all animations.
        Layout:
        Row 1: Walking down
        Row 2: Walking left
        Row 3: Walking right
        Row 4: Walking up
        Row 5: Idle animations
        Row 6: Attack animations
        """
        # 6 rows (4 directions + idle + attack) x 4 frames per animation
        sheet = Image.new('RGBA', (self.sprite_size * 4, self.sprite_size * 6), (0, 0, 0, 0))
        
        # Generate each row of animations
        animations = [
            self._create_walk_down_frames(colors),
            self._create_walk_left_frames(colors),
            self._create_walk_right_frames(colors),
            self._create_walk_up_frames(colors),
            self._create_idle_frames(colors),
            self._create_attack_frames(colors)
        ]

        # Place each animation row in the spritesheet
        for row, frames in enumerate(animations):
            for col, frame in enumerate(frames):
                sheet.paste(frame, (col * self.sprite_size, row * self.sprite_size))

        return sheet

    def _create_walk_down_frames(self, colors, frames=4):
        """Create walking down animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Body bounce offset
            bounce = math.sin(i * math.pi / 2) * 2
            
            # Body
            body_top = 12 + bounce
            draw.rectangle([10, body_top, 22, body_top + 12], colors['body'])
            
            # Head
            draw.ellipse([8, 4 + bounce, 24, 20 + bounce], colors['head'])
            
            # Eyes
            draw.rectangle([12, 10 + bounce, 14, 12 + bounce], colors['detail'])
            draw.rectangle([18, 10 + bounce, 20, 12 + bounce], colors['detail'])
            
            # Legs with walking animation
            leg_offset = math.sin((i + 0.5) * math.pi) * 3
            draw.rectangle([12, body_top + 12, 15, body_top + 20], colors['legs'])
            draw.rectangle([17, body_top + 12, 20, body_top + 20], colors['legs'])
            
            frames_list.append(img)
        return frames_list

    def _create_walk_left_frames(self, colors, frames=4):
        """Create walking left animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            bounce = math.sin(i * math.pi / 2) * 2
            
            # Body
            draw.rectangle([12, 12 + bounce, 24, 24 + bounce], colors['body'])
            
            # Head
            draw.ellipse([8, 4 + bounce, 20, 20 + bounce], colors['head'])
            
            # Eye
            draw.rectangle([12, 10 + bounce, 14, 12 + bounce], colors['detail'])
            
            # Legs with walking animation
            leg_offset = math.sin((i + 0.5) * math.pi) * 3
            draw.rectangle([14 + leg_offset, 24 + bounce, 17 + leg_offset, 30 + bounce], colors['legs'])
            draw.rectangle([19 - leg_offset, 24 + bounce, 22 - leg_offset, 30 + bounce], colors['legs'])
            
            frames_list.append(img)
        return frames_list

    def _create_walk_right_frames(self, colors, frames=4):
        """Create walking right animation frames."""
        frames_list = []
        for left_frame in self._create_walk_left_frames(colors, frames):
            # Flip the left-facing frames horizontally
            right_frame = left_frame.transpose(Image.FLIP_LEFT_RIGHT)
            frames_list.append(right_frame)
        return frames_list

    def _create_walk_up_frames(self, colors, frames=4):
        """Create walking up animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            bounce = math.sin(i * math.pi / 2) * 2
            
            # Body
            draw.rectangle([10, 12 + bounce, 22, 24 + bounce], colors['body'])
            
            # Head (from back)
            draw.ellipse([8, 4 + bounce, 24, 20 + bounce], colors['head'])
            
            # Hair detail
            draw.rectangle([10, 6 + bounce, 22, 12 + bounce], colors['detail'])
            
            # Legs with walking animation
            leg_offset = math.sin((i + 0.5) * math.pi) * 3
            draw.rectangle([12, 24 + bounce, 15, 30 + bounce], colors['legs'])
            draw.rectangle([17, 24 + bounce, 20, 30 + bounce], colors['legs'])
            
            frames_list.append(img)
        return frames_list

    def _create_idle_frames(self, colors, frames=4):
        """Create idle animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Subtle breathing animation
            breath = math.sin(i * math.pi / 2) * 1
            
            # Body
            draw.rectangle([10, 12 + breath, 22, 24 + breath], colors['body'])
            
            # Head
            draw.ellipse([8, 4 + breath, 24, 20 + breath], colors['head'])
            
            # Eyes
            draw.rectangle([12, 10 + breath, 14, 12 + breath], colors['detail'])
            draw.rectangle([18, 10 + breath, 20, 12 + breath], colors['detail'])
            
            # Legs
            draw.rectangle([12, 24 + breath, 15, 30 + breath], colors['legs'])
            draw.rectangle([17, 24 + breath, 20, 30 + breath], colors['legs'])
            
            frames_list.append(img)
        return frames_list

    def _create_attack_frames(self, colors, frames=4):
        """Create attack animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Attack animation with arm swing
            swing = math.sin(i * math.pi / 2) * 8
            
            # Body
            draw.rectangle([10, 12, 22, 24], colors['body'])
            
            # Head
            draw.ellipse([8, 4, 24, 20], colors['head'])
            
            # Eyes
            draw.rectangle([12, 10, 14, 12], colors['detail'])
            draw.rectangle([18, 10, 20, 12], colors['detail'])
            
            # Legs
            draw.rectangle([12, 24, 15, 30], colors['legs'])
            draw.rectangle([17, 24, 20, 30], colors['legs'])
            
            # Attacking arm
            draw.rectangle([22 + swing, 14, 28 + swing, 17], colors['body'])
            
            frames_list.append(img)
        return frames_list

    def generate_character(self):
        """Generate a character spritesheet with default colors."""
        colors = {
            'body': (255, 0, 0, 255),      # Red body
            'head': (255, 218, 185, 255),  # Peach skin
            'detail': (0, 0, 0, 255),      # Black details
            'legs': (0, 0, 255, 255)       # Blue legs
        }
        
        sheet = self.create_character_spritesheet(colors)
        sheet.save(self.base_path / 'player_full.png')
        print("Generated character spritesheet!")

if __name__ == "__main__":
    generator = CharacterGenerator()
    generator.generate_character()