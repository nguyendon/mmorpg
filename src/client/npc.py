import pygame
import math
from pathlib import Path
from src.common.constants import TILE_SIZE, PLAYER_SIZE
from .sprite_manager import SpriteManager

class NPC:
    def __init__(self, x, y, npc_type="villager"):
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.dialogue = []
        self.interaction_range = TILE_SIZE * 2  # 2 tiles range for interaction
        self.is_talking = False
        
        # Animation properties
        self.sprite_manager = SpriteManager()
        self.sprites_loaded = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2  # Slower than player
        self.idle_offset = 0  # For floating effect
        
        # Load sprites
        self._load_sprites()
        
    def _load_sprites(self):
        """Load NPC sprites from spritesheet."""
        if not self.sprites_loaded:
            # Get the absolute path to the sprite
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            sprite_path = project_root / 'src' / 'assets' / 'images' / 'characters' / f'npc_{self.npc_type}.png'
            
            if sprite_path.exists():
                self.sprite_manager.load_spritesheet(f'npc_{self.npc_type}', str(sprite_path), PLAYER_SIZE)
                self.sprites_loaded = True
            else:
                print(f"Error: NPC sprite not found at {sprite_path}")
                # Create a colored rectangle as fallback
                self.sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
                if self.npc_type == "villager":
                    self.sprite.fill((0, 255, 0))  # Green for villagers
                elif self.npc_type == "merchant":
                    self.sprite.fill((0, 0, 255))  # Blue for merchants
                else:  # guard
                    self.sprite.fill((255, 0, 0))  # Red for guards
        
    def add_dialogue(self, text):
        """Add dialogue options for the NPC"""
        self.dialogue.append(text)
        
    def get_next_dialogue(self):
        """Get the next dialogue line"""
        if not self.dialogue:
            return "..."
        return self.dialogue[0]  # For now, just return the first line
        
    def can_interact(self, player_x, player_y):
        """Check if player is in range to interact"""
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        return distance <= self.interaction_range
        
    def update(self, dt):
        """Update NPC animations"""
        # Update idle floating animation
        self.idle_offset = math.sin(pygame.time.get_ticks() * 0.003) * 2
        
        # Update sprite animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
    def draw(self, screen, camera_x, camera_y):
        """Draw the NPC on the screen"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.idle_offset  # Add floating effect
        
        # Draw shadow
        shadow_height = 4
        shadow_surface = pygame.Surface((PLAYER_SIZE, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 128), 
                          (0, 0, PLAYER_SIZE, shadow_height))
        screen.blit(shadow_surface, (
            screen_x,
            screen_y + PLAYER_SIZE - shadow_height/2
        ))
        
        if self.sprites_loaded:
            # Get the idle animation frame (row 4 in the spritesheet)
            sprite = self.sprite_manager.get_animation_frame(
                f'npc_{self.npc_type}', 
                4 * 4 + self.animation_frame  # Row 4 (idle) * 4 frames + current frame
            )
            if sprite:
                screen.blit(sprite, (screen_x, screen_y))
        else:
            # Use fallback colored rectangle
            screen.blit(self.sprite, (screen_x, screen_y))
        
        # Draw interaction indicator if in range
        if self.is_talking:
            # Draw multiple circles for a glowing effect
            for radius in range(8, 3, -1):
                alpha = int(255 * (1 - (radius - 4) / 4))  # Fade out larger circles
                indicator_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(indicator_surface, (255, 255, 255, alpha), 
                                (radius, radius), radius)
                screen.blit(indicator_surface, 
                          (screen_x + PLAYER_SIZE/2 - radius,
                           screen_y - 15 - radius))
            
            # Draw exclamation mark
            font = pygame.font.Font(None, 24)
            text = font.render("!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_x + PLAYER_SIZE/2, screen_y - 20))
            screen.blit(text, text_rect)