import pygame
import os
from enum import Enum, auto
from pathlib import Path
from ..common.constants import PLAYER_SPEED, PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from .sprite_manager import SpriteManager

class Direction(Enum):
    DOWN = 0
    LEFT = 1
    RIGHT = 2
    UP = 3

class AnimationState(Enum):
    IDLE = 4
    ATTACK = 5

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        
        # Character stats
        self.level = 1
        self.xp = 0
        self.max_health = 100
        self.current_health = self.max_health
        self.strength = 10
        self.defense = 5
        
        # Animation properties
        self.sprite_manager = SpriteManager()
        self._load_sprites()
        self.direction = Direction.DOWN
        self.state = AnimationState.IDLE
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Lower is faster
        self.is_moving = False
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0.4  # Duration of attack animation

    def _load_sprites(self):
        """Load player sprites from spritesheet."""
        # Get the absolute path to the assets directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        sprite_path = project_root / 'src' / 'assets' / 'images' / 'characters' / 'player_full.png'
        
        if not sprite_path.exists():
            print(f"Error: Sprite file not found at {sprite_path}")
            return
            
        self.sprite_manager.load_spritesheet('player', str(sprite_path), PLAYER_SIZE)

    def move(self, dx, dy, game_map):
        """Move the player by the given delta x and y, considering map collisions."""
        new_x = self.x + (dx * self.speed)
        new_y = self.y + (dy * self.speed)
        
        # Update movement state and direction
        self.is_moving = dx != 0 or dy != 0
        if self.is_moving:
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
        
        # Check new positions independently to allow sliding along walls
        if game_map.is_walkable(new_x + PLAYER_SIZE/2, self.y + PLAYER_SIZE/2):
            self.x = new_x
            self.rect.x = new_x
        
        if game_map.is_walkable(self.x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
            self.y = new_y
            self.rect.y = new_y

    def handle_input(self, game_map):
        """Handle keyboard input for player movement and actions."""
        if not self.is_attacking:  # Only allow movement if not attacking
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

        # Handle attack input
        mouse = pygame.mouse.get_pressed()
        if mouse[0] and not self.is_attacking:  # Left mouse button
            self.start_attack()

    def start_attack(self):
        """Start attack animation."""
        self.is_attacking = True
        self.state = AnimationState.ATTACK
        self.attack_timer = 0
        self.animation_frame = 0

    def update(self, dt):
        """Update animation state."""
        if self.is_attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.state = AnimationState.IDLE
                self.animation_frame = 0
            else:
                # Update attack animation frame
                self.animation_timer += dt
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    self.animation_frame = (self.animation_frame + 1) % 4
        else:
            if self.is_moving:
                self.animation_timer += dt
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    self.animation_frame = (self.animation_frame + 1) % 4
            else:
                self.state = AnimationState.IDLE
                self.animation_timer += dt
                if self.animation_timer >= self.animation_speed * 2:  # Slower idle animation
                    self.animation_timer = 0
                    self.animation_frame = (self.animation_frame + 1) % 4

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the player on the screen with camera offset."""
        sprite_row = self.state.value if not self.is_moving else self.direction.value
        sprite = self.sprite_manager.get_animation_frame('player', 
            sprite_row * 4 + self.animation_frame)
        
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