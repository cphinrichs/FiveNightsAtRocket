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
        
        # If computer is active and player is in office, show working screen
        if game_state.computer_active and not game_state.free_roam_mode and not game_state.camera_active:
            self._render_working_screen()
        elif game_state.free_roam_mode and game_state.is_playing():
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
            
        # Draw camera label with background
        font = self.assets.get_font('medium')
        txt = font.render(f"CAM: {room_name}", True, COLOR_TITLE)
        
        label_bg = pygame.Surface((txt.get_width() + 20, txt.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(label_bg, (0, 0, 0, 180), label_bg.get_rect())
        self.screen.blit(label_bg, (30, 30))
        self.screen.blit(txt, (40, 35))
        
    def _render_working_screen(self):
        """Render the working screen (computer view)."""
        working_image = self.assets.get_working_image()
        
        if working_image:
            # Scale image to fit screen
            img_w, img_h = working_image.get_size()
            
            # Scale to fill screen height
            scale = HEIGHT / img_h
            scaled_w = int(img_w * scale)
            scaled_h = HEIGHT
            
            # If wider than screen, scale to width instead
            if scaled_w > WIDTH:
                scale = WIDTH / img_w
                scaled_w = WIDTH
                scaled_h = int(img_h * scale)
            
            scaled_image = pygame.transform.smoothscale(working_image, (scaled_w, scaled_h))
            
            # Center on screen
            x_offset = (WIDTH - scaled_w) // 2
            y_offset = (HEIGHT - scaled_h) // 2
            self.screen.blit(scaled_image, (x_offset, y_offset))
        else:
            # Fallback if image not loaded
            self.screen.fill((20, 30, 40))
            font = self.assets.get_font('large')
            txt = font.render("WORKING...", True, (100, 255, 100))
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))
        
    def _render_office_view(self, game_state: GameState):
        """Render the office view."""
        pygame.draw.rect(self.screen, COLOR_OFFICE_BG, (0, 0, WIDTH, HEIGHT))
        
        # Draw computer screen indicator (smaller, less obtrusive)
        computer_color = (100, 200, 100) if game_state.computer_active else (50, 50, 70)
        computer_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 120)
        pygame.draw.rect(self.screen, computer_color, computer_rect)
        pygame.draw.rect(self.screen, (80, 80, 80), computer_rect, 2)
        
        # Small computer status indicator
        font_small = self.assets.get_font('small')
        if game_state.computer_active:
            comp_txt = font_small.render("WORKING", True, (50, 255, 50))
        else:
            comp_txt = font_small.render("Slacking...", True, (255, 150, 150))
        self.screen.blit(comp_txt, (WIDTH//2 - comp_txt.get_width()//2, HEIGHT//2 - 10))
        
        # Draw door indicators showing if enemies are at doors
        if self.enemy_manager:
            left_enemies, right_enemies = self.enemy_manager.get_enemies_at_doors()
            self._render_door_warnings(left_enemies, right_enemies)
    
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
        
        # Draw room name in corner
        font = self.assets.get_font('medium')
        room_txt = font.render(room.name, True, COLOR_TITLE)
        
        # Add background for room name
        name_bg = pygame.Surface((room_txt.get_width() + 20, room_txt.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(name_bg, (0, 0, 0, 180), name_bg.get_rect())
        self.screen.blit(name_bg, (10, 10))
        self.screen.blit(room_txt, (20, 15))
        
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
        font = self.assets.get_font('small')
        
        # Create semi-transparent background for HUD
        hud_bg = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)
        pygame.draw.rect(hud_bg, (0, 0, 0, 180), hud_bg.get_rect())
        self.screen.blit(hud_bg, (0, HEIGHT - 140))
        
        if game_state.free_roam_mode:
            # Compact HUD for free roam - single row
            hud_text = f"Power: {game_state.power:05.1f}%  |  Egg: {'YES' if game_state.has_egg else 'NO'}  |  Fridge: {game_state.fridge_stock}/3  |  Time: {int(game_state.night_time)}s"
            txt = font.render(hud_text, True, COLOR_TEXT)
            self.screen.blit(txt, (20, HEIGHT - 30))
        else:
            # Office HUD - organized in columns
            y_start = HEIGHT - 130
            
            # Left column - Status
            status_lines = [
                f"Power: {game_state.power:05.1f}%",
                f"Time: {int(game_state.night_time)}s ({int(game_state.night_time // 60)}m)",
            ]
            for i, line in enumerate(status_lines):
                txt = font.render(line, True, COLOR_TEXT)
                self.screen.blit(txt, (20, y_start + i * 25))
            
            # Middle column - Resources
            resource_lines = [
                f"Egg: {'✓ YES' if game_state.has_egg else '✗ NO'}",
                f"Fridge: {game_state.fridge_stock}/3",
            ]
            for i, line in enumerate(resource_lines):
                txt = font.render(line, True, COLOR_TEXT)
                self.screen.blit(txt, (220, y_start + i * 25))
            
            # Right column - Controls
            status_icon = "💻" if game_state.computer_active else "📱"
            control_lines = [
                f"{status_icon} {'WORK' if game_state.computer_active else 'SLACK'} [SPACE]",
                f"Camera: {'ON' if game_state.camera_active else 'OFF'} [C]",
                f"Doors: L[A] R[D]",
                f"Leave: [W]",
            ]
            for i, line in enumerate(control_lines):
                txt = font.render(line, True, COLOR_TEXT)
                self.screen.blit(txt, (WIDTH - 220, y_start + i * 25))
            
    def _render_game_over(self):
        """Render game over screen."""
        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        # Game over box
        box_width = 600
        box_height = 250
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2
        
        # Box background
        pygame.draw.rect(self.screen, (40, 20, 20), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, COLOR_GAME_OVER, (box_x, box_y, box_width, box_height), 4)
        
        # Title
        font_large = self.assets.get_font('large')
        txt = font_large.render("GAME OVER", True, COLOR_GAME_OVER)
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, box_y + 30))
        
    def _render_game_over_message(self, game_state: GameState):
        """Render the game over message if present."""
        if game_state.death_message:
            font_med = self.assets.get_font('medium')
            font_small = self.assets.get_font('small')
            
            # Death message
            txt = font_med.render(game_state.death_message, True, (255, 180, 180))
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 + 10))
            
            # Restart instruction
            restart_txt = font_small.render("Press R to Restart", True, (200, 200, 200))
            self.screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, HEIGHT//2 + 60))
        
    def _render_win(self):
        """Render win screen."""
        # Light overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 50, 0, 200), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        # Win box
        box_width = 600
        box_height = 250
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2
        
        # Box background
        pygame.draw.rect(self.screen, (20, 40, 20), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, COLOR_WIN, (box_x, box_y, box_width, box_height), 4)
        
        # Title
        font_large = self.assets.get_font('large')
        font_small = self.assets.get_font('small')
        
        txt = font_large.render("6 AM - YOU WIN!", True, COLOR_WIN)
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, box_y + 50))
        
        # Restart instruction
        restart_txt = font_small.render("Press R to Restart", True, (200, 200, 200))
        self.screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, box_y + 150))
