import pygame
from .player import AttackType

class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def draw_bar(self, screen, x, y, width, height, current, maximum, color, shine_color):
        """Draw a stylized bar with gradient and shine effect"""
        # Background (dark)
        pygame.draw.rect(screen, (40, 40, 40), (x, y, width, height))
        
        if current > 0:
            # Calculate fill width
            fill_width = int((current / maximum) * width)
            
            # Main bar color
            pygame.draw.rect(screen, color, (x, y, fill_width, height))
            
            # Gradient shine effect
            shine_height = int(height * 0.4)
            shine_surface = pygame.Surface((fill_width, shine_height), pygame.SRCALPHA)
            for i in range(shine_height):
                alpha = int(255 * (1 - i/shine_height))
                pygame.draw.line(shine_surface, (*shine_color, alpha),
                               (0, i), (fill_width, i))
            screen.blit(shine_surface, (x, y))
            
            # Edge highlight
            pygame.draw.line(screen, shine_color, (x, y), (x + fill_width, y))
            
        # Border
        pygame.draw.rect(screen, (60, 60, 60), (x, y, width, height), 1)
        
    def draw_resource_text(self, screen, x, y, current, maximum, color):
        """Draw resource text (e.g., '100/100')"""
        text = f"{int(current)}/{maximum}"
        text_surface = self.small_font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        
        # Draw text shadow
        shadow_surface = self.small_font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(x+1, y+1))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def draw(self, screen, player, game_map):
        # Constants for bar dimensions and positions
        BAR_WIDTH = 200
        BAR_HEIGHT = 20
        BAR_X = 20
        HEALTH_Y = 20
        MANA_Y = 50
        
        # Draw health bar
        self.draw_bar(screen, BAR_X, HEALTH_Y, BAR_WIDTH, BAR_HEIGHT,
                     player.current_health, player.max_health,
                     (200, 50, 50), (255, 150, 150))
        self.draw_resource_text(screen, BAR_X + BAR_WIDTH/2, HEALTH_Y + BAR_HEIGHT/2,
                              player.current_health, player.max_health,
                              (255, 255, 255))
        
        # Draw mana bar
        self.draw_bar(screen, BAR_X, MANA_Y, BAR_WIDTH, BAR_HEIGHT,
                     player.current_mana, player.max_mana,
                     (50, 50, 200), (150, 150, 255))
        self.draw_resource_text(screen, BAR_X + BAR_WIDTH/2, MANA_Y + BAR_HEIGHT/2,
                              player.current_mana, player.max_mana,
                              (255, 255, 255))
        
        # Draw ability costs when hovering or on cooldown
        ability_info = [
            ("Spin (K)", 30, player.attack_timers[AttackType.SPIN]),
            ("Dash (L)", 20, player.attack_timers[AttackType.DASH]),
            ("Wave (U)", 40, player.attack_timers[AttackType.WAVE])
        ]
        
        x = BAR_X
        y = MANA_Y + BAR_HEIGHT + 20
        
        for ability, cost, cooldown in ability_info:
            # Background for ability cost display
            bg_color = (40, 40, 40) if player.current_mana >= cost else (60, 30, 30)
            pygame.draw.rect(screen, bg_color, (x, y, 100, 25))
            pygame.draw.rect(screen, (60, 60, 60), (x, y, 100, 25), 1)
            
            # Ability name and cost
            text = f"{ability}: {cost}"
            color = (255, 255, 255) if player.current_mana >= cost else (200, 100, 100)
            
            # Show cooldown if applicable
            if cooldown > 0:
                text = f"{ability}: {cooldown:.1f}s"
                color = (200, 200, 100)
            
            text_surface = self.small_font.render(text, True, color)
            screen.blit(text_surface, (x + 5, y + 5))
            
            y += 30  # Move down for next ability