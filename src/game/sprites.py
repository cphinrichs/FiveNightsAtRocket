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
    Generate a sprite for the player character using Brunton.png image.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        direction: Direction the player is facing
        
    Returns:
        pygame.Surface with the player sprite
    """
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    try:
        # Try to load Brunton.png image (relative path for pygbag)
        try:
            player_image = pygame.image.load('images/Brunton.png').convert_alpha()
        except:
            # Fallback to absolute path for desktop
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, 'images', 'Brunton.png')
            player_image = pygame.image.load(image_path).convert_alpha()
        
        # Scale the image to fit the sprite dimensions while maintaining aspect ratio
        # Use 2x resolution for better quality, then scale down with smoothscale
        image_rect = player_image.get_rect()
        scale_factor = min(width / image_rect.width, height / image_rect.height) * 2.0  # 2x resolution
        new_width = int(image_rect.width * scale_factor)
        new_height = int(image_rect.height * scale_factor)
        
        # Use smoothscale for high-quality scaling
        scaled_image = pygame.transform.smoothscale(player_image, (new_width, new_height))
        
        # Flip the image based on direction
        if direction == Direction.LEFT:
            scaled_image = pygame.transform.flip(scaled_image, True, False)
        # Keep image upright for all other directions (UP, DOWN, RIGHT)
        
        # Scale down to final size with smoothscale for crisp rendering
        final_width = int(new_width / 2)
        final_height = int(new_height / 2)
        final_image = pygame.transform.smoothscale(scaled_image, (final_width, final_height))
        
        # Center the image on the sprite surface
        image_x = (width - final_width) // 2
        image_y = (height - final_height) // 2
        sprite.blit(final_image, (image_x, image_y))
        
    except Exception as e:
        # Fallback to simple colored sprite if image fails to load
        print(f"Warning: Could not load Brunton.png, using fallback sprite: {e}")
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


def create_enemy_sprite(width: int, height: int, color: Tuple[int, int, int], state: str, 
                       name: str = "", intern_id: int = 1) -> pygame.Surface:
    """
    Generate a sprite for an enemy using their character image.
    
    Args:
        width: Width of the sprite
        height: Height of the sprite
        color: Base color of the enemy (used as fallback)
        state: Current state of the enemy (affects appearance)
        name: Name of the enemy (used to load appropriate image)
        intern_id: For NextGenIntern enemies, which intern image to use (1, 2, or 3)
        
    Returns:
        pygame.Surface with the enemy sprite
    """
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Map enemy names to image files
    image_map = {
        "Jo-nathan": "Jo-nathan.png",
        "Jeromathy": "Jeromathy.png",
        "Angellica": "Angellica.png",
        "Runnit": "runnit.png",
        "NextGen Intern": f"NextGen_intern_{intern_id}.png"
    }
    
    try:
        # Try to load the character image
        image_file = image_map.get(name, None)
        
        if image_file:
            try:
                # Try relative path first (pygbag)
                enemy_image = pygame.image.load(f'images/{image_file}').convert_alpha()
            except:
                # Fallback to absolute path (desktop)
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(current_dir, 'images', image_file)
                enemy_image = pygame.image.load(image_path).convert_alpha()
            
            # Scale the image to fit the sprite dimensions while maintaining aspect ratio
            # Use 2x resolution for better quality, then scale down with smoothscale
            image_rect = enemy_image.get_rect()
            scale_factor = min(width / image_rect.width, height / image_rect.height) * 2.0  # 2x resolution
            new_width = int(image_rect.width * scale_factor)
            new_height = int(image_rect.height * scale_factor)
            
            # Use smoothscale for high-quality scaling
            scaled_image = pygame.transform.smoothscale(enemy_image, (new_width, new_height))
            
            # Scale down to final size with smoothscale for crisp rendering
            final_width = int(new_width / 2)
            final_height = int(new_height / 2)
            final_image = pygame.transform.smoothscale(scaled_image, (final_width, final_height))
            
            # Center the image on the sprite surface
            image_x = (width - final_width) // 2
            image_y = (height - final_height) // 2
            sprite.blit(final_image, (image_x, image_y))
            
            # Add state indicator overlay
            if state == "chasing":
                # Red glow effect for chasing
                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.circle(overlay, (255, 0, 0, 80), (width - 10, 10), 8)
                sprite.blit(overlay, (0, 0))
            elif state in ["eating", "at_desk"]:
                # Green indicator for calm states
                pygame.draw.circle(sprite, (0, 255, 0, 180), (width - 5, 5), 5)
            elif state in ["idle", "patrolling", "returning_to_desk"]:
                # Yellow indicator for idle/patrolling/returning states
                pygame.draw.circle(sprite, (255, 255, 0, 180), (width - 5, 5), 5)
            elif state in ["going_for_snack", "returning"]:
                # Orange indicator for interns on the move
                pygame.draw.circle(sprite, (255, 165, 0, 180), (width - 5, 5), 5)
            else:
                # Default: blue indicator for any other state
                pygame.draw.circle(sprite, (100, 150, 255, 180), (width - 5, 5), 5)
            
            return sprite
    except Exception as e:
        # Fallback to colored sprite if image fails to load
        print(f"Warning: Could not load {name} image, using fallback sprite: {e}")
        pass
    
    # Fallback: Original colored sprite
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
