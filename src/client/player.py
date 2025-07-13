import pygame
import sys
from ..common.constants import PLAYER_SPEED, PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        # Create a simple rectangle for now - we'll replace with sprites later
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = (255, 0, 0)  # Red color for visibility

    def move(self, dx, dy):
        """Move the player by the given delta x and y."""
        new_x = self.x + (dx * self.speed)
        new_y = self.y + (dy * self.speed)
        
        # Basic boundary checking
        if 0 <= new_x <= SCREEN_WIDTH - PLAYER_SIZE:
            self.x = new_x
            self.rect.x = new_x
        
        if 0 <= new_y <= SCREEN_HEIGHT - PLAYER_SIZE:
            self.y = new_y
            self.rect.y = new_y

    def handle_input(self):
        """Handle keyboard input for player movement."""
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/√2
            dy *= 0.707

        self.move(dx, dy)

    def draw(self, screen):
        """Draw the player on the screen."""
        pygame.draw.rect(screen, self.color, self.rect)

    def get_position(self):
        """Return the current position as a tuple."""
        return (self.x, self.y)