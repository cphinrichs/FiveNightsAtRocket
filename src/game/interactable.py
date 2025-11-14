"""
Five Nights at Rocket - Interactable Objects
Contains the Interactable class for items the player can interact with
"""

import pygame
from typing import Tuple, Optional
from enums import InteractableType, GameState
from constants import *
from sprites import create_interactable_sprite


class Interactable:
    """
    Objects that the player can interact with (refrigerators, cabinets, etc.).
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 obj_type: InteractableType, color: Tuple[int, int, int]):
        """
        Initialize an interactable object.
        
        Args:
            x: X position
            y: Y position
            width: Width of the object
            height: Height of the object
            obj_type: Type of interactable
            color: RGB color tuple
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obj_type
        self.color = color
        self.cooldown = 0
        self.label: Optional[str] = None  # Custom label for desks
        self.sprite = None  # Will be generated once
        
    def get_rect(self) -> pygame.Rect:
        """Get the object's collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def can_interact(self, player) -> bool:
        """
        Check if the player can interact with this object.
        
        Args:
            player: Player object
            
        Returns:
            True if player can interact, False otherwise
        """
        player_rect = player.get_rect()
        obj_rect = self.get_rect()
        
        # Larger interaction range for camera and laptop (30 pixels instead of 20)
        if self.type in [InteractableType.CAMERA, InteractableType.LAPTOP]:
            inflate_amount = 30
        else:
            inflate_amount = 20
            
        return player_rect.colliderect(obj_rect.inflate(inflate_amount, inflate_amount)) and self.cooldown <= 0
    
    def interact(self, player, game) -> str:
        """
        Handle interaction with the object.
        
        Args:
            player: Player object
            game: Game instance
            
        Returns:
            Message to display to the player
        """
        if self.type == InteractableType.REFRIGERATOR:
            # Refrigerator can always give an egg if player doesn't have one
            # Check if player has egg (could be True or False)
            has_egg = player.inventory.get("egg", False)
            if not has_egg or has_egg == False:
                player.inventory["egg"] = True
                self.cooldown = 0.5  # Short cooldown for refrigerator
                game.play_sound('pickup')
                return "Got an egg!"
            else:
                return "Already have an egg"
        
        # All other interactables have a cooldown
        self.cooldown = 1.0  # 1 second cooldown
        
        if self.type == InteractableType.CABINET:
            player.inventory["snacks"] = min(5, player.inventory["snacks"] + 1)
            game.play_sound('restock')
            return f"Refilled snacks! ({player.inventory['snacks']}/5)"
        
        elif self.type == InteractableType.CAMERA:
            game.switch_state(GameState.CAMERA)
            # Camera sound is played in switch_state
            return "Opening cameras..."
        
        # Laptop and Desk are handled elsewhere (Y/C keys for laptop, desks are non-interactable)
        
        return ""
    
    def update(self, dt: float):
        """
        Update the interactable (cooldown timer).
        
        Args:
            dt: Delta time (seconds)
        """
        if self.cooldown > 0:
            self.cooldown -= dt
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Draw the interactable to the screen.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        rect = self.get_rect()
        screen_x = rect.x - camera_offset[0]
        screen_y = rect.y - camera_offset[1]
        
        # Generate sprite once if not already created
        if self.sprite is None:
            display_label = self.label if self.label else self.type.value
            self.sprite = create_interactable_sprite(self.width, self.height, 
                                                     self.color, display_label)
        
        surface.blit(self.sprite, (screen_x, screen_y))
