import pygame
from ..common.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class UI:
    def __init__(self):
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)
        
        # Font initialization
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # UI Element positions
        self.health_bar_pos = (10, 10)
        self.health_bar_size = (200, 20)
        self.minimap_size = 150
        self.minimap_pos = (SCREEN_WIDTH - self.minimap_size - 10, 10)
        self.stats_pos = (10, 40)
        
        # Create minimap surface
        self.minimap_surface = pygame.Surface((self.minimap_size, self.minimap_size))
        
    def draw_health_bar(self, screen, current_health, max_health):
        """Draw the player's health bar"""
        # Background
        pygame.draw.rect(screen, self.GRAY, (*self.health_bar_pos, *self.health_bar_size))
        
        # Calculate health percentage
        health_percentage = current_health / max_health
        health_width = int(self.health_bar_size[0] * health_percentage)
        
        # Health bar (green for player)
        pygame.draw.rect(screen, self.GREEN, 
                        (self.health_bar_pos[0], self.health_bar_pos[1], 
                         health_width, self.health_bar_size[1]))
        
        # Health text
        health_text = f"{current_health}/{max_health} HP"
        text_surface = self.font.render(health_text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=(self.health_bar_pos[0] + self.health_bar_size[0]/2,
                                                 self.health_bar_pos[1] + self.health_bar_size[1]/2))
        screen.blit(text_surface, text_rect)

    def draw_minimap(self, screen, game_map, player_pos):
        """Draw a minimap showing the player's position and surroundings"""
        # Clear minimap surface
        self.minimap_surface.fill(self.BLACK)
        
        # Calculate scale factors
        scale_x = self.minimap_size / (game_map.width * game_map.tile_size)
        scale_y = self.minimap_size / (game_map.height * game_map.tile_size)
        
        # Draw map tiles
        for y in range(game_map.height):
            for x in range(game_map.width):
                tile = game_map.tiles[y][x]
                tile_x = int(x * game_map.tile_size * scale_x)
                tile_y = int(y * game_map.tile_size * scale_y)
                tile_size = max(1, int(game_map.tile_size * scale_x))
                
                # Choose color based on tile type
                color = self.GRAY
                if not tile.walkable:
                    color = self.BLACK
                elif tile.tile_type.name == 'WATER':
                    color = self.BLUE
                elif tile.tile_type.name == 'GRASS':
                    color = self.GREEN
                
                pygame.draw.rect(self.minimap_surface, color,
                               (tile_x, tile_y, tile_size, tile_size))
        
        # Draw player position
        player_x = int(player_pos[0] * scale_x)
        player_y = int(player_pos[1] * scale_y)
        pygame.draw.circle(self.minimap_surface, self.RED, (player_x, player_y), 3)
        
        # Draw border
        pygame.draw.rect(self.minimap_surface, self.WHITE, 
                        (0, 0, self.minimap_size, self.minimap_size), 1)
        
        # Draw minimap to screen
        screen.blit(self.minimap_surface, self.minimap_pos)

    def draw_stats(self, screen, player):
        """Draw player stats"""
        stats = [
            f"Level: {player.level if hasattr(player, 'level') else 1}",
            f"XP: {player.xp if hasattr(player, 'xp') else 0}",
            f"Position: ({int(player.x)}, {int(player.y)})"
        ]
        
        for i, stat in enumerate(stats):
            text_surface = self.small_font.render(stat, True, self.WHITE)
            screen.blit(text_surface, 
                       (self.stats_pos[0], self.stats_pos[1] + i * 20))

    def draw(self, screen, player, game_map):
        """Draw all UI elements"""
        # Draw health bar using player's actual health values
        self.draw_health_bar(screen, player.current_health, player.max_health)
        
        # Draw minimap
        self.draw_minimap(screen, game_map, (player.x, player.y))
        
        # Draw stats
        self.draw_stats(screen, player)