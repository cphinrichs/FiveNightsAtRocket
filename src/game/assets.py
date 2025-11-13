"""Asset loading and management."""
import pygame
from typing import Dict, Optional
from config import ROOM_IMAGES, ROOMS


class AssetManager:
    """Manages loading and storage of game assets."""
    
    def __init__(self):
        self.room_images: Dict[str, Optional[pygame.Surface]] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
    def load_all(self):
        """Load all game assets."""
        self._load_room_images()
        self._load_fonts()
        
    def _load_room_images(self):
        """Load images for each room."""
        for room, path in ROOM_IMAGES.items():
            try:
                self.room_images[room] = pygame.image.load(path).convert()
                print(f"[INFO] Loaded image for {room}: {path}")
            except Exception as e:
                print(f"[ERROR] Could not load image for {room} at {path}: {e}")
                self.room_images[room] = None
                
    def _load_fonts(self):
        """Load fonts for UI."""
        self.fonts['small'] = pygame.font.Font(None, 24)
        self.fonts['medium'] = pygame.font.Font(None, 32)
        self.fonts['large'] = pygame.font.Font(None, 64)
        
    def get_room_image(self, room: str) -> Optional[pygame.Surface]:
        """Get the image for a specific room."""
        return self.room_images.get(room)
        
    def get_font(self, size: str) -> pygame.font.Font:
        """Get a font by size name."""
        return self.fonts.get(size, self.fonts['medium'])
