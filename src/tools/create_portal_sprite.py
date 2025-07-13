import pygame
import os

def create_portal_sprite():
    # Create a 32x32 surface with alpha
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    # Draw a purple circle with fade effect
    for radius in range(16, 0, -1):
        alpha = int((radius / 16.0) * 255)
        color = (128, 0, 255, alpha)
        pygame.draw.circle(surface, color, (16, 16), radius)
    
    # Save the image
    pygame.image.save(surface, "src/assets/images/tiles/portal.png")

if __name__ == "__main__":
    pygame.init()
    create_portal_sprite()
    pygame.quit()