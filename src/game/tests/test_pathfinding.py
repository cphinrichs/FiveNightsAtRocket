"""
Unit tests for pathfinding algorithms
Tests simple_pathfind function
"""

import pytest
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathfinding import simple_pathfind


class TestPathfinding:
    """Test simple pathfinding algorithm"""
    
    @pytest.fixture
    def empty_room(self):
        """Create an empty room with no walls"""
        pygame.init()
        return pygame.Rect(0, 0, 800, 600)
    
    def test_pathfind_right(self, empty_room):
        """Test pathfinding toward right"""
        dx, dy = simple_pathfind((100, 100), (200, 100), [], empty_room)
        assert dx > 0  # Moving right
        assert abs(dy) < 0.1  # Minimal vertical movement
    
    def test_pathfind_left(self, empty_room):
        """Test pathfinding toward left"""
        dx, dy = simple_pathfind((200, 100), (100, 100), [], empty_room)
        assert dx < 0  # Moving left
        assert abs(dy) < 0.1  # Minimal vertical movement
    
    def test_pathfind_up(self, empty_room):
        """Test pathfinding toward up"""
        dx, dy = simple_pathfind((100, 200), (100, 100), [], empty_room)
        assert abs(dx) < 0.1  # Minimal horizontal movement
        assert dy < 0  # Moving up
    
    def test_pathfind_down(self, empty_room):
        """Test pathfinding toward down"""
        dx, dy = simple_pathfind((100, 100), (100, 200), [], empty_room)
        assert abs(dx) < 0.1  # Minimal horizontal movement
        assert dy > 0  # Moving down
    
    def test_pathfind_diagonal_horizontal_priority(self, empty_room):
        """Test diagonal movement prioritizes larger axis difference"""
        # More horizontal than vertical difference
        dx, dy = simple_pathfind((100, 100), (300, 150), [], empty_room)
        # Should move right since horizontal diff (200) > vertical diff (50)
        assert abs(dx) > 0
    
    def test_pathfind_diagonal_vertical_priority(self, empty_room):
        """Test diagonal movement prioritizes vertical when larger"""
        # More vertical than horizontal difference
        dx, dy = simple_pathfind((100, 100), (150, 300), [], empty_room)
        # Should move down since vertical diff (200) > horizontal diff (50)
        assert abs(dy) > 0
    
    def test_pathfind_same_position(self, empty_room):
        """Test pathfinding when at same position"""
        dx, dy = simple_pathfind((100, 100), (100, 100), [], empty_room)
        # Should return no movement
        assert dx == 0
        assert dy == 0
    
    def test_pathfind_close_positions(self, empty_room):
        """Test pathfinding with very close positions"""
        dx, dy = simple_pathfind((100, 100), (101, 101), [], empty_room)
        # Should return zero since within threshold
        assert dx == 0 and dy == 0
    
    def test_pathfind_normalized_direction(self, empty_room):
        """Test that pathfind returns normalized direction"""
        dx, dy = simple_pathfind((0, 300), (100, 300), [], empty_room)
        # Direction should be normalized
        magnitude = (dx**2 + dy**2)**0.5
        assert 0.9 <= magnitude <= 1.1  # Approximately normalized
    
    def test_pathfind_all_directions(self, empty_room):
        """Test pathfinding in all 4 cardinal directions"""
        center = (400, 300)
        
        # Test cardinal directions
        directions = [
            ((600, 300), "right"),
            ((200, 300), "left"),
            ((400, 100), "up"),
            ((400, 500), "down"),
        ]
        
        for target, direction in directions:
            dx, dy = simple_pathfind(center, target, [], empty_room)
            # Verify movement is in correct general direction
            if direction == "right":
                assert dx > 0
            elif direction == "left":
                assert dx < 0
            elif direction == "up":
                assert dy < 0
            elif direction == "down":
                assert dy > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
