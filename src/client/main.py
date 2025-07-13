import pygame
import sys
from .player import Player
from .map import GameMap
from .ui import UI
from .enemy import Enemy
from ..common.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SIZE

class GameClient:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MMORPG Client")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create game map (30x30 tiles)
        self.game_map = GameMap(30, 30)
        
        # Create player at center of screen
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player = Player(player_x, player_y)

        # Initialize UI
        self.ui = UI()

        # Initialize enemies list and spawn some test enemies
        self.enemies = []
        self._spawn_test_enemies()

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
            "J - Basic Attack",
            "K - Special Attack (AoE)",
            "H - Toggle Help Menu",
            "R - Emergency Respawn",
            "ESC - Quit Game",
            "",
            "Combat:",
            "Basic Attack: Press J to attack in facing direction",
            "Special Attack: Press K for spinning attack",
            "Red enemies will chase and attack you",
            "Green bar is your health",
            "Red bar is enemy health",
            "",
            "Tips:",
            "Stay out of water!",
            "Special attack has longer cooldown",
            "Face enemies to attack them",
            "Use knockback to your advantage"
        ]
        
    def _spawn_test_enemies(self):
        """Spawn some test enemies around the map"""
        # Spawn 5 goblins in different locations
        enemy_positions = [
            (300, 300),
            (500, 200),
            (200, 500),
            (600, 600),
            (400, 400)
        ]
        
        for pos in enemy_positions:
            self.enemies.append(Enemy(*pos, "goblin"))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.show_help = not self.show_help
                elif event.key == pygame.K_r:  # Add emergency respawn
                    self.player.x = SCREEN_WIDTH // 2
                    self.player.y = SCREEN_HEIGHT // 2
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.player.attack(self.enemies)

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
        
        # Remove dead enemies
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive]
        
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
        
        # Update camera to follow player
        self.camera_x = self.player.x - SCREEN_WIDTH // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2
        
        # Keep camera within map bounds
        self.camera_x = max(0, min(self.camera_x, 
                                 self.game_map.width * self.game_map.tile_size - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, 
                                 self.game_map.height * self.game_map.tile_size - SCREEN_HEIGHT))

    def render(self):
        # Fill background
        self.screen.fill((0, 0, 0))
        
        # Draw game map
        self.game_map.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw player
        self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw UI
        self.ui.draw(self.screen, self.player, self.game_map)
        
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