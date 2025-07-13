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
            self._create_walk_down_frames(colors),
            self._create_walk_left_frames(colors),
            self._create_walk_right_frames(colors),
            self._create_walk_up_frames(colors),
            self._create_idle_frames(colors),
            self._create_attack_frames(colors)
        ]

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
            bounce = math.sin(i * math.pi / 2) * 1
            
            # Draw legs with walking animation
            leg_offset = math.sin((i + 0.5) * math.pi) * 2
            # Left leg
            draw.rectangle([14 - leg_offset, 22 + bounce, 17 - leg_offset, 30 + bounce], colors['pants'])
            draw.rectangle([14 - leg_offset, 28 + bounce, 17 - leg_offset, 31 + bounce], colors['boots'])
            # Right leg
            draw.rectangle([15 + leg_offset, 22 + bounce, 18 + leg_offset, 30 + bounce], colors['pants'])
            draw.rectangle([15 + leg_offset, 28 + bounce, 18 + leg_offset, 31 + bounce], colors['boots'])
            
            # Torso
            draw.rectangle([13, 14 + bounce, 19, 22 + bounce], colors['shirt'])
            # Add shading to torso
            shade_color = self._darken_color(colors['shirt'])
            draw.rectangle([13, 20 + bounce, 19, 22 + bounce], shade_color)
            
            # Arms with swing
            arm_swing = math.sin(i * math.pi / 2) * 2
            # Left arm
            draw.rectangle([11 - arm_swing, 14 + bounce, 13 - arm_swing, 22 + bounce], colors['shirt'])
            # Right arm
            draw.rectangle([19 + arm_swing, 14 + bounce, 21 + arm_swing, 22 + bounce], colors['shirt'])
            
            # Belt
            draw.rectangle([13, 21 + bounce, 19, 22 + bounce], colors['belt'])
            
            # Head
            draw.ellipse([12, 6 + bounce, 20, 14 + bounce], colors['skin'])
            
            # Hair (more detailed)
            self._draw_hair(draw, 12, 4 + bounce, colors)
            
            # Face details
            eye_level = 9 + bounce
            # Left eye
            draw.ellipse([14, eye_level, 15, eye_level + 1], colors['eyes'])
            # Right eye
            draw.ellipse([17, eye_level, 18, eye_level + 1], colors['eyes'])
            
            frames_list.append(img)
        return frames_list

    def _create_walk_left_frames(self, colors, frames=4):
        """Create walking left animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            bounce = math.sin(i * math.pi / 2) * 1
            
            # Draw legs with walking animation
            leg_offset = math.sin((i + 0.5) * math.pi) * 2
            # Back leg
            draw.rectangle([17 + leg_offset, 22 + bounce, 20 + leg_offset, 30 + bounce], colors['pants'])
            draw.rectangle([17 + leg_offset, 28 + bounce, 20 + leg_offset, 31 + bounce], colors['boots'])
            # Front leg
            draw.rectangle([14 - leg_offset, 22 + bounce, 17 - leg_offset, 30 + bounce], colors['pants'])
            draw.rectangle([14 - leg_offset, 28 + bounce, 17 - leg_offset, 31 + bounce], colors['boots'])
            
            # Torso
            draw.rectangle([14, 14 + bounce, 20, 22 + bounce], colors['shirt'])
            # Add shading
            shade_color = self._darken_color(colors['shirt'])
            draw.rectangle([18, 14 + bounce, 20, 22 + bounce], shade_color)
            
            # Arms with swing
            arm_swing = math.sin(i * math.pi / 2) * 2
            # Back arm
            draw.rectangle([18 + arm_swing, 14 + bounce, 20 + arm_swing, 22 + bounce], colors['shirt'])
            # Front arm
            draw.rectangle([12 - arm_swing, 14 + bounce, 14 - arm_swing, 22 + bounce], colors['shirt'])
            
            # Belt
            draw.rectangle([14, 21 + bounce, 20, 22 + bounce], colors['belt'])
            
            # Head
            draw.ellipse([13, 6 + bounce, 21, 14 + bounce], colors['skin'])
            
            # Hair (side view)
            self._draw_hair_side(draw, 13, 4 + bounce, colors)
            
            # Face details (side view)
            eye_level = 9 + bounce
            draw.ellipse([15, eye_level, 16, eye_level + 1], colors['eyes'])
            
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
            
            bounce = math.sin(i * math.pi / 2) * 1
            
            # Draw legs with walking animation
            leg_offset = math.sin((i + 0.5) * math.pi) * 2
            # Left leg
            draw.rectangle([14 - leg_offset, 22 + bounce, 17 - leg_offset, 30 + bounce], colors['pants'])
            draw.rectangle([14 - leg_offset, 28 + bounce, 17 - leg_offset, 31 + bounce], colors['boots'])
            # Right leg
            draw.rectangle([15 + leg_offset, 22 + bounce, 18 + leg_offset, 30 + bounce], colors['pants'])
            draw.rectangle([15 + leg_offset, 28 + bounce, 18 + leg_offset, 31 + bounce], colors['boots'])
            
            # Torso
            draw.rectangle([13, 14 + bounce, 19, 22 + bounce], colors['shirt'])
            
            # Arms with swing
            arm_swing = math.sin(i * math.pi / 2) * 2
            # Left arm
            draw.rectangle([11 - arm_swing, 14 + bounce, 13 - arm_swing, 22 + bounce], colors['shirt'])
            # Right arm
            draw.rectangle([19 + arm_swing, 14 + bounce, 21 + arm_swing, 22 + bounce], colors['shirt'])
            
            # Belt
            draw.rectangle([13, 21 + bounce, 19, 22 + bounce], colors['belt'])
            
            # Head (from back)
            draw.ellipse([12, 6 + bounce, 20, 14 + bounce], colors['skin'])
            
            # Hair (from back)
            self._draw_hair_back(draw, 11, 4 + bounce, colors)
            
            frames_list.append(img)
        return frames_list

    def _create_idle_frames(self, colors, frames=4):
        """Create idle animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Subtle breathing animation
            breath = math.sin(i * math.pi / 2) * 0.5
            
            # Legs
            draw.rectangle([14, 22, 17, 30], colors['pants'])
            draw.rectangle([15, 22, 18, 30], colors['pants'])
            draw.rectangle([14, 28, 17, 31], colors['boots'])
            draw.rectangle([15, 28, 18, 31], colors['boots'])
            
            # Torso with breathing
            draw.rectangle([13, 14 + breath, 19, 22 + breath], colors['shirt'])
            # Shading
            shade_color = self._darken_color(colors['shirt'])
            draw.rectangle([13, 20 + breath, 19, 22 + breath], shade_color)
            
            # Arms
            draw.rectangle([11, 14 + breath, 13, 22 + breath], colors['shirt'])
            draw.rectangle([19, 14 + breath, 21, 22 + breath], colors['shirt'])
            
            # Belt
            draw.rectangle([13, 21 + breath, 19, 22 + breath], colors['belt'])
            
            # Head with subtle movement
            draw.ellipse([12, 6 + breath, 20, 14 + breath], colors['skin'])
            
            # Hair
            self._draw_hair(draw, 12, 4 + breath, colors)
            
            # Face details
            eye_level = 9 + breath
            # Blinking animation
            if i == 3:  # Blink on last frame
                draw.line([14, eye_level, 15, eye_level], colors['eyes'])
                draw.line([17, eye_level, 18, eye_level], colors['eyes'])
            else:
                draw.ellipse([14, eye_level, 15, eye_level + 1], colors['eyes'])
                draw.ellipse([17, eye_level, 18, eye_level + 1], colors['eyes'])
            
            frames_list.append(img)
        return frames_list

    def _create_attack_frames(self, colors, frames=4):
        """Create attack animation frames."""
        frames_list = []
        for i in range(frames):
            img = Image.new('RGBA', (self.sprite_size, self.sprite_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Attack animation with dynamic pose
            attack_angle = math.sin(i * math.pi / 2) * 30
            
            # Legs in stable stance
            draw.rectangle([14, 22, 17, 30], colors['pants'])
            draw.rectangle([15, 22, 18, 30], colors['pants'])
            draw.rectangle([14, 28, 17, 31], colors['boots'])
            draw.rectangle([15, 28, 18, 31], colors['boots'])
            
            # Torso with twist
            twist = math.sin(i * math.pi / 2) * 2
            draw.rectangle([13 + twist, 14, 19 + twist, 22], colors['shirt'])
            
            # Arms with attack motion
            arm_extend = math.sin(i * math.pi / 2) * 6
            # Back arm
            draw.rectangle([11 + twist, 14, 13 + twist, 22], colors['shirt'])
            # Attack arm
            draw.rectangle([19 + twist + arm_extend, 14, 21 + twist + arm_extend, 22], colors['shirt'])
            
            # Belt
            draw.rectangle([13 + twist, 21, 19 + twist, 22], colors['belt'])
            
            # Head following attack motion
            head_turn = math.sin(i * math.pi / 2) * 2
            draw.ellipse([12 + head_turn, 6, 20 + head_turn, 14], colors['skin'])
            
            # Hair with motion
            self._draw_hair(draw, 12 + head_turn, 4, colors, arm_extend/2)
            
            # Face details
            eye_level = 9
            draw.ellipse([14 + head_turn, eye_level, 15 + head_turn, eye_level + 1], colors['eyes'])
            draw.ellipse([17 + head_turn, eye_level, 18 + head_turn, eye_level + 1], colors['eyes'])
            
            frames_list.append(img)
        return frames_list

    def _draw_hair(self, draw, x, y, colors, wind=0):
        """Draw detailed hairstyle from front view."""
        # Base hair shape
        draw.ellipse([x-1, y, x+9, y+8], colors['hair'])
        # Bangs
        draw.rectangle([x, y+4, x+8, y+6], colors['hair'])
        # Side locks with wind effect
        draw.ellipse([x-1+wind, y+2, x+2+wind, y+10], colors['hair'])
        draw.ellipse([x+6+wind, y+2, x+9+wind, y+10], colors['hair'])
        # Highlights
        highlight_color = self._lighten_color(colors['hair'])
        draw.ellipse([x+2, y+1, x+4, y+3], highlight_color)

    def _draw_hair_side(self, draw, x, y, colors):
        """Draw detailed hairstyle from side view."""
        # Main hair mass
        draw.ellipse([x-1, y, x+7, y+8], colors['hair'])
        # Bangs
        draw.rectangle([x, y+4, x+5, y+6], colors['hair'])
        # Back flow
        draw.ellipse([x+4, y+2, x+7, y+10], colors['hair'])
        # Highlight
        highlight_color = self._lighten_color(colors['hair'])
        draw.ellipse([x+1, y+1, x+3, y+3], highlight_color)

    def _draw_hair_back(self, draw, x, y, colors):
        """Draw detailed hairstyle from back view."""
        # Full hair volume
        draw.ellipse([x, y, x+10, y+8], colors['hair'])
        # Lower layer
        draw.rectangle([x+1, y+6, x+9, y+10], colors['hair'])
        # Side volumes
        draw.ellipse([x, y+2, x+3, y+10], colors['hair'])
        draw.ellipse([x+7, y+2, x+10, y+10], colors['hair'])
        # Highlight
        highlight_color = self._lighten_color(colors['hair'])
        draw.ellipse([x+4, y+1, x+6, y+3], highlight_color)

    def _lighten_color(self, color):
        """Create a lighter version of the color for highlights."""
        return tuple(min(255, c + 40) for c in color[:-1]) + (color[-1],)

    def _darken_color(self, color):
        """Create a darker version of the color for shading."""
        return tuple(max(0, c - 40) for c in color[:-1]) + (color[-1],)

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
        }
        
        # Female character colors
        female_colors = {
            'skin': (255, 224, 189, 255),     # Lighter peach skin tone
            'hair': (218, 165, 32, 255),      # Golden hair
            'shirt': (147, 112, 219, 255),    # Medium purple shirt
            'pants': (186, 85, 211, 255),     # Medium orchid pants
            'boots': (139, 69, 19, 255),      # Brown boots
            'belt': (218, 165, 32, 255),      # Golden belt
            'eyes': (0, 0, 0, 255),           # Black eyes
        }
        
        # Generate male character
        male_sheet = self.create_character_spritesheet(male_colors, 'male')
        male_sheet.save(self.base_path / 'player_male.png')
        print("Generated male character spritesheet!")
        
        # Generate female character
        female_sheet = self.create_character_spritesheet(female_colors, 'female')
        female_sheet.save(self.base_path / 'player_female.png')
        print("Generated female character spritesheet!")

if __name__ == "__main__":
    generator = CharacterGenerator()
    generator.generate_characters()