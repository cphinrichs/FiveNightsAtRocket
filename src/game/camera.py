"""Camera system for viewing different rooms."""
import pygame
from typing import Optional
from config import ROOMS, WIDTH, HEIGHT, CAMERA_ZOOM


class Camera:
    """Manages camera viewing, panning, and room switching."""
    
    def __init__(self):
        self.current_room_index = 0
        self.pan_x = 0.0
        self.pan_velocity = 60.0  # pixels per second
        self.pan_direction = 1  # 1 = right, -1 = left
        
    def update(self, dt: float, room_image: Optional[pygame.Surface]):
        """Update camera panning."""
        if not room_image:
            return
            
        img_w, img_h = room_image.get_size()
        
        # Apply zoom factor
        zoomed_w = int(img_w * CAMERA_ZOOM)
        zoomed_h = int(img_h * CAMERA_ZOOM)
        
        # Account for scaling to HEIGHT
        if zoomed_h != HEIGHT:
            scale = HEIGHT / zoomed_h
            effective_w = int(zoomed_w * scale)
        else:
            effective_w = zoomed_w
            
        max_pan = max(0, effective_w - WIDTH)
        
        # Update pan position
        self.pan_x += self.pan_direction * self.pan_velocity * dt
        
        # Reverse direction at edges
        if self.pan_x >= max_pan:
            self.pan_x = max_pan
            self.pan_direction = -1
        elif self.pan_x <= 0:
            self.pan_x = 0
            self.pan_direction = 1
            
    def switch_room(self, direction: int):
        """Switch to adjacent room. Direction: -1 for left, 1 for right."""
        new_index = self.current_room_index + direction
        
        if 0 <= new_index < len(ROOMS):
            self.current_room_index = new_index
            self.pan_x = 0.0
            self.pan_direction = 1
            
    def get_current_room_name(self) -> str:
        """Get the name of the current room."""
        return ROOMS[self.current_room_index]
        
    def render_view(self, screen: pygame.Surface, room_image: Optional[pygame.Surface]):
        """Render the camera view with zooming and panning, scaling only once for sharpness."""
        if not room_image:
            return None

        img_w, img_h = room_image.get_size()
        # Calculate the target height (display height) and width (with zoom)
        target_h = HEIGHT
        scale = (CAMERA_ZOOM * target_h) / img_h
        target_w = int(img_w * scale)

        # Scale the image once to the final size
        img_scaled = pygame.transform.smoothscale(room_image, (target_w, target_h))

        # Calculate max pan based on scaled image
        max_pan = max(0, target_w - WIDTH)
        clamped_pan = min(max(0, self.pan_x), max_pan)
        view_rect = pygame.Rect(int(clamped_pan), 0, WIDTH, target_h)
        screen.blit(img_scaled, (0, 0), view_rect)
