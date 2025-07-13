import pygame
import os

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.animations = {}
        
    def load_sprite(self, name, path, scale=1):
        """Load a single sprite from a file."""
        try:
            sprite = pygame.image.load(path).convert_alpha()
            if scale != 1:
                new_size = (int(sprite.get_width() * scale), 
                          int(sprite.get_height() * scale))
                sprite = pygame.transform.scale(sprite, new_size)
            self.sprites[name] = sprite
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading sprite {name} from {path}: {e}")
            return False
            
    def load_spritesheet(self, name, path, sprite_size, scale=1):
        """Load sprites from a spritesheet."""
        try:
            spritesheet = pygame.image.load(path).convert_alpha()
            width = spritesheet.get_width()
            height = spritesheet.get_height()
            
            sprites = []
            for y in range(0, height, sprite_size):
                for x in range(0, width, sprite_size):
                    rect = pygame.Rect(x, y, sprite_size, sprite_size)
                    sprite = spritesheet.subsurface(rect)
                    if scale != 1:
                        new_size = (int(sprite_size * scale), 
                                  int(sprite_size * scale))
                        sprite = pygame.transform.scale(sprite, new_size)
                    sprites.append(sprite)
                    
            self.animations[name] = sprites
            return True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading spritesheet {name} from {path}: {e}")
            return False
    
    def get_sprite(self, name):
        """Get a single sprite by name."""
        return self.sprites.get(name)
        
    def get_animation_frame(self, name, frame):
        """Get a specific frame from an animation."""
        if name in self.animations:
            return self.animations[name][frame % len(self.animations[name])]
        return None