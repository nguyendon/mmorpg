import pygame
from .items import ItemType

class Inventory:
    def __init__(self, size=20):
        self.size = size
        self.items = []
        self.selected_slot = None
        self.visible = False
        self.slot_size = 40
        self.padding = 10
        self.font = pygame.font.Font(None, 24)
        self.tooltip_font = pygame.font.Font(None, 20)
        
    def add_item(self, item):
        """Add an item to the inventory"""
        if len(self.items) < self.size:
            self.items.append(item)
            return True
        return False
        
    def remove_item(self, index):
        """Remove an item from the inventory"""
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None
        
    def get_item(self, index):
        """Get an item without removing it"""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def draw(self, screen):
        """Draw the inventory if visible"""
        if not self.visible:
            return
            
        # Calculate inventory dimensions
        cols = 5
        rows = (self.size + cols - 1) // cols
        width = cols * (self.slot_size + self.padding) + self.padding
        height = rows * (self.slot_size + self.padding) + self.padding
        
        # Draw inventory background
        inventory_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(inventory_surface, (0, 0, 0, 200), 
                        (0, 0, width, height))
        
        # Draw slots
        for i in range(self.size):
            row = i // cols
            col = i % cols
            x = col * (self.slot_size + self.padding) + self.padding
            y = row * (self.slot_size + self.padding) + self.padding
            
            # Draw slot background
            slot_color = (60, 60, 60, 200) if i == self.selected_slot else (40, 40, 40, 200)
            pygame.draw.rect(inventory_surface, slot_color,
                           (x, y, self.slot_size, self.slot_size))
            
            # Draw item if slot is filled
            if i < len(self.items):
                item = self.items[i]
                if item.icon:
                    # Center the icon in the slot
                    icon_x = x + (self.slot_size - item.icon.get_width()) // 2
                    icon_y = y + (self.slot_size - item.icon.get_height()) // 2
                    inventory_surface.blit(item.icon, (icon_x, icon_y))
                    
                    # Draw stack count if applicable
                    if hasattr(item, 'count') and item.count > 1:
                        count_text = self.font.render(str(item.count), True, (255, 255, 255))
                        inventory_surface.blit(count_text, (x + self.slot_size - 20, y + self.slot_size - 20))
            
            # Draw slot border
            pygame.draw.rect(inventory_surface, (80, 80, 80, 255),
                           (x, y, self.slot_size, self.slot_size), 1)
        
        # Draw inventory on screen
        screen_x = (screen.get_width() - width) // 2
        screen_y = (screen.get_height() - height) // 2
        screen.blit(inventory_surface, (screen_x, screen_y))
        
        # Draw tooltip for selected item
        mouse_pos = pygame.mouse.get_pos()
        slot_x = (mouse_pos[0] - screen_x - self.padding) // (self.slot_size + self.padding)
        slot_y = (mouse_pos[1] - screen_y - self.padding) // (self.slot_size + self.padding)
        slot_index = slot_y * cols + slot_x
        
        if (0 <= slot_x < cols and 0 <= slot_y < rows and 
            slot_index < len(self.items)):
            item = self.items[slot_index]
            self._draw_tooltip(screen, item, mouse_pos[0], mouse_pos[1])
    
    def _draw_tooltip(self, screen, item, x, y):
        """Draw item tooltip"""
        # Prepare tooltip text
        lines = [
            item.name,
            f"Type: {item.item_type.name.capitalize()}",
            "",
            item.description
        ]
        
        # Add stats if they exist
        if item.stats:
            lines.append("")
            for stat, value in item.stats.items():
                if value > 0:
                    lines.append(f"+{value} {stat.capitalize()}")
                else:
                    lines.append(f"{value} {stat.capitalize()}")
        
        # Calculate tooltip dimensions
        line_height = self.tooltip_font.get_height()
        max_width = max(self.tooltip_font.size(line)[0] for line in lines)
        tooltip_width = max_width + 20
        tooltip_height = len(lines) * line_height + 20
        
        # Adjust position to keep tooltip on screen
        x = min(x, screen.get_width() - tooltip_width - 10)
        y = min(y, screen.get_height() - tooltip_height - 10)
        
        # Draw tooltip background
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, (0, 0, 0, 230), 
                        (0, 0, tooltip_width, tooltip_height))
        pygame.draw.rect(tooltip_surface, (80, 80, 80, 255),
                        (0, 0, tooltip_width, tooltip_height), 1)
        
        # Draw tooltip text
        for i, line in enumerate(lines):
            if line:  # Skip empty lines
                color = (255, 255, 255)
                if i == 0:  # Item name
                    color = self._get_rarity_color(item)
                text_surface = self.tooltip_font.render(line, True, color)
                tooltip_surface.blit(text_surface, (10, 10 + i * line_height))
        
        screen.blit(tooltip_surface, (x, y))
    
    def _get_rarity_color(self, item):
        """Get color based on item rarity"""
        if 'rarity' in item.stats:
            rarities = {
                'common': (255, 255, 255),     # White
                'uncommon': (0, 255, 0),       # Green
                'rare': (0, 112, 221),         # Blue
                'epic': (163, 53, 238),        # Purple
                'legendary': (255, 128, 0)      # Orange
            }
            return rarities.get(item.stats['rarity'], (255, 255, 255))
        return (255, 255, 255)  # Default white
    
    def handle_click(self, screen_x, screen_y, screen_width, screen_height):
        """Handle mouse click in inventory"""
        if not self.visible:
            return
            
        # Calculate inventory position
        inv_x = (screen_width - (5 * (self.slot_size + self.padding) + self.padding)) // 2
        inv_y = (screen_height - ((self.size // 5) * (self.slot_size + self.padding) + self.padding)) // 2
        
        # Calculate clicked slot
        slot_x = (screen_x - inv_x - self.padding) // (self.slot_size + self.padding)
        slot_y = (screen_y - inv_y - self.padding) // (self.slot_size + self.padding)
        slot_index = slot_y * 5 + slot_x
        
        if (0 <= slot_x < 5 and 
            0 <= slot_y < (self.size // 5) and
            slot_index < len(self.items)):
            self.selected_slot = slot_index
            return self.items[slot_index]
        
        self.selected_slot = None
        return None