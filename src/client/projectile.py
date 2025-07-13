import pygame
import math
from ..common.constants import PLAYER_SIZE

class Projectile:
    def __init__(self, x, y, direction, speed, damage, range, color=(255, 255, 0)):
        self.x = x
        self.y = y
        self.direction = direction  # Normalized vector (dx, dy)
        self.speed = speed
        self.damage = damage
        self.range = range
        self.color = color
        self.distance_traveled = 0
        self.alive = True
        self.rect = pygame.Rect(x, y, 8, 8)  # Small projectile hitbox
        
    def update(self, dt, game_map, enemies):
        """Update projectile position and check for collisions"""
        if not self.alive:
            return
            
        # Move projectile
        dx = self.direction[0] * self.speed * dt
        dy = self.direction[1] * self.speed * dt
        
        # Update position
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Update distance traveled
        self.distance_traveled += math.sqrt(dx*dx + dy*dy)
        
        # Check if out of range
        if self.distance_traveled >= self.range:
            self.alive = False
            return
            
        # Check for wall collision
        if not game_map.is_walkable(self.x + 4, self.y + 4):
            self.alive = False
            return
            
        # Check for enemy collision
        for enemy in enemies:
            if enemy.is_alive and self.rect.colliderect(enemy.rect):
                # Calculate knockback direction
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    knockback_direction = (dx/length, dy/length)
                else:
                    knockback_direction = self.direction
                
                # Deal damage to enemy
                enemy.take_damage(self.damage, knockback_direction, (255, 255, 0))
                self.alive = False
                return
                
    def draw(self, screen, camera_x, camera_y):
        """Draw the projectile"""
        if not self.alive:
            return
            
        # Draw projectile trail
        trail_length = 20
        end_x = self.x - self.direction[0] * trail_length
        end_y = self.y - self.direction[1] * trail_length
        
        # Draw trail (semi-transparent)
        pygame.draw.line(screen, (*self.color, 128),
                        (self.x - camera_x + 4, self.y - camera_y + 4),
                        (end_x - camera_x + 4, end_y - camera_y + 4), 3)
        
        # Draw projectile
        pygame.draw.circle(screen, self.color,
                         (int(self.x - camera_x + 4), int(self.y - camera_y + 4)), 4)