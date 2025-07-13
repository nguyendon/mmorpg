import random
from .enemy import Enemy

class EnemySpawner:
    def __init__(self, game_map):
        self.game_map = game_map
        self.spawn_timer = 0
        self.spawn_interval = 5.0  # Spawn every 5 seconds
        self.max_enemies = 10
        self.min_distance_from_player = 200
        self.max_spawn_attempts = 10
        
    def update(self, dt, player, current_enemies):
        """Update spawner and potentially spawn new enemies"""
        self.spawn_timer += dt
        
        if (self.spawn_timer >= self.spawn_interval and 
            len(current_enemies) < self.max_enemies):
            self.spawn_timer = 0
            
            # Try to spawn an enemy
            spawn_point = self._find_spawn_point(player)
            if spawn_point:
                enemy = self._create_enemy(*spawn_point)
                if enemy:
                    return enemy
        return None
        
    def _find_spawn_point(self, player):
        """Find a valid spawn point away from the player"""
        for _ in range(self.max_spawn_attempts):
            # Generate random position
            x = random.randint(0, self.game_map.width - 1) * self.game_map.tile_size
            y = random.randint(0, self.game_map.height - 1) * self.game_map.tile_size
            
            # Check if position is walkable
            if not self.game_map.is_walkable(x, y):
                continue
                
            # Check distance from player
            dx = x - player.x
            dy = y - player.y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance >= self.min_distance_from_player:
                return (x, y)
                
        return None
        
    def _create_enemy(self, x, y):
        """Create a random enemy type at the given position"""
        enemy_type = random.choice(["goblin", "zombie"])
        enemy = Enemy(x, y, enemy_type)
        return enemy