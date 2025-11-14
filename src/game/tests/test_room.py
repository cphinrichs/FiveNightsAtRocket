"""
Unit tests for Room class
Tests room boundaries, walls, and collision detection
"""

import pytest
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from room import Room
from enums import RoomType


class TestRoom:
    """Test Room class"""
    
    @pytest.fixture
    def office_room(self):
        """Create a standard office room for testing"""
        pygame.init()
        return Room(RoomType.OFFICE, 0, 0, 600, 600)
    
    def test_room_initialization(self, office_room):
        """Test room initializes with correct properties"""
        assert office_room.type == RoomType.OFFICE  # 'type' not 'room_type'
        assert office_room.x == 0
        assert office_room.y == 0
        assert office_room.width == 600
        assert office_room.height == 600
        assert isinstance(office_room.walls, list)
        assert isinstance(office_room.interactables, list)
    
    def test_room_boundaries(self, office_room):
        """Test room boundary properties"""
        # Room has defined boundaries
        assert office_room.x == 0
        assert office_room.y == 0
        assert office_room.width == 600
        assert office_room.height == 600
        
        # Can create rect from room bounds
        room_rect = pygame.Rect(office_room.x, office_room.y, office_room.width, office_room.height)
        assert room_rect.width == 600
        assert room_rect.height == 600
    
    def test_walls_are_rects(self, office_room):
        """Test walls are pygame Rects"""
        # Manually add a wall rect
        wall = pygame.Rect(10, 10, 100, 20)
        office_room.walls.append(wall)
        
        assert len(office_room.walls) >= 1
        
        # Check wall is a Rect
        added_wall = office_room.walls[-1]
        assert isinstance(added_wall, pygame.Rect)
        assert added_wall.x == 10
        assert added_wall.y == 10
        assert added_wall.width == 100
        assert added_wall.height == 20
    
    def test_add_multiple_walls(self, office_room):
        """Test adding multiple wall rects"""
        initial_count = len(office_room.walls)
        office_room.walls.append(pygame.Rect(0, 0, 50, 50))
        office_room.walls.append(pygame.Rect(100, 100, 50, 50))
        office_room.walls.append(pygame.Rect(200, 200, 50, 50))
        
        assert len(office_room.walls) == initial_count + 3
    
    def test_room_with_doorway(self):
        """Test room with doorway walls"""
        pygame.init()
        room = Room(RoomType.CLASSROOM, 0, 0, 600, 600)
        initial_walls = len(room.walls)
        
        # Add walls with doorway
        room.add_walls_with_doorway(
            wall_side="top",
            doorway_start=250,
            doorway_end=350
        )
        
        # Should have added walls on both sides of doorway
        assert len(room.walls) > initial_walls
    
    def test_collision_detection(self, office_room):
        """Test wall collision detection"""
        # Add a wall rect
        wall = pygame.Rect(100, 100, 50, 50)
        office_room.walls.append(wall)
        
        # Create test rect that overlaps
        test_rect = pygame.Rect(110, 110, 20, 20)
        
        # Check collision with walls
        colliding = False
        for wall in office_room.walls:
            if test_rect.colliderect(wall):
                colliding = True
                break
        
        assert colliding == True
    
    def test_no_collision_detection(self, office_room):
        """Test no collision when not overlapping"""
        # Add a wall rect
        wall = pygame.Rect(100, 100, 50, 50)
        office_room.walls.append(wall)
        
        # Create test rect far from wall
        test_rect = pygame.Rect(300, 300, 20, 20)
        
        # Check no collision
        colliding = False
        for wall in office_room.walls:
            if test_rect.colliderect(wall):
                colliding = True
                break
        
        assert colliding == False
    
    def test_add_interactable(self, office_room):
        """Test adding interactables to room"""
        from interactable import Interactable
        from enums import InteractableType
        
        initial_count = len(office_room.interactables)
        
        # Add interactable
        interactable = Interactable(100, 100, 50, 50, InteractableType.DESK, (100, 100, 100))
        office_room.interactables.append(interactable)
        
        assert len(office_room.interactables) == initial_count + 1
        assert isinstance(office_room.interactables[-1], Interactable)
    
    def test_room_types(self):
        """Test creating different room types"""
        pygame.init()
        
        rooms = [
            Room(RoomType.OFFICE, 0, 0, 600, 600),
            Room(RoomType.MEETING_ROOM, 625, 400, 400, 300),
            Room(RoomType.CLASSROOM, 700, 0, 600, 600),
            Room(RoomType.BREAK_ROOM, -200, 0, 400, 600),
            Room(RoomType.HALLWAY, 0, 625, 600, 200)
        ]
        
        for room in rooms:
            assert room.type in RoomType
            assert room.width > 0
            assert room.height > 0


class TestRoomCollisionSystem:
    """Test room collision system integration"""
    
    def test_multiple_walls_collision(self):
        """Test collision with multiple walls"""
        pygame.init()
        room = Room(RoomType.OFFICE, 0, 0, 600, 600)
        
        # Add multiple wall rects
        room.walls.append(pygame.Rect(100, 100, 50, 50))
        room.walls.append(pygame.Rect(200, 200, 50, 50))
        room.walls.append(pygame.Rect(300, 300, 50, 50))
        
        # Test collision with second wall
        test_rect = pygame.Rect(210, 210, 20, 20)
        
        colliding_walls = []
        for wall in room.walls:
            if test_rect.colliderect(wall):
                colliding_walls.append(wall)
        
        assert len(colliding_walls) >= 1
    
    def test_wall_boundaries(self):
        """Test wall boundary checking"""
        pygame.init()
        room = Room(RoomType.OFFICE, 0, 0, 600, 600)
        wall = pygame.Rect(100, 100, 50, 50)
        room.walls.append(wall)
        
        wall_rect = room.walls[-1]
        
        # Test exact boundaries
        assert wall_rect.left == 100
        assert wall_rect.top == 100
        assert wall_rect.width == 50
        assert wall_rect.height == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
