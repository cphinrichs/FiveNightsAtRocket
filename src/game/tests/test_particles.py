"""
Unit tests for particle system
Tests Particle and ParticleSystem classes
"""

import pytest
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from particles import Particle, ParticleSystem


class TestParticle:
    """Test Particle class"""
    
    @pytest.fixture
    def particle(self):
        """Create a test particle"""
        pygame.init()
        return Particle(100, 100, 10, 10, (255, 0, 0), lifetime=2.0)
    
    def test_particle_initialization(self, particle):
        """Test particle initializes correctly"""
        assert particle.x == 100
        assert particle.y == 100
        assert particle.dx == 10
        assert particle.dy == 10
        assert particle.color == (255, 0, 0)
        assert particle.lifetime == 2.0
        assert particle.max_lifetime == 2.0
    
    def test_particle_aging(self, particle):
        """Test particle ages over time"""
        initial_lifetime = particle.lifetime
        particle.update(0.5)
        
        assert particle.lifetime < initial_lifetime
        assert particle.lifetime == 1.5
    
    def test_particle_death(self, particle):
        """Test particle dies after lifetime"""
        particle.update(1.0)
        assert particle.is_alive() == True
        
        particle.update(1.5)
        assert particle.is_alive() == False
    
    def test_particle_movement(self, particle):
        """Test particle moves based on velocity"""
        initial_x = particle.x
        initial_y = particle.y
        
        particle.update(1.0)
        
        # Position should change based on velocity
        assert particle.x != initial_x
        assert particle.y != initial_y
        assert particle.x == initial_x + (10 * 1.0)  # vx * dt
    
    def test_particle_velocity(self):
        """Test particle velocity affects movement"""
        pygame.init()
        particle = Particle(100, 100, 50, 0, (255, 255, 255), lifetime=2.0)
        
        initial_x = particle.x
        particle.update(1.0)
        
        # Velocity should move particle
        assert particle.x > initial_x
        assert particle.x == initial_x + 50  # dx * dt
    
    def test_particle_maintains_velocity(self):
        """Test particle maintains velocity over time"""
        pygame.init()
        particle = Particle(100, 100, 10, 20, (255, 255, 255), lifetime=2.0)
        
        initial_dx = particle.dx
        initial_dy = particle.dy
        particle.update(0.5)
        
        # Velocity should remain constant (no gravity in basic particles)
        assert particle.dx == initial_dx
        assert particle.dy == initial_dy
    
    def test_particle_lifespan(self):
        """Test particle tracks lifetime correctly"""
        pygame.init()
        particle = Particle(100, 100, 0, 0, (255, 255, 255), lifetime=5.0)
        
        particle.update(2.0)
        assert particle.lifetime == 3.0
        
        particle.update(2.0)
        assert particle.lifetime == 1.0
        
        particle.update(1.0)
        assert particle.lifetime == 0.0
        assert particle.is_alive() == False


class TestParticleSystem:
    """Test ParticleSystem class"""
    
    @pytest.fixture
    def particle_system(self):
        """Create a test particle system"""
        pygame.init()
        return ParticleSystem()
    
    def test_system_initialization(self, particle_system):
        """Test particle system initializes empty"""
        assert len(particle_system.particles) == 0
    
    def test_emit_particle(self, particle_system):
        """Test emitting particles"""
        particle_system.emit(100, 100, (255, 0, 0), count=1, spread=50, lifetime=1.0)
        
        assert len(particle_system.particles) == 1
    
    def test_emit_multiple_particles(self, particle_system):
        """Test emitting multiple particles"""
        particle_system.emit(100, 100, (255, 0, 0), count=5, spread=50, lifetime=1.0)
        
        assert len(particle_system.particles) == 5
    
    def test_particle_cleanup(self, particle_system):
        """Test dead particles are removed"""
        # Emit particle with short lifetime
        particle_system.emit(100, 100, (255, 0, 0), count=1, spread=50, lifetime=0.5)
        
        assert len(particle_system.particles) == 1
        
        # Update past lifetime
        particle_system.update(1.0)
        
        # Dead particle should be removed
        assert len(particle_system.particles) == 0
    
    def test_multiple_particles_update(self, particle_system):
        """Test multiple particles update independently"""
        # Emit particles with different lifetimes
        particle_system.emit(100, 100, (255, 0, 0), count=1, spread=50, lifetime=1.0)
        particle_system.emit(200, 200, (0, 255, 0), count=1, spread=50, lifetime=2.0)
        
        assert len(particle_system.particles) == 2
        
        # Update 1.5 seconds
        particle_system.update(1.5)
        
        # First particle should be dead, second alive
        assert len(particle_system.particles) == 1
    
    def test_particle_spread(self, particle_system):
        """Test particles emit with velocity spread"""
        particle_system.emit(
            100, 100, 
            color=(255, 255, 255),
            count=10,
            spread=100,
            lifetime=2.0
        )
        
        # Check particles have varied velocities
        velocities = set()
        for particle in particle_system.particles:
            velocities.add((round(particle.dx, 1), round(particle.dy, 1)))
        
        # Should have some variation in velocities
        assert len(velocities) > 1
    
    def test_system_clear(self, particle_system):
        """Test clearing all particles"""
        particle_system.emit(100, 100, (255, 0, 0), count=5, spread=50, lifetime=10.0)
        assert len(particle_system.particles) == 5
        
        particle_system.particles.clear()
        assert len(particle_system.particles) == 0
    
    def test_particle_positions_start_at_emission(self, particle_system):
        """Test emitted particles start at emission point"""
        particle_system.emit(
            150, 200,
            color=(255, 255, 255),
            count=10,
            spread=50,
            lifetime=2.0
        )
        
        # All particles should start at emission point
        for particle in particle_system.particles:
            assert particle.x == 150
            assert particle.y == 200


class TestParticleIntegration:
    """Test particle system integration"""
    
    def test_particle_lifecycle(self):
        """Test complete particle lifecycle"""
        pygame.init()
        system = ParticleSystem()
        
        # Emit particles
        system.emit(100, 100, (255, 100, 0), count=3, spread=50, lifetime=2.0)
        assert len(system.particles) == 3
        
        # Update - particles should be alive
        system.update(0.5)
        assert len(system.particles) == 3
        
        # Update more
        system.update(1.0)
        assert len(system.particles) == 3
        
        # Update past lifetime
        system.update(1.0)
        assert len(system.particles) == 0
    
    def test_continuous_emission(self):
        """Test continuous particle emission"""
        pygame.init()
        system = ParticleSystem()
        
        # Emit in multiple frames
        for i in range(5):
            system.emit(100, 100, (255, 255, 255), count=1, spread=50, lifetime=10.0)
            system.update(0.1)
        
        # Should have accumulated particles
        assert len(system.particles) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
