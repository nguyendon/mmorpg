from enum import Enum, auto
import random

class TileType(Enum):
    GRASS = auto()
    WATER = auto()
    WALL = auto()
    STONE = auto()
    SAND = auto()
    PORTAL = auto()

class Tile:
    # Dictionary to map tile types to sprite patterns
    TILE_SPRITES = {
        TileType.GRASS: ['grass_{}.png'.format(i) for i in range(3)],
        TileType.WATER: ['water_{}.png'.format(i) for i in range(4)],
        TileType.WALL: ['wall_{}.png'.format(i) for i in range(2)],
        TileType.STONE: ['stone_{}.png'.format(i) for i in range(3)],
        TileType.SAND: ['sand_{}.png'.format(i) for i in range(3)],
        TileType.PORTAL: ['portal.png'],  # We'll need to create this sprite
    }

    # Transition tiles mapping
    TRANSITIONS = {
        (TileType.GRASS, TileType.SAND): 'grass_sand_{}.png',
        (TileType.GRASS, TileType.WATER): 'grass_water_{}.png',
        (TileType.SAND, TileType.WATER): 'sand_water_{}.png',
        (TileType.GRASS, TileType.STONE): 'grass_stone_{}.png',
        (TileType.STONE, TileType.WALL): 'stone_wall_{}.png',
    }

    def __init__(self, tile_type: TileType):
        self.tile_type = tile_type
        self.sprite_name = random.choice(self.TILE_SPRITES[tile_type])
        self.walkable = tile_type not in [TileType.WATER, TileType.WALL]  # Portals are walkable
        self.animation_frame = 0
        self.transition = None
        self.transition_direction = None

    def update_animation(self):
        """Update animation frame for animated tiles (like water)"""
        if self.tile_type == TileType.WATER:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.sprite_name = f'water_{self.animation_frame}.png'

    def set_transition(self, neighbor_type, direction):
        """Set transition to another tile type in the specified direction"""
        key = (self.tile_type, neighbor_type)
        if key in self.TRANSITIONS:
            self.transition = key
            self.transition_direction = direction
            return True
        return False

    def get_transition_sprite(self):
        """Get the transition sprite name if any"""
        if self.transition and self.transition_direction:
            return self.TRANSITIONS[self.transition].format(self.transition_direction)
        return None