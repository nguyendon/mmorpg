import pygame
import sys
import random
from .player import Player
from .map import GameMap
from .map_manager import MapManager
from .ui import UI
from .enemy import Enemy
from .item import Item, ItemType, ItemDrop
from .particle_system import ParticleSystem
from .enemy_spawner import EnemySpawner
from .npc_spawner import NPCSpawner
from ..common.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SIZE
from ..common.tiles import TileType

class GameClient:
    def __init__(self):
        # Initialize pygame first
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MMORPG Client")
        self.clock = pygame.time.Clock()
        self.running = True
        self._initialized = True

        # Create map manager and multiple maps
        self.map_manager = MapManager()
        
        # Create main town map (30x30 tiles)
        town_map = GameMap(30, 30)
        self.map_manager.add_map("town", town_map)
        
        # Create forest map (40x40 tiles)
        forest_map = GameMap(40, 40)
        self._customize_forest_map(forest_map)
        self.map_manager.add_map("forest", forest_map)
        
        # Create dungeon map (25x25 tiles)
        dungeon_map = GameMap(25, 25)
        self._customize_dungeon_map(dungeon_map)
        self.map_manager.add_map("dungeon", dungeon_map)
        
        # Add portals between maps
        # Town -> Forest portal
        self.map_manager.add_portal(
            "town", 28 * 32, 15 * 32,  # Position in town map
            "forest", 2 * 32, 15 * 32   # Target position in forest map
        )
        
        # Forest -> Town portal
        self.map_manager.add_portal(
            "forest", 1 * 32, 15 * 32,  # Position in forest map
            "town", 27 * 32, 15 * 32    # Target position in town map
        )
        
        # Forest -> Dungeon portal
        self.map_manager.add_portal(
            "forest", 38 * 32, 20 * 32,  # Position in forest map
            "dungeon", 2 * 32, 12 * 32   # Target position in dungeon map
        )
        
        # Dungeon -> Forest portal
        self.map_manager.add_portal(
            "dungeon", 1 * 32, 12 * 32,  # Position in dungeon map
            "forest", 37 * 32, 20 * 32   # Target position in forest map
        )
        
        # Create player at center of town
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player = Player(player_x, player_y)

        # Give player a starting gun
        starting_gun = Item("Starting Pistol", ItemType.GUN, "A reliable starter weapon", "pistol.png", {
            "damage": 10,
            "range": 300,
            "cooldown": 0.5,
            "projectile_speed": 500
        })
        self.player.pickup_item(starting_gun)
        self.player.equip_item(0)  # Equip the gun in the first slot

        # Initialize UI
        self.ui = UI()
        self.equipment_visible = True  # Track equipment menu visibility

        # Initialize particle system
        self.particle_system = ParticleSystem()
        self.player.particle_system = self.particle_system

        # Initialize enemy spawner and enemies list
        self.enemy_spawner = EnemySpawner(self.map_manager.get_current_map())
        self.enemies = []
        self.items = []  # List to store active items
        self._spawn_test_enemies()
        
        # Initialize NPC spawner and spawn some NPCs
        self.npc_spawner = NPCSpawner()
        self._spawn_npcs()

        # Camera position
        self.camera_x = 0
        self.camera_y = 0

        # Animation timer
        self.animation_timer = 0
        self.animation_interval = 0.25  # Update animations every 250ms

        # Help menu
        self.show_help = False
        self.help_font = pygame.font.Font(None, 32)
        self.help_text = [
            "Controls:",
            "WASD / Arrow Keys - Move",
            "J - Basic Attack (Free)",
            "K - Spin Attack (30 Mana)",
            "L - Dash Attack (20 Mana)",
            "U - Wave Attack (40 Mana)",
            "SPACE - Fire Gun (if equipped)",
            "I - Toggle Inventory",
            "Q - Toggle Equipment Menu",
            "E - Interact with NPCs/Portals",
            "H - Toggle Help Menu",
            "R - Emergency Respawn",
            "ESC - Quit Game",
            "",
            "Combat:",
            "Basic Attack (J): Quick slash",
            "Spin Attack (K): Hit all nearby enemies",
            "Dash Attack (L): Quick dash with damage",
            "Wave Attack (U): Ranged energy wave",
            "Gun (SPACE): Ranged weapon attack",
            "",
            "Items:",
            "Pick up items by walking over them",
            "Open inventory with I key",
            "Click items to equip/use them",
            "Potions heal automatically",
            "Guns must be equipped to use",
            "",
            "Tips:",
            "Stay out of water!",
            "Different attacks have different cooldowns",
            "Mana regenerates over time",
            "Talk to NPCs for information",
            "Critical hits show yellow numbers",
            "Special attacks show cyan numbers",
            "Purple portals teleport you to new areas"
        ]
        
        # Dialog system
        self.show_dialog = False
        self.current_dialog = ""
        self.dialog_font = pygame.font.Font(None, 36)

    def _customize_forest_map(self, forest_map):
        """Create a forest-themed map with more trees and water"""
        # Add more water features
        for x in range(10, 15):
            for y in range(8, 35):
                forest_map.tiles[y][x].tile_type = TileType.WATER
                
        # Add stone formations
        for x in range(25, 30):
            for y in range(15, 20):
                forest_map.tiles[y][x].tile_type = TileType.STONE
                
        forest_map._calculate_transitions()

    def _customize_dungeon_map(self, dungeon_map):
        """Create a dungeon-themed map with more walls and stone"""
        # Create outer walls
        for x in range(dungeon_map.width):
            dungeon_map.tiles[0][x].tile_type = TileType.WALL
            dungeon_map.tiles[dungeon_map.height-1][x].tile_type = TileType.WALL
            
        for y in range(dungeon_map.height):
            dungeon_map.tiles[y][0].tile_type = TileType.WALL
            dungeon_map.tiles[y][dungeon_map.width-1].tile_type = TileType.WALL
            
        # Add stone floor
        for y in range(1, dungeon_map.height-1):
            for x in range(1, dungeon_map.width-1):
                dungeon_map.tiles[y][x].tile_type = TileType.STONE
                
        # Add some internal walls to create rooms
        for x in range(8, 12):
            for y in range(5, 20):
                if y != 12:  # Leave a gap for passage
                    dungeon_map.tiles[y][x].tile_type = TileType.WALL
                    
        dungeon_map._calculate_transitions()
            
    def __del__(self):
        if self._initialized:
            pygame.quit()
            self._initialized = False
            
    def _spawn_npcs(self):
        """Spawn initial set of NPCs in safe locations"""
        # Spawn a villager
        self.npc_spawner.spawn_npc(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 - 100,
            "villager"
        )
        
        # Spawn a merchant
        self.npc_spawner.spawn_npc(
            SCREEN_WIDTH // 2 + 100,
            SCREEN_HEIGHT // 2 - 100,
            "merchant"
        )
        
        # Spawn a guard
        self.npc_spawner.spawn_npc(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 150,
            "guard"
        )
        
    def _spawn_test_enemies(self):
        """Spawn initial set of enemies"""
        for _ in range(5):
            if spawn_point := self.enemy_spawner._find_spawn_point(self.player):
                enemy = self.enemy_spawner._create_enemy(*spawn_point)
                if enemy:
                    self.enemies.append(enemy)
                    if self.particle_system:
                        self.particle_system.create_spawn_effect(
                            enemy.x + PLAYER_SIZE/2,
                            enemy.y + PLAYER_SIZE/2
                        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_i:
                    # Toggle inventory
                    self.player.inventory.visible = not self.player.inventory.visible
                elif event.key == pygame.K_q:
                    # Toggle equipment menu
                    self.equipment_visible = not self.equipment_visible
                elif event.key == pygame.K_e:
                    # Check for NPC interaction
                    for npc in self.npc_spawner.npcs:
                        if npc.can_interact(self.player.x, self.player.y):
                            self.show_dialog = True
                            self.current_dialog = npc.get_next_dialogue()
                            break
                elif event.key == pygame.K_r:  # Emergency respawn
                    self.player.x = SCREEN_WIDTH // 2
                    self.player.y = SCREEN_HEIGHT // 2
                    self.player.rect.x = self.player.x
                    self.player.rect.y = self.player.y
                    # Reset any movement-blocking states
                    self.player.knockback_distance = 0
                    self.player.current_attack = None
                    self.player.is_attacking = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    self.show_dialog = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Handle inventory clicks if inventory is visible
                    if self.player.inventory.visible:
                        mouse_pos = pygame.mouse.get_pos()
                        clicked_item = self.player.inventory.handle_click(
                            mouse_pos[0], mouse_pos[1],
                            self.screen.get_width(), self.screen.get_height()
                        )
                        if clicked_item:
                            self.player.equip_item(self.player.inventory.selected_slot)

    def update(self):
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.map_manager.update(dt)
        
        # Update player's enemy reference
        self.player.current_enemies = self.enemies
        
        # Handle player input and movement
        current_map = self.map_manager.get_current_map()
        self.player.handle_input(current_map)
        self.player.update(dt, current_map)
        
        # Check for portal transitions
        if not self.map_manager.is_transitioning:
            portal = self.map_manager.check_portal(
                self.player.x + PLAYER_SIZE/2, 
                self.player.y + PLAYER_SIZE/2,
                PLAYER_SIZE
            )
            if portal:
                # Check for E key press
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e]:
                    self.map_manager.start_transition(portal)
        
        # Handle ongoing transition
        if self.map_manager.is_transitioning:
            target_pos = self.map_manager.update(dt)  # Returns (x, y) when transition completes
            if target_pos:
                target_x, target_y = target_pos
                
                # Update player position to target coordinates
                # Ensure exact pixel alignment by rounding to integers
                self.player.x = round(target_x - PLAYER_SIZE/2)
                self.player.y = round(target_y - PLAYER_SIZE/2)
                self.player.rect.x = self.player.x
                self.player.rect.y = self.player.y
                
                # Reset player state to prevent any movement carrying over
                self.player.knockback_distance = 0
                self.player.current_attack = None
                self.player.is_attacking = False
                self.player.velocity_x = 0
                self.player.velocity_y = 0
                
                # Clear enemies when changing maps
                self.enemies.clear()
                # Update enemy spawner to use new map
                self.enemy_spawner = EnemySpawner(self.map_manager.get_current_map())
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player, current_map)
        
        # Update NPCs
        self.npc_spawner.update(self.player.x, self.player.y)
        
        # Remove dead enemies and create death effects
        for enemy in self.enemies[:]:
            if not enemy.is_alive:
                if self.particle_system:
                    self.particle_system.create_death_effect(
                        enemy.x + PLAYER_SIZE/2,
                        enemy.y + PLAYER_SIZE/2
                    )
                if random.random() < 0.3:  # 30% chance for item drop
                    # 20% chance for gun, 80% chance for potion
                    if random.random() < 0.2:
                        item = Item("Pistol", ItemType.GUN, "A basic ranged weapon", "pistol.png", {
                            "damage": 15,
                            "range": 300,
                            "cooldown": 0.5,
                            "projectile_speed": 500
                        })
                    else:
                        potion_type = "greater_health_potion" if random.random() < 0.3 else "health_potion"
                        item = Item("Health Potion", ItemType.POTION, "Restores HP", "potion.png", {
                            "heal": 60 if potion_type == "greater_health_potion" else 30
                        })
                    item_drop = ItemDrop(item, enemy.x, enemy.y)
                    self.items.append(item_drop)
                self.enemies.remove(enemy)
                
        # Update items and check for pickups
        for item in self.items[:]:
            item.update(dt)
            dx = self.player.x - item.x
            dy = self.player.y - item.y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= item.pickup_range:
                if item.item.item_type == ItemType.POTION:
                    self.player.current_health = min(
                        self.player.max_health,
                        self.player.current_health + item.item.stats['heal']
                    )
                    if self.particle_system:
                        self.particle_system.create_hit_effect(
                            self.player.rect.centerx,
                            self.player.rect.centery,
                            color=(0, 255, 0)
                        )
                    self.items.remove(item)
                else:
                    # Add non-potion items to inventory
                    if self.player.pickup_item(item.item):
                        if self.particle_system:
                            self.particle_system.create_hit_effect(
                                self.player.rect.centerx,
                                self.player.rect.centery,
                                color=(255, 255, 0)  # Gold color for items
                            )
                        self.items.remove(item)
        
        # Try to spawn new enemy
        if new_enemy := self.enemy_spawner.update(dt, self.player, self.enemies):
            self.enemies.append(new_enemy)
            if self.particle_system:
                self.particle_system.create_spawn_effect(
                    new_enemy.x + PLAYER_SIZE/2,
                    new_enemy.y + PLAYER_SIZE/2
                )
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Check if player is in unwalkable tile and force respawn if stuck
        player_tile_x = int(self.player.x // current_map.tile_size)
        player_tile_y = int(self.player.y // current_map.tile_size)
        if not current_map.is_walkable(self.player.x + PLAYER_SIZE/2, self.player.y + PLAYER_SIZE/2):
            # Try to find nearest walkable tile
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    test_x = (player_tile_x + dx) * current_map.tile_size + current_map.tile_size/2
                    test_y = (player_tile_y + dy) * current_map.tile_size + current_map.tile_size/2
                    if current_map.is_walkable(test_x, test_y):
                        self.player.x = test_x - PLAYER_SIZE/2
                        self.player.y = test_y - PLAYER_SIZE/2
                        self.player.rect.x = self.player.x
                        self.player.rect.y = self.player.y
                        self.player.knockback_distance = 0
                        self.player.current_attack = None
                        self.player.is_attacking = False
                        break
                else:
                    continue
                break
            else:
                # If no nearby walkable tiles found, respawn at center
                self.player.x = SCREEN_WIDTH // 2
                self.player.y = SCREEN_HEIGHT // 2
                self.player.rect.x = self.player.x
                self.player.rect.y = self.player.y
                self.player.knockback_distance = 0
                self.player.current_attack = None
                self.player.is_attacking = False
        
        # Update camera to follow player
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        
        # Calculate maximum camera bounds
        max_x = max(0, current_map.width * current_map.tile_size - SCREEN_WIDTH)
        max_y = max(0, current_map.height * current_map.tile_size - SCREEN_HEIGHT)
        
        # Keep camera within bounds
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

    def draw_status_bar(self, screen):
        """Draw the player's status bar at the top of the screen"""
        # Status bar background
        bar_height = 80  # Increased height to accommodate all bars
        padding = 10
        pygame.draw.rect(screen, (40, 40, 40), 
                        (0, 0, SCREEN_WIDTH, bar_height))
        pygame.draw.line(screen, (60, 60, 60),
                        (0, bar_height), (SCREEN_WIDTH, bar_height), 2)

        # Level display
        font = pygame.font.Font(None, 32)
        level_text = f"Level {self.player.level}"
        level_surface = font.render(level_text, True, (255, 255, 255))
        screen.blit(level_surface, (padding, padding))

        # Bar dimensions
        bar_width = 200
        bar_height = 15
        bar_x = level_surface.get_width() + padding * 2
        
        # Health bar
        health_bar_y = padding
        health_pct = self.player.current_health / self.player.max_health
        
        # Health bar background
        pygame.draw.rect(screen, (60, 60, 60),
                        (bar_x, health_bar_y, bar_width, bar_height))
        
        # Health bar fill
        if health_pct > 0:
            green = int(255 * health_pct)
            red = int(255 * (1 - health_pct))
            health_color = (red, green, 0)
            pygame.draw.rect(screen, health_color,
                           (bar_x, health_bar_y, bar_width * health_pct, bar_height))
            # Add highlight
            highlight_height = max(1, int(bar_height * 0.3))
            pygame.draw.rect(screen, (min(red + 50, 255), min(green + 50, 255), 50),
                           (bar_x, health_bar_y, bar_width * health_pct, highlight_height))
        
        # Health text
        health_text = f"HP: {int(self.player.current_health)}/{self.player.max_health}"
        health_text_surface = font.render(health_text, True, (255, 255, 255))
        screen.blit(health_text_surface, 
                   (bar_x + bar_width + padding,
                    health_bar_y))

        # Mana bar
        mana_bar_y = health_bar_y + bar_height + 5
        mana_pct = self.player.current_mana / self.player.max_mana
        
        # Mana bar background
        pygame.draw.rect(screen, (60, 60, 60),
                        (bar_x, mana_bar_y, bar_width, bar_height))
        
        # Mana bar fill
        if mana_pct > 0:
            mana_color = (50, 50, 255)
            pygame.draw.rect(screen, mana_color,
                           (bar_x, mana_bar_y, bar_width * mana_pct, bar_height))
            # Add highlight
            highlight_height = max(1, int(bar_height * 0.3))
            pygame.draw.rect(screen, (100, 100, 255),
                           (bar_x, mana_bar_y, bar_width * mana_pct, highlight_height))
        
        # Mana text
        mana_text = f"MP: {int(self.player.current_mana)}/{self.player.max_mana}"
        mana_text_surface = font.render(mana_text, True, (255, 255, 255))
        screen.blit(mana_text_surface, 
                   (bar_x + bar_width + padding,
                    mana_bar_y))

        # XP bar
        xp_bar_y = mana_bar_y + bar_height + 5
        xp_pct = self.player.xp / self.player.xp_to_next_level
        
        # XP bar background
        pygame.draw.rect(screen, (60, 60, 60),
                        (bar_x, xp_bar_y, bar_width, bar_height))
        
        # XP bar fill
        if xp_pct > 0:
            xp_color = (255, 215, 0)  # Gold color
            pygame.draw.rect(screen, xp_color,
                           (bar_x, xp_bar_y, bar_width * xp_pct, bar_height))
            # Add highlight
            highlight_height = max(1, int(bar_height * 0.3))
            pygame.draw.rect(screen, (255, 235, 100),
                           (bar_x, xp_bar_y, bar_width * xp_pct, highlight_height))
        
        # XP text
        xp_text = f"XP: {self.player.xp}/{self.player.xp_to_next_level}"
        xp_text_surface = font.render(xp_text, True, (255, 255, 255))
        screen.blit(xp_text_surface, 
                   (bar_x + bar_width + padding,
                    xp_bar_y))

        # Stats
        stats_x = bar_x + bar_width + max(health_text_surface.get_width(), 
                                        max(mana_text_surface.get_width(),
                                            xp_text_surface.get_width())) + padding * 2
        small_font = pygame.font.Font(None, 24)
        stats_text = f"STR: {self.player.strength}  DEF: {self.player.defense}  SPD: {int(self.player.speed)}"
        stats_surface = small_font.render(stats_text, True, (200, 200, 200))
        screen.blit(stats_surface,
                   (stats_x, padding))

    def render(self):
        # Fill background
        self.screen.fill((0, 0, 0))
        
        # Draw current map
        self.map_manager.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw NPCs
        self.npc_spawner.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw items
        for item in self.items:
            item.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw player
        self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw particle effects
        self.particle_system.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw UI
        if self.equipment_visible:
            self.ui.draw(self.screen, self.player, self.map_manager.get_current_map())
        else:
            # Draw only status bar and other essential UI elements
            self.draw_status_bar(self.screen)
        
        # Draw status bar
        self.draw_status_bar(self.screen)
        
        # Draw portal prompt if near a portal
        if not self.map_manager.is_transitioning:
            portal = self.map_manager.check_portal(
                self.player.x + PLAYER_SIZE/2, 
                self.player.y + PLAYER_SIZE/2,
                PLAYER_SIZE
            )
            if portal:
                font = pygame.font.Font(None, 36)
                prompt = font.render("Press E to enter portal", True, (255, 255, 255))
                prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 100))
                self.screen.blit(prompt, prompt_rect)
        
        # Draw dialog box if active
        if self.show_dialog:
            # Semi-transparent background for dialog box
            dialog_surface = pygame.Surface((SCREEN_WIDTH * 0.8, 100))
            dialog_surface.fill((0, 0, 0))
            dialog_surface.set_alpha(200)
            
            # Position dialog box at bottom of screen
            dialog_rect = dialog_surface.get_rect()
            dialog_rect.centerx = SCREEN_WIDTH // 2
            dialog_rect.bottom = SCREEN_HEIGHT - 20
            
            # Draw dialog box
            self.screen.blit(dialog_surface, dialog_rect)
            
            # Draw dialog text
            text_surface = self.dialog_font.render(self.current_dialog, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=dialog_rect.center)
            self.screen.blit(text_surface, text_rect)
            
            # Draw "Press E" prompt
            prompt_surface = self.dialog_font.render("Press E to continue", True, (200, 200, 200))
            prompt_rect = prompt_surface.get_rect(bottom=dialog_rect.bottom - 10, 
                                                right=dialog_rect.right - 10)
            self.screen.blit(prompt_surface, prompt_rect)
        
        # Draw help menu
        if self.show_help:
            # Semi-transparent background
            help_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            help_surface.fill((0, 0, 0))
            help_surface.set_alpha(128)
            self.screen.blit(help_surface, (0, 0))
            
            # Draw help text
            y = 50
            for line in self.help_text:
                if line:  # Skip empty lines
                    text_surface = self.help_font.render(line, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(centerx=SCREEN_WIDTH/2, y=y)
                    self.screen.blit(text_surface, text_rect)
                y += 40
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

if __name__ == "__main__":
    client = GameClient()
    client.run()
    pygame.quit()
    sys.exit()