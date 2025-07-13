import pygame
from ..common.constants import PLAYER_SIZE

class Item:
    # Item type configurations
    ITEM_TYPES = {
        "health_potion": {
            "name": "Health Potion",
            "description": "Restores 30 HP",
            "color": (255, 0, 0),  # Red
            "heal_amount": 30,
            "pickup_range": 30
        },
        "greater_health_potion": {
            "name": "Greater Health Potion",
            "description": "Restores 75 HP",
            "color": (200, 0, 100),  # Dark pink
            "heal_amount": 75,
            "pickup_range": 30
        }
    }

    def __init__(self, x, y, item_type="health_potion"):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.rect = pygame.Rect(x, y, PLAYER_SIZE//2, PLAYER_SIZE//2)  # Items are smaller than players
        
        # Get item configuration
        config = self.ITEM_TYPES.get(item_type, self.ITEM_TYPES["health_potion"])
        
        self.name = config["name"]
        self.description = config["description"]
        self.color = config["color"]
        self.heal_amount = config["heal_amount"]
        self.pickup_range = config["pickup_range"]
        
        # Create sprite
        self.sprite = pygame.Surface((PLAYER_SIZE//2, PLAYER_SIZE//2), pygame.SRCALPHA)
        self._create_item_sprite()
        
        # Floating animation
        self.float_offset = 0
        self.float_speed = 2
        self.float_direction = 1
        
    def _create_item_sprite(self):
        """Create the item sprite"""
        size = PLAYER_SIZE//2
        
        # Draw potion bottle
        bottle_color = self.color
        pygame.draw.rect(self.sprite, bottle_color, 
                        (size//4, size//3, size//2, size//2))
        
        # Draw bottle neck
        neck_color = tuple(max(c - 30, 0) for c in bottle_color)
        pygame.draw.rect(self.sprite, neck_color,
                        (size//3, size//4, size//3, size//3))
        
        # Draw highlight
        highlight_color = (255, 255, 255, 100)
        pygame.draw.line(self.sprite, highlight_color,
                        (size//4 + 2, size//3 + 2),
                        (size//4 + 4, size//3 + 8), 2)
        
    def update(self, dt):
        """Update item animation"""
        self.float_offset += self.float_speed * self.float_direction * dt
        
        if abs(self.float_offset) >= 5:  # Max float distance
            self.float_direction *= -1  # Reverse direction
            
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the item with floating animation"""
        # Draw shadow
        shadow_height = 4
        shadow_surface = pygame.Surface((PLAYER_SIZE//2, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 128),
                          (0, 0, PLAYER_SIZE//2, shadow_height))
        
        screen.blit(shadow_surface, (
            self.rect.x - camera_x,
            self.rect.y + PLAYER_SIZE//2 - shadow_height/2 - camera_y
        ))
        
        # Draw item with float offset
        screen.blit(self.sprite, (
            self.rect.x - camera_x,
            self.rect.y - camera_y + self.float_offset
        ))