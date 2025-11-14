"""
Five Nights at Rocket - Room Class
Contains the Room class for managing game rooms and their layouts
"""

import pygame
from typing import List, Tuple
from enums import RoomType, InteractableType
from constants import *
from interactable import Interactable


class Room:
    """
    Represents a room in the game with walls, interactables, and connections.
    """
    
    def __init__(self, room_type: RoomType, x: int, y: int, width: int, height: int):
        """
        Initialize a room.
        
        Args:
            room_type: Type of room
            x: X position
            y: Y position
            width: Room width
            height: Room height
        """
        self.type = room_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.connections: List[Tuple[RoomType, pygame.Rect]] = []
        self.interactables: List[Interactable] = []
        self.walls: List[pygame.Rect] = []
        self.doorways: List[pygame.Rect] = []  # Track doorway locations (no walls)
        self._setup_room()
    
    def _setup_room(self):
        """Setup walls and interactables based on room type."""
        # Walls will be added with breaks for doorways in _init_game
        # For now just add interactables
        
        # Add room-specific interactables
        if self.type == RoomType.BREAK_ROOM:
            # Refrigerator (tall room, avoid doorway on right at y=150-250)
            self.interactables.append(Interactable(
                self.x + 40, self.y + 50, 60, 80, 
                InteractableType.REFRIGERATOR, (200, 200, 220)
            ))
            # Cabinet (below refrigerator, away from doorway)
            self.interactables.append(Interactable(
                self.x + 40, self.y + 280, 60, 60, 
                InteractableType.CABINET, (139, 90, 60)
            ))
        
        elif self.type == RoomType.MEETING_ROOM:
            # Camera system (moved down from y+50 to y+100 for better access)
            self.interactables.append(Interactable(
                self.x + self.width // 2 - 40, self.y + 100, 80, 60, 
                InteractableType.CAMERA, DARK_GRAY
            ))
        
        elif self.type == RoomType.CLASSROOM:
            # Laptop
            self.interactables.append(Interactable(
                self.x + self.width // 2 - 30, self.y + self.height // 2 - 20, 
                60, 40, InteractableType.LAPTOP, (50, 50, 60)
            ))
            
            # Jo-nathan's desk in bottom left corner
            jonathan_desk = Interactable(
                self.x + 40, self.y + self.height - 90, 80, 60, 
                InteractableType.DESK, (101, 67, 33)
            )
            jonathan_desk.label = "Jo-nathan"
            self.interactables.append(jonathan_desk)
        
        elif self.type == RoomType.OFFICE:
            # Jeromathy's desk with label
            desk = Interactable(
                self.x + 80, self.y + 80, 80, 60, 
                InteractableType.DESK, (101, 67, 33)
            )
            desk.label = "Jeromathy"
            self.interactables.append(desk)
        
        elif self.type == RoomType.HALLWAY:
            # Angellica's desk with label (moved down and left)
            desk = Interactable(
                self.x + 200, self.y + 150, 80, 60, 
                InteractableType.DESK, (101, 67, 33)
            )
            desk.label = "Angellica"
            self.interactables.append(desk)
    
    def add_walls_with_doorway(self, wall_side: str, doorway_start: int, doorway_end: int):
        """
        Add walls with a break for a doorway.
        
        Args:
            wall_side: Which wall ("top", "bottom", "left", "right")
            doorway_start: Start position of doorway
            doorway_end: End position of doorway
        """
        wall_thickness = 20
        
        if wall_side == "top":
            # Left part of top wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x, self.y, doorway_start, wall_thickness))
            # Right part of top wall
            if doorway_end < self.width:
                self.walls.append(pygame.Rect(self.x + doorway_end, self.y, 
                                              self.width - doorway_end, wall_thickness))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x + doorway_start, self.y, 
                                            doorway_end - doorway_start, wall_thickness))
        
        elif wall_side == "bottom":
            # Left part of bottom wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x, self.y + self.height - wall_thickness, 
                                              doorway_start, wall_thickness))
            # Right part of bottom wall
            if doorway_end < self.width:
                self.walls.append(pygame.Rect(self.x + doorway_end, self.y + self.height - wall_thickness, 
                                              self.width - doorway_end, wall_thickness))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x + doorway_start, self.y + self.height - wall_thickness, 
                                            doorway_end - doorway_start, wall_thickness))
        
        elif wall_side == "left":
            # Top part of left wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x, self.y, wall_thickness, doorway_start))
            # Bottom part of left wall
            if doorway_end < self.height:
                self.walls.append(pygame.Rect(self.x, self.y + doorway_end, 
                                              wall_thickness, self.height - doorway_end))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x, self.y + doorway_start, 
                                            wall_thickness, doorway_end - doorway_start))
        
        elif wall_side == "right":
            # Top part of right wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x + self.width - wall_thickness, self.y, 
                                              wall_thickness, doorway_start))
            # Bottom part of right wall
            if doorway_end < self.height:
                self.walls.append(pygame.Rect(self.x + self.width - wall_thickness, self.y + doorway_end, 
                                              wall_thickness, self.height - doorway_end))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x + self.width - wall_thickness, self.y + doorway_start, 
                                            wall_thickness, doorway_end - doorway_start))
    
    def add_solid_wall(self, wall_side: str):
        """
        Add a solid wall with no doorway.
        
        Args:
            wall_side: Which wall ("top", "bottom", "left", "right")
        """
        wall_thickness = 20
        
        if wall_side == "top":
            self.walls.append(pygame.Rect(self.x, self.y, self.width, wall_thickness))
        elif wall_side == "bottom":
            self.walls.append(pygame.Rect(self.x, self.y + self.height - wall_thickness, 
                                          self.width, wall_thickness))
        elif wall_side == "left":
            self.walls.append(pygame.Rect(self.x, self.y, wall_thickness, self.height))
        elif wall_side == "right":
            self.walls.append(pygame.Rect(self.x + self.width - wall_thickness, self.y, 
                                          wall_thickness, self.height))
    
    def add_door(self, to_room: RoomType, door_rect: pygame.Rect):
        """
        Add a connection to another room.
        
        Args:
            to_room: Room type to connect to
            door_rect: Rectangle representing the door
        """
        self.connections.append((to_room, door_rect))
    
    def get_rect(self) -> pygame.Rect:
        """Get the room's boundary rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Draw the room to the screen.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        # Draw floor
        floor_rect = pygame.Rect(
            self.x - camera_offset[0],
            self.y - camera_offset[1],
            self.width,
            self.height
        )
        
        # Floor color based on room type
        floor_colors = {
            RoomType.OFFICE: (80, 80, 90),
            RoomType.BREAK_ROOM: (90, 85, 75),
            RoomType.MEETING_ROOM: (75, 80, 90),
            RoomType.CLASSROOM: (85, 90, 80),
            RoomType.HALLWAY: (70, 70, 75)
        }
        floor_color = floor_colors.get(self.type, GRAY)
        pygame.draw.rect(surface, floor_color, floor_rect)
        
        # Draw walls
        for wall in self.walls:
            wall_rect = pygame.Rect(
                wall.x - camera_offset[0],
                wall.y - camera_offset[1],
                wall.width,
                wall.height
            )
            pygame.draw.rect(surface, (60, 60, 70), wall_rect)
            pygame.draw.rect(surface, (40, 40, 50), wall_rect, 2)
        
        # Draw interactables
        for interactable in self.interactables:
            interactable.draw(surface, camera_offset)
        
        # Note: Doorways are now breaks in walls, not drawn separately
        
        # Room label
        font = pygame.font.Font(None, 32)
        label_surf = font.render(self.type.value, True, WHITE)
        label_rect = label_surf.get_rect(
            centerx=self.x + self.width // 2 - camera_offset[0],
            top=self.y + 30 - camera_offset[1]
        )
        
        # Label background
        bg_rect = label_rect.inflate(20, 10)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        surface.blit(s, bg_rect)
        surface.blit(label_surf, label_rect)
