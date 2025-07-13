import pygame
from enum import Enum, auto
from pathlib import Path

class ItemType(Enum):
    WEAPON = auto()
    ARMOR = auto()
    POTION = auto()
    MATERIAL = auto()
    QUEST = auto()
    GUN = auto()  # Add gun type

# Define some standard items
ITEM_TEMPLATES = {
    "health_potion": {
        "name": "Health Potion",
        "type": ItemType.POTION,
        "description": "Restores 30 HP",
        "icon_name": "health_potion.png",
        "stats": {"heal": 30}
    },
    "pistol": {
        "name": "Pistol",
        "type": ItemType.GUN,
        "description": "A basic ranged weapon",
        "icon_name": "pistol.png",
        "stats": {
            "damage": 15,
            "range": 300,
            "cooldown": 0.5,
            "projectile_speed": 500
        }
    }
}

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
        self.bob_offset = 0
        self.bob_speed = 2
        self.bob_height = 5
        self.pickup_range = 50
        self.alive = True
        
    def update(self, dt):
        """Update the item drop's floating animation"""
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * self.bob_height
        
    def draw(self, screen, camera_x, camera_y):
        """Draw the item drop on the screen"""
        if self.item.icon:
            screen_x = self.x - camera_x
            screen_y = self.y - camera_y + self.bob_offset
            
            # Draw shadow
            shadow_surface = pygame.Surface((32, 4), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, 128), (0, 0, 32, 4))
            screen.blit(shadow_surface, (screen_x, screen_y + 32))
            
            # Draw item
            screen.blit(self.item.icon, (screen_x, screen_y))
            
            # Draw sparkle effect
            if pygame.time.get_ticks() % 1000 < 500:  # Blink every second
                pygame.draw.circle(screen, (255, 255, 255, 128), 
                                (int(screen_x + 16), int(screen_y + 16)), 2)
    
    def can_pickup(self, player_x, player_y):
        """Check if the player is in range to pick up the item"""
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        return distance <= self.pickup_range