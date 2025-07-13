import pygame
import math
import random
from pathlib import Path
from ..common.constants import PLAYER_SIZE

class Enemy:
    def __init__(self, x, y, enemy_type="goblin"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        
        # Stats
        self.level = 1
        self.max_health = 50
        self.current_health = self.max_health
        self.strength = 8
        self.defense = 3
        self.attack_range = 50  # Pixels
        self.aggro_range = 200  # Pixels
        self.speed = 2
        
        # State
        self.is_alive = True
        self.is_attacking = False
        self.attack_cooldown = 1.0  # Seconds
        self.attack_timer = 0
        self.hit_cooldown = 0.5  # Invulnerability time after being hit
        self.hit_timer = 0
        self.is_hit = False
        self.knockback_distance = 0
        self.knockback_direction = (0, 0)
        
        # Create a more detailed enemy appearance
        self.sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self._create_enemy_sprite()  # Default color will be used
        
        # Combat text
        self.damage_numbers = []  # List of (damage, x, y, timer, color) tuples
        self.damage_number_duration = 1.0  # How long damage numbers stay on screen
        
    def _create_enemy_sprite(self, color=(150, 0, 0)):
        """Create a more detailed enemy sprite"""
        # Main body (dark red or custom color)
        pygame.draw.rect(self.sprite, color, 
                        (4, 4, PLAYER_SIZE-8, PLAYER_SIZE-8))
        
        # Lighter outline (brighten the base color)
        outline_color = tuple(min(c + 50, 255) for c in color)
        pygame.draw.rect(self.sprite, outline_color, 
                        (4, 4, PLAYER_SIZE-8, PLAYER_SIZE-8), 2)
        
        # Eyes (white with black pupils)
        eye_color = (255, 255, 255)
        pupil_color = (0, 0, 0)
        
        # Left eye
        pygame.draw.ellipse(self.sprite, eye_color, 
                          (8, 8, 8, 12))
        pygame.draw.ellipse(self.sprite, pupil_color, 
                          (10, 12, 4, 4))
        
        # Right eye
        pygame.draw.ellipse(self.sprite, eye_color, 
                          (PLAYER_SIZE-16, 8, 8, 12))
        pygame.draw.ellipse(self.sprite, pupil_color, 
                          (PLAYER_SIZE-14, 12, 4, 4))
        
        # Angry eyebrows
        brow_color = tuple(max(c - 50, 0) for c in color)  # Darker than base color
        pygame.draw.line(self.sprite, brow_color, 
                        (6, 6), (14, 10), 2)
        pygame.draw.line(self.sprite, brow_color, 
                        (PLAYER_SIZE-6, 6), (PLAYER_SIZE-14, 10), 2)
        
        # Spikes on top
        spike_color = outline_color
        spike_points = [
            (8, 4), (12, 0), (16, 4),
            (16, 4), (20, 0), (24, 4),
            (24, 4), (28, 0), (32, 4)
        ]
        pygame.draw.lines(self.sprite, spike_color, False, spike_points, 2)
        
    def update(self, dt, player, game_map):
        """Update enemy state"""
        if not self.is_alive:
            return
            
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
            new_x = self.x + self.knockback_direction[0] * move_distance
            new_y = self.y + self.knockback_direction[1] * move_distance
            
            if game_map.is_walkable(new_x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
                self.x = new_x
                self.y = new_y
                self.rect.x = new_x
                self.rect.y = new_y
            else:
                # If we hit a wall, stop knockback
                self.knockback_distance = 0
            
            self.knockback_distance -= move_distance
            
        else:
            # Normal movement and combat
            dist_to_player = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
            
            # If player is in aggro range, move toward them
            if dist_to_player < self.aggro_range:
                if dist_to_player > self.attack_range:  # Only move if not in attack range
                    # Calculate direction to player
                    dx = player.x - self.x
                    dy = player.y - self.y
                    length = math.sqrt(dx**2 + dy**2)
                    if length > 0:
                        dx = dx / length
                        dy = dy / length
                        
                        # Move toward player
                        new_x = self.x + dx * self.speed
                        new_y = self.y + dy * self.speed
                        
                        # Check collision with map
                        if game_map.is_walkable(new_x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
                            self.x = new_x
                            self.y = new_y
                            self.rect.x = new_x
                            self.rect.y = new_y
                
                # Attack if in range and cooldown is ready
                if dist_to_player <= self.attack_range and self.attack_timer <= 0:
                    self.attack(player)
                    
        # Update damage numbers
        self.damage_numbers = [(dmg, x, y, timer - dt, color) 
                             for dmg, x, y, timer, color in self.damage_numbers 
                             if timer > 0]
    
    def take_damage(self, damage, knockback_direction=None, damage_color=(255, 255, 255)):
        """Take damage and handle knockback"""
        if not self.is_alive or self.hit_timer > 0:
            return
            
        # Apply defense reduction
        actual_damage = max(1, damage - self.defense)
        self.current_health -= actual_damage
        
        # Add damage number with color
        self.damage_numbers.append((
            actual_damage,
            self.x + random.randint(-10, 10),
            self.y - 20,
            self.damage_number_duration,
            damage_color
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
            self.is_alive = False
            
    def attack(self, player):
        """Attack the player"""
        self.is_attacking = True
        self.attack_timer = self.attack_cooldown
        
        # Calculate knockback direction
        dx = player.x - self.x
        dy = player.y - self.y
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            knockback_direction = (dx/length, dy/length)
        else:
            knockback_direction = (1, 0)
            
        # Deal damage to player
        player.take_damage(self.strength, knockback_direction)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the enemy"""
        if not self.is_alive:
            return
            
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Flash white when hit
        if self.is_hit:
            white_sprite = self.sprite.copy()
            white_sprite.fill((255, 255, 255))
            screen.blit(white_sprite, (screen_x, screen_y))
        else:
            screen.blit(self.sprite, (screen_x, screen_y))
            
        # Draw health bar
        health_pct = self.current_health / self.max_health
        bar_width = self.rect.width
        bar_height = 5
        bar_x = screen_x
        bar_y = screen_y - 10
        
        # Background (gray)
        pygame.draw.rect(screen, (128, 128, 128),
                        (bar_x, bar_y, bar_width, bar_height))
        # Health (red for enemies)
        pygame.draw.rect(screen, (255, 0, 0),
                        (bar_x, bar_y, bar_width * health_pct, bar_height))
                        
        # Draw damage numbers with colors
        font = pygame.font.Font(None, 20)
        for damage, x, y, timer, color in self.damage_numbers:
            # Float up and fade out
            y_offset = (self.damage_number_duration - timer) * 30
            alpha = int(255 * (timer / self.damage_number_duration))
            
            text = font.render(str(damage), True, color)
            text.set_alpha(alpha)
            screen.blit(text, (x - camera_x, y - y_offset - camera_y))