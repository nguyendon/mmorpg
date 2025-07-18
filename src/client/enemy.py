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
            "speed": 100,  # Increased speed
            "attack_range": 50,
            "aggro_range": 300,  # Increased range
            "exp_value": 10
        },
        "zombie": {
            "health": 75,
            "strength": 12,
            "defense": 2,
            "speed": 80,  # Increased speed
            "attack_range": 40,
            "aggro_range": 350,  # Increased range
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
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2  # Seconds per frame
        self.facing_left = False
        
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
        
        # Aggro state
        self.is_aggroed = False
        self.aggro_duration = 10.0  # How long to chase player after losing sight
        self.aggro_timer = 0
        self.last_seen_pos = None  # Last known player position
        
        # Pathfinding state
        self.stuck_timer = 0
        self.stuck_threshold = 0.5  # Time before considering enemy stuck
        self.last_position = (x, y)
        self.stuck_cooldown = 0
        
        # Load sprite sheet
        self.sprites = {}
        self._load_sprites()
        
        # Combat text
        self.damage_numbers = []  # List of (damage, x, y, timer, color) tuples
        self.damage_number_duration = 1.0  # How long damage numbers stay on screen
        
    def _load_sprites(self):
        """Load the appropriate sprite sheet based on enemy type"""
        if self.enemy_type == "zombie":
            self._load_zombie_sprites()
        else:
            self._load_goblin_sprites()
            
    def _load_zombie_sprites(self):
        """Load zombie sprite sheet and extract animation frames"""
        # Load the sprite sheet
        try:
            sprite_sheet = pygame.image.load("src/assets/images/enemies/zombie.png").convert_alpha()
            
            # Define frame positions (each frame is 32x32 pixels)
            frame_width = 32
            frame_height = 32
            
            # Extract walking animation frames (first row)
            self.sprites['walk'] = []
            for i in range(3):  # 3 frames of walking animation
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                # Scale up the frame to match player size
                frame = pygame.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
                self.sprites['walk'].append(frame)
                
            # Extract attack animation frames (second row)
            self.sprites['attack'] = []
            for i in range(2):  # 2 frames of attack animation
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sprite_sheet, (0, 0), (i * frame_width, frame_height, frame_width, frame_height))
                # Scale up the frame to match player size
                frame = pygame.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
                self.sprites['attack'].append(frame)
                
        except pygame.error as e:
            print(f"Error loading zombie sprites: {e}")
            # Fallback to basic rectangle if sprite loading fails
            self.sprites['walk'] = [self._create_basic_sprite()]
            self.sprites['attack'] = [self._create_basic_sprite()]
            
    def _load_goblin_sprites(self):
        """Create basic goblin sprite"""
        sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        
        # Main body
        pygame.draw.rect(sprite, (150, 0, 0), 
                        (4, 4, PLAYER_SIZE-8, PLAYER_SIZE-8))
        
        # Add texture/pattern
        pattern_color = (120, 0, 0)
        for y in range(4, PLAYER_SIZE-8, 4):
            for x in range(4, PLAYER_SIZE-8, 4):
                if (x + y) % 8 == 0:
                    pygame.draw.rect(sprite, pattern_color, (x, y, 2, 2))
        
        # Eyes
        eye_color = (255, 255, 200)
        pupil_color = (255, 0, 0)
        
        # Left eye
        pygame.draw.ellipse(sprite, eye_color, (8, 8, 8, 12))
        pygame.draw.ellipse(sprite, pupil_color, (10, 12, 4, 4))
        
        # Right eye
        pygame.draw.ellipse(sprite, eye_color, 
                          (PLAYER_SIZE-16, 8, 8, 12))
        pygame.draw.ellipse(sprite, pupil_color, 
                          (PLAYER_SIZE-14, 12, 4, 4))
        
        # Store the sprite for both walk and attack animations
        self.sprites['walk'] = [sprite]
        self.sprites['attack'] = [sprite]
        
    def _create_basic_sprite(self):
        """Create a basic rectangular sprite as fallback"""
        sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(sprite, (255, 0, 0), 
                        (4, 4, PLAYER_SIZE-8, PLAYER_SIZE-8))
        return sprite
        
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
            
            # Check if player is in line of sight (simple raycast)
            has_line_of_sight = self._check_line_of_sight(player, game_map)
            
            # Update aggro state
            if dist_to_player < self.aggro_range and has_line_of_sight:
                self.is_aggroed = True
                self.aggro_timer = self.aggro_duration
                self.last_seen_pos = (player.x, player.y)
            elif self.is_aggroed:
                self.aggro_timer -= dt
                if self.aggro_timer <= 0:
                    self.is_aggroed = False
                    self.last_seen_pos = None
            
            # Movement logic
            if self.is_aggroed:
                # Update facing direction
                self.facing_left = player.x < self.x
                
                if dist_to_player > self.attack_range:  # Only move if not in attack range
                    # Calculate direction to target (either player or last seen position)
                    target_x = player.x if has_line_of_sight else self.last_seen_pos[0]
                    target_y = player.y if has_line_of_sight else self.last_seen_pos[1]
                    
                    dx = target_x - self.x
                    dy = target_y - self.y
                    length = math.sqrt(dx**2 + dy**2)
                    if length > 0:
                        dx = dx / length
                        dy = dy / length
                        
                        # Check if stuck
                        current_pos = (self.x, self.y)
                        if (abs(current_pos[0] - self.last_position[0]) < 1 and
                            abs(current_pos[1] - self.last_position[1]) < 1):
                            self.stuck_timer += dt
                        else:
                            self.stuck_timer = 0
                            self.last_position = current_pos
                        
                        # If stuck, try alternative movement patterns
                        if self.stuck_timer >= self.stuck_threshold and self.stuck_cooldown <= 0:
                            # Try moving perpendicular to the stuck direction
                            attempted_moves = [
                                (-dy, dx),  # 90 degrees right
                                (dy, -dx),  # 90 degrees left
                                (-dx, -dy), # Backwards
                                (dx, 0),    # Horizontal only
                                (0, dy)     # Vertical only
                            ]
                            self.stuck_cooldown = 1.0  # Wait before trying again
                        else:
                            # Normal movement patterns
                            attempted_moves = [
                                (dx, dy),  # Try direct path first
                                (dx, 0),   # Try horizontal movement
                                (0, dy),   # Try vertical movement
                                (-dy, dx), # Try perpendicular movement (right)
                                (dy, -dx)  # Try perpendicular movement (left)
                            ]
                        
                        # Update stuck cooldown
                        if self.stuck_cooldown > 0:
                            self.stuck_cooldown -= dt
                        
                        # Try each movement pattern
                        moved = False
                        for move_dx, move_dy in attempted_moves:
                            # Scale movement by speed and time
                            new_x = self.x + move_dx * self.speed * dt
                            new_y = self.y + move_dy * self.speed * dt
                            
                            # Check if new position is walkable
                            if game_map.is_walkable(new_x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
                                # Move to new position
                                self.x = new_x
                                self.y = new_y
                                self.rect.x = new_x
                                self.rect.y = new_y
                                moved = True
                                break
                        
                        # Update animation if we moved
                        if moved:
                            self.animation_timer += dt
                            if self.animation_timer >= self.animation_speed:
                                self.animation_timer = 0
                                self.animation_frame = (self.animation_frame + 1) % len(self.sprites['walk'])
                
                # Attack if in range and cooldown is ready
                if dist_to_player <= self.attack_range and self.attack_timer <= 0 and has_line_of_sight:
                    self.attack(player)
                    
        # Update damage numbers
        self.damage_numbers = [(dmg, x, y, timer - dt, color) 
                             for dmg, x, y, timer, color in self.damage_numbers 
                             if timer > 0]
                             
    def _check_line_of_sight(self, player, game_map):
        """Check if there's a clear line of sight to the player"""
        # Get start and end points
        start_x = self.x + PLAYER_SIZE/2
        start_y = self.y + PLAYER_SIZE/2
        end_x = player.x + PLAYER_SIZE/2
        end_y = player.y + PLAYER_SIZE/2
        
        # Calculate direction and distance
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return True
            
        # Normalize direction
        dx = dx / distance
        dy = dy / distance
        
        # Check points along the line
        steps = int(distance / (PLAYER_SIZE/2))  # Check every half player size
        for i in range(steps):
            check_x = start_x + dx * i * (PLAYER_SIZE/2)
            check_y = start_y + dy * i * (PLAYER_SIZE/2)
            
            # If any point is not walkable, there's no line of sight
            if not game_map.is_walkable(check_x, check_y):
                return False
                
        return True
    
    def take_damage(self, damage, knockback_direction=None, damage_color=(255, 255, 255), player=None):
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
            # Grant XP to player when defeated
            if player and hasattr(player, 'gain_xp'):
                scaled_xp = int(self.exp_value * (1 + (self.level - 1) * 0.1))  # 10% more XP per level
                player.gain_xp(scaled_xp)
            
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
        
        # Get current sprite based on state
        sprite_list = self.sprites['attack'] if self.is_attacking else self.sprites['walk']
        current_sprite = sprite_list[self.animation_frame % len(sprite_list)]
        
        # Flip sprite if facing left
        if self.facing_left:
            current_sprite = pygame.transform.flip(current_sprite, True, False)
        
        # Flash white when hit
        if self.is_hit:
            white_sprite = current_sprite.copy()
            white_sprite.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(white_sprite, (screen_x, screen_y))
        else:
            screen.blit(current_sprite, (screen_x, screen_y))
            
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