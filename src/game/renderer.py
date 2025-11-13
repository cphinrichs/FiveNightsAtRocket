"""Rendering system for drawing all game elements."""
import pygame
from typing import Optional, TYPE_CHECKING
from config import (
    WIDTH, HEIGHT,
    COLOR_BG, COLOR_OFFICE_BG, COLOR_CAMERA_FALLBACK,
    COLOR_DOOR_CLOSED, COLOR_DOOR_OPEN,
    COLOR_TEXT, COLOR_TITLE, COLOR_GAME_OVER, COLOR_WIN, COLOR_ENEMY
)
from game_state import GameState
from camera import Camera
from assets import AssetManager

if TYPE_CHECKING:
    from enemies import EnemyManager


class Renderer:
    """Handles all rendering operations."""
    
    def __init__(self, screen: pygame.Surface, assets: AssetManager):
        self.screen = screen
        self.assets = assets
        self.enemy_manager: Optional['EnemyManager'] = None
        
    def set_enemy_manager(self, enemy_manager: 'EnemyManager'):
        """Set the enemy manager for rendering enemies."""
        self.enemy_manager = enemy_manager
        
    def render_frame(self, game_state: GameState, camera: Camera):
        """Render a complete frame."""
        self.screen.fill(COLOR_BG)
        
        if game_state.camera_active and game_state.is_playing():
            self._render_camera_view(camera)
        else:
            self._render_office_view()
            
        self._render_hud(game_state)
        
        if game_state.game_over:
            self._render_game_over()
            self._render_game_over_message(game_state)
        elif game_state.win:
            self._render_win()
            
        pygame.display.flip()
        
    def _render_camera_view(self, camera: Camera):
        """Render the camera view."""
        room_name = camera.get_current_room_name()
        room_image = self.assets.get_room_image(room_name)
        
        if room_image:
            camera.render_view(self.screen, room_image)
        else:
            # Fallback if image not loaded
            pygame.draw.rect(self.screen, COLOR_CAMERA_FALLBACK, (0, 0, WIDTH, HEIGHT))
            
        # Draw enemies in this room
        if self.enemy_manager:
            enemies_here = self.enemy_manager.get_enemies_in_room(room_name)
            if enemies_here:
                self._render_enemies_on_camera(enemies_here)
            
        # Draw camera label
        font = self.assets.get_font('large')
        txt = font.render(f"CAM: {room_name}", True, COLOR_TITLE)
        self.screen.blit(txt, (40, 40))
        
    def _render_office_view(self):
        """Render the office view."""
        pygame.draw.rect(self.screen, COLOR_OFFICE_BG, (0, 0, WIDTH, HEIGHT))
        
        # Draw office title
        font = self.assets.get_font('large')
        office_txt = font.render("OFFICE", True, COLOR_TITLE)
        self.screen.blit(office_txt, (WIDTH//2 - office_txt.get_width()//2, 40))
        
        # Draw door indicators showing if enemies are at doors
        if self.enemy_manager:
            left_enemies, right_enemies = self.enemy_manager.get_enemies_at_doors()
            self._render_door_warnings(left_enemies, right_enemies)
        
    def _render_enemies_on_camera(self, enemies):
        """Render enemy indicators on camera view."""
        font = self.assets.get_font('medium')
        y_offset = 100
        
        for enemy in enemies:
            # Draw enemy name with highlight
            txt = font.render(f"⚠ {enemy.name}", True, COLOR_ENEMY)
            bg_rect = txt.get_rect()
            bg_rect.topleft = (40, y_offset)
            bg_rect.inflate_ip(20, 10)
            
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
            pygame.draw.rect(self.screen, COLOR_ENEMY, bg_rect, 2)
            self.screen.blit(txt, (50, y_offset + 5))
            
            y_offset += 40
            
    def _render_door_warnings(self, left_enemies, right_enemies):
        """Render warnings when enemies are at doors."""
        font = self.assets.get_font('medium')
        
        # Left door warning
        if left_enemies:
            for i, enemy in enumerate(left_enemies):
                txt = font.render(f"⚠ {enemy.name}", True, COLOR_ENEMY)
                self.screen.blit(txt, (20, HEIGHT//3 + i * 30))
                
        # Right door warning
        if right_enemies:
            for i, enemy in enumerate(right_enemies):
                txt = font.render(f"{enemy.name} ⚠", True, COLOR_ENEMY)
                txt_rect = txt.get_rect()
                txt_rect.right = WIDTH - 20
                txt_rect.top = HEIGHT//3 + i * 30
                self.screen.blit(txt, txt_rect)
        
    def _render_doors(self, left_closed: bool, right_closed: bool):
        """Render door indicators."""
        door_l_color = COLOR_DOOR_CLOSED if left_closed else COLOR_DOOR_OPEN
        door_r_color = COLOR_DOOR_CLOSED if right_closed else COLOR_DOOR_OPEN
        
        pygame.draw.rect(self.screen, door_l_color, (0, HEIGHT//3, 60, HEIGHT//3))
        pygame.draw.rect(self.screen, door_r_color, (WIDTH-60, HEIGHT//3, 60, HEIGHT//3))
        
    def _render_hud(self, game_state: GameState):
        """Render HUD elements."""
        font = self.assets.get_font('medium')
        
        hud_lines = [
            f"Power: {game_state.power:05.1f}%",
            f"Camera: {'ON' if game_state.camera_active else 'OFF'} (C)",
            f"Doors: L={'CLOSED' if game_state.left_door_closed else 'OPEN'} (A) | R={'CLOSED' if game_state.right_door_closed else 'OPEN'} (D)",
            f"Time: {int(game_state.night_time)}s / {int(game_state.night_time // 60)}m",
            "Camera: LEFT/RIGHT to switch rooms"
        ]
        
        for i, line in enumerate(hud_lines):
            txt = font.render(line, True, COLOR_TEXT)
            self.screen.blit(txt, (20, HEIGHT - 30 - (len(hud_lines)-i)*28))
            
    def _render_game_over(self):
        """Render game over screen."""
        font_large = self.assets.get_font('large')
        font_med = self.assets.get_font('medium')
        
        txt = font_large.render("GAME OVER", True, COLOR_GAME_OVER)
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2 - 30))
        
    def _render_game_over_message(self, game_state: GameState):
        """Render the game over message if present."""
        if game_state.death_message:
            font = self.assets.get_font('medium')
            txt = font.render(game_state.death_message, True, COLOR_GAME_OVER)
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 + 20))
        
    def _render_win(self):
        """Render win screen."""
        font = self.assets.get_font('large')
        txt = font.render("6 AM - YOU WIN!", True, COLOR_WIN)
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))
