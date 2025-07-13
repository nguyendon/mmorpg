import pygame
import os
from ..common.constants import PLAYER_SPEED, PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from .sprite_manager import SpriteManager

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        
        # Animation properties
        self.sprite_manager = SpriteManager()
        self._load_sprites()
        self.animation_frame = 0
        self.animation_speed = 0.2  # Lower is faster
        self.animation_timer = 0
        self.is_moving = False

    def _load_sprites(self):
        """Load player sprites."""
        sprite_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'characters', 'player.png')
        self.sprite_manager.load_spritesheet('player_walk', sprite_path, PLAYER_SIZE)

    def move(self, dx, dy, game_map):
        """Move the player by the given delta x and y, considering map collisions."""
        new_x = self.x + (dx * self.speed)
        new_y = self.y + (dy * self.speed)
        
        # Update is_moving state
        self.is_moving = dx != 0 or dy != 0
        
        # Check new positions independently to allow sliding along walls
        if game_map.is_walkable(new_x + PLAYER_SIZE/2, self.y + PLAYER_SIZE/2):
            self.x = new_x
            self.rect.x = new_x
        
        if game_map.is_walkable(self.x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
            self.y = new_y
            self.rect.y = new_y

    def handle_input(self, game_map):
        """Handle keyboard input for player movement."""
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/√2
            dy *= 0.707

        self.move(dx, dy, game_map)

    def update(self, dt):
        """Update animation state."""
        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the player on the screen with camera offset."""
        sprite = self.sprite_manager.get_animation_frame('player_walk', self.animation_frame)
        if sprite:
            screen.blit(sprite, (
                self.rect.x - camera_x,
                self.rect.y - camera_y
            ))
        else:
            # Fallback to rectangle if sprite loading failed
            draw_rect = pygame.Rect(
                self.rect.x - camera_x,
                self.rect.y - camera_y,
                self.rect.width,
                self.rect.height
            )
            pygame.draw.rect(screen, (255, 0, 0), draw_rect)

    def get_position(self):
        """Return the current position as a tuple."""
        return (self.x, self.y)