"""Free roam mode manager - allows player to walk around the office."""
import pygame
import random
import math
from typing import List, Tuple, Optional, TYPE_CHECKING
from config import WIDTH, HEIGHT

if TYPE_CHECKING:
    from enemies import EnemyManager


class FreeRoamPlayer:
    """Player character in free roam mode."""
    
    def __init__(self, x: int, y: int):
        self.x = float(x)
        self.y = float(y)
        self.size = 40
        self.speed = 4
        self.rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        
    def move(self, dx: float, dy: float, walls: List[pygame.Rect], furniture: List[pygame.Rect]) -> bool:
        """
        Move player with collision detection.
        Returns True if player moved, False if blocked.
        """
        old_x, old_y = self.x, self.y
        moved = False
        
        # Try X movement
        if dx != 0:
            self.x += dx
            self.rect.x = int(self.x)
            
            # Check collisions
            collision = False
            for wall in walls:
                if self.rect.colliderect(wall):
                    collision = True
                    break
            
            if not collision:
                for furn in furniture:
                    if self.rect.colliderect(furn):
                        collision = True
                        break
            
            if collision:
                self.x = old_x
                self.rect.x = int(self.x)
            else:
                moved = True
        
        # Try Y movement
        if dy != 0:
            self.y += dy
            self.rect.y = int(self.y)
            
            # Check collisions
            collision = False
            for wall in walls:
                if self.rect.colliderect(wall):
                    collision = True
                    break
            
            if not collision:
                for furn in furniture:
                    if self.rect.colliderect(furn):
                        collision = True
                        break
            
            if collision:
                self.y = old_y
                self.rect.y = int(self.y)
            else:
                moved = True
        
        return moved
        
    def teleport_to(self, x: int, y: int):
        """Teleport player to a new position."""
        self.x = float(x)
        self.y = float(y)
        self.rect.topleft = (int(self.x), int(self.y))


class RoomData:
    """Data for a single room in free roam mode."""
    
    def __init__(self, name: str, floor_color: Tuple[int, int, int], 
                 walls: List[pygame.Rect], furniture: List[dict], 
                 transitions: List[Tuple[pygame.Rect, int, int, int]]):
        self.name = name
        self.floor_color = floor_color
        self.walls = walls
        self.furniture = furniture
        self.transitions = transitions


