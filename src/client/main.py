import pygame
import sys
from .player import Player
from .map import GameMap
from .ui import UI
from ..common.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

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

        # Camera position
        self.camera_x = 0
        self.camera_y = 0

        # Animation timer
        self.animation_timer = 0
        self.animation_interval = 0.25  # Update animations every 250ms

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.game_map.update(dt)
        
        # Handle player input and movement
        self.player.handle_input(self.game_map)
        self.player.update(dt)
        
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
        
        # Draw player
        self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw UI
        self.ui.draw(self.screen, self.player, self.game_map)
        
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