import pygame

# Create a 32x32 potion icon
icon = pygame.Surface((32, 32), pygame.SRCALPHA)

# Draw potion bottle
pygame.draw.rect(icon, (255, 0, 0), (12, 14, 8, 12))  # Main body (red)
pygame.draw.rect(icon, (200, 0, 0), (13, 12, 6, 2))   # Neck
pygame.draw.rect(icon, (150, 0, 0), (14, 10, 4, 2))   # Top

# Add highlights
pygame.draw.line(icon, (255, 150, 150), (14, 16), (16, 18), 2)  # Shine

# Save the icon
pygame.image.save(icon, "src/assets/images/items/potion.png")