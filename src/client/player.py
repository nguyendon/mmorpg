import pygame
import os
import math
import random
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
        
        # Combat properties
        self.attack_range = 60  # Pixels
        self.attack_cooldown = 0.5  # Seconds
        self.attack_timer = 0
        self.hit_cooldown = 0.5  # Invulnerability time after being hit
        self.hit_timer = 0
        self.is_hit = False
        self.knockback_distance = 0
        self.knockback_direction = (0, 0)
        self.damage_numbers = []  # List of (damage, x, y, timer) tuples
        self.damage_number_duration = 1.0  # How long damage numbers stay on screen
        
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
        # Only prevent movement during attack animation, not during knockback
        if not self.is_attacking:
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
                self.direction = Direction.LEFT
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
                self.direction = Direction.RIGHT
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
                self.direction = Direction.UP
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
                self.direction = Direction.DOWN

            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707  # 1/√2
                dy *= 0.707

            # Update movement state
            self.is_moving = dx != 0 or dy != 0

            # Try to move
            new_x = self.x + (dx * self.speed)
            new_y = self.y + (dy * self.speed)

            # Check new positions independently to allow sliding along walls
            if game_map.is_walkable(new_x + PLAYER_SIZE/2, self.y + PLAYER_SIZE/2):
                self.x = new_x
                self.rect.x = new_x

            if game_map.is_walkable(self.x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
                self.y = new_y
                self.rect.y = new_y

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
        """Update animation state and combat timers."""
        # Update timers
        if self.attack_timer > 0:
            self.attack_timer -= dt
        if self.hit_timer > 0:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.is_hit = False
                
        # Handle knockback
        if self.knockback_distance > 0:
            move_distance = min(self.knockback_distance, 10 * dt)
            self.x += self.knockback_direction[0] * move_distance
            self.y += self.knockback_direction[1] * move_distance
            self.rect.x = self.x
            self.rect.y = self.y
            self.knockback_distance -= move_distance
        
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
                    
        # Update damage numbers
        self.damage_numbers = [(dmg, x, y, timer - dt) 
                             for dmg, x, y, timer in self.damage_numbers 
                             if timer > 0]
                    
    def take_damage(self, damage, knockback_direction=None):
        """Take damage from an attack and handle knockback"""
        if self.hit_timer > 0:  # Still in invulnerability frames
            return
            
        # Apply defense reduction
        actual_damage = max(1, damage - self.defense)
        self.current_health -= actual_damage
        
        # Add damage number
        self.damage_numbers.append((
            actual_damage,
            self.x + random.randint(-10, 10),
            self.y - 20,
            self.damage_number_duration
        ))
        
        # Apply knockback
        if knockback_direction:
            self.knockback_distance = 30
            self.knockback_direction = knockback_direction
        
        self.is_hit = True
        self.hit_timer = self.hit_cooldown
        
        # Check if dead
        if self.current_health <= 0:
            self.current_health = 0
            # Handle death (could add game over screen here)
            
    def attack(self, enemies):
        """Perform attack and check for hits on enemies"""
        if not self.is_attacking and self.attack_timer <= 0:
            self.is_attacking = True
            self.state = AnimationState.ATTACK
            self.attack_timer = 0
            self.animation_frame = 0
            
            # Get attack hitbox based on direction
            attack_rect = self._get_attack_hitbox()
            
            # Check for hits on enemies
            for enemy in enemies:
                if enemy.is_alive and attack_rect.colliderect(enemy.rect):
                    # Calculate knockback direction
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    length = math.sqrt(dx**2 + dy**2)
                    if length > 0:
                        knockback_direction = (dx/length, dy/length)
                    else:
                        knockback_direction = (1, 0)
                        
                    # Deal damage
                    enemy.take_damage(self.strength, knockback_direction)
                    
    def _get_attack_hitbox(self):
        """Get the attack hitbox based on player direction"""
        if self.direction == Direction.LEFT:
            return pygame.Rect(self.rect.x - self.attack_range, self.rect.y,
                             self.attack_range, self.rect.height)
        elif self.direction == Direction.RIGHT:
            return pygame.Rect(self.rect.right, self.rect.y,
                             self.attack_range, self.rect.height)
        elif self.direction == Direction.UP:
            return pygame.Rect(self.rect.x, self.rect.y - self.attack_range,
                             self.rect.width, self.attack_range)
        else:  # Direction.DOWN
            return pygame.Rect(self.rect.x, self.rect.bottom,
                             self.rect.width, self.attack_range)

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the player on the screen with camera offset."""
        sprite_row = self.state.value if not self.is_moving else self.direction.value
        sprite = self.sprite_manager.get_animation_frame('player', 
            sprite_row * 4 + self.animation_frame)
        
        if sprite:
            # Flash white when hit
            if self.is_hit:
                white_sprite = sprite.copy()
                white_sprite.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
                screen.blit(white_sprite, (
                    self.rect.x - camera_x,
                    self.rect.y - camera_y
                ))
            else:
                screen.blit(sprite, (
                    self.rect.x - camera_x,
                    self.rect.y - camera_y
                ))
                
            # Draw damage numbers
            font = pygame.font.Font(None, 20)
            for damage, x, y, timer in self.damage_numbers:
                # Float up and fade out
                y_offset = (self.damage_number_duration - timer) * 30
                alpha = int(255 * (timer / self.damage_number_duration))
                
                text = font.render(str(damage), True, (255, 255, 255))
                text.set_alpha(alpha)
                screen.blit(text, (x - camera_x, y - y_offset - camera_y))
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