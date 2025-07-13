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
        enemy_types = [
            {
                'type': 'goblin',
                'health': 50,
                'strength': 8,
                'defense': 3,
                'speed': 2,
                'color': (150, 0, 0)  # Red goblin
            },
            {
                'type': 'ogre',
                'health': 100,
                'strength': 15,
                'defense': 5,
                'speed': 1,
                'color': (100, 50, 0)  # Brown ogre
            },
            {
                'type': 'speeder',
                'health': 30,
                'strength': 5,
                'defense': 1,
                'speed': 4,
                'color': (200, 0, 0)  # Bright red speeder
            }
        ]
        
        enemy_type = random.choice(enemy_types)
        enemy = Enemy(x, y, enemy_type['type'])
        
        # Customize enemy stats
        enemy.max_health = enemy_type['health']
        enemy.current_health = enemy.max_health
        enemy.strength = enemy_type['strength']
        enemy.defense = enemy_type['defense']
        enemy.speed = enemy_type['speed']
        
        # Create custom sprite for this enemy type
        enemy.sprite.fill((0, 0, 0, 0))  # Clear sprite
        enemy._create_enemy_sprite(enemy_type['color'])
        
        return enemy