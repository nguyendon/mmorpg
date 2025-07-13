import pygame
from src.common.constants import TILE_SIZE, PLAYER_SIZE

class NPC:
    def __init__(self, x, y, npc_type="villager"):
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.dialogue = []
        self.interaction_range = TILE_SIZE * 2  # 2 tiles range for interaction
        self.is_talking = False
        
        # Create a temporary colored rectangle based on NPC type
        self.sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        if npc_type == "villager":
            self.sprite.fill((0, 255, 0))  # Green for villagers
        elif npc_type == "merchant":
            self.sprite.fill((0, 0, 255))  # Blue for merchants
        else:  # guard
            self.sprite.fill((255, 0, 0))  # Red for guards
        
    def add_dialogue(self, text):
        """Add dialogue options for the NPC"""
        self.dialogue.append(text)
        
    def get_next_dialogue(self):
        """Get the next dialogue line"""
        if not self.dialogue:
            return "..."
        return self.dialogue[0]  # For now, just return the first line
        
    def can_interact(self, player_x, player_y):
        """Check if player is in range to interact"""
        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        return distance <= self.interaction_range
        
    def draw(self, screen, camera_x, camera_y):
        """Draw the NPC on the screen"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw NPC sprite
        screen.blit(self.sprite, (screen_x, screen_y))
        
        # Draw interaction indicator if in range
        if self.is_talking:
            pygame.draw.circle(screen, (255, 255, 255), 
                            (int(screen_x + PLAYER_SIZE/2), int(screen_y - 10)), 5)