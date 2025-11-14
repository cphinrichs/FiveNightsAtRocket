"""
VIEW LAYER - Rendering and Visual Presentation
==============================================
This module handles all visual rendering of the game.
Views are responsible for:
- Drawing sprites and UI elements
- Rendering game state visually
- Camera positioning and offsets
- Visual effects and animations
- NO game logic or input handling (that's Model and Controller)
"""

import pygame
from typing import Tuple, Dict, List
from models import (
    Player, Enemy, Interactable, Room, Particle,
    GameState, Direction, RoomType
)


# ============================================================
# COLORS - Visual constants
# ============================================================

# Basic colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Vibrant colors
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 150, 220)
YELLOW = (255, 220, 50)
ORANGE = (255, 165, 0)
PURPLE = (180, 100, 220)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)

# UI colors
UI_BG = (30, 30, 40, 220)
UI_BORDER = (100, 100, 120)
UI_HIGHLIGHT = (255, 200, 50)
UI_TEXT = WHITE
UI_DANGER = RED
UI_SUCCESS = GREEN


# ============================================================
# SPRITE GENERATION - Create visual sprites programmatically
# ============================================================

def create_player_sprite(width: int, height: int, direction: Direction) -> pygame.Surface:
    """
    Generate a sprite for the player character.
    Player appearance changes based on facing direction.
    
    Args:
        width, height: Sprite dimensions
        direction: Which way player is facing
        
    Returns:
        pygame.Surface with player sprite drawn on it
    """
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    color = (50, 150, 220)  # Blue
    
    # Draw body
    pygame.draw.rect(sprite, color, (0, 0, width, height), border_radius=5)
    pygame.draw.rect(sprite, (30, 100, 180), (0, 0, width, height), 3, border_radius=5)
    
    # Draw eyes based on direction
    center_x = width // 2
    center_y = height // 2
    
    if direction in [Direction.UP, Direction.DOWN]:
        # Facing up/down: show both eyes
        eye_offset = 8
        pygame.draw.circle(sprite, WHITE, (center_x - eye_offset, center_y - 5), 5)
        pygame.draw.circle(sprite, WHITE, (center_x + eye_offset, center_y - 5), 5)
        pygame.draw.circle(sprite, BLACK, (center_x - eye_offset, center_y - 5), 3)
        pygame.draw.circle(sprite, BLACK, (center_x + eye_offset, center_y - 5), 3)
    else:
        # Facing left/right: show one eye
        eye_x = center_x + (10 if direction == Direction.RIGHT else -10)
        pygame.draw.circle(sprite, WHITE, (eye_x, center_y - 5), 5)
        pygame.draw.circle(sprite, BLACK, (eye_x, center_y - 5), 3)
    
    return sprite


def create_enemy_sprite(width: int, height: int, color: Tuple[int, int, int], 
                       state: str, name: str = "", intern_id: int = 1) -> pygame.Surface:
    """
    Generate a sprite for an enemy character using their character image.
    Enemy appearance changes based on their current state.
    
    Args:
        width, height: Sprite dimensions
        color: Base RGB color of enemy (used as fallback)
        state: Current behavior state (idle, chasing, eating, etc.)
        name: Name of the enemy (used to load appropriate image)
        intern_id: For NextGenIntern enemies, which intern image to use (1, 2, or 3)
        
    Returns:
        pygame.Surface with enemy sprite drawn on it
    """
    # Import the function from sprites.py to use the implementation there
    from sprites import create_enemy_sprite as _create_enemy_sprite
    return _create_enemy_sprite(width, height, color, state, name, intern_id)


