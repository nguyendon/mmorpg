import pygame
import sys
from .player import Player
from ..common.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class GameClient:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MMORPG Client")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create player at center of screen
        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player = Player(player_x, player_y)

        # Set up basic colors
        self.colors = {
            'BLACK': (0, 0, 0),
            'WHITE': (255, 255, 255),
            'GRAY': (128, 128, 128)
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        # Handle player input and movement
        self.player.handle_input()

    def render(self):
        # Fill background
        self.screen.fill(self.colors['GRAY'])
        
        # Draw game world elements here
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI elements here
        
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