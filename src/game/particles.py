"""
Five Nights at Rocket - Particle System
Handles particle effects for visual feedback
"""

import pygame
import math
import random
from typing import List, Tuple


class Particle:
    """
    Individual particle in a particle effect.
    """
    
    def __init__(self, x: float, y: float, dx: float, dy: float, 
                 color: Tuple[int, int, int], lifetime: float, size: float = 4):
        """
        Initialize a particle.
        
        Args:
            x: Initial x position
            y: Initial y position
            dx: X velocity
            dy: Y velocity
            color: RGB color tuple
            lifetime: How long the particle lives (seconds)
            size: Size of the particle
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255

    def update(self, dt: float):
        """Update particle position and fade."""
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Draw the particle to the screen."""
        if self.lifetime > 0:
            alpha = max(0, min(255, self.alpha))
            color = (*self.color, alpha)
            pos = (int(self.x - camera_offset[0]), int(self.y - camera_offset[1]))
            
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(temp_surface, (pos[0] - int(self.size), pos[1] - int(self.size)))

    def is_alive(self) -> bool:
        """Check if particle is still alive."""
        return self.lifetime > 0


class ParticleSystem:
    """
    Manages multiple particles for visual effects.
    """
    
    def __init__(self):
        """Initialize the particle system."""
        self.particles: List[Particle] = []

    def emit(self, x: float, y: float, color: Tuple[int, int, int], 
             count: int = 10, spread: float = 100, lifetime: float = 1.0):
        """
        Emit particles from a position.
        
        Args:
            x: X position to emit from
            y: Y position to emit from
            color: RGB color tuple
            count: Number of particles to emit
            spread: Maximum speed of particles
            lifetime: How long particles live (seconds)
        """
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, spread)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.uniform(2, 6)
            particle = Particle(x, y, dx, dy, color, lifetime, size)
            self.particles.append(particle)

    def update(self, dt: float):
        """Update all particles."""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface, camera_offset)
