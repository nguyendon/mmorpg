import pygame
import sys
from .player import Player
from .map import GameMap
from .ui import UI
from .enemy import Enemy
from .particle_system import ParticleSystem
from .enemy_spawner import EnemySpawner
from .npc_spawner import NPCSpawner
from ..common.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SIZE

class GameClient:
    def __init__(self):
        # Initialize pygame first
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MMORPG Client")
        self.clock = pygame.time.Clock()
        self.running = True
        self._initialized = True

        # Create game map (30x30 tiles)
        self.game_map = GameMap(30, 30)
        
        # Create player at center of screen
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player = Player(player_x, player_y)

        # Initialize UI
        self.ui = UI()

        # Initialize particle system
        self.particle_system = ParticleSystem()
        self.player.particle_system = self.particle_system

        # Initialize enemy spawner and enemies list
        self.enemy_spawner = EnemySpawner(self.game_map)
        self.enemies = []
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
            "E - Interact with NPCs",
            "H - Toggle Help Menu",
            "R - Emergency Respawn",
            "ESC - Quit Game",
            "",
            "Combat:",
            "Basic Attack (J): Quick slash",
            "Spin Attack (K): Hit all nearby enemies",
            "Dash Attack (L): Quick dash with damage",
            "Wave Attack (U): Ranged energy wave",
            "",
            "Tips:",
            "Stay out of water!",
            "Different attacks have different cooldowns",
            "Mana regenerates over time",
            "Talk to NPCs for information",
            "Critical hits show yellow numbers",
            "Special attacks show cyan numbers"
        ]
        
        # Dialog system
        self.show_dialog = False
        self.current_dialog = ""
        self.dialog_font = pygame.font.Font(None, 36)
        
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
                    # Create spawn effect
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

    def update(self):
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.game_map.update(dt)
        
        # Update player's enemy reference
        self.player.current_enemies = self.enemies
        
        # Handle player input and movement
        self.player.handle_input(self.game_map)
        self.player.update(dt, self.game_map)
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player, self.game_map)
        
        # Update NPCs
        self.npc_spawner.update(self.player.x, self.player.y)
        
        # Remove dead enemies and create death effects
        for enemy in self.enemies[:]:  # Copy list to safely remove while iterating
            if not enemy.is_alive:
                if self.particle_system:
                    self.particle_system.create_death_effect(
                        enemy.x + PLAYER_SIZE/2,
                        enemy.y + PLAYER_SIZE/2
                    )
                self.enemies.remove(enemy)
        
        # Try to spawn new enemy
        if new_enemy := self.enemy_spawner.update(dt, self.player, self.enemies):
            self.enemies.append(new_enemy)
            # Create spawn effect
            if self.particle_system:
                self.particle_system.create_spawn_effect(
                    new_enemy.x + PLAYER_SIZE/2,
                    new_enemy.y + PLAYER_SIZE/2
                )
        
        # Update particle system
        self.particle_system.update(dt)
        
        # Check if player is in unwalkable tile and force respawn if stuck
        player_tile_x = int(self.player.x // self.game_map.tile_size)
        player_tile_y = int(self.player.y // self.game_map.tile_size)
        if not self.game_map.is_walkable(self.player.x + PLAYER_SIZE/2, self.player.y + PLAYER_SIZE/2):
            # Try to find nearest walkable tile
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    test_x = (player_tile_x + dx) * self.game_map.tile_size + self.game_map.tile_size/2
                    test_y = (player_tile_y + dy) * self.game_map.tile_size + self.game_map.tile_size/2
                    if self.game_map.is_walkable(test_x, test_y):
                        self.player.x = test_x - PLAYER_SIZE/2
                        self.player.y = test_y - PLAYER_SIZE/2
                        self.player.rect.x = self.player.x
                        self.player.rect.y = self.player.y
                        # Reset any movement-blocking states
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
                # Reset all movement-blocking states
                self.player.knockback_distance = 0
                self.player.current_attack = None
                self.player.is_attacking = False
        
        # Update camera to follow player
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        
        # Calculate maximum camera bounds
        max_x = max(0, self.game_map.width * self.game_map.tile_size - SCREEN_WIDTH)
        max_y = max(0, self.game_map.height * self.game_map.tile_size - SCREEN_HEIGHT)
        
        # Keep camera within bounds
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

    def render(self):
        # Fill background
        self.screen.fill((0, 0, 0))
        
        # Draw game map
        self.game_map.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw NPCs
        self.npc_spawner.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw player
        self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw particle effects
        self.particle_system.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw UI
        self.ui.draw(self.screen, self.player, self.game_map)
        
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