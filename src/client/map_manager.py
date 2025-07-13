from .map import GameMap
from ..common.tiles import Tile, TileType

class Portal:
    def __init__(self, target_map_id, target_x, target_y):
        self.target_map_id = target_map_id
        self.target_x = target_x
        self.target_y = target_y

class MapManager:
    def __init__(self):
        self.maps = {}
        self.current_map_id = None
        self.portals = {}  # Dictionary of {(map_id, x, y): Portal}
        
    def add_map(self, map_id, game_map):
        """Add a map to the manager"""
        self.maps[map_id] = game_map
        if self.current_map_id is None:
            self.current_map_id = map_id
            
    def add_portal(self, map_id, x, y, target_map_id, target_x, target_y):
        """Add a portal at the specified location"""
        # Convert pixel coordinates to tile coordinates
        tile_x = x // self.maps[map_id].tile_size
        tile_y = y // self.maps[map_id].tile_size
        
        # Create portal
        portal = Portal(target_map_id, target_x, target_y)
        self.portals[(map_id, tile_x, tile_y)] = portal
        
        # Set portal tile
        self.maps[map_id].tiles[tile_y][tile_x] = Tile(TileType.PORTAL)
        
    def get_current_map(self):
        """Get the currently active map"""
        return self.maps.get(self.current_map_id)
        
    def check_portal(self, x, y):
        """Check if there's a portal at the given position and handle transition"""
        if not self.current_map_id:
            return None
            
        current_map = self.maps[self.current_map_id]
        tile_x = x // current_map.tile_size
        tile_y = y // current_map.tile_size
        
        portal = self.portals.get((self.current_map_id, tile_x, tile_y))
        if portal:
            # Change current map
            self.current_map_id = portal.target_map_id
            # Return the target coordinates for the player
            return portal.target_x, portal.target_y
            
        return None
        
    def update(self, dt):
        """Update the current map"""
        current_map = self.get_current_map()
        if current_map:
            current_map.update(dt)
            
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the current map"""
        current_map = self.get_current_map()
        if current_map:
            current_map.draw(screen, camera_x, camera_y)