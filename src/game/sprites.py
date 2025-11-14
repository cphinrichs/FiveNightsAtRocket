"""
Five Nights at Rocket - Sprite Generation
Functions for generating sprite graphics for game entities
"""

import pygame
from typing import Tuple
from enums import Direction
from constants import *


def create_player_sprite(width: int, height: int, direction: Direction) -> pygame.Surface:
    """
    Generate a sprite for the player character.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        direction: Direction the player is facing
        
    Returns:
        pygame.Surface with the player sprite
    """
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    color = (50, 150, 220)
    
    # Body
    pygame.draw.rect(sprite, color, (0, 0, width, height), border_radius=5)
    pygame.draw.rect(sprite, (30, 100, 180), (0, 0, width, height), 3, border_radius=5)
    
    # Eyes
    center_x = width // 2
    center_y = height // 2
    
    if direction in [Direction.UP, Direction.DOWN]:
        eye_offset = 8
        pygame.draw.circle(sprite, WHITE, (center_x - eye_offset, center_y - 5), 5)
        pygame.draw.circle(sprite, WHITE, (center_x + eye_offset, center_y - 5), 5)
        pygame.draw.circle(sprite, BLACK, (center_x - eye_offset, center_y - 5), 3)
        pygame.draw.circle(sprite, BLACK, (center_x + eye_offset, center_y - 5), 3)
    else:
        eye_x = center_x + (10 if direction == Direction.RIGHT else -10)
        pygame.draw.circle(sprite, WHITE, (eye_x, center_y - 5), 5)
        pygame.draw.circle(sprite, BLACK, (eye_x, center_y - 5), 3)
    
    return sprite


def create_enemy_sprite(width: int, height: int, color: Tuple[int, int, int], state: str) -> pygame.Surface:
    """
    Generate a sprite for an enemy.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        color: Base color of the enemy
        state: Current state of the enemy (affects appearance)
        
    Returns:
        pygame.Surface with the enemy sprite
    """
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Body with gradient effect
    pygame.draw.rect(sprite, color, (0, 0, width, height), border_radius=5)
    
    # Darker outline
    darker_color = tuple(max(0, c - 50) for c in color)
    pygame.draw.rect(sprite, darker_color, (0, 0, width, height), 3, border_radius=5)
    
    # Eyes based on state
    center_x = width // 2
    center_y = height // 2
    
    if state in ["chasing"]:
        pygame.draw.circle(sprite, RED, (center_x - 8, center_y - 5), 6)
        pygame.draw.circle(sprite, RED, (center_x + 8, center_y - 5), 6)
        pygame.draw.circle(sprite, (255, 100, 100), (center_x - 8, center_y - 5), 3)
        pygame.draw.circle(sprite, (255, 100, 100), (center_x + 8, center_y - 5), 3)
    elif state in ["eating", "at_desk", "idle"]:
        pygame.draw.circle(sprite, WHITE, (center_x - 8, center_y - 5), 6)
        pygame.draw.circle(sprite, WHITE, (center_x + 8, center_y - 5), 6)
        pygame.draw.circle(sprite, YELLOW, (center_x - 8, center_y - 5), 3)
        pygame.draw.circle(sprite, YELLOW, (center_x + 8, center_y - 5), 3)
    else:
        pygame.draw.circle(sprite, ORANGE, (center_x - 8, center_y - 5), 6)
        pygame.draw.circle(sprite, ORANGE, (center_x + 8, center_y - 5), 6)
        pygame.draw.circle(sprite, YELLOW, (center_x - 8, center_y - 5), 3)
        pygame.draw.circle(sprite, YELLOW, (center_x + 8, center_y - 5), 3)
    
    # State indicator
    if state == "chasing":
        pygame.draw.circle(sprite, RED, (width - 5, 5), 5)
    elif state in ["eating", "at_desk"]:
        pygame.draw.circle(sprite, GREEN, (width - 5, 5), 5)
    elif state == "idle":
        pygame.draw.circle(sprite, YELLOW, (width - 5, 5), 5)
    
    return sprite


def create_interactable_sprite(width: int, height: int, color: Tuple[int, int, int], 
                               type_name: str) -> pygame.Surface:
    """
    Generate a sprite for an interactable object.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        color: Base color of the object
        type_name: Name of the object type (for label)
        
    Returns:
        pygame.Surface with the interactable sprite
    """
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    pygame.draw.rect(sprite, color, (0, 0, width, height), border_radius=3)
    pygame.draw.rect(sprite, BLACK, (0, 0, width, height), 2, border_radius=3)
    
    # Icon/label
    font = pygame.font.Font(None, 16)
    label = type_name[:8]
    text_surf = font.render(label, True, WHITE)
    text_rect = text_surf.get_rect(center=(width // 2, height // 2))
    sprite.blit(text_surf, text_rect)
    
    return sprite


def create_name_tag(name: str, color: Tuple[int, int, int] = WHITE) -> pygame.Surface:
    """
    Generate a name tag sprite.
    
    Args:
        name: Name to display on the tag
        color: Text color
        
    Returns:
        pygame.Surface with the name tag
    """
    font = pygame.font.Font(None, 20 if len(name) < 10 else 18)
    text_surf = font.render(name, True, color)
    
    # Create background
    bg_rect = text_surf.get_rect()
    bg_rect.inflate_ip(8, 4)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect(), border_radius=3)
    
    # Blit text onto background
    text_rect = text_surf.get_rect(center=(bg_rect.width // 2, bg_rect.height // 2))
    bg_surface.blit(text_surf, text_rect)
    
    return bg_surface
