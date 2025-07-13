from PIL import Image, ImageDraw
import os
from pathlib import Path
import random

class TerrainGenerator:
    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.base_path = Path(__file__).parent.parent / 'assets' / 'images' / 'tiles'
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _add_noise(self, color, amount=10):
        """Add slight color variation to create texture."""
        return tuple(
            max(0, min(255, c + random.randint(-amount, amount)))
            for c in color[:3]
        ) + (255,)  # Keep alpha at 255

    def _create_grass_texture(self, base_color, num_variations=3):
        """Create grass tiles with subtle variations."""
        for i in range(num_variations):
            img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Base grass color
            draw.rectangle([0, 0, self.tile_size, self.tile_size], base_color)
            
            # Add grass blade details
            for _ in range(8):
                x = random.randint(2, self.tile_size-4)
                y = random.randint(2, self.tile_size-4)
                # Darker grass blades
                blade_color = tuple(max(0, c - 30) for c in base_color[:3]) + (255,)
                draw.line(
                    [x, y, x + random.randint(-3, 3), y - random.randint(4, 8)],
                    blade_color,
                    width=2
                )
            
            img.save(self.base_path / f'grass_{i}.png')

    def _create_water_texture(self, base_color, num_frames=4):
        """Create animated water tiles."""
        for i in range(num_frames):
            img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Base water color
            draw.rectangle([0, 0, self.tile_size, self.tile_size], base_color)
            
            # Add wave effect
            wave_offset = (i / num_frames) * 2 * 3.14159  # Full sine wave over all frames
            for y in range(self.tile_size):
                wave_color = self._add_noise(base_color, 15)
                line_width = int(2 + math.sin(wave_offset + y * 0.2) * 2)
                draw.line(
                    [0, y, self.tile_size, y],
                    wave_color,
                    width=line_width
                )
            
            img.save(self.base_path / f'water_{i}.png')

    def _create_stone_texture(self, base_color, num_variations=3):
        """Create stone tiles with cracks and variations."""
        for i in range(num_variations):
            img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Base stone color
            draw.rectangle([0, 0, self.tile_size, self.tile_size], base_color)
            
            # Add stone texture
            for _ in range(5):
                x = random.randint(4, self.tile_size-4)
                y = random.randint(4, self.tile_size-4)
                # Darker cracks
                crack_color = tuple(max(0, c - 40) for c in base_color[:3]) + (255,)
                # Random crack pattern
                points = [(x, y)]
                for _ in range(3):
                    x += random.randint(-4, 4)
                    y += random.randint(-4, 4)
                    points.append((x, y))
                draw.line(points, crack_color, width=1)
            
            img.save(self.base_path / f'stone_{i}.png')

    def _create_wall_texture(self, base_color, num_variations=2):
        """Create wall tiles with brick patterns."""
        for i in range(num_variations):
            img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Base wall color
            draw.rectangle([0, 0, self.tile_size, self.tile_size], base_color)
            
            # Add brick pattern
            brick_height = self.tile_size // 4
            mortar_color = tuple(min(255, c + 20) for c in base_color[:3]) + (255,)
            
            for y in range(0, self.tile_size, brick_height):
                # Horizontal mortar lines
                draw.line([(0, y), (self.tile_size, y)], mortar_color)
                
                # Vertical mortar lines with offset every other row
                offset = (self.tile_size // 2) if (y // brick_height) % 2 == 0 else 0
                for x in range(offset, self.tile_size, self.tile_size // 2):
                    draw.line([(x, y), (x, y + brick_height)], mortar_color)
            
            img.save(self.base_path / f'wall_{i}.png')

    def _create_sand_texture(self, base_color, num_variations=3):
        """Create sand tiles with subtle dune patterns."""
        for i in range(num_variations):
            img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Base sand color
            draw.rectangle([0, 0, self.tile_size, self.tile_size], base_color)
            
            # Add sand ripple texture
            for y in range(0, self.tile_size, 2):
                ripple_color = self._add_noise(base_color, 5)
                offset = int(math.sin(y * 0.2 + i) * 3)
                draw.line(
                    [(0, y + offset), (self.tile_size, y)],
                    ripple_color,
                    width=1
                )
            
            img.save(self.base_path / f'sand_{i}.png')

    def _create_transition_tile(self, type1, type2, direction):
        """Create transition tiles between different terrain types."""
        img = Image.new('RGBA', (self.tile_size, self.tile_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Base color is type1
        draw.rectangle([0, 0, self.tile_size, self.tile_size], type1)
        
        # Create transition based on direction
        if direction == "top":
            points = [(0, 0), (self.tile_size, 0), (self.tile_size, self.tile_size//2),
                     (0, self.tile_size//2)]
        elif direction == "right":
            points = [(self.tile_size//2, 0), (self.tile_size, 0), (self.tile_size, self.tile_size),
                     (self.tile_size//2, self.tile_size)]
        elif direction == "bottom":
            points = [(0, self.tile_size//2), (self.tile_size, self.tile_size//2),
                     (self.tile_size, self.tile_size), (0, self.tile_size)]
        elif direction == "left":
            points = [(0, 0), (self.tile_size//2, 0), (self.tile_size//2, self.tile_size),
                     (0, self.tile_size)]
        
        draw.polygon(points, type2)
        
        return img

    def generate_all_tiles(self):
        """Generate all terrain tiles including variations and transitions."""
        # Base colors for different terrain types
        colors = {
            'grass': (34, 139, 34, 255),    # Forest green
            'water': (0, 0, 139, 255),      # Dark blue
            'stone': (169, 169, 169, 255),  # Gray
            'wall': (128, 128, 128, 255),   # Dark gray
            'sand': (238, 214, 175, 255),   # Tan
        }

        print("Generating terrain tiles...")
        
        # Generate base tiles with variations
        self._create_grass_texture(colors['grass'])
        self._create_water_texture(colors['water'])
        self._create_stone_texture(colors['stone'])
        self._create_wall_texture(colors['wall'])
        self._create_sand_texture(colors['sand'])
        
        # Generate transition tiles
        terrain_pairs = [
            ('grass', 'sand'),
            ('grass', 'water'),
            ('sand', 'water'),
            ('grass', 'stone'),
            ('stone', 'wall')
        ]
        
        directions = ['top', 'right', 'bottom', 'left']
        
        for t1, t2 in terrain_pairs:
            for direction in directions:
                transition = self._create_transition_tile(
                    colors[t1],
                    colors[t2],
                    direction
                )
                transition.save(self.base_path / f'{t1}_{t2}_{direction}.png')
        
        print("Terrain generation complete!")

if __name__ == "__main__":
    import math  # Added for math.sin
    generator = TerrainGenerator()
    generator.generate_all_tiles()