class FreeRoamManager:
    """Manages free roam mode gameplay."""
    
    def __init__(self):
        self.player = FreeRoamPlayer(150, 50)
        self.current_room_id = 0
        self.rooms = self._create_rooms()
        
    def _create_rooms(self) -> dict:
        """Create room definitions for free roam."""
        # Define colors
        CARPET_BLUE = (30, 35, 45)
        DARK_FLOOR = (25, 25, 28)
        DESK_BROWN = (55, 45, 35)
        OFFICE_GRAY = (50, 55, 60)
        RUSTY_BROWN = (60, 50, 40)
        DIM_YELLOW = (80, 80, 50)
        SICKLY_GREEN = (40, 60, 40)
        WALL_DARK = (45, 45, 50)
        
        rooms = {}
        
        # Office Room
        rooms[0] = RoomData(
            name="Office",
            floor_color=CARPET_BLUE,
            walls=[
                pygame.Rect(0, 0, WIDTH, 20),  # Top
                pygame.Rect(0, 0, 20, HEIGHT),  # Left
                pygame.Rect(0, HEIGHT - 20, WIDTH, 20),  # Bottom
                pygame.Rect(WIDTH - 20, 0, 20, HEIGHT // 2 - 60),  # Right top
                pygame.Rect(WIDTH - 20, HEIGHT // 2 + 60, 20, HEIGHT // 2 - 60),  # Right bottom
            ],
            furniture=[
                {'rect': pygame.Rect(80, 100, 200, 50), 'color': DESK_BROWN, 'type': 'desk'},
                {'rect': pygame.Rect(320, 100, 200, 50), 'color': DESK_BROWN, 'type': 'desk'},
                {'rect': pygame.Rect(80, 180, 200, 50), 'color': DESK_BROWN, 'type': 'desk'},
                {'rect': pygame.Rect(320, 180, 200, 50), 'color': DESK_BROWN, 'type': 'desk'},
                {'rect': pygame.Rect(80, 260, 200, 50), 'color': DESK_BROWN, 'type': 'desk'},
                {'rect': pygame.Rect(320, 260, 200, 50), 'color': DESK_BROWN, 'type': 'desk'},
                {'rect': pygame.Rect(150, 400, 150, 80), 'color': RUSTY_BROWN, 'type': 'desk', 'label': 'Manager Desk'},
            ],
            transitions=[
                (pygame.Rect(WIDTH - 20, HEIGHT // 2 - 60, 20, 120), 1, 40, HEIGHT // 2),
            ]
        )
        
        # Hallway
        rooms[1] = RoomData(
            name="Hallway",
            floor_color=DARK_FLOOR,
            walls=[
                pygame.Rect(0, 0, WIDTH, 20),  # Top
                pygame.Rect(0, 0, 20, HEIGHT // 2 - 60),  # Left top
                pygame.Rect(0, HEIGHT // 2 + 60, 20, HEIGHT // 2 - 60),  # Left bottom
                pygame.Rect(0, HEIGHT - 20, WIDTH, 20),  # Bottom
                pygame.Rect(WIDTH - 20, 0, 20, HEIGHT // 2 - 60),  # Right top
                pygame.Rect(WIDTH - 20, HEIGHT // 2 + 60, 20, HEIGHT // 2 - 60),  # Right bottom
            ],
            furniture=[
                {'rect': pygame.Rect(50, 50, 35, 80), 'color': OFFICE_GRAY, 'type': 'cabinet'},
                {'rect': pygame.Rect(50, 150, 35, 80), 'color': OFFICE_GRAY, 'type': 'cabinet'},
                {'rect': pygame.Rect(WIDTH - 85, 50, 35, 80), 'color': OFFICE_GRAY, 'type': 'cabinet'},
                {'rect': pygame.Rect(WIDTH - 85, 150, 35, 80), 'color': OFFICE_GRAY, 'type': 'cabinet'},
            ],
            transitions=[
                (pygame.Rect(0, HEIGHT // 2 - 60, 20, 120), 0, WIDTH - 60, HEIGHT // 2),
                (pygame.Rect(WIDTH - 20, HEIGHT // 2 - 60, 20, 120), 2, 40, HEIGHT // 2),
            ]
        )
        
        # Break Room
        rooms[2] = RoomData(
            name="Break Room",
            floor_color=CARPET_BLUE,
            walls=[
                pygame.Rect(0, 0, WIDTH, 20),  # Top
                pygame.Rect(0, 0, 20, HEIGHT // 2 - 60),  # Left top
                pygame.Rect(0, HEIGHT // 2 + 60, 20, HEIGHT // 2 - 60),  # Left bottom
                pygame.Rect(0, HEIGHT - 20, WIDTH, 20),  # Bottom
                pygame.Rect(WIDTH - 20, 0, 20, HEIGHT),  # Right
            ],
            furniture=[
                {'rect': pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 75, 200, 150), 'color': DESK_BROWN, 'type': 'table'},
                {'rect': pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 - 30, 40, 40), 'color': RUSTY_BROWN, 'type': 'supply', 'label': 'Supply 1'},
                {'rect': pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 30, 40, 40), 'color': DIM_YELLOW, 'type': 'supply', 'label': 'Supply 2'},
                {'rect': pygame.Rect(WIDTH // 2 + 40, HEIGHT // 2 - 30, 40, 40), 'color': SICKLY_GREEN, 'type': 'supply', 'label': 'Supply 3'},
                {'rect': pygame.Rect(50, 50, 60, 100), 'color': WALL_DARK, 'type': 'vending'},
            ],
            transitions=[
                (pygame.Rect(0, HEIGHT // 2 - 60, 20, 120), 1, WIDTH - 60, HEIGHT // 2),
            ]
        )
        
        return rooms
    
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> Tuple[bool, Optional[str]]:
        """
        Update free roam logic.
        Returns (player_moved, interaction) where interaction is 'supply' or 'exit' if applicable.
        """
        dx, dy = 0, 0
        
        # Movement input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.player.speed
        
        # Move player
        room = self.rooms[self.current_room_id]
        furniture_rects = [f['rect'] for f in room.furniture]
        player_moved = self.player.move(dx, dy, room.walls, furniture_rects)
        
        # Check room transitions
        for trans_rect, dest_room, spawn_x, spawn_y in room.transitions:
            if self.player.rect.colliderect(trans_rect):
                self.current_room_id = dest_room
                self.player.teleport_to(spawn_x, spawn_y)
                break
        
        # Check for interactions (supply boxes)
        interaction = None
        if keys[pygame.K_e] or keys[pygame.K_SPACE]:
            for furn in room.furniture:
                if furn.get('type') == 'supply':
                    inflated = furn['rect'].inflate(50, 50)
                    if self.player.rect.colliderect(inflated):
                        interaction = 'supply'
                        break
        
        return player_moved, interaction
    
    def reset_to_office(self):
        """Reset player to office starting position."""
        self.current_room_id = 0
        self.player.teleport_to(150, 50)
    
    def get_current_room(self) -> RoomData:
        """Get the current room data."""
        return self.rooms[self.current_room_id]
    
    def get_player_position(self) -> Tuple[int, int]:
        """Get player's current position."""
        return (int(self.player.x), int(self.player.y))
    
    def get_player_rect(self) -> pygame.Rect:
        """Get player's collision rect."""
        return self.player.rect
    
    def is_player_in_room(self, room_id: int) -> bool:
        """Check if player is in a specific room."""
        return self.current_room_id == room_id
