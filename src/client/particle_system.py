import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity=(0, 0), lifetime=1.0, size=3, gravity=0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        self.alpha = 255

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def create_hit_effect(self, x, y, color=(255, 255, 255)):
        """Create a hit effect at the given position"""
        num_particles = 10
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(0.3, 0.6)
            size = random.randint(2, 4)
            self.particles.append(Particle(x, y, color, velocity, lifetime, size))
            
    def create_slash_effect(self, x, y, direction, color=(255, 255, 100)):
        """Create a slash effect in the given direction"""
        num_particles = 15
        base_angle = {
            'UP': -math.pi/2,
            'DOWN': math.pi/2,
            'LEFT': math.pi,
            'RIGHT': 0
        }.get(direction, 0)
        
        arc = math.pi/3  # 60-degree arc
        for _ in range(num_particles):
            angle = base_angle + random.uniform(-arc/2, arc/2)
            speed = random.uniform(100, 200)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(0.2, 0.4)
            size = random.randint(3, 6)
            self.particles.append(Particle(x, y, color, velocity, lifetime, size))
            
    def create_special_attack_effect(self, x, y, color=(0, 255, 255)):
        """Create a spinning attack effect"""
        num_particles = 30
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi
            speed = random.uniform(150, 250)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(0.5, 0.8)
            size = random.randint(4, 7)
            self.particles.append(Particle(x, y, color, velocity, lifetime, size))
            
    def create_death_effect(self, x, y, color=(150, 0, 0)):
        """Create a death explosion effect"""
        num_particles = 20
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(0.7, 1.2)
            size = random.randint(3, 8)
            particle = Particle(x, y, color, velocity, lifetime, size, gravity=200)
            self.particles.append(particle)
            
    def create_spawn_effect(self, x, y, color=(200, 0, 0)):
        """Create a spawn effect"""
        num_particles = 25
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(0.5, 1.0)
            size = random.randint(3, 6)
            # Particles move inward for spawn effect
            particle = Particle(
                x + math.cos(angle) * 50,
                y + math.sin(angle) * 50,
                color,
                (-velocity[0], -velocity[1]),
                lifetime,
                size
            )
            self.particles.append(particle)

    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            # Update position
            particle.x += particle.velocity_x * dt
            particle.y += particle.velocity_y * dt
            
            # Apply gravity
            particle.velocity_y += particle.gravity * dt
            
            # Update lifetime and alpha
            particle.lifetime -= dt
            particle.alpha = int((particle.lifetime / particle.max_lifetime) * 255)
            
            # Remove dead particles
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw all particles"""
        for particle in self.particles:
            # Create a surface for the particle with alpha channel
            particle_surface = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
            
            # Draw the particle with current alpha
            pygame.draw.circle(
                particle_surface,
                (*particle.color, particle.alpha),
                (particle.size, particle.size),
                particle.size
            )
            
            # Draw to screen with camera offset
            screen.blit(
                particle_surface,
                (particle.x - particle.size - camera_x,
                 particle.y - particle.size - camera_y)
            )