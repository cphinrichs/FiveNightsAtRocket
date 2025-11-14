"""
Five Nights at Rocket - Base Entity Classes
Contains Entity base class and Player class
"""

import pygame
import math
from typing import Tuple
from enums import Direction
from constants import *
from sprites import create_player_sprite, create_name_tag


class Entity:
    """
    Base class for all game entities (player, enemies).
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, color: Tuple[int, int, int]):
        """
        Initialize an entity.
        
        Args:
            x: Initial x position
            y: Initial y position
            width: Width of the entity
            height: Height of the entity
            color: RGB color tuple
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 150
        self.direction = Direction.DOWN
        
    def get_rect(self) -> pygame.Rect:
        """Get the entity's collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def get_center(self) -> Tuple[float, float]:
        """Get the center position of the entity."""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Draw the entity to the screen.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        rect = self.get_rect()
        screen_rect = pygame.Rect(
            rect.x - camera_offset[0],
            rect.y - camera_offset[1],
            rect.width,
            rect.height
        )
        pygame.draw.rect(surface, self.color, screen_rect)
        pygame.draw.rect(surface, BLACK, screen_rect, 2)
        
        # Draw direction indicator
        center_x = screen_rect.centerx
        center_y = screen_rect.centery
        if self.direction == Direction.UP:
            pygame.draw.polygon(surface, WHITE, [
                (center_x, center_y - 10),
                (center_x - 6, center_y),
                (center_x + 6, center_y)
            ])
        elif self.direction == Direction.DOWN:
            pygame.draw.polygon(surface, WHITE, [
                (center_x, center_y + 10),
                (center_x - 6, center_y),
                (center_x + 6, center_y)
            ])
        elif self.direction == Direction.LEFT:
            pygame.draw.polygon(surface, WHITE, [
                (center_x - 10, center_y),
                (center_x, center_y - 6),
                (center_x, center_y + 6)
            ])
        elif self.direction == Direction.RIGHT:
            pygame.draw.polygon(surface, WHITE, [
                (center_x + 10, center_y),
                (center_x, center_y - 6),
                (center_x, center_y + 6)
            ])


class Player(Entity):
    """
    The player character controlled by the user.
    """
    
    def __init__(self, x: float, y: float):
        """
        Initialize the player.
        
        Args:
            x: Initial x position
            y: Initial y position
        """
        super().__init__(x, y, 40, 40, BLUE)
        self.inventory = {"snacks": 5, "egg": False}  # Start with full snacks
        self.on_youtube = False
        self.speed = 200
        self.sprite_cache = {}  # Cache sprites for each direction
        self.name_tag = create_name_tag("Brenton")
        
    def move(self, dx: float, dy: float, dt: float):
        """
        Move the player in a direction.
        
        Args:
            dx: X direction (-1, 0, 1)
            dy: Y direction (-1, 0, 1)
            dt: Delta time (seconds)
        """
        if dx != 0 or dy != 0:
            # Normalize diagonal movement
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
            
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
            
            # Update direction
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            elif dy != 0:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Draw the player to the screen.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        rect = self.get_rect()
        screen_x = rect.x - camera_offset[0]
        screen_y = rect.y - camera_offset[1]
        
        # Get or create sprite for current direction
        dir_key = self.direction.name
        if dir_key not in self.sprite_cache:
            self.sprite_cache[dir_key] = create_player_sprite(self.width, self.height, self.direction)
        
        sprite = self.sprite_cache[dir_key]
        surface.blit(sprite, (screen_x, screen_y))
        
        # Draw name tag
        name_x = screen_x + self.width // 2 - self.name_tag.get_width() // 2
        name_y = screen_y - self.name_tag.get_height() - 5
        surface.blit(self.name_tag, (name_x, name_y))
