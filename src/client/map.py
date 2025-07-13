import pygame
from pathlib import Path
from ..common.tiles import Tile, TileType
from .sprite_manager import SpriteManager

class GameMap:
    def __init__(self, width, height, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles = []
        
        # Initialize sprite manager
        self.sprite_manager = SpriteManager()
        self.sprites_loaded = False
        
        # Initialize with grass
        self.tiles = [[Tile(TileType.GRASS) for _ in range(width)] for _ in range(height)]
        
        # Initialize last safe position (center of map)
        self.last_safe_x = (width * tile_size) / 2
        self.last_safe_y = (height * tile_size) / 2
        
        # Add some sample features (we'll make this data-driven later)
        self._create_sample_map()
        self._calculate_transitions()

    def ensure_sprites_loaded(self):
        """Ensure sprites are loaded before drawing"""
        if not self.sprites_loaded:
            self._load_sprites()
            self.sprites_loaded = True

    def _load_sprites(self):
        """Load all tile sprites."""
        # Get the absolute path to the assets directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        base_path = project_root / 'src' / 'assets' / 'images' / 'tiles'
        
        if not base_path.exists():
            print(f"Error: Tiles directory not found at {base_path}")
            return
            
        # Load all PNG files in the tiles directory
        for filepath in base_path.glob('*.png'):
            self.sprite_manager.load_sprite(filepath.name, str(filepath))

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

    def _calculate_transitions(self):
        """Calculate transitions between different terrain types."""
        directions = {
            'top': (0, -1),
            'right': (1, 0),
            'bottom': (0, 1),
            'left': (-1, 0)
        }

        for y in range(self.height):
            for x in range(self.width):
                current_tile = self.tiles[y][x]
                
                # Check each direction for different terrain types
                for direction, (dx, dy) in directions.items():
                    nx, ny = x + dx, y + dy
                    
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        neighbor_tile = self.tiles[ny][nx]
                        if neighbor_tile.tile_type != current_tile.tile_type:
                            current_tile.set_transition(neighbor_tile.tile_type, direction)

    def update(self, dt):
        """Update animated tiles."""
        for row in self.tiles:
            for tile in row:
                tile.update_animation()

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the visible portion of the map"""
        # Ensure sprites are loaded before drawing
        self.ensure_sprites_loaded()
        
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
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                
                # Draw base tile
                sprite = self.sprite_manager.get_sprite(tile.sprite_name)
                if sprite:
                    screen.blit(sprite, (screen_x, screen_y))
                
                # Draw transition if exists
                transition_sprite_name = tile.get_transition_sprite()
                if transition_sprite_name:
                    transition_sprite = self.sprite_manager.get_sprite(transition_sprite_name)
                    if transition_sprite:
                        screen.blit(transition_sprite, (screen_x, screen_y))

    def is_walkable(self, x, y):
        """Check if a tile position is walkable"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        # Check bounds first
        if not (0 <= tile_x < self.width and 0 <= tile_y < self.height):
            return False
            
        current_tile = self.tiles[tile_y][tile_x]
        
        # If in water, allow movement only if already in that tile
        # This prevents getting stuck in water but makes it impossible to enter
        if current_tile.tile_type == TileType.WATER:
            player_current_tile_x = int(self.last_safe_x // self.tile_size)
            player_current_tile_y = int(self.last_safe_y // self.tile_size)
            return tile_x == player_current_tile_x and tile_y == player_current_tile_y
            
        # Update last safe position if on walkable ground
        if current_tile.walkable:
            self.last_safe_x = tile_x * self.tile_size + self.tile_size / 2
            self.last_safe_y = tile_y * self.tile_size + self.tile_size / 2
            
        return current_tile.walkable

    def get_tile(self, x, y):
        """Get the tile at a specific position"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.tiles[tile_y][tile_x]
        return None