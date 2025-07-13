import pygame

class SpriteManager:
    def __init__(self):
        self.sprites = {}  # Dictionary to store individual sprites
        self.spritesheets = {}  # Dictionary to store sprite sheets
        
    def load_sprite(self, name, path):
        """Load a single sprite"""
        try:
            self.sprites[name] = pygame.image.load(path).convert_alpha()
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading sprite {name} from {path}: {e}")
            return False
            
    def load_spritesheet(self, name, path, sprite_size):
        """Load a sprite sheet and split it into individual sprites"""
        try:
            sheet = pygame.image.load(path).convert_alpha()
            self.spritesheets[name] = []
            
            # Get the dimensions of the sprite sheet
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            
            # Calculate number of sprites in each direction
            cols = sheet_width // sprite_size
            rows = sheet_height // sprite_size
            
            # Split the sheet into individual sprites
            for row in range(rows):
                for col in range(cols):
                    x = col * sprite_size
                    y = row * sprite_size
                    sprite = sheet.subsurface((x, y, sprite_size, sprite_size))
                    self.spritesheets[name].append(sprite)
                    
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading spritesheet {name} from {path}: {e}")
            # Create a default colored square as fallback
            fallback = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            fallback.fill((255, 0, 255))  # Magenta for missing sprites
            self.spritesheets[name] = [fallback] * 16  # 16 frames for basic animation
            return False
            
    def get_sprite(self, name):
        """Get a single sprite by name"""
        return self.sprites.get(name)
        
    def get_animation_frame(self, name, frame):
        """Get a frame from a sprite sheet"""
        if name in self.spritesheets:
            frames = self.spritesheets[name]
            if 0 <= frame < len(frames):
                return frames[frame]
        return None