from enum import Enum, auto

class TileType(Enum):
    GRASS = auto()
    WATER = auto()
    WALL = auto()
    STONE = auto()
    SAND = auto()

class Tile:
    # Dictionary to store tile colors (temporary until we add sprites)
    TILE_COLORS = {
        TileType.GRASS: (34, 139, 34),    # Forest green
        TileType.WATER: (0, 0, 139),      # Dark blue
        TileType.WALL: (128, 128, 128),   # Gray
        TileType.STONE: (169, 169, 169),  # Dark gray
        TileType.SAND: (238, 214, 175),   # Tan
    }

    def __init__(self, tile_type: TileType):
        self.tile_type = tile_type
        self.color = self.TILE_COLORS[tile_type]
        self.walkable = tile_type not in [TileType.WATER, TileType.WALL]