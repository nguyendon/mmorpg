import pygame

# Create a 32x32 pistol icon
icon = pygame.Surface((32, 32), pygame.SRCALPHA)

# Draw gun body (gray)
pygame.draw.rect(icon, (100, 100, 100), (8, 12, 16, 8))  # Main body
pygame.draw.rect(icon, (100, 100, 100), (20, 10, 8, 12))  # Barrel

# Draw handle (brown)
pygame.draw.rect(icon, (139, 69, 19), (10, 20, 6, 8))

# Add highlights (lighter gray)
pygame.draw.line(icon, (150, 150, 150), (8, 12), (24, 12))  # Top highlight
pygame.draw.line(icon, (150, 150, 150), (20, 10), (28, 10))  # Barrel highlight

# Save the icon
pygame.image.save(icon, "src/assets/images/items/pistol.png")