def create_interactable_sprite(width: int, height: int, color: Tuple[int, int, int], 
                               type_name: str) -> pygame.Surface:
    """
    Generate a sprite for an interactable object.
    Shows a colored box with label text.
    
    Args:
        width, height: Sprite dimensions
        color: RGB color of object
        type_name: Label to display on object
        
    Returns:
        pygame.Surface with interactable sprite drawn on it
    """
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw box
    pygame.draw.rect(sprite, color, (0, 0, width, height), border_radius=3)
    pygame.draw.rect(sprite, BLACK, (0, 0, width, height), 2, border_radius=3)
    
    # Draw label text
    font = pygame.font.Font(None, 16)
    label = type_name[:8]  # Truncate long names
    text_surf = font.render(label, True, WHITE)
    text_rect = text_surf.get_rect(center=(width // 2, height // 2))
    sprite.blit(text_surf, text_rect)
    
    return sprite


def create_name_tag(name: str, color: Tuple[int, int, int] = WHITE) -> pygame.Surface:
    """
    Generate a name tag sprite to display above entities.
    
    Args:
        name: Text to display
        color: Text color
        
    Returns:
        pygame.Surface with name tag drawn on it
    """
    font = pygame.font.Font(None, 20 if len(name) < 10 else 18)
    text_surf = font.render(name, True, color)
    
    # Create background slightly larger than text
    bg_rect = text_surf.get_rect()
    bg_rect.inflate_ip(8, 4)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect(), border_radius=3)
    
    # Blit text onto background
    text_rect = text_surf.get_rect(center=(bg_rect.width // 2, bg_rect.height // 2))
    bg_surface.blit(text_surf, text_rect)
    
    return bg_surface


# ============================================================
# PARTICLE RENDERER
# ============================================================

class ParticleRenderer:
    """Handles rendering of particle effects"""
    
    @staticmethod
    def draw_particle(particle: Particle, surface: pygame.Surface, 
                     camera_offset: Tuple[int, int]):
        """
        Draw a single particle to the screen.
        
        Args:
            particle: Particle to render
            surface: Surface to draw on
            camera_offset: Camera position offset
        """
        # Calculate screen position
        screen_x = int(particle.x - camera_offset[0])
        screen_y = int(particle.y - camera_offset[1])
        
        # Create translucent circle
        temp_surface = pygame.Surface((int(particle.size * 2), int(particle.size * 2)), 
                                      pygame.SRCALPHA)
        
        # Draw particle with alpha
        color = (*particle.color, particle.alpha)
        pygame.draw.circle(temp_surface, color, 
                          (int(particle.size), int(particle.size)), 
                          int(particle.size))
        
        surface.blit(temp_surface, (screen_x - particle.size, screen_y - particle.size))
    
    @staticmethod
    def draw_particles(particles: List[Particle], surface: pygame.Surface,
                      camera_offset: Tuple[int, int]):
        """
        Draw all particles in a list.
        
        Args:
            particles: List of particles to render
            surface: Surface to draw on
            camera_offset: Camera position offset
        """
        for particle in particles:
            ParticleRenderer.draw_particle(particle, surface, camera_offset)


# ============================================================
# ENTITY RENDERERS - Draw game objects
# ============================================================

class PlayerRenderer:
    """Handles rendering of the player character"""
    
    def __init__(self):
        """Initialize player renderer with sprite cache"""
        self.sprite_cache = {}  # Cache sprites for each direction
        self.name_tag = create_name_tag("Brenton")
    
    def draw(self, player: Player, surface: pygame.Surface, 
             camera_offset: Tuple[int, int]):
        """
        Draw the player character.
        
        Args:
            player: Player entity to draw
            surface: Surface to draw on
            camera_offset: Camera position offset
        """
        rect = player.get_rect()
        screen_x = rect.x - camera_offset[0]
        screen_y = rect.y - camera_offset[1]
        
        # Get or create sprite for current direction
        dir_key = player.direction.name
        if dir_key not in self.sprite_cache:
            self.sprite_cache[dir_key] = create_player_sprite(
                player.width, player.height, player.direction
            )
        
        # Draw sprite
        sprite = self.sprite_cache[dir_key]
        surface.blit(sprite, (screen_x, screen_y))
        
        # Draw name tag above player
        name_x = screen_x + player.width // 2 - self.name_tag.get_width() // 2
        name_y = screen_y - self.name_tag.get_height() - 5
        surface.blit(self.name_tag, (name_x, name_y))


class EnemyRenderer:
    """Handles rendering of enemy characters"""
    
    def __init__(self):
        """Initialize enemy renderer with sprite cache"""
        self.sprite_cache = {}  # Cache sprites per enemy per state
        self.name_tags = {}     # Cache name tags per enemy
    
    def draw(self, enemy: Enemy, surface: pygame.Surface,
             camera_offset: Tuple[int, int]):
        """
        Draw an enemy character.
        
        Args:
            enemy: Enemy entity to draw
            surface: Surface to draw on
            camera_offset: Camera position offset
        """
        rect = enemy.get_rect()
        screen_x = rect.x - camera_offset[0]
        screen_y = rect.y - camera_offset[1]
        
        # Cache key combines enemy name, state, and intern_id if applicable
        intern_id = getattr(enemy, 'intern_id', 1)
        cache_key = f"{enemy.name}_{enemy.state}_{intern_id}"
        
        # Get or create sprite for current state
        if cache_key not in self.sprite_cache:
            self.sprite_cache[cache_key] = create_enemy_sprite(
                enemy.width, enemy.height, enemy.color, enemy.state,
                enemy.name, intern_id
            )
        
        # Draw sprite
        sprite = self.sprite_cache[cache_key]
        surface.blit(sprite, (screen_x, screen_y))
        
        # Get or create name tag
        if enemy.name not in self.name_tags:
            self.name_tags[enemy.name] = create_name_tag(enemy.name)
        
        # Draw name tag above enemy
        name_tag = self.name_tags[enemy.name]
        name_x = screen_x + enemy.width // 2 - name_tag.get_width() // 2
        name_y = screen_y - name_tag.get_height() - 5
        surface.blit(name_tag, (name_x, name_y))


class InteractableRenderer:
    """Handles rendering of interactable objects"""
    
    def __init__(self):
        """Initialize interactable renderer"""
        pass
    
    def draw(self, interactable: Interactable, surface: pygame.Surface,
             camera_offset: Tuple[int, int]):
        """
        Draw an interactable object.
        Sprites are cached on the interactable itself.
        
        Args:
            interactable: Interactable to draw
            surface: Surface to draw on
            camera_offset: Camera position offset
        """
        rect = interactable.get_rect()
        screen_x = rect.x - camera_offset[0]
        screen_y = rect.y - camera_offset[1]
        
        # Generate sprite if not already created
        if not hasattr(interactable, 'sprite') or interactable.sprite is None:
            display_label = interactable.label if interactable.label else interactable.type.value
            interactable.sprite = create_interactable_sprite(
                interactable.width, interactable.height,
                interactable.color, display_label
            )
        
        # Draw sprite
        surface.blit(interactable.sprite, (screen_x, screen_y))


class RoomRenderer:
    """Handles rendering of rooms (floors, walls, labels)"""
    
    @staticmethod
    def draw(room: Room, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Draw a room including floor, walls, and interactables.
        
        Args:
            room: Room to draw
            surface: Surface to draw on
            camera_offset: Camera position offset
        """
        # Calculate screen position
        screen_x = room.x - camera_offset[0]
        screen_y = room.y - camera_offset[1]
        floor_rect = pygame.Rect(screen_x, screen_y, room.width, room.height)
        
        # Draw floor with room-specific color
        floor_colors = {
            RoomType.OFFICE: (80, 80, 90),
            RoomType.BREAK_ROOM: (70, 85, 70),
            RoomType.MEETING_ROOM: (85, 75, 75),
            RoomType.CLASSROOM: (75, 80, 95),
            RoomType.HALLWAY: (75, 75, 75),
        }
        floor_color = floor_colors.get(room.type, (80, 80, 80))
        pygame.draw.rect(surface, floor_color, floor_rect)
        
        # Draw grid pattern on floor for texture
        grid_color = tuple(max(0, c - 10) for c in floor_color)
        tile_size = 64
        for gx in range(0, room.width, tile_size):
            pygame.draw.line(surface, grid_color,
                           (screen_x + gx, screen_y),
                           (screen_x + gx, screen_y + room.height))
        for gy in range(0, room.height, tile_size):
            pygame.draw.line(surface, grid_color,
                           (screen_x, screen_y + gy),
                           (screen_x + room.width, screen_y + gy))
        
        # Draw walls
        for wall in room.walls:
            wall_rect = pygame.Rect(
                wall.x - camera_offset[0],
                wall.y - camera_offset[1],
                wall.width,
                wall.height
            )
            pygame.draw.rect(surface, (60, 60, 70), wall_rect)
            pygame.draw.rect(surface, (40, 40, 50), wall_rect, 2)
        
        # Draw room label
        font = pygame.font.Font(None, 32)
        label_surf = font.render(room.type.value, True, WHITE)
        label_rect = label_surf.get_rect(
            centerx=screen_x + room.width // 2,
            top=screen_y + 30
        )
        
        # Label background
        bg_rect = label_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        surface.blit(bg_surface, bg_rect)
        surface.blit(label_surf, label_rect)


# ============================================================
# UI RENDERERS - HUD and interface elements
# ============================================================

class HUDRenderer:
    """Renders the heads-up display (inventory, time, battery, etc.)"""
    
    @staticmethod
    def draw(surface: pygame.Surface, game_data: dict):
        """
        Draw the HUD elements.
        
        Args:
            surface: Surface to draw on
            game_data: Dictionary containing game state information
        """
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Draw inventory panel (top-left)
        HUDRenderer._draw_inventory(surface, game_data.get('inventory', {}))
        
        # Draw time/day counter (top-center)
        HUDRenderer._draw_time(surface, game_data.get('current_time', 0), 
                               game_data.get('current_day', 1))
        
        # Draw battery (top-right)
        HUDRenderer._draw_battery(surface, game_data.get('battery', 100))
        
        # Draw message if any (bottom-center)
        message = game_data.get('message', '')
        if message:
            HUDRenderer._draw_message(surface, message)
    
    @staticmethod
    def _draw_inventory(surface: pygame.Surface, inventory: dict):
        """Draw player inventory (snacks and eggs)"""
        font = pygame.font.Font(None, 28)
        y_offset = 20
        
        # Snacks
        snacks = inventory.get('snacks', 0)
        snacks_text = f"🍪 Snacks: {snacks}/5"
        snacks_color = GREEN if snacks > 2 else (YELLOW if snacks > 0 else RED)
        snacks_surf = font.render(snacks_text, True, snacks_color)
        surface.blit(snacks_surf, (20, y_offset))
        
        # Eggs
        y_offset += 35
        has_egg = inventory.get('egg', False)
        egg_text = f"🥚 Egg: {'Yes' if has_egg else 'No'}"
        egg_color = GREEN if has_egg else GRAY
        egg_surf = font.render(egg_text, True, egg_color)
        surface.blit(egg_surf, (20, y_offset))
    
    @staticmethod
    def _draw_time(surface: pygame.Surface, current_time: float, current_day: int):
        """Draw current game time and day"""
        screen_width = surface.get_width()
        font = pygame.font.Font(None, 32)
        
        # Calculate time display (9am = 0, 5pm = 1.0)
        hour = 9 + int(current_time * 8)  # 8 hours from 9am to 5pm
        minute = int((current_time * 8 * 60) % 60)
        time_str = f"Day {current_day}/5 - {hour}:{minute:02d}"
        
        time_surf = font.render(time_str, True, WHITE)
        time_rect = time_surf.get_rect(centerx=screen_width // 2, top=20)
        
        # Background
        bg_rect = time_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        surface.blit(bg_surface, bg_rect)
        surface.blit(time_surf, time_rect)
    
    @staticmethod
    def _draw_battery(surface: pygame.Surface, battery: float):
        """Draw battery level indicator"""
        screen_width = surface.get_width()
        font = pygame.font.Font(None, 28)
        
        # Battery text
        battery_text = f"🔋 Battery: {int(battery)}%"
        battery_color = GREEN if battery > 50 else (YELLOW if battery > 20 else RED)
        battery_surf = font.render(battery_text, True, battery_color)
        battery_rect = battery_surf.get_rect(topright=(screen_width - 20, 20))
        surface.blit(battery_surf, battery_rect)
        
        # Battery bar
        bar_width = 150
        bar_height = 20
        bar_x = screen_width - 20 - bar_width
        bar_y = 55
        
        # Background bar
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Filled portion
        filled_width = int(bar_width * (battery / 100))
        pygame.draw.rect(surface, battery_color, (bar_x, bar_y, filled_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    @staticmethod
    def _draw_message(surface: pygame.Surface, message: str):
        """Draw temporary message at bottom of screen"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        font = pygame.font.Font(None, 32)
        msg_surf = font.render(message, True, WHITE)
        msg_rect = msg_surf.get_rect(centerx=screen_width // 2, 
                                     bottom=screen_height - 30)
        
        # Background
        bg_rect = msg_rect.inflate(30, 15)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        surface.blit(bg_surface, bg_rect)
        surface.blit(msg_surf, msg_rect)


# ============================================================
# MENU RENDERERS - Title screens and overlays
# ============================================================

class MenuRenderer:
    """Renders menu screens (main menu, tutorial, game over, etc.)"""
    
    @staticmethod
    def draw_main_menu(surface: pygame.Surface):
        """Draw the main menu screen"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Background
        surface.fill(BLACK)
        
        # Title
        title_font = pygame.font.Font(None, 80)
        title_surf = title_font.render("Five Nights at Rocket", True, ORANGE)
        title_rect = title_surf.get_rect(center=(screen_width // 2, 200))
        surface.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_surf = subtitle_font.render("Survive the office until 5pm", True, WHITE)
        subtitle_rect = subtitle_surf.get_rect(center=(screen_width // 2, 280))
        surface.blit(subtitle_surf, subtitle_rect)
        
        # Instructions
        font = pygame.font.Font(None, 32)
        instructions = [
            "Press SPACE to start",
            "",
            "Controls:",
            "WASD - Move",
            "E - Interact",
            "ESC - Pause/Close cameras"
        ]
        
        y = 350
        for line in instructions:
            text_surf = font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(screen_width // 2, y))
            surface.blit(text_surf, text_rect)
            y += 40
    
    @staticmethod
    def draw_tutorial(surface: pygame.Surface):
        """Draw the tutorial/help screen"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Semi-transparent background
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 56)
        title_surf = title_font.render("How to Survive", True, YELLOW)
        title_rect = title_surf.get_rect(center=(screen_width // 2, 80))
        surface.blit(title_surf, title_rect)
        
        # Tips
        font = pygame.font.Font(None, 28)
        tips = [
            "• Survive from 9am to 5pm each day for 5 days",
            "• Enemies take time to activate - use this to prepare!",
            "• Jo-nathan ALWAYS chases you relentlessly",
            "• Give Jo-nathan an egg to distract him for 10 seconds",
            "• Jeromathy hunts you down if snacks hit 0",
            "• Angellica pursues you if you watch YouTube",
            "• Enemies navigate around walls to catch you!",
            "• NextGen Intern takes snacks but is harmless",
            "• Use cameras to track enemies (drains battery)",
            "",
            "Press SPACE to begin"
        ]
        
        y = 180
        for tip in tips:
            text_surf = font.render(tip, True, WHITE)
            text_rect = text_surf.get_rect(centerx=screen_width // 2, y=y)
            surface.blit(text_surf, text_rect)
            y += 45
    
    @staticmethod
    def draw_game_over(surface: pygame.Surface, reason: str):
        """Draw game over screen"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Dark overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))
        
        # Game Over text
        title_font = pygame.font.Font(None, 96)
        title_surf = title_font.render("GAME OVER", True, RED)
        title_rect = title_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
        surface.blit(title_surf, title_rect)
        
        # Reason
        reason_font = pygame.font.Font(None, 40)
        reason_surf = reason_font.render(reason, True, WHITE)
        reason_rect = reason_surf.get_rect(center=(screen_width // 2, screen_height // 2))
        surface.blit(reason_surf, reason_rect)
        
        # Restart prompt
        prompt_font = pygame.font.Font(None, 32)
        prompt_surf = prompt_font.render("Press SPACE to restart", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(screen_width // 2, screen_height // 2 + 80))
        surface.blit(prompt_surf, prompt_rect)
    
    @staticmethod
    def draw_victory(surface: pygame.Surface):
        """Draw victory screen"""
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Bright overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, 100))  # Golden glow
        surface.blit(overlay, (0, 0))
        
        # Victory text
        title_font = pygame.font.Font(None, 96)
        title_surf = title_font.render("VICTORY!", True, GREEN)
        title_rect = title_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
        surface.blit(title_surf, title_rect)
        
        # Message
        msg_font = pygame.font.Font(None, 40)
        msg_surf = msg_font.render("You survived 5 nights!", True, WHITE)
        msg_rect = msg_surf.get_rect(center=(screen_width // 2, screen_height // 2))
        surface.blit(msg_surf, msg_rect)
        
        # Restart prompt
        prompt_font = pygame.font.Font(None, 32)
        prompt_surf = prompt_font.render("Press SPACE to play again", True, WHITE)
        prompt_rect = prompt_surf.get_rect(center=(screen_width // 2, screen_height // 2 + 80))
        surface.blit(prompt_surf, prompt_rect)


# ============================================================
# CAMERA VIEW RENDERER - Security camera display
# ============================================================

class CameraRenderer:
    """Renders the security camera view"""
    
    @staticmethod
    def draw(surface: pygame.Surface, rooms: Dict[RoomType, Room], 
             enemies: List[Enemy], current_view: RoomType):
        """
        Draw the camera view interface.
        
        Args:
            surface: Surface to draw on
            rooms: Dictionary of all rooms
            enemies: List of all enemies
            current_view: Which room camera is currently viewing
        """
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Background
        surface.fill(BLACK)
        
        # Camera feed (simplified top-down view of selected room)
        room = rooms.get(current_view)
        if room:
            # Draw room
            feed_rect = pygame.Rect(200, 100, 880, 440)
            pygame.draw.rect(surface, (40, 40, 50), feed_rect)
            pygame.draw.rect(surface, GREEN, feed_rect, 3)
            
            # Room label
            font = pygame.font.Font(None, 48)
            label_surf = font.render(f"CAMERA: {room.type.value}", True, GREEN)
            label_rect = label_surf.get_rect(centerx=screen_width // 2, top=120)
            surface.blit(label_surf, label_rect)
            
            # Show enemies in this room
            small_font = pygame.font.Font(None, 32)
            enemies_in_room = [e for e in enemies if e.current_room == room.type]
            if enemies_in_room:
                enemy_text = "Enemies detected: " + ", ".join(e.name for e in enemies_in_room)
            else:
                enemy_text = "No enemies detected"
            enemy_surf = small_font.render(enemy_text, True, RED if enemies_in_room else GREEN)
            enemy_rect = enemy_surf.get_rect(centerx=screen_width // 2, centery=feed_rect.centery)
            surface.blit(enemy_surf, enemy_rect)
        
        # Camera selection instructions
        instructions = "Select Camera: [1]Office [2]Break Room [3]Meeting [4]Classroom [5]Hallway  [ESC]Close"
        inst_font = pygame.font.Font(None, 24)
        inst_surf = inst_font.render(instructions, True, WHITE)
        inst_rect = inst_surf.get_rect(centerx=screen_width // 2, bottom=screen_height - 30)
        surface.blit(inst_surf, inst_rect)
