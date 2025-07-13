import pygame
import math
import random
from pathlib import Path
from ..common.constants import PLAYER_SIZE

class Enemy:
    # Enemy type configurations
    ENEMY_TYPES = {
        "goblin": {
            "health": 50,
            "strength": 8,
            "defense": 3,
            "speed": 2,
            "attack_range": 50,
            "aggro_range": 200,
            "color": (150, 0, 0),  # Red
            "exp_value": 10
        },
        "zombie": {
            "health": 75,
            "strength": 12,
            "defense": 2,
            "speed": 1,
            "attack_range": 40,
            "aggro_range": 250,
            "color": (0, 150, 50),  # Green
            "exp_value": 15
        }
    }

    def __init__(self, x, y, enemy_type="goblin"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        
        # Get enemy configuration
        config = self.ENEMY_TYPES.get(enemy_type, self.ENEMY_TYPES["goblin"])
        
        # Stats
        self.level = 1
        self.max_health = config["health"]
        self.current_health = self.max_health
        self.strength = config["strength"]
        self.defense = config["defense"]
        self.attack_range = config["attack_range"]
        self.aggro_range = config["aggro_range"]
        self.speed = config["speed"]
        self.exp_value = config["exp_value"]
        self.base_color = config["color"]
        
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
        
        # Create sprite
        self.sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self._create_enemy_sprite()  # Default color will be used
        
        # Combat text
        self.damage_numbers = []  # List of (damage, x, y, timer, color) tuples
        self.damage_number_duration = 1.0  # How long damage numbers stay on screen
        
    def _create_enemy_sprite(self):
        """Create a detailed enemy sprite based on type"""
        if self.enemy_type == "zombie":
            self._create_zombie_sprite()
        else:  # goblin or default
            self._create_goblin_sprite()
            
    def _create_zombie_sprite(self):
        """Create a zombie-specific sprite"""
        size = PLAYER_SIZE
        
        # Base body shape (irregular and asymmetric)
        body_color = (86, 137, 87)  # Moldy green
        rot_color = (68, 78, 67)    # Darker rotting color
        flesh_color = (163, 73, 73)  # Exposed flesh
        
        # Draw basic body shape
        points = [
            (8, 8),                  # Top left
            (size-8, 10),            # Top right (slightly lower)
            (size-10, size-8),       # Bottom right
            (12, size-10)            # Bottom left
        ]
        pygame.draw.polygon(self.sprite, body_color, points)
        
        # Add rotting texture and decay
        for y in range(8, size-8, 2):
            for x in range(8, size-8, 2):
                if random.random() < 0.4:  # 40% chance for decay spots
                    rot_size = random.randint(1, 4)
                    alpha = random.randint(100, 200)
                    decay_surface = pygame.Surface((rot_size*2, rot_size*2), pygame.SRCALPHA)
                    pygame.draw.circle(decay_surface, (*rot_color, alpha), 
                                    (rot_size, rot_size), rot_size)
                    self.sprite.blit(decay_surface, (x, y))
        
        # Exposed bones (white/yellowish)
        bone_color = (227, 218, 201)  # Off-white bone color
        # Exposed rib cage on one side
        rib_start_y = 20
        for i in range(4):  # Draw 4 ribs
            y = rib_start_y + i * 6
            # Draw exposed flesh behind ribs
            pygame.draw.ellipse(self.sprite, flesh_color,
                              (size-25, y-1, 15, 5))
            # Draw rib
            pygame.draw.arc(self.sprite, bone_color,
                          (size-22, y, 12, 4), 0, 3.14, 2)
        
        # Tattered clothing
        cloth_color = (40, 40, 45, 180)  # Dark gray with transparency
        cloth_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Ragged shirt
        shirt_points = [
            (10, 15),
            (size-10, 18),  # Asymmetric top
            (size-12, 35),
            (8, 32)
        ]
        pygame.draw.polygon(cloth_surface, cloth_color, shirt_points)
        
        # Add tears and holes in clothing
        for _ in range(5):
            tear_x = random.randint(12, size-12)
            tear_y = random.randint(18, 30)
            tear_size = random.randint(3, 7)
            pygame.draw.circle(cloth_surface, (0, 0, 0, 0),  # Transparent hole
                             (tear_x, tear_y), tear_size)
        
        self.sprite.blit(cloth_surface, (0, 0))
        
        # Head features
        # Sunken, asymmetric eye sockets
        socket_color = (27, 32, 27)  # Very dark green
        pygame.draw.ellipse(self.sprite, socket_color, (12, 12, 12, 8))  # Left socket
        pygame.draw.ellipse(self.sprite, socket_color, (size-28, 10, 14, 9))  # Right socket
        
        # One glowing eye, one empty socket
        # Glowing eye (left)
        glow_color = (255, 238, 131, 100)  # Yellow glow
        eye_color = (255, 238, 131)  # Solid yellow
        pupil_color = (200, 0, 0)    # Dark red pupil
        
        # Create glow effect
        glow_surface = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (7, 7), 7)
        self.sprite.blit(glow_surface, (11, 11))
        
        # Eye and pupil
        pygame.draw.circle(self.sprite, eye_color, (16, 16), 3)
        pygame.draw.circle(self.sprite, pupil_color, (16, 16), 1)
        
        # Empty socket with wound (right)
        wound_color = (135, 44, 44)  # Dark red
        pygame.draw.ellipse(self.sprite, wound_color, (size-25, 12, 10, 7))
        # Add some dripping effect
        drip_points = [(size-20, 19), (size-20, 24)]
        pygame.draw.lines(self.sprite, wound_color, False, drip_points, 2)
        
        # Twisted, gaping mouth with exposed teeth
        jaw_offset = random.randint(-2, 2)  # Random jaw misalignment
        mouth_y = 28
        
        # Draw mouth cavity
        pygame.draw.ellipse(self.sprite, (40, 20, 20), 
                          (15, mouth_y, size-30, 8))
        
        # Add teeth (irregular and broken)
        teeth_color = (227, 218, 201)  # Same as bone color
        for x in range(16, size-16, 4):
            if random.random() < 0.7:  # 70% chance for each tooth
                height = random.randint(2, 5)
                # Upper teeth
                pygame.draw.rect(self.sprite, teeth_color,
                               (x, mouth_y, 2, height))
                # Lower teeth (misaligned)
                if random.random() < 0.8:  # Some teeth missing from bottom
                    pygame.draw.rect(self.sprite, teeth_color,
                                   (x + jaw_offset, mouth_y + 6, 2, height))
        
        # Add hanging flesh/skin bits
        for _ in range(3):
            x = random.randint(10, size-10)
            y = random.randint(15, size-15)
            length = random.randint(4, 8)
            flesh_points = [
                (x, y),
                (x + random.randint(-2, 2), y + length)
            ]
            pygame.draw.lines(self.sprite, flesh_color, False, flesh_points, 2)
        
        # Add some green drool/slime
        slime_color = (144, 238, 144, 160)  # Light green, semi-transparent
        slime_surface = pygame.Surface((4, 8), pygame.SRCALPHA)
        pygame.draw.line(slime_surface, slime_color, 
                        (2, 0), (2, 8), 3)
        self.sprite.blit(slime_surface, (size//2-2, mouth_y + 8))
            
    def _create_goblin_sprite(self):
        """Create a goblin-specific sprite"""
        # Main body
        pygame.draw.rect(self.sprite, self.base_color, 
                        (4, 4, PLAYER_SIZE-8, PLAYER_SIZE-8))
        
        # Add texture/pattern
        pattern_color = tuple(max(c - 30, 0) for c in self.base_color)
        for y in range(4, PLAYER_SIZE-8, 4):
            for x in range(4, PLAYER_SIZE-8, 4):
                if (x + y) % 8 == 0:
                    pygame.draw.rect(self.sprite, pattern_color, (x, y, 2, 2))
        
        # Lighter outline with gradient
        for i in range(2):
            outline_color = tuple(min(c + 50 + i*30, 255) for c in self.base_color)
            pygame.draw.rect(self.sprite, outline_color, 
                           (4-i, 4-i, PLAYER_SIZE-8+i*2, PLAYER_SIZE-8+i*2), 1)
        
        # Eyes (glowing effect)
        eye_color = (255, 255, 200)  # Slightly yellow tint
        pupil_color = (255, 0, 0)    # Red pupils
        glow_color = (255, 255, 100, 100)  # Semi-transparent glow
        
        # Create glow effect
        glow_surface = pygame.Surface((12, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surface, glow_color, (0, 0, 12, 16))
        
        # Left eye
        self.sprite.blit(glow_surface, (6, 6))
        pygame.draw.ellipse(self.sprite, eye_color, (8, 8, 8, 12))
        pygame.draw.ellipse(self.sprite, pupil_color, (10, 12, 4, 4))
        
        # Right eye
        self.sprite.blit(glow_surface, (PLAYER_SIZE-18, 6))
        pygame.draw.ellipse(self.sprite, eye_color, 
                          (PLAYER_SIZE-16, 8, 8, 12))
        pygame.draw.ellipse(self.sprite, pupil_color, 
                          (PLAYER_SIZE-14, 12, 4, 4))
        
        # Angry eyebrows with gradient
        brow_colors = [tuple(max(c - 50 - i*20, 0) for c in self.base_color) for i in range(2)]
        for i, brow_color in enumerate(brow_colors):
            pygame.draw.line(self.sprite, brow_color, 
                           (6, 6+i), (14, 10+i), 2-i)
            pygame.draw.line(self.sprite, brow_color, 
                           (PLAYER_SIZE-6, 6+i), (PLAYER_SIZE-14, 10+i), 2-i)
        
        # Spikes on top with gradient
        spike_colors = [tuple(min(c + 50 + i*30, 255) for c in self.base_color) for i in range(2)]
        spike_points = [
            (8, 4), (12, 0), (16, 4),
            (16, 4), (20, 0), (24, 4),
            (24, 4), (28, 0), (32, 4)
        ]
        for i, spike_color in enumerate(spike_colors):
            offset = i
            adjusted_points = [(x, y+offset) for x, y in spike_points]
            pygame.draw.lines(self.sprite, spike_color, False, adjusted_points, 2-i)
        
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
        # Check if player is in attack range
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.attack_range:
            return
            
        self.is_attacking = True
        self.attack_timer = self.attack_cooldown
        
        # Calculate knockback direction
        if distance > 0:
            knockback_direction = (dx/distance, dy/distance)
        else:
            knockback_direction = (1, 0)
            
        # Deal damage to player
        damage = random.randint(
            int(self.strength * 0.8),
            int(self.strength * 1.2)
        )  # Add some randomness
        player.take_damage(damage, knockback_direction)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the enemy"""
        if not self.is_alive:
            return
            
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Draw shadow
        shadow_height = 4
        shadow_surface = pygame.Surface((PLAYER_SIZE, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 128), 
                          (0, 0, PLAYER_SIZE, shadow_height))
        screen.blit(shadow_surface, (
            screen_x,
            screen_y + PLAYER_SIZE - shadow_height/2
        ))
        
        # Flash white when hit
        if self.is_hit:
            white_sprite = self.sprite.copy()
            white_sprite.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(white_sprite, (screen_x, screen_y))
        else:
            screen.blit(self.sprite, (screen_x, screen_y))
            
        # Draw health bar with improved visuals
        health_pct = self.current_health / self.max_health
        bar_width = self.rect.width
        bar_height = 5
        bar_x = screen_x
        bar_y = screen_y - 10
        
        # Background (dark gray)
        pygame.draw.rect(screen, (64, 64, 64),
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health (red gradient based on health percentage)
        if health_pct > 0:
            red = 255
            green = int(255 * health_pct * 0.5)  # Less green for a more aggressive look
            health_color = (red, green, 0)
            pygame.draw.rect(screen, health_color,
                           (bar_x, bar_y, bar_width * health_pct, bar_height))
            
            # Add highlight
            highlight_height = max(1, int(bar_height * 0.3))
            pygame.draw.rect(screen, (min(red + 50, 255), min(green + 50, 255), 50),
                           (bar_x, bar_y, bar_width * health_pct, highlight_height))
                        
        # Draw damage numbers with improved visuals
        font = pygame.font.Font(None, 24)
        for damage, x, y, timer, color in self.damage_numbers:
            # Float up and fade out with bounce effect
            progress = (self.damage_number_duration - timer) / self.damage_number_duration
            y_offset = -30 * progress  # Base upward movement
            
            # Add bounce effect
            bounce = math.sin(progress * math.pi * 2) * 5 * (1 - progress)
            y_offset += bounce
            
            # Scale based on damage
            scale = min(1.5, 1 + damage / 50)  # Max 1.5x size for big hits
            
            # Fade out
            alpha = int(255 * (1 - progress))
            
            # Render with outline for better visibility
            text = font.render(str(damage), True, color)
            text = pygame.transform.scale(text, 
                (int(text.get_width() * scale), 
                 int(text.get_height() * scale)))
            
            # Create outline
            outline = font.render(str(damage), True, (0, 0, 0))
            outline = pygame.transform.scale(outline, 
                (int(outline.get_width() * scale), 
                 int(outline.get_height() * scale)))
            
            # Position for centered text
            text_x = x - text.get_width()/2 - camera_x
            text_y = y + y_offset - text.get_height()/2 - camera_y
            
            # Draw outline then text
            for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                outline.set_alpha(alpha)
                screen.blit(outline, (text_x + dx, text_y + dy))
            text.set_alpha(alpha)
            screen.blit(text, (text_x, text_y))
            
        # Draw attack indicator when enemy is attacking
        if self.is_attacking:
            attack_radius = self.attack_range
            attack_surface = pygame.Surface((attack_radius*2, attack_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(attack_surface, (255, 0, 0, 50), 
                             (attack_radius, attack_radius), attack_radius)
            screen.blit(attack_surface, (
                screen_x + PLAYER_SIZE/2 - attack_radius,
                screen_y + PLAYER_SIZE/2 - attack_radius
            ))