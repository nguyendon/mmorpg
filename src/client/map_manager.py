import pygame
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
        self.transition_timer = 0
        self.is_transitioning = False
        self.pending_portal = None
        
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
        
    def check_portal(self, x, y, player_size):
        """Check if there's a portal at the given position"""
        if not self.current_map_id or self.is_transitioning:
            return None
            
        current_map = self.maps[self.current_map_id]
        
        # Check a box around the player's position for portals
        check_points = [
            (x, y),  # Center
            (x - player_size/4, y - player_size/4),  # Top-left
            (x + player_size/4, y - player_size/4),  # Top-right
            (x - player_size/4, y + player_size/4),  # Bottom-left
            (x + player_size/4, y + player_size/4)   # Bottom-right
        ]
        
        for check_x, check_y in check_points:
            tile_x = int(check_x // current_map.tile_size)
            tile_y = int(check_y // current_map.tile_size)
            
            portal = self.portals.get((self.current_map_id, tile_x, tile_y))
            if portal:
                return portal
                
        return None
        
    def start_transition(self, portal):
        """Start the portal transition process"""
        if not self.is_transitioning:
            self.is_transitioning = True
            self.transition_timer = 1.0  # 1 second transition
            self.pending_portal = portal
            
    def update(self, dt):
        """Update the current map and handle transitions"""
        current_map = self.get_current_map()
        if current_map:
            current_map.update(dt)
            
        # Handle transition timer
        if self.is_transitioning and self.transition_timer > 0:
            self.transition_timer -= dt
            if self.transition_timer <= 0 and self.pending_portal:
                # Complete the transition
                self.current_map_id = self.pending_portal.target_map_id
                target_pos = (self.pending_portal.target_x, self.pending_portal.target_y)
                self.is_transitioning = False
                self.pending_portal = None
                return target_pos  # Return the target position when transition completes
        
        return None  # Return None if no transition completed
        
    def get_transition_alpha(self):
        """Get the current transition overlay alpha value"""
        if self.is_transitioning:
            if self.transition_timer > 0.5:
                # Fade out (0 -> 255)
                return int(255 * (1.0 - (self.transition_timer - 0.5) * 2))
            else:
                # Fade in (255 -> 0)
                return int(255 * (self.transition_timer * 2))
        return 0
        
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw the current map and transition effect"""
        current_map = self.get_current_map()
        if current_map:
            current_map.draw(screen, camera_x, camera_y)
            
        # Draw transition overlay
        if self.is_transitioning:
            overlay = pygame.Surface((screen.get_width(), screen.get_height()))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(self.get_transition_alpha())
            screen.blit(overlay, (0, 0))