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
    from free_roam_manager import FreeRoamManager


class Renderer:
    """Handles all rendering operations."""
    
    def __init__(self, screen: pygame.Surface, assets: AssetManager):
        self.screen = screen
        self.assets = assets
        self.enemy_manager: Optional['EnemyManager'] = None
        self.free_roam_manager: Optional['FreeRoamManager'] = None
        
    def set_enemy_manager(self, enemy_manager: 'EnemyManager'):
        """Set the enemy manager for rendering enemies."""
        self.enemy_manager = enemy_manager
        
    def set_free_roam_manager(self, free_roam_manager: 'FreeRoamManager'):
        """Set the free roam manager for rendering free roam mode."""
        self.free_roam_manager = free_roam_manager
        
    def render_frame(self, game_state: GameState, camera: Camera):
        """Render a complete frame."""
        self.screen.fill(COLOR_BG)
        
        if game_state.free_roam_mode and game_state.is_playing():
            self._render_free_roam_view()
        elif game_state.camera_active and game_state.is_playing():
            self._render_camera_view(camera)
        else:
            self._render_office_view(game_state)
            
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
        
    def _render_office_view(self, game_state: GameState):
        """Render the office view."""
        pygame.draw.rect(self.screen, COLOR_OFFICE_BG, (0, 0, WIDTH, HEIGHT))
        
        # Draw computer screen indicator
        computer_color = (100, 200, 100) if game_state.computer_active else (50, 50, 70)
        computer_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 200)
        pygame.draw.rect(self.screen, computer_color, computer_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), computer_rect, 3)
        
        # Computer status text
        font_med = self.assets.get_font('medium')
        if game_state.computer_active:
            comp_txt = font_med.render("WORKING", True, (50, 255, 50))
            self.screen.blit(comp_txt, (WIDTH//2 - comp_txt.get_width()//2, HEIGHT//2 - 50))
        else:
            comp_txt = font_med.render("Slacking on Phone...", True, (255, 100, 100))
            self.screen.blit(comp_txt, (WIDTH//2 - comp_txt.get_width()//2, HEIGHT//2 - 50))
        
        # Draw office title
        font = self.assets.get_font('large')
        office_txt = font.render("OFFICE", True, COLOR_TITLE)
        self.screen.blit(office_txt, (WIDTH//2 - office_txt.get_width()//2, 40))
        
        # Draw door indicators showing if enemies are at doors
        if self.enemy_manager:
            left_enemies, right_enemies = self.enemy_manager.get_enemies_at_doors()
            self._render_door_warnings(left_enemies, right_enemies)
        
        # Show prompt to enter free roam
        if not game_state.camera_active:
            font_small = self.assets.get_font('medium')
            prompt = font_small.render("Press W to leave office | SPACE to toggle computer", True, (180, 180, 180))
            self.screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 200))
    
    def _render_free_roam_view(self):
        """Render the free roam mode view."""
        if not self.free_roam_manager:
            return
        
        room = self.free_roam_manager.get_current_room()
        
        # Draw floor
        self.screen.fill(room.floor_color)
        
        # Draw walls
        for wall in room.walls:
            self._draw_wall(wall)
        
        # Draw furniture
        for furn in room.furniture:
            self._draw_furniture(furn)
            
            # Show interaction prompts for supply boxes
            if furn.get('type') == 'supply' and self.free_roam_manager:
                player_rect = self.free_roam_manager.get_player_rect()
                inflated = furn['rect'].inflate(50, 50)
                if player_rect.colliderect(inflated):
                    font_small = self.assets.get_font('medium')
                    prompt = font_small.render("E/SPACE - Pick up Egg or Restock Fridge", True, (255, 255, 100))
                    prompt_bg = pygame.Surface((prompt.get_width() + 10, prompt.get_height() + 6), pygame.SRCALPHA)
                    pygame.draw.rect(prompt_bg, (0, 0, 0, 200), prompt_bg.get_rect())
                    prompt_bg.blit(prompt, (5, 3))
                    self.screen.blit(prompt_bg, (furn['rect'].centerx - prompt_bg.get_width()//2, furn['rect'].y - 40))
        
        # Draw transitions (doorways)
        for trans_rect, _, _, _ in room.transitions:
            pygame.draw.rect(self.screen, (12, 12, 15), trans_rect)
            pygame.draw.rect(self.screen, (120, 20, 20), trans_rect, 2)
        
        # Draw player
        player_x, player_y = self.free_roam_manager.get_player_position()
        player_rect = pygame.Rect(player_x, player_y, 40, 40)
        pygame.draw.rect(self.screen, (70, 130, 180), player_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), player_rect, 2)
        
        # Draw enemies in current room
        if self.enemy_manager:
            room_id = self.free_roam_manager.current_room_id
            enemies_here = self.enemy_manager.get_enemies_in_free_roam_room(room_id)
            
            for enemy in enemies_here:
                # Draw enemy at their actual position
                enemy_x = int(enemy.free_roam_x)
                enemy_y = int(enemy.free_roam_y)
                enemy_rect = pygame.Rect(enemy_x, enemy_y, 45, 45)
                
                # Draw menacing shadow
                shadow_rect = pygame.Rect(enemy_x + 3, enemy_y + 3, 45, 45)
                pygame.draw.rect(self.screen, (20, 20, 20), shadow_rect)
                
                # Draw enemy body
                pygame.draw.rect(self.screen, (60, 40, 70), enemy_rect)
                pygame.draw.rect(self.screen, COLOR_ENEMY, enemy_rect, 3)
                
                # Draw glowing eyes
                eye_color = (255, 50, 50)
                pygame.draw.circle(self.screen, eye_color, (enemy_x + 12, enemy_y + 15), 4)
                pygame.draw.circle(self.screen, eye_color, (enemy_x + 33, enemy_y + 15), 4)
                
                # Draw enemy name above with background
                font_small = self.assets.get_font('medium')
                name_txt = font_small.render(enemy.name, True, COLOR_ENEMY)
                name_bg = pygame.Surface((name_txt.get_width() + 10, name_txt.get_height() + 4), pygame.SRCALPHA)
                pygame.draw.rect(name_bg, (40, 40, 40, 200), name_bg.get_rect())
                name_bg.blit(name_txt, (5, 2))
                self.screen.blit(name_bg, (enemy_x - 5, enemy_y - 30))
        
        # Draw room name
        font = self.assets.get_font('large')
        room_txt = font.render(room.name, True, COLOR_TITLE)
        self.screen.blit(room_txt, (20, 20))
        
        # Draw instructions
        font_small = self.assets.get_font('medium')
        instructions = font_small.render("ESC - Return to Office | WASD/Arrows - Move", True, (180, 180, 180))
        self.screen.blit(instructions, (20, HEIGHT - 30))
    
    def _draw_wall(self, rect: pygame.Rect):
        """Draw a textured wall."""
        wall_color = (55, 55, 60)
        pygame.draw.rect(self.screen, wall_color, rect)
        # Highlight edge
        highlight = tuple(min(255, c + 15) for c in wall_color)
        if rect.width > rect.height:
            pygame.draw.rect(self.screen, highlight, (rect.x, rect.y, rect.width, 2))
        else:
            pygame.draw.rect(self.screen, highlight, (rect.x, rect.y, 2, rect.height))
    
    def _draw_furniture(self, furn: dict):
        """Draw a piece of furniture."""
        pygame.draw.rect(self.screen, furn['color'], furn['rect'])
        pygame.draw.rect(self.screen, (255, 255, 255), furn['rect'], 1)
        
        # Draw label if present
        if 'label' in furn and furn['label']:
            font = self.assets.get_font('medium')
            label_txt = font.render(furn['label'], True, (255, 255, 255))
            label_rect = label_txt.get_rect(center=furn['rect'].center)
            self.screen.blit(label_txt, label_rect)
        
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
        
        if game_state.free_roam_mode:
            # Simplified HUD for free roam
            hud_lines = [
                f"Power: {game_state.power:05.1f}%",
                f"Egg: {'YES' if game_state.has_egg else 'NO'}",
                f"Fridge: {game_state.fridge_stock}/3",
                f"Time: {int(game_state.night_time)}s / {int(game_state.night_time // 60)}m",
            ]
        else:
            status_icon = "💻" if game_state.computer_active else "📱"
            hud_lines = [
                f"Power: {game_state.power:05.1f}%",
                f"Status: {status_icon} {'WORKING' if game_state.computer_active else 'SLACKING'}",
                f"Egg: {'YES' if game_state.has_egg else 'NO'}",
                f"Fridge: {game_state.fridge_stock}/3 items",
                f"Camera: {'ON' if game_state.camera_active else 'OFF'} (C) | Computer: (SPACE)",
                f"Doors: L={'CLOSED' if game_state.left_door_closed else 'OPEN'} (A) | R={'CLOSED' if game_state.right_door_closed else 'OPEN'} (D)",
                f"Time: {int(game_state.night_time)}s / {int(game_state.night_time // 60)}m",
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
