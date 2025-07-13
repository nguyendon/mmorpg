import pygame
from enum import Enum, auto
from pathlib import Path

class ItemType(Enum):
    WEAPON = auto()
    ARMOR = auto()
    POTION = auto()
    GUN = auto()

class Item:
    def __init__(self, name, item_type, description, icon_name, stats=None):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.icon_name = icon_name
        self.stats = stats or {}
        self.icon = None
        self._load_icon()
    
    def _load_icon(self):
        """Load the item's icon"""
        try:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            icon_path = project_root / 'src' / 'assets' / 'images' / 'items' / self.icon_name
            
            if icon_path.exists():
                self.icon = pygame.image.load(str(icon_path))
                self.icon = pygame.transform.scale(self.icon, (32, 32))
            else:
                # Create a default colored rectangle if icon not found
                self.icon = pygame.Surface((32, 32))
                if self.item_type == ItemType.WEAPON:
                    self.icon.fill((255, 0, 0))  # Red for weapons
                elif self.item_type == ItemType.ARMOR:
                    self.icon.fill((0, 0, 255))  # Blue for armor
                elif self.item_type == ItemType.POTION:
                    self.icon.fill((0, 255, 0))  # Green for potions
                elif self.item_type == ItemType.GUN:
                    self.icon.fill((150, 150, 150))  # Gray for guns
                else:
                    self.icon.fill((128, 128, 128))  # Gray for other items
        except Exception as e:
            print(f"Error loading icon for {self.name}: {e}")
            self.icon = pygame.Surface((32, 32))
            self.icon.fill((128, 128, 128))

class ItemDrop:
    def __init__(self, item, x, y):
        self.item = item
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 32, 32)  # Items are 32x32
        self.pickup_range = 50
        self.bob_offset = 0
        self.bob_speed = 2
        self.bob_direction = 1
        
    def update(self, dt):
        """Update item animation"""
        self.bob_offset += self.bob_speed * self.bob_direction * dt
        
        if abs(self.bob_offset) >= 5:  # Max float distance
            self.bob_direction *= -1  # Reverse direction
            
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the item with floating animation"""
        # Draw shadow
        shadow_height = 4
        shadow_surface = pygame.Surface((32, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 128),
                          (0, 0, 32, shadow_height))
        
        screen.blit(shadow_surface, (
            self.x - camera_x,
            self.y + 32 - shadow_height/2 - camera_y
        ))
        
        # Draw item with bob offset
        if self.item.icon:
            screen.blit(self.item.icon, (
                self.x - camera_x,
                self.y - camera_y + self.bob_offset
            ))
            
            # Draw sparkle effect
            if pygame.time.get_ticks() % 1000 < 500:  # Blink every second
                pygame.draw.circle(screen, (255, 255, 255, 128), 
                                (int(self.x - camera_x + 16), 
                                 int(self.y - camera_y + self.bob_offset + 16)), 2)