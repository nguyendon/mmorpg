import pygame
from ..common.tiles import Tile, TileType

class GameMap:
    def __init__(self, width, height, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles = []
        
        # Initialize with grass
        self.tiles = [[Tile(TileType.GRASS) for _ in range(width)] for _ in range(height)]
        
        # Add some sample features (we'll make this data-driven later)
        self._create_sample_map()

    def _create_sample_map(self):
        """Create a sample map with various features"""
        # Add some water
        for x in range(5, 8):
            for y in range(5, 15):
                self.tiles[y][x] = Tile(TileType.WATER)
        
        # Add some walls
        for x in range(10, 15):
            self.tiles[5][x] = Tile(TileType.WALL)
            self.tiles[10][x] = Tile(TileType.WALL)
        
        # Add some stone
        for x in range(18, 22):
            for y in range(8, 12):
                self.tiles[y][x] = Tile(TileType.STONE)
        
        # Add some sand
        for x in range(3, 7):
            for y in range(18, 22):
                self.tiles[y][x] = Tile(TileType.SAND)

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the visible portion of the map"""
        # Get the visible range based on screen size
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        start_x = max(0, camera_x // self.tile_size)
        end_x = min(self.width, (camera_x + screen_width) // self.tile_size + 1)
        start_y = max(0, camera_y // self.tile_size)
        end_y = min(self.height, (camera_y + screen_height) // self.tile_size + 1)
        
        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                rect = pygame.Rect(
                    x * self.tile_size - camera_x,
                    y * self.tile_size - camera_y,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(screen, tile.color, rect)
                # Add a grid line
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

    def is_walkable(self, x, y):
        """Check if a tile position is walkable"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x].walkable
        return False

    def get_tile(self, x, y):
        """Get the tile at a specific position"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x]
        return None