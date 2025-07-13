from enum import Enum, auto

class TileType(Enum):
    GRASS = auto()
    WATER = auto()
    WALL = auto()
    STONE = auto()
    SAND = auto()

class Tile:
    # Dictionary to map tile types to sprite names
    TILE_SPRITES = {
        TileType.GRASS: 'grass.png',
        TileType.WATER: 'water.png',
        TileType.WALL: 'wall.png',
        TileType.STONE: 'stone.png',
        TileType.SAND: 'sand.png',
    }

    def __init__(self, tile_type: TileType):
        self.tile_type = tile_type
        self.sprite_name = self.TILE_SPRITES[tile_type]
        self.walkable = tile_type not in [TileType.WATER, TileType.WALL]