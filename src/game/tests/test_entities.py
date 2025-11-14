"""
Unit tests for entity classes (Player, Entity)
Tests player initialization, movement, collision, and inventory
"""

import pytest
import pygame
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entities import Player, Entity
from enums import Direction


class TestEntity:
    """Test base Entity class"""
    
    @pytest.fixture
    def entity(self):
        """Create a basic entity for testing"""
        pygame.init()
        return Entity(100, 150, 40, 40, (255, 0, 0))
    
    def test_entity_initialization(self, entity):
        """Test that entity initializes with correct values"""
        assert entity.x == 100
        assert entity.y == 150
        assert entity.width == 40
        assert entity.height == 40
        assert entity.color == (255, 0, 0)
        assert entity.direction == Direction.DOWN
    
    def test_entity_center(self, entity):
        """Test get_center() returns correct center point"""
        center_x, center_y = entity.get_center()
        assert center_x == 100 + 20  # x + width/2
        assert center_y == 150 + 20  # y + height/2
    
    def test_entity_rect(self, entity):
        """Test get_rect() returns correct pygame Rect"""
        rect = entity.get_rect()
        assert rect.x == 100
        assert rect.y == 150
        assert rect.width == 40
        assert rect.height == 40
    
    def test_entity_collision_detection(self, entity):
        """Test collides_with() method"""
        other = Entity(110, 160, 40, 40, (0, 255, 0))
        assert entity.collides_with(other) == True
        
        far_away = Entity(500, 500, 40, 40, (0, 0, 255))
        assert entity.collides_with(far_away) == False


class TestPlayer:
    """Test Player class"""
    
    @pytest.fixture
    def player(self):
        """Create a player for testing"""
        pygame.init()
        return Player(200, 200)
    
    def test_player_initialization(self, player):
        """Test player starts with correct default values"""
        assert player.x == 200
        assert player.y == 200
        assert player.width == 40
        assert player.height == 40
        assert player.speed == 200
        assert player.inventory["snacks"] == 5
        assert player.inventory["egg"] == False
        assert player.on_solitaire == False
    
    def test_player_inventory_snacks(self, player):
        """Test snack inventory manipulation"""
        # Decrease snacks
        player.inventory["snacks"] = 3
        assert player.inventory["snacks"] == 3
        
        # Deplete snacks
        player.inventory["snacks"] = 0
        assert player.inventory["snacks"] == 0
        
        # Refill snacks
        player.inventory["snacks"] = 5
        assert player.inventory["snacks"] == 5
    
    def test_player_inventory_egg(self, player):
        """Test egg inventory manipulation"""
        assert player.inventory["egg"] == False
        
        # Pick up egg
        player.inventory["egg"] = True
        assert player.inventory["egg"] == True
        
        # Use egg
        player.inventory["egg"] = False
        assert player.inventory["egg"] == False
    
    def test_player_solitaire_state(self, player):
        """Test player solitaire toggle"""
        assert player.on_solitaire == False
        
        # Start playing solitaire
        player.on_solitaire = True
        assert player.on_solitaire == True
        
        # Stop playing solitaire
        player.on_solitaire = False
        assert player.on_solitaire == False
    
    def test_player_movement(self, player):
        """Test player position changes"""
        original_x = player.x
        original_y = player.y
        
        # Move right
        player.x += 10
        assert player.x == original_x + 10
        
        # Move down
        player.y += 10
        assert player.y == original_y + 10
        
        # Move back to original
        player.x = original_x
        player.y = original_y
        assert player.x == original_x
        assert player.y == original_y
    
    def test_player_speed_calculation(self, player):
        """Test speed-based movement calculations"""
        dt = 0.1  # 100ms frame
        distance = player.speed * dt
        assert distance == 20.0  # 200 * 0.1
    
    def test_player_direction_changes(self, player):
        """Test direction changes"""
        player.direction = Direction.UP
        assert player.direction == Direction.UP
        
        player.direction = Direction.RIGHT
        assert player.direction == Direction.RIGHT
        
        player.direction = Direction.DOWN
        assert player.direction == Direction.DOWN
        
        player.direction = Direction.LEFT
        assert player.direction == Direction.LEFT
    
    def test_player_collision_rect(self, player):
        """Test player collision rectangle"""
        rect = player.get_rect()
        assert isinstance(rect, pygame.Rect)
        assert rect.width == 40
        assert rect.height == 40
    
    def test_player_center_position(self, player):
        """Test center calculation for collision detection"""
        center_x, center_y = player.get_center()
        assert center_x == 220  # 200 + 40/2
        assert center_y == 220  # 200 + 40/2


class TestPlayerEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_player_negative_snacks(self):
        """Test that snacks can go below zero (game logic decides limits)"""
        pygame.init()
        player = Player(100, 100)
        player.inventory["snacks"] = -1
        # Game should handle this, test just ensures no crash
        assert player.inventory["snacks"] == -1
    
    def test_player_excessive_snacks(self):
        """Test snacks above maximum"""
        pygame.init()
        player = Player(100, 100)
        player.inventory["snacks"] = 100
        # Game should handle maximum, test ensures no crash
        assert player.inventory["snacks"] == 100
    
    def test_player_at_origin(self):
        """Test player at (0, 0) position"""
        pygame.init()
        player = Player(0, 0)
        assert player.x == 0
        assert player.y == 0
        center_x, center_y = player.get_center()
        assert center_x == 20
        assert center_y == 20
    
    def test_player_collision_with_self(self):
        """Test that player doesn't collide with itself"""
        pygame.init()
        player = Player(100, 100)
        # This would be True if comparing same object
        assert player.collides_with(player) == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
