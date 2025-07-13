import pygame
import os
import math
import random
from enum import Enum, auto
from pathlib import Path
from ..common.constants import PLAYER_SPEED, PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from ..common.tiles import Tile, TileType
from .sprite_manager import SpriteManager
from .inventory import Inventory
from .items import ItemType

class Direction(Enum):
    DOWN = 0
    LEFT = 1
    RIGHT = 2
    UP = 3

class AnimationState(Enum):
    IDLE = 4
    ATTACK = 5
    DASH = 6
    CAST = 7

class AttackType(Enum):
    SLASH = 1  # Basic melee attack
    SPIN = 2   # 360-degree attack (costs mana)
    DASH = 3   # Dash attack (costs mana)
    WAVE = 4   # Energy wave attack (costs mana)

class DamageType(Enum):
    NORMAL = (255, 255, 255)  # White for normal damage
    CRITICAL = (255, 255, 0)  # Yellow for critical hits
    SPECIAL = (0, 255, 255)   # Cyan for special attack damage

class Player:
    # Constants
    MAX_DAMAGE_NUMBERS = 50
    MANA_REGEN_RATE = 10  # Mana points per second
    
    def __init__(self, x, y, gender='male'):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.gender = gender
        
        # Character stats
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100  # Base XP needed for level 2
        self.max_health = 100
        self.current_health = self.max_health
        self.max_mana = 100
        self.current_mana = self.max_mana
        self.base_strength = 10
        self.base_defense = 5
        self.base_speed = PLAYER_SPEED
        self.strength = self.base_strength
        self.defense = self.base_defense
        self.speed = self.base_speed
        
        # Combat properties
        self.attack_range = 60  # Pixels
        self.attack_cooldown = 0.5  # Seconds
        self.attack_timer = 0
        self.hit_cooldown = 0.5  # Invulnerability time after being hit
        self.hit_timer = 0
        self.is_hit = False
        self.knockback_distance = 0
        self.knockback_direction = (0, 0)
        self.damage_numbers = []  # List of (damage, x, y, timer, color) tuples
        self.damage_number_duration = 1.0  # How long damage numbers stay on screen
        
        # Attack properties
        self.current_attack = None
        self.attack_timers = {
            AttackType.SLASH: 0,
            AttackType.SPIN: 0,
            AttackType.DASH: 0,
            AttackType.WAVE: 0
        }
        self.attack_cooldowns = {
            AttackType.SLASH: 0.5,
            AttackType.SPIN: 2.0,
            AttackType.DASH: 1.5,
            AttackType.WAVE: 3.0
        }
        self.mana_costs = {
            AttackType.SLASH: 0,    # Basic attack is free
            AttackType.SPIN: 30,    # Spin attack costs 30 mana
            AttackType.DASH: 20,    # Dash attack costs 20 mana
            AttackType.WAVE: 40     # Wave attack costs 40 mana
        }
        
        # Gun properties
        self.gun = None
        self.gun_cooldown = 0
        self.projectiles = []
        
        # Dash attack properties
        self.dash_speed = 500
        self.dash_duration = 0.2
        self.dash_timer = 0
        self.dash_direction = (0, 0)
        
        # Wave attack properties
        self.wave_speed = 300
        self.wave_lifetime = 0.5
        self.waves = []  # List of active wave attacks
        
        # Reference to enemies and particle system (will be set by GameClient)
        self.current_enemies = []
        self.particle_system = None
        
        # Animation properties
        self.sprite_manager = SpriteManager()
        self.sprites_loaded = False
        self.direction = Direction.DOWN
        self.state = AnimationState.IDLE
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # Lower is faster
        self.is_moving = False
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0.4  # Duration of attack animation
        
        # Critical hit chance
        self.crit_chance = 0.2  # 20% chance for critical hit
        self.crit_multiplier = 1.5  # 50% more damage on crit
        
        # Inventory system
        self.inventory = Inventory()
        self.equipment = {
            'weapon': None,
            'armor': None,
            'accessory': None
        }
        
        # Load sprites
        self._load_sprites()

    def _load_sprites(self):
        """Load player sprites from spritesheet."""
        if not self.sprites_loaded:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            sprite_path = project_root / 'src' / 'assets' / 'images' / 'characters' / f'player_{self.gender}.png'
            
            if not sprite_path.exists():
                print(f"Error: Sprite file not found at {sprite_path}")
                return
                
            self.sprite_manager.load_spritesheet('player', str(sprite_path), PLAYER_SIZE)
            self.sprites_loaded = True
        
    def handle_input(self, game_map):
        """Handle keyboard input for player movement and actions."""
        # Only prevent movement during attack animation, not during knockback
        if not self.is_attacking and not self.current_attack:
            keys = pygame.key.get_pressed()
            dx = 0
            dy = 0

            # Movement
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

            # Calculate new positions
            new_x = self.x + (dx * self.speed)
            new_y = self.y + (dy * self.speed)

            # Get current tile type
            current_tile = game_map.get_tile(self.x + PLAYER_SIZE/2, self.y + PLAYER_SIZE/2)
            movement_speed = self.speed

            # Adjust speed for water tiles
            if current_tile and current_tile.tile_type == TileType.WATER:
                movement_speed *= 0.5  # 50% slower in water

            # Apply movement with adjusted speed
            new_x = self.x + (dx * movement_speed)
            new_y = self.y + (dy * movement_speed)

            # Check new positions independently to allow sliding along walls
            if game_map.is_walkable(new_x + PLAYER_SIZE/2, self.y + PLAYER_SIZE/2):
                self.x = new_x
                self.rect.x = new_x

            if game_map.is_walkable(self.x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
                self.y = new_y
                self.rect.y = new_y

        # Attack inputs
        keys = pygame.key.get_pressed()
        if not self.current_attack:
            if keys[pygame.K_j] and self.attack_timers[AttackType.SLASH] <= 0:
                self.slash_attack()
            elif keys[pygame.K_k] and self.attack_timers[AttackType.SPIN] <= 0:
                if self.current_mana >= self.mana_costs[AttackType.SPIN]:
                    self.spin_attack()
            elif keys[pygame.K_l] and self.attack_timers[AttackType.DASH] <= 0:
                if self.current_mana >= self.mana_costs[AttackType.DASH]:
                    self.dash_attack()
            elif keys[pygame.K_u] and self.attack_timers[AttackType.WAVE] <= 0:
                if self.current_mana >= self.mana_costs[AttackType.WAVE]:
                    self.wave_attack()
            elif keys[pygame.K_SPACE] and self.gun and self.gun_cooldown <= 0:
                self.shoot()

    def update(self, dt, game_map=None):
        """Update player state"""
        # Update gun cooldown
        if self.gun_cooldown > 0:
            self.gun_cooldown -= dt
            
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(dt, game_map, self.current_enemies)
            if not projectile.alive:
                self.projectiles.remove(projectile)
                
        # Regenerate mana
        self.current_mana = min(self.max_mana, 
                              self.current_mana + self.MANA_REGEN_RATE * dt)
        
        # Update attack timers
        for attack_type in AttackType:
            if self.attack_timers[attack_type] > 0:
                self.attack_timers[attack_type] -= dt
                
        # Update current attack
        if self.current_attack:
            if self.current_attack == AttackType.DASH:
                if self.dash_timer > 0:
                    # Move in dash direction
                    new_x = self.x + self.dash_direction[0] * self.dash_speed * dt
                    new_y = self.y + self.dash_direction[1] * self.dash_speed * dt
                    
                    # Check if new position is walkable
                    if game_map and game_map.is_walkable(new_x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
                        self.x = new_x
                        self.y = new_y
                        self.rect.x = new_x
                        self.rect.y = new_y
                        
                        # Create dash effect
                        if self.particle_system:
                            self.particle_system.create_hit_effect(
                                self.rect.centerx, self.rect.centery,
                                color=(255, 200, 0)  # Golden color for dash
                            )
                        
                        # Check for enemy hits
                        for enemy in self.current_enemies:
                            if enemy.is_alive and self.rect.colliderect(enemy.rect):
                                enemy.take_damage(
                                    int(self.strength * 1.5),  # 50% more damage
                                    self.dash_direction,
                                    DamageType.SPECIAL.value,
                                    self
                                )
                    
                    self.dash_timer -= dt
                else:
                    self.current_attack = None
                    self.state = AnimationState.IDLE
                    self.is_attacking = False
            else:
                # Other attacks end after their animation
                if self.attack_timers[self.current_attack] <= self.attack_duration:
                    self.current_attack = None
                    self.state = AnimationState.IDLE
                    self.is_attacking = False
        
        # Update wave attacks
        self.update_wave_attacks(dt)
        
        # Update other timers and states
        if self.hit_timer > 0:
            self.hit_timer -= dt
            if self.hit_timer <= 0:
                self.is_hit = False
                
        # Handle knockback
        if self.knockback_distance > 0:
            move_distance = min(self.knockback_distance, 10 * dt)
            new_x = self.x + self.knockback_direction[0] * move_distance
            new_y = self.y + self.knockback_direction[1] * move_distance
            
            # Check if new position is walkable
            if game_map is None or game_map.is_walkable(new_x + PLAYER_SIZE/2, new_y + PLAYER_SIZE/2):
                self.x = new_x
                self.y = new_y
                self.rect.x = new_x
                self.rect.y = new_y
            else:
                # If we hit a wall, stop knockback
                self.knockback_distance = 0
            
            self.knockback_distance -= move_distance
        
        # Update damage numbers
        self.damage_numbers = [(dmg, x, y, timer - dt, color) 
                             for dmg, x, y, timer, color in self.damage_numbers 
                             if timer > 0]
        # Limit the number of damage numbers
        if len(self.damage_numbers) > self.MAX_DAMAGE_NUMBERS:
            self.damage_numbers = self.damage_numbers[-self.MAX_DAMAGE_NUMBERS:]
        
        # Update animation frame
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the player and any effects"""
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen, camera_x, camera_y)
            
        # Ensure sprites are loaded before drawing
        if not self.sprites_loaded:
            self._load_sprites()
        
        sprite_row = self.state.value if not self.is_moving else self.direction.value
        sprite = self.sprite_manager.get_animation_frame('player', 
            sprite_row * 4 + self.animation_frame)
        
        if sprite:
            # Draw player shadow
            shadow_height = 4
            shadow_surface = pygame.Surface((PLAYER_SIZE, shadow_height), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, 128), 
                              (0, 0, PLAYER_SIZE, shadow_height))
            screen.blit(shadow_surface, (
                self.rect.x - camera_x,
                self.rect.y + PLAYER_SIZE - shadow_height/2 - camera_y
            ))
            
            # Flash white when hit
            if self.is_hit:
                white_sprite = sprite.copy()
                white_sprite.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(white_sprite, (
                    self.rect.x - camera_x,
                    self.rect.y - camera_y
                ))
            else:
                screen.blit(sprite, (
                    self.rect.x - camera_x,
                    self.rect.y - camera_y
                ))
                
            # Draw damage numbers with colors and effects
            font = pygame.font.Font(None, 24)  # Slightly larger font
            for damage, x, y, timer, color in self.damage_numbers:
                # Float up and fade out with bounce effect
                progress = (self.damage_number_duration - timer) / self.damage_number_duration
                y_offset = -30 * progress  # Base upward movement
                
                # Add bounce effect
                bounce = math.sin(progress * math.pi * 2) * 5 * (1 - progress)
                y_offset += bounce
                
                # Scale based on damage (bigger numbers = bigger text)
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
                
            # Debug: draw attack hitbox when attacking
            if self.is_attacking and self.current_attack:
                hitbox = self._get_attack_hitbox()
                # Draw attack effect
                attack_surface = pygame.Surface((hitbox.width, hitbox.height), pygame.SRCALPHA)
                if self.current_attack == AttackType.SLASH:
                    pygame.draw.rect(attack_surface, (255, 255, 255, 50), 
                                   (0, 0, hitbox.width, hitbox.height))
                elif self.current_attack == AttackType.SPIN:
                    pygame.draw.circle(attack_surface, (255, 255, 0, 50),
                                    (hitbox.width/2, hitbox.height/2),
                                    max(hitbox.width, hitbox.height)/2)
                elif self.current_attack == AttackType.WAVE:
                    pygame.draw.rect(attack_surface, (0, 255, 255, 50),
                                   (0, 0, hitbox.width, hitbox.height))
                screen.blit(attack_surface, (hitbox.x - camera_x, hitbox.y - camera_y))
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
        
    def pickup_item(self, item):
        """Try to pick up an item"""
        return self.inventory.add_item(item)
        
    def use_item(self, item_index):
        """Use an item from inventory"""
        item = self.inventory.get_item(item_index)
        if not item:
            return False
            
        if item.item_type == ItemType.POTION:
            # Handle potion effects
            if 'heal' in item.stats:
                self.current_health = min(self.max_health, 
                                       self.current_health + item.stats['heal'])
                self.inventory.remove_item(item_index)
                return True
            elif 'mana' in item.stats:
                self.current_mana = min(self.max_mana, 
                                    self.current_mana + item.stats['mana'])
                self.inventory.remove_item(item_index)
                return True
        
        return False
        
    def equip_item(self, item_index):
        """Equip an item from inventory"""
        item = self.inventory.get_item(item_index)
        if not item:
            return False
            
        if item.item_type == ItemType.WEAPON:
            # Unequip current weapon if any
            if self.equipment['weapon']:
                self.inventory.add_item(self.equipment['weapon'])
            self.equipment['weapon'] = self.inventory.remove_item(item_index)
            # Update stats
            self.update_equipment_stats()
            return True
            
        elif item.item_type == ItemType.ARMOR:
            # Unequip current armor if any
            if self.equipment['armor']:
                self.inventory.add_item(self.equipment['armor'])
            self.equipment['armor'] = self.inventory.remove_item(item_index)
            # Update stats
            self.update_equipment_stats()
            return True
            
        elif item.item_type == ItemType.GUN:
            # Unequip current gun if any
            if self.gun:
                self.inventory.add_item(self.gun)
            # Remove and equip new gun
            self.gun = self.inventory.remove_item(item_index)
            return True
            
        return False
        
    def shoot(self):
        """Fire the equipped gun"""
        if not self.gun or self.gun_cooldown > 0:
            return
            
        # Get direction based on player facing
        if self.direction == Direction.LEFT:
            direction = (-1, 0)
        elif self.direction == Direction.RIGHT:
            direction = (1, 0)
        elif self.direction == Direction.UP:
            direction = (0, -1)
        else:  # Direction.DOWN
            direction = (0, 1)
            
        # Create new projectile
        from .projectile import Projectile
        projectile = Projectile(
            self.rect.centerx,
            self.rect.centery,
            direction,
            self.gun.stats['projectile_speed'],
            self.gun.stats['damage'],
            self.gun.stats['range']
        )
        
        self.projectiles.append(projectile)
        self.gun_cooldown = self.gun.stats['cooldown']
        
        # Create muzzle flash effect
        if self.particle_system:
            self.particle_system.create_hit_effect(
                self.rect.centerx + direction[0] * 20,
                self.rect.centery + direction[1] * 20,
                color=(255, 255, 0)
            )
        
    def gain_xp(self, amount):
        """Add XP and check for level up"""
        self.xp += amount
        
        # Check for level up
        while self.xp >= self.xp_to_next_level:
            self.level_up()
            
    def level_up(self):
        """Level up the character and increase stats"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        
        # Increase XP needed for next level (exponential growth)
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        
        # Increase base stats
        self.base_strength += 2
        self.base_defense += 1
        self.base_speed += 5
        
        # Increase max health and mana
        old_max_health = self.max_health
        old_max_mana = self.max_mana
        
        self.max_health = int(self.max_health * 1.2)  # 20% increase
        self.max_mana = int(self.max_mana * 1.15)    # 15% increase
        
        # Heal for the difference in max health/mana
        self.current_health += (self.max_health - old_max_health)
        self.current_mana += (self.max_mana - old_max_mana)
        
        # Update current stats
        self.update_stats()
        
        # Create level up effect
        if self.particle_system:
            self.particle_system.create_special_attack_effect(
                self.rect.centerx, self.rect.centery,
                color=(255, 215, 0)  # Gold color for level up
            )
            
    def update_stats(self):
        """Update current stats based on base stats and equipment"""
        self.strength = self.base_strength
        self.defense = self.base_defense
        self.speed = self.base_speed
        
        # Add equipment bonuses
        for item in self.equipment.values():
            if item:
                if 'damage' in item.stats:
                    self.strength += item.stats['damage']
                if 'defense' in item.stats:
                    self.defense += item.stats['defense']
                if 'speed' in item.stats:
                    self.speed += item.stats['speed']
                    
    def update_equipment_stats(self):
        """Update player stats based on equipped items"""
        # Reset to base stats
        self.update_stats()
                    
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
                             
    def slash_attack(self):
        """Basic melee attack"""
        self.current_attack = AttackType.SLASH
        self.attack_timers[AttackType.SLASH] = self.attack_cooldowns[AttackType.SLASH]
        self.state = AnimationState.ATTACK
        self.is_attacking = True
        
        # Get attack hitbox
        attack_rect = self._get_attack_hitbox()
        
        # Create slash effect
        if self.particle_system:
            center_x = attack_rect.centerx
            center_y = attack_rect.centery
            self.particle_system.create_slash_effect(
                center_x, center_y, self.direction.name)
        
        # Check for hits
        for enemy in self.current_enemies:
            if enemy.is_alive and attack_rect.colliderect(enemy.rect):
                # Calculate knockback direction
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                length = math.sqrt(dx**2 + dy**2)
                if length > 0:
                    knockback_direction = (dx/length, dy/length)
                else:
                    knockback_direction = (1, 0)
                    
                # Check for critical hit
                is_crit = random.random() < self.crit_chance
                damage = self.strength * self.crit_multiplier if is_crit else self.strength
                damage_type = DamageType.CRITICAL if is_crit else DamageType.NORMAL
                
                # Deal damage
                enemy.take_damage(int(damage), knockback_direction, damage_type.value, self)

    def spin_attack(self):
        """360-degree spinning attack"""
        # Consume mana
        self.current_mana -= self.mana_costs[AttackType.SPIN]
        
        self.current_attack = AttackType.SPIN
        self.attack_timers[AttackType.SPIN] = self.attack_cooldowns[AttackType.SPIN]
        self.state = AnimationState.ATTACK
        self.is_attacking = True
        
        # Create spin effect
        if self.particle_system:
            self.particle_system.create_special_attack_effect(
                self.rect.centerx, self.rect.centery)
        
        # Check for hits in all directions
        for enemy in self.current_enemies:
            if enemy.is_alive:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance <= self.attack_range * 1.5:  # Larger range for spin attack
                    # Calculate knockback direction
                    knockback_direction = (dx/distance, dy/distance) if distance > 0 else (1, 0)
                    
                    # Deal damage
                    enemy.take_damage(
                        int(self.strength * 1.2),  # 20% more damage
                        knockback_direction,
                        DamageType.SPECIAL.value,
                        self
                    )

    def dash_attack(self):
        """Quick dash that damages enemies in path"""
        # Consume mana
        self.current_mana -= self.mana_costs[AttackType.DASH]
        
        self.current_attack = AttackType.DASH
        self.attack_timers[AttackType.DASH] = self.attack_cooldowns[AttackType.DASH]
        self.state = AnimationState.DASH
        self.is_attacking = True
        
        # Set dash direction based on current facing
        if self.direction == Direction.LEFT:
            self.dash_direction = (-1, 0)
        elif self.direction == Direction.RIGHT:
            self.dash_direction = (1, 0)
        elif self.direction == Direction.UP:
            self.dash_direction = (0, -1)
        else:  # Direction.DOWN
            self.dash_direction = (0, 1)
            
        self.dash_timer = self.dash_duration

    def wave_attack(self):
        """Send out an energy wave"""
        # Consume mana
        self.current_mana -= self.mana_costs[AttackType.WAVE]
        
        self.current_attack = AttackType.WAVE
        self.attack_timers[AttackType.WAVE] = self.attack_cooldowns[AttackType.WAVE]
        self.state = AnimationState.CAST
        self.is_attacking = True
        
        # Create wave based on direction
        if self.direction == Direction.LEFT:
            direction = (-1, 0)
        elif self.direction == Direction.RIGHT:
            direction = (1, 0)
        elif self.direction == Direction.UP:
            direction = (0, -1)
        else:  # Direction.DOWN
            direction = (0, 1)
            
        # Add wave to active waves list
        self.waves.append({
            'x': self.rect.centerx,
            'y': self.rect.centery,
            'direction': direction,
            'lifetime': self.wave_lifetime,
            'hit_enemies': set()  # Track which enemies have been hit by this wave
        })
        
        # Create wave effect
        if self.particle_system:
            self.particle_system.create_special_attack_effect(
                self.rect.centerx, self.rect.centery,
                color=(0, 200, 255)  # Light blue for wave attack
            )

    def take_damage(self, damage, knockback_direction=None):
        """Take damage from an enemy and handle knockback"""
        if self.hit_timer > 0:  # Still in invulnerability period
            return
            
        # Apply defense reduction
        actual_damage = max(1, damage - self.defense)
        self.current_health -= actual_damage
        
        # Add damage number
        self.damage_numbers.append((
            actual_damage,
            self.x + random.randint(-10, 10),
            self.y - 20,
            self.damage_number_duration,
            DamageType.NORMAL.value
        ))
        
        # Apply knockback
        if knockback_direction:
            self.knockback_distance = 30
            self.knockback_direction = knockback_direction
        
        self.is_hit = True
        self.hit_timer = self.hit_cooldown
        
        # Check if dead (you might want to add game over logic here)
        if self.current_health <= 0:
            self.current_health = 0
            
    def update_wave_attacks(self, dt):
        """Update active wave attacks"""
        for wave in self.waves[:]:  # Copy list to safely remove while iterating
            # Move wave
            wave['x'] += wave['direction'][0] * self.wave_speed * dt
            wave['y'] += wave['direction'][1] * self.wave_speed * dt
            
            # Create particle trail
            if self.particle_system:
                self.particle_system.create_hit_effect(
                    wave['x'], wave['y'],
                    color=(0, 200, 255)
                )
            
            # Check for enemy hits
            wave_rect = pygame.Rect(
                wave['x'] - 20, wave['y'] - 20,
                40, 40
            )
            
            for enemy in self.current_enemies:
                if (enemy.is_alive and 
                    enemy not in wave['hit_enemies'] and
                    wave_rect.colliderect(enemy.rect)):
                    # Calculate knockback direction
                    knockback_direction = wave['direction']
                    
                    # Deal damage
                    enemy.take_damage(
                        int(self.strength * 0.8),  # 80% normal damage
                        knockback_direction,
                        DamageType.SPECIAL.value,
                        self
                    )
                    
                    # Mark enemy as hit by this wave
                    wave['hit_enemies'].add(enemy)
            
            # Update lifetime
            wave['lifetime'] -= dt
            if wave['lifetime'] <= 0:
                self.waves.remove(wave)