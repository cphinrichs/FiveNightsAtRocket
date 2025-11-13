"""
Five Nights at Rocket - A survival game with strategy and time management
Navigate the office, avoid enemies, manage resources, and survive until 5pm
"""

import asyncio
import pygame
import sys
from enum import Enum
from typing import Dict, List, Tuple, Optional
import math
import random

# Initialize Pygame
pygame.init()

# Game Configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 64

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 150, 220)
YELLOW = (255, 220, 50)
ORANGE = (255, 165, 0)
PURPLE = (180, 100, 220)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)

# UI Colors
UI_BG = (30, 30, 40, 220)
UI_BORDER = (100, 100, 120)
UI_HIGHLIGHT = (255, 200, 50)
UI_TEXT = WHITE
UI_DANGER = RED
UI_SUCCESS = GREEN

# Game States
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    CAMERA = 3
    PAUSED = 4
    GAME_OVER = 5
    VICTORY = 6
    TUTORIAL = 7

# Room Types
class RoomType(Enum):
    OFFICE = "Office"
    BREAK_ROOM = "Break Room"
    MEETING_ROOM = "Meeting Room"
    CLASSROOM = "Classroom"
    HALLWAY = "Hallway"

# Direction enumeration
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class InteractableType(Enum):
    REFRIGERATOR = "refrigerator"
    CABINET = "cabinet"
    CAMERA = "camera"
    LAPTOP = "laptop"
    DESK = "desk"
    DOOR = "door"


# ============================================================
# PARTICLE SYSTEM
# ============================================================

class Particle:
    def __init__(self, x: float, y: float, dx: float, dy: float, 
                 color: Tuple[int, int, int], lifetime: float, size: float = 4):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255

    def update(self, dt: float):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        if self.lifetime > 0:
            alpha = max(0, min(255, self.alpha))
            color = (*self.color, alpha)
            pos = (int(self.x - camera_offset[0]), int(self.y - camera_offset[1]))
            
            # Create temporary surface for alpha blending
            temp_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (int(self.size), int(self.size)), int(self.size))
            surface.blit(temp_surface, (pos[0] - int(self.size), pos[1] - int(self.size)))

    def is_alive(self) -> bool:
        return self.lifetime > 0


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def emit(self, x: float, y: float, color: Tuple[int, int, int], 
             count: int = 10, spread: float = 100, lifetime: float = 1.0):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, spread)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            size = random.uniform(2, 6)
            particle = Particle(x, y, dx, dy, color, lifetime, size)
            self.particles.append(particle)

    def update(self, dt: float):
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        for particle in self.particles:
            particle.draw(surface, camera_offset)


# ============================================================
# ENTITY BASE CLASS
# ============================================================

class Entity:
    def __init__(self, x: float, y: float, width: int, height: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 150
        self.direction = Direction.DOWN
        
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def get_center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
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


# ============================================================
# PLAYER CLASS
# ============================================================

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40, 40, BLUE)
        self.inventory = {"snacks": 5, "egg": False}  # Start with full snacks
        self.on_youtube = False
        self.speed = 200
        
    def move(self, dx: float, dy: float, dt: float):
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
        rect = self.get_rect()
        screen_rect = pygame.Rect(
            rect.x - camera_offset[0],
            rect.y - camera_offset[1],
            rect.width,
            rect.height
        )
        
        # Player body
        pygame.draw.rect(surface, self.color, screen_rect, border_radius=5)
        pygame.draw.rect(surface, (30, 100, 180), screen_rect, 3, border_radius=5)
        
        # Draw face/direction
        center_x = screen_rect.centerx
        center_y = screen_rect.centery
        
        # Eyes
        if self.direction in [Direction.UP, Direction.DOWN]:
            eye_offset = 8
            pygame.draw.circle(surface, WHITE, (center_x - eye_offset, center_y - 5), 5)
            pygame.draw.circle(surface, WHITE, (center_x + eye_offset, center_y - 5), 5)
            pygame.draw.circle(surface, BLACK, (center_x - eye_offset, center_y - 5), 3)
            pygame.draw.circle(surface, BLACK, (center_x + eye_offset, center_y - 5), 3)
        else:
            eye_x = center_x + (10 if self.direction == Direction.RIGHT else -10)
            pygame.draw.circle(surface, WHITE, (eye_x, center_y - 5), 5)
            pygame.draw.circle(surface, BLACK, (eye_x, center_y - 5), 3)
        
        # Name tag
        font = pygame.font.Font(None, 20)
        name_surf = font.render("Brenton", True, WHITE)
        name_rect = name_surf.get_rect(centerx=screen_rect.centerx, bottom=screen_rect.top - 5)
        
        # Name background
        bg_rect = name_rect.inflate(8, 4)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=3)
        surface.blit(name_surf, name_rect)


# ============================================================
# ENEMY CLASSES
# ============================================================

class Enemy(Entity):
    def __init__(self, x: float, y: float, width: int, height: int, 
                 color: Tuple[int, int, int], name: str):
        super().__init__(x, y, width, height, color)
        self.name = name
        self.speed = 80
        self.state = "idle"
        self.target_pos: Optional[Tuple[float, float]] = None
        self.wait_timer = 0
        self.path_timer = 0
        self.current_room: RoomType = RoomType.OFFICE  # Track which room enemy is in
        
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        rect = self.get_rect()
        screen_rect = pygame.Rect(
            rect.x - camera_offset[0],
            rect.y - camera_offset[1],
            rect.width,
            rect.height
        )
        
        # Enemy body with gradient effect
        pygame.draw.rect(surface, self.color, screen_rect, border_radius=5)
        
        # Darker outline
        darker_color = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.rect(surface, darker_color, screen_rect, 3, border_radius=5)
        
        # Enemy eyes - different based on state
        center_x = screen_rect.centerx
        center_y = screen_rect.centery
        
        if self.state in ["chasing"]:
            # Menacing red eyes when chasing
            pygame.draw.circle(surface, RED, (center_x - 8, center_y - 5), 6)
            pygame.draw.circle(surface, RED, (center_x + 8, center_y - 5), 6)
            pygame.draw.circle(surface, (255, 100, 100), (center_x - 8, center_y - 5), 3)
            pygame.draw.circle(surface, (255, 100, 100), (center_x + 8, center_y - 5), 3)
        elif self.state in ["eating", "at_desk", "idle"]:
            # Calm yellow/white eyes when idle or at desk
            pygame.draw.circle(surface, WHITE, (center_x - 8, center_y - 5), 6)
            pygame.draw.circle(surface, WHITE, (center_x + 8, center_y - 5), 6)
            pygame.draw.circle(surface, YELLOW, (center_x - 8, center_y - 5), 3)
            pygame.draw.circle(surface, YELLOW, (center_x + 8, center_y - 5), 3)
        else:
            # Default orange eyes
            pygame.draw.circle(surface, ORANGE, (center_x - 8, center_y - 5), 6)
            pygame.draw.circle(surface, ORANGE, (center_x + 8, center_y - 5), 6)
            pygame.draw.circle(surface, YELLOW, (center_x - 8, center_y - 5), 3)
            pygame.draw.circle(surface, YELLOW, (center_x + 8, center_y - 5), 3)
        
        # Name tag
        font = pygame.font.Font(None, 18)
        name_surf = font.render(self.name, True, WHITE)
        name_rect = name_surf.get_rect(centerx=screen_rect.centerx, bottom=screen_rect.top - 5)
        
        # Name background
        bg_rect = name_rect.inflate(6, 3)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=3)
        surface.blit(name_surf, name_rect)
        
        # State indicator
        if self.state == "chasing":
            pygame.draw.circle(surface, RED, (screen_rect.right - 5, screen_rect.top + 5), 5)
        elif self.state in ["eating", "at_desk"]:
            pygame.draw.circle(surface, GREEN, (screen_rect.right - 5, screen_rect.top + 5), 5)
        elif self.state == "idle":
            pygame.draw.circle(surface, YELLOW, (screen_rect.right - 5, screen_rect.top + 5), 5)


class Jonathan(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 38, 38, (200, 100, 50), "Jo-nathan")
        self.speed = 60  # Reduced from 90
        self.egg_eaten = False
        self.eating_timer = 0
        self.activation_delay = 15.0  # Wait 15 seconds before starting to chase (increased from 5)
        self.classroom_pos = (x, y)  # Remember classroom position
        
    def update(self, dt: float, player: Player, rooms: Dict, current_room: str):
        # Activation delay - Jo-nathan doesn't chase immediately
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return
        
        # If returning to classroom to eat, move there
        if self.state == "returning_to_classroom":
            old_x, old_y = self.x, self.y
            
            cx, cy = self.classroom_pos
            ex, ey = self.get_center()
            
            dx = cx - ex
            dy = cy - ey
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 10:
                dx /= dist
                dy /= dist
                self.x += dx * self.speed * 1.5 * dt  # Move faster when returning
                self.y += dy * self.speed * 1.5 * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
            else:
                # Reached classroom, start eating
                self.state = "eating"
            
            return old_x, old_y
        
        # If eating an egg, stay in classroom
        if self.eating_timer > 0:
            self.eating_timer -= dt
            self.state = "eating"
            if self.eating_timer <= 0:
                self.egg_eaten = False  # Can be fed again after eating
            return
        
        # Save old position for collision detection
        old_x, old_y = self.x, self.y
        
        # Jo-nathan always chases the player (egg just delays him temporarily)
        self.state = "chasing"
        
        # Chase player with pathfinding
        px, py = player.get_center()
        ex, ey = self.get_center()
        
        # Get current room info for pathfinding
        current_room_obj = rooms.get(self.current_room)
        if current_room_obj:
            # Use pathfinding to navigate around walls
            dx, dy = simple_pathfind((ex, ey), (px, py), 
                                    current_room_obj.walls, 
                                    current_room_obj.get_rect())
            
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
            
            # Update direction
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
        
        return old_x, old_y  # Return old position for collision revert


class Jeromathy(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 38, 38, (100, 150, 200), "Jeromathy")
        self.speed = 50  # Reduced from 70
        self.patrol_points = []
        self.current_patrol_index = 0
        self.check_snacks_timer = 0
        self.is_angry = False
        self.desk_pos = (x, y)
        self.at_desk_timer = 0
        self.activation_delay = 8.0  # Wait 8 seconds before starting patrol
        
    def update(self, dt: float, player: Player, snacks_depleted: bool, rooms: Dict):
        # Activation delay - Jeromathy stays at desk initially
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return
        
        # Save old position
        old_x, old_y = self.x, self.y
        
        self.check_snacks_timer += dt
        
        # Check snacks periodically, not immediately
        if snacks_depleted and not self.is_angry and self.check_snacks_timer > 10.0:
            self.is_angry = True
            self.state = "chasing"
            self.speed = 85  # Reduced from 110
        
        if self.is_angry:
            # Chase player across any room (removed same-room restriction)
            self.state = "chasing"
            px, py = player.get_center()
            ex, ey = self.get_center()
            
            # Get current room info for pathfinding
            current_room_obj = rooms.get(self.current_room)
            if current_room_obj:
                # Use pathfinding to navigate around walls
                dx, dy = simple_pathfind((ex, ey), (px, py), 
                                        current_room_obj.walls, 
                                        current_room_obj.get_rect())
                
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
        else:
            # Patrol or stay at desk
            self.state = "patrolling"
            self.wait_timer -= dt
            
            # Spend time at desk
            if self.at_desk_timer > 0:
                self.at_desk_timer -= dt
                # Stay at desk position
                dx_to_desk = self.desk_pos[0] - self.x
                dy_to_desk = self.desk_pos[1] - self.y
                dist_to_desk = math.sqrt(dx_to_desk * dx_to_desk + dy_to_desk * dy_to_desk)
                
                if dist_to_desk > 5:
                    dx_to_desk /= dist_to_desk
                    dy_to_desk /= dist_to_desk
                    self.x += dx_to_desk * self.speed * dt
                    self.y += dy_to_desk * self.speed * dt
            elif self.wait_timer <= 0:
                # Return to desk periodically
                self.at_desk_timer = 5.0  # Stay at desk for 5 seconds
                self.wait_timer = 10.0  # Patrol for 10 seconds
        
        return old_x, old_y


class Angellica(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 38, 38, (200, 100, 200), "Angellica")
        self.speed = 70  # Reduced from 100
        self.watching_youtube = False
        self.desk_pos = (x, y)
        self.at_desk_timer = 0
        self.patrol_timer = 0
        self.activation_delay = 10.0  # Wait 10 seconds before becoming active
        
    def update(self, dt: float, player: Player, rooms: Dict):
        # Activation delay - Angellica stays at desk initially
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return
        
        # Save old position
        old_x, old_y = self.x, self.y
        
        if player.on_youtube:
            # Chase player across any room (removed same-room restriction)
            self.state = "chasing"
            px, py = player.get_center()
            ex, ey = self.get_center()
            
            # Get current room info for pathfinding
            current_room_obj = rooms.get(self.current_room)
            if current_room_obj:
                # Use pathfinding to navigate around walls
                dx, dy = simple_pathfind((ex, ey), (px, py), 
                                        current_room_obj.walls, 
                                        current_room_obj.get_rect())
                
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
        else:
            # Patrol between desk and other locations
            self.patrol_timer += dt
            
            # Spend time at desk
            if self.at_desk_timer > 0:
                self.at_desk_timer -= dt
                self.state = "at_desk"
                
                # Move toward desk
                dx_to_desk = self.desk_pos[0] - self.x
                dy_to_desk = self.desk_pos[1] - self.y
                dist_to_desk = math.sqrt(dx_to_desk * dx_to_desk + dy_to_desk * dy_to_desk)
                
                if dist_to_desk > 5:
                    dx_to_desk /= dist_to_desk
                    dy_to_desk /= dist_to_desk
                    self.x += dx_to_desk * self.speed * 0.5 * dt  # Slower when returning
                    self.y += dy_to_desk * self.speed * 0.5 * dt
                    
                    if abs(dx_to_desk) > abs(dy_to_desk):
                        self.direction = Direction.RIGHT if dx_to_desk > 0 else Direction.LEFT
                    else:
                        self.direction = Direction.DOWN if dy_to_desk > 0 else Direction.UP
            elif self.patrol_timer > 15.0:  # Return to desk every 15 seconds
                self.at_desk_timer = 8.0  # Stay at desk for 8 seconds
                self.patrol_timer = 0
            else:
                self.state = "idle"
        
        return old_x, old_y


class NextGenIntern(Enemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 38, 38, (100, 200, 100), "NextGen Intern")
        self.speed = 60
        self.state = "idle"
        self.snack_timer = 0
        self.going_for_snack = False
        self.returning_to_classroom = False
        self.breakroom_pos: Optional[Tuple[float, float]] = None
        self.classroom_pos = (x, y)
        self.activation_delay = 15.0  # Wait 15 seconds before first snack trip
        
    def update(self, dt: float, player: Player, breakroom_pos: Tuple[float, float], 
               game_instance):
        # Activation delay
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return
        
        # Save old position
        old_x, old_y = self.x, self.y
        
        self.breakroom_pos = breakroom_pos
        self.snack_timer += dt
        
        # Randomly go for snacks every 30-60 seconds
        snack_interval = 45.0  # Average 45 seconds
        
        if not self.going_for_snack and not self.returning_to_classroom and self.snack_timer > snack_interval:
            # Time to go get a snack!
            self.going_for_snack = True
            self.state = "going_for_snack"
            self.snack_timer = 0
        
        if self.going_for_snack:
            # Move toward break room
            bx, by = self.breakroom_pos
            ex, ey = self.get_center()
            
            dx = bx - ex
            dy = by - ey
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < 50:  # Arrived at break room
                # Take a snack
                if player.inventory["snacks"] > 0:
                    player.inventory["snacks"] -= 1
                    game_instance.show_message("NextGen Intern took a snack!", 2.0)
                self.going_for_snack = False
                self.returning_to_classroom = True
                self.state = "returning"
            else:
                # Keep moving toward break room
                dx /= dist
                dy /= dist
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
        
        elif self.returning_to_classroom:
            # Move back to classroom
            cx, cy = self.classroom_pos
            ex, ey = self.get_center()
            
            dx = cx - ex
            dy = cy - ey
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < 20:  # Back at classroom
                self.returning_to_classroom = False
                self.state = "idle"
            else:
                # Keep moving toward classroom
                dx /= dist
                dy /= dist
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
        else:
            self.state = "idle"
        
        return old_x, old_y


# ============================================================
# INTERACTABLE OBJECTS
# ============================================================

class Interactable:
    def __init__(self, x: float, y: float, width: int, height: int, 
                 obj_type: InteractableType, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obj_type
        self.color = color
        self.cooldown = 0
        self.label: Optional[str] = None  # Custom label for desks
        
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def can_interact(self, player: Player) -> bool:
        player_rect = player.get_rect()
        obj_rect = self.get_rect()
        return player_rect.colliderect(obj_rect.inflate(20, 20)) and self.cooldown <= 0
    
    def interact(self, player: Player, game) -> str:
        """Returns a message to display"""
        self.cooldown = 1.0  # 1 second cooldown
        
        if self.type == InteractableType.REFRIGERATOR:
            if not player.inventory["egg"]:
                player.inventory["egg"] = True
                return "Got an egg!"
            return "Already have an egg"
        
        elif self.type == InteractableType.CABINET:
            player.inventory["snacks"] = min(5, player.inventory["snacks"] + 1)
            return f"Grabbed snacks! ({player.inventory['snacks']}/5)"
        
        elif self.type == InteractableType.CAMERA:
            game.switch_state(GameState.CAMERA)
            return "Opening cameras..."
        
        elif self.type == InteractableType.LAPTOP:
            return "Use [Y] for YouTube, [C] for coding"
        
        elif self.type == InteractableType.DESK:
            return "Jeromathy's desk"
        
        return ""
    
    def update(self, dt: float):
        if self.cooldown > 0:
            self.cooldown -= dt
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        rect = self.get_rect()
        screen_rect = pygame.Rect(
            rect.x - camera_offset[0],
            rect.y - camera_offset[1],
            rect.width,
            rect.height
        )
        
        pygame.draw.rect(surface, self.color, screen_rect, border_radius=3)
        pygame.draw.rect(surface, BLACK, screen_rect, 2, border_radius=3)
        
        # Icon/label
        font = pygame.font.Font(None, 16)
        if self.label:
            # Use custom label (for desks with names)
            text_surf = font.render(self.label, True, WHITE)
        else:
            label = self.type.value[:8]
            text_surf = font.render(label, True, WHITE)
        text_rect = text_surf.get_rect(center=screen_rect.center)
        surface.blit(text_surf, text_rect)


# ============================================================
# ROOM CLASS
# ============================================================

class Room:
    def __init__(self, room_type: RoomType, x: int, y: int, width: int, height: int):
        self.type = room_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.connections: List[Tuple[RoomType, pygame.Rect]] = []
        self.interactables: List[Interactable] = []
        self.walls: List[pygame.Rect] = []
        self.doorways: List[pygame.Rect] = []  # Track doorway locations (no walls)
        self._setup_room()
    
    def _setup_room(self):
        """Setup walls and interactables based on room type"""
        # Walls will be added with breaks for doorways in _init_game
        # For now just add interactables
        
        # Add room-specific interactables
        if self.type == RoomType.BREAK_ROOM:
            # Refrigerator (tall room, avoid doorway on right at y=150-250)
            self.interactables.append(Interactable(
                self.x + 40, self.y + 50, 60, 80, 
                InteractableType.REFRIGERATOR, (200, 200, 220)
            ))
            # Cabinet (below refrigerator, away from doorway)
            self.interactables.append(Interactable(
                self.x + 40, self.y + 280, 60, 60, 
                InteractableType.CABINET, (139, 90, 60)
            ))
        
        elif self.type == RoomType.MEETING_ROOM:
            # Camera system
            self.interactables.append(Interactable(
                self.x + self.width // 2 - 40, self.y + 50, 80, 60, 
                InteractableType.CAMERA, DARK_GRAY
            ))
        
        elif self.type == RoomType.CLASSROOM:
            # Laptop
            self.interactables.append(Interactable(
                self.x + self.width // 2 - 30, self.y + self.height // 2 - 20, 
                60, 40, InteractableType.LAPTOP, (50, 50, 60)
            ))
        
        elif self.type == RoomType.OFFICE:
            # Jeromathy's desk with label
            desk = Interactable(
                self.x + 80, self.y + 80, 80, 60, 
                InteractableType.DESK, (101, 67, 33)
            )
            desk.label = "Jeromathy"
            self.interactables.append(desk)
        
        elif self.type == RoomType.HALLWAY:
            # Angellica's desk with label
            desk = Interactable(
                self.x + 250, self.y + 100, 80, 60, 
                InteractableType.DESK, (101, 67, 33)
            )
            desk.label = "Angellica"
            self.interactables.append(desk)
    
    def add_walls_with_doorway(self, wall_side: str, doorway_start: int, doorway_end: int):
        """Add walls with a break for a doorway"""
        wall_thickness = 20
        
        if wall_side == "top":
            # Left part of top wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x, self.y, doorway_start, wall_thickness))
            # Right part of top wall
            if doorway_end < self.width:
                self.walls.append(pygame.Rect(self.x + doorway_end, self.y, 
                                              self.width - doorway_end, wall_thickness))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x + doorway_start, self.y, 
                                            doorway_end - doorway_start, wall_thickness))
        
        elif wall_side == "bottom":
            # Left part of bottom wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x, self.y + self.height - wall_thickness, 
                                              doorway_start, wall_thickness))
            # Right part of bottom wall
            if doorway_end < self.width:
                self.walls.append(pygame.Rect(self.x + doorway_end, self.y + self.height - wall_thickness, 
                                              self.width - doorway_end, wall_thickness))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x + doorway_start, self.y + self.height - wall_thickness, 
                                            doorway_end - doorway_start, wall_thickness))
        
        elif wall_side == "left":
            # Top part of left wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x, self.y, wall_thickness, doorway_start))
            # Bottom part of left wall
            if doorway_end < self.height:
                self.walls.append(pygame.Rect(self.x, self.y + doorway_end, 
                                              wall_thickness, self.height - doorway_end))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x, self.y + doorway_start, 
                                            wall_thickness, doorway_end - doorway_start))
        
        elif wall_side == "right":
            # Top part of right wall
            if doorway_start > 0:
                self.walls.append(pygame.Rect(self.x + self.width - wall_thickness, self.y, 
                                              wall_thickness, doorway_start))
            # Bottom part of right wall
            if doorway_end < self.height:
                self.walls.append(pygame.Rect(self.x + self.width - wall_thickness, self.y + doorway_end, 
                                              wall_thickness, self.height - doorway_end))
            # Track doorway location
            self.doorways.append(pygame.Rect(self.x + self.width - wall_thickness, self.y + doorway_start, 
                                            wall_thickness, doorway_end - doorway_start))
    
    def add_solid_wall(self, wall_side: str):
        """Add a solid wall with no doorway"""
        wall_thickness = 20
        
        if wall_side == "top":
            self.walls.append(pygame.Rect(self.x, self.y, self.width, wall_thickness))
        elif wall_side == "bottom":
            self.walls.append(pygame.Rect(self.x, self.y + self.height - wall_thickness, 
                                          self.width, wall_thickness))
        elif wall_side == "left":
            self.walls.append(pygame.Rect(self.x, self.y, wall_thickness, self.height))
        elif wall_side == "right":
            self.walls.append(pygame.Rect(self.x + self.width - wall_thickness, self.y, 
                                          wall_thickness, self.height))
    
    def add_door(self, to_room: RoomType, door_rect: pygame.Rect):
        """Add a connection to another room"""
        self.connections.append((to_room, door_rect))
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        # Draw floor
        floor_rect = pygame.Rect(
            self.x - camera_offset[0],
            self.y - camera_offset[1],
            self.width,
            self.height
        )
        
        # Floor color based on room type
        floor_colors = {
            RoomType.OFFICE: (80, 80, 90),
            RoomType.BREAK_ROOM: (90, 85, 75),
            RoomType.MEETING_ROOM: (75, 80, 90),
            RoomType.CLASSROOM: (85, 90, 80),
            RoomType.HALLWAY: (70, 70, 75)
        }
        floor_color = floor_colors.get(self.type, GRAY)
        pygame.draw.rect(surface, floor_color, floor_rect)
        
        # Draw walls
        for wall in self.walls:
            wall_rect = pygame.Rect(
                wall.x - camera_offset[0],
                wall.y - camera_offset[1],
                wall.width,
                wall.height
            )
            pygame.draw.rect(surface, (60, 60, 70), wall_rect)
            pygame.draw.rect(surface, (40, 40, 50), wall_rect, 2)
        
        # Draw interactables
        for interactable in self.interactables:
            interactable.draw(surface, camera_offset)
        
        # Note: Doorways are now breaks in walls, not drawn separately
        
        # Room label
        font = pygame.font.Font(None, 32)
        label_surf = font.render(self.type.value, True, WHITE)
        label_rect = label_surf.get_rect(
            centerx=self.x + self.width // 2 - camera_offset[0],
            top=self.y + 30 - camera_offset[1]
        )
        
        # Label background
        bg_rect = label_rect.inflate(20, 10)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        surface.blit(s, bg_rect)
        surface.blit(label_surf, label_rect)


# ============================================================
# PATHFINDING HELPER
# ============================================================

def simple_pathfind(enemy_pos: Tuple[float, float], target_pos: Tuple[float, float], 
                   walls: List[pygame.Rect], room_bounds: pygame.Rect) -> Tuple[float, float]:
    """
    Simple pathfinding that tries to navigate around walls.
    Returns a direction (dx, dy) to move towards.
    """
    ex, ey = enemy_pos
    tx, ty = target_pos
    
    # Direct vector to target
    dx = tx - ex
    dy = ty - ey
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist < 5:
        return 0, 0
    
    # Normalize
    dx /= dist
    dy /= dist
    
    # Check if direct path is clear (sample points along the path)
    steps = int(dist / 20)  # Check every 20 pixels
    direct_clear = True
    
    if steps > 0:
        for i in range(1, steps + 1):
            check_x = ex + (dx * dist * i / steps)
            check_y = ey + (dy * dist * i / steps)
            check_rect = pygame.Rect(check_x - 15, check_y - 15, 30, 30)
            
            for wall in walls:
                if check_rect.colliderect(wall):
                    direct_clear = False
                    break
            
            if not direct_clear:
                break
    
    # If direct path is clear, go directly
    if direct_clear:
        return dx, dy
    
    # Otherwise, try alternative directions
    # Try moving primarily along one axis at a time
    alternatives = [
        (1, 0),   # Right
        (-1, 0),  # Left
        (0, 1),   # Down
        (0, -1),  # Up
        (0.7, 0.7),   # Diagonal down-right
        (-0.7, 0.7),  # Diagonal down-left
        (0.7, -0.7),  # Diagonal up-right
        (-0.7, -0.7)  # Diagonal up-left
    ]
    
    best_dir = None
    best_score = -float('inf')
    
    for alt_dx, alt_dy in alternatives:
        # Check if this direction is blocked
        test_x = ex + alt_dx * 25
        test_y = ey + alt_dy * 25
        test_rect = pygame.Rect(test_x - 15, test_y - 15, 30, 30)
        
        blocked = False
        for wall in walls:
            if test_rect.colliderect(wall):
                blocked = True
                break
        
        if blocked or not room_bounds.collidepoint(test_x, test_y):
            continue
        
        # Score based on how much it moves us toward target
        score = alt_dx * (tx - ex) + alt_dy * (ty - ey)
        
        if score > best_score:
            best_score = score
            best_dir = (alt_dx, alt_dy)
    
    if best_dir:
        return best_dir
    
    # If all else fails, return original direction (will likely hit wall)
    return dx, dy


# ============================================================
# GAME CLASS
# ============================================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Five Nights at Rocket")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Game time
        self.current_time = 9.0  # 9:00 AM
        self.target_time = 17.0  # 5:00 PM
        self.time_speed = 1.0  # Hours per real second
        
        # Battery
        self.battery = 100
        self.max_battery = 100
        self.battery_drain_rate = 5  # Per second when cameras open (reduced from 15)
        
        # Day progression
        self.current_day = 1
        self.max_days = 5
        
        # Game objects
        self.player: Optional[Player] = None
        self.rooms: Dict[RoomType, Room] = {}
        self.current_room: RoomType = RoomType.OFFICE
        self.enemies: List[Enemy] = []
        self.particle_system = ParticleSystem()
        
        # UI
        self.message = ""
        self.message_timer = 0
        self.shake_intensity = 0
        self.fade_alpha = 0
        
        # Camera view
        self.camera_selected_room: Optional[RoomType] = None
        
        # Tutorial
        self.show_tutorial = True
        
        self._init_game()
    
    def _init_game(self):
        """Initialize game objects"""
        # Create rooms with proper layout
        # Layout: Break Room <- Office <- Hallway -> Classroom
        #                                     |
        #                                Meeting Room
        
        room_width = 450
        room_height = 400
        hallway_width = 550  # Wider hallway
        thin_room_height = 250  # Thinner height for Meeting Room
        break_room_width = 200  # Thin width for tall Break Room
        break_room_height = 400  # Tall Break Room
        
        # Horizontal layout for main path
        self.rooms[RoomType.BREAK_ROOM] = Room(RoomType.BREAK_ROOM, -100, 100, break_room_width, break_room_height)
        self.rooms[RoomType.OFFICE] = Room(RoomType.OFFICE, 100, 100, room_width, room_height)
        self.rooms[RoomType.HALLWAY] = Room(RoomType.HALLWAY, 550, 100, hallway_width, room_height)
        self.rooms[RoomType.CLASSROOM] = Room(RoomType.CLASSROOM, 1100, 100, room_width, room_height)
        self.rooms[RoomType.MEETING_ROOM] = Room(RoomType.MEETING_ROOM, 550, 500, hallway_width, thin_room_height)
        
        # Setup walls with doorways
        # Break Room: doorway on right to Office (tall and thin to left of office)
        self.rooms[RoomType.BREAK_ROOM].add_solid_wall("top")
        self.rooms[RoomType.BREAK_ROOM].add_solid_wall("left")
        self.rooms[RoomType.BREAK_ROOM].add_walls_with_doorway("right", 150, 250)  # Doorway to Office
        self.rooms[RoomType.BREAK_ROOM].add_solid_wall("bottom")
        
        # Office: doorway on left to Break Room, doorway on right to Hallway
        self.rooms[RoomType.OFFICE].add_solid_wall("top")
        self.rooms[RoomType.OFFICE].add_walls_with_doorway("left", 150, 250)  # Doorway to Break Room
        self.rooms[RoomType.OFFICE].add_solid_wall("bottom")
        self.rooms[RoomType.OFFICE].add_walls_with_doorway("right", 150, 250)  # Doorway to Hallway
        
        # Hallway: doorway on left to Office, doorway on right to Classroom, doorway on bottom to Meeting
        self.rooms[RoomType.HALLWAY].add_solid_wall("top")
        self.rooms[RoomType.HALLWAY].add_walls_with_doorway("left", 150, 250)  # Doorway to Office
        self.rooms[RoomType.HALLWAY].add_walls_with_doorway("right", 150, 250)  # Doorway to Classroom
        self.rooms[RoomType.HALLWAY].add_walls_with_doorway("bottom", 200, 350)  # Doorway to Meeting (wider for wider hallway)
        
        # Classroom: doorway on left to Hallway
        self.rooms[RoomType.CLASSROOM].add_solid_wall("top")
        self.rooms[RoomType.CLASSROOM].add_solid_wall("right")
        self.rooms[RoomType.CLASSROOM].add_solid_wall("bottom")
        self.rooms[RoomType.CLASSROOM].add_walls_with_doorway("left", 150, 250)  # Doorway to Hallway
        
        # Meeting Room: doorway on top to Hallway
        self.rooms[RoomType.MEETING_ROOM].add_walls_with_doorway("top", 200, 350)  # Doorway to Hallway (wider for wider hallway)
        self.rooms[RoomType.MEETING_ROOM].add_solid_wall("left")
        self.rooms[RoomType.MEETING_ROOM].add_solid_wall("right")
        self.rooms[RoomType.MEETING_ROOM].add_solid_wall("bottom")
        
        # Add connection info for door transitions
        # Break Room connections (left of office, tall and thin)
        door_break_office = pygame.Rect(95, 250, 10, 100)
        self.rooms[RoomType.BREAK_ROOM].add_door(RoomType.OFFICE, door_break_office)
        
        # Office connections
        self.rooms[RoomType.OFFICE].add_door(RoomType.BREAK_ROOM, door_break_office)
        door_office_hall = pygame.Rect(545, 250, 10, 100)
        self.rooms[RoomType.OFFICE].add_door(RoomType.HALLWAY, door_office_hall)
        
        # Hallway connections
        self.rooms[RoomType.HALLWAY].add_door(RoomType.OFFICE, door_office_hall)
        door_hall_classroom = pygame.Rect(1095, 250, 10, 100)
        door_hall_meeting = pygame.Rect(750, 495, 150, 10)
        self.rooms[RoomType.HALLWAY].add_door(RoomType.CLASSROOM, door_hall_classroom)
        self.rooms[RoomType.HALLWAY].add_door(RoomType.MEETING_ROOM, door_hall_meeting)
        
        # Classroom connections
        self.rooms[RoomType.CLASSROOM].add_door(RoomType.HALLWAY, door_hall_classroom)
        
        # Meeting Room connections
        self.rooms[RoomType.MEETING_ROOM].add_door(RoomType.HALLWAY, door_hall_meeting)
        
        # Create player in office
        office = self.rooms[RoomType.OFFICE]
        self.player = Player(office.x + office.width // 2, office.y + office.height // 2)
        
        # Create enemies - ONE OF EACH
        # Only create if not already in the list (prevents duplicates on day reset)
        if not self.enemies:
            # Jo-nathan in Classroom
            classroom = self.rooms[RoomType.CLASSROOM]
            jonathan = Jonathan(classroom.x + 200, classroom.y + 200)
            jonathan.current_room = RoomType.CLASSROOM
            self.enemies.append(jonathan)
            
            # Jeromathy in Office
            office = self.rooms[RoomType.OFFICE]
            jeromathy = Jeromathy(office.x + 150, office.y + 150)
            jeromathy.desk_pos = (office.x + 120, office.y + 110)
            jeromathy.current_room = RoomType.OFFICE
            self.enemies.append(jeromathy)
            
            # Angellica in Hallway
            hallway = self.rooms[RoomType.HALLWAY]
            angellica = Angellica(hallway.x + 300, hallway.y + 150)
            angellica.desk_pos = (hallway.x + 290, hallway.y + 130)
            angellica.current_room = RoomType.HALLWAY
            self.enemies.append(angellica)
            
            # NextGen Intern in Classroom
            classroom = self.rooms[RoomType.CLASSROOM]
            intern = NextGenIntern(classroom.x + 100, classroom.y + 300)
            intern.current_room = RoomType.CLASSROOM
            self.enemies.append(intern)
        else:
            # Reset enemy positions for new day
            for enemy in self.enemies:
                if isinstance(enemy, Jonathan):
                    classroom = self.rooms[RoomType.CLASSROOM]
                    enemy.x = classroom.x + 200
                    enemy.y = classroom.y + 200
                    enemy.current_room = RoomType.CLASSROOM
                    enemy.activation_delay = 5.0
                    enemy.egg_eaten = False
                    enemy.eating_timer = 0
                elif isinstance(enemy, Jeromathy):
                    office = self.rooms[RoomType.OFFICE]
                    enemy.x = office.x + 150
                    enemy.y = office.y + 150
                    enemy.desk_pos = (office.x + 120, office.y + 110)
                    enemy.current_room = RoomType.OFFICE
                    enemy.activation_delay = 8.0
                    enemy.is_angry = False
                    enemy.check_snacks_timer = 0
                elif isinstance(enemy, Angellica):
                    hallway = self.rooms[RoomType.HALLWAY]
                    enemy.x = hallway.x + 300
                    enemy.y = hallway.y + 150
                    enemy.desk_pos = (hallway.x + 290, hallway.y + 130)
                    enemy.current_room = RoomType.HALLWAY
                    enemy.activation_delay = 10.0
                elif isinstance(enemy, NextGenIntern):
                    classroom = self.rooms[RoomType.CLASSROOM]
                    enemy.x = classroom.x + 100
                    enemy.y = classroom.y + 300
                    enemy.current_room = RoomType.CLASSROOM
                    enemy.activation_delay = 15.0
                    enemy.snack_timer = 0
                    enemy.going_for_snack = False
                    enemy.returning_to_classroom = False
    
    def switch_state(self, new_state: GameState):
        self.state = new_state
        
        if new_state == GameState.CAMERA:
            self.camera_selected_room = RoomType.OFFICE
        elif new_state == GameState.PLAYING:
            self.player.on_youtube = False
    
    def show_message(self, message: str, duration: float = 2.0):
        self.message = message
        self.message_timer = duration
    
    def screen_shake(self, intensity: float = 10):
        self.shake_intensity = intensity
    
    def check_collision_with_walls(self, entity: Entity) -> bool:
        """Check if entity collides with walls in current room"""
        entity_rect = entity.get_rect()
        current_room = self.rooms[self.current_room]
        
        # Check walls in current room
        for wall in current_room.walls:
            if entity_rect.colliderect(wall):
                # Check if we're in a doorway - if so, allow movement
                in_doorway = False
                for doorway in current_room.doorways:
                    if entity_rect.colliderect(doorway):
                        in_doorway = True
                        break
                
                if not in_doorway:
                    return True
        
        return False
    
    def check_enemy_collision_with_walls(self, enemy: Enemy) -> bool:
        """Check if enemy collides with walls in their current room"""
        enemy_rect = enemy.get_rect()
        if enemy.current_room not in self.rooms:
            return True  # Safety check
        
        enemy_room = self.rooms[enemy.current_room]
        
        # Check walls in enemy's current room
        for wall in enemy_room.walls:
            if enemy_rect.colliderect(wall):
                # Check if we're in a doorway - if so, allow movement
                in_doorway = False
                for doorway in enemy_room.doorways:
                    if enemy_rect.colliderect(doorway):
                        in_doorway = True
                        break
                
                if not in_doorway:
                    return True
        
        return False
    
    def check_enemy_room_transitions(self):
        """Check if enemies move through doors and update their current_room"""
        for enemy in self.enemies:
            if enemy.current_room not in self.rooms:
                continue
            
            enemy_rect = enemy.get_rect()
            current_room = self.rooms[enemy.current_room]
            
            # Check all connections from the enemy's current room
            for to_room_type, door_rect in current_room.connections:
                if enemy_rect.colliderect(door_rect):
                    # Enemy is transitioning to a new room
                    enemy.current_room = to_room_type
                    break
    
    def check_door_transitions(self):
        """Check if player walks through a door"""
        if not self.player:
            return
        
        player_rect = self.player.get_rect()
        current_room = self.rooms[self.current_room]
        
        for to_room_type, door_rect in current_room.connections:
            if player_rect.colliderect(door_rect):
                # Transition to new room (silently, no effects)
                self.current_room = to_room_type
                break
    
    def check_enemy_collisions(self):
        """Check if any enemy catches the player"""
        if not self.player:
            return
        
        player_rect = self.player.get_rect()
        
        for enemy in self.enemies:
            # Skip NextGen Intern - they're harmless
            if isinstance(enemy, NextGenIntern):
                continue
            
            enemy_rect = enemy.get_rect()
            # Check actual collision, not just same room (enemies can chase across rooms)
            if player_rect.colliderect(enemy_rect):
                # Special case for Jonathan with egg
                if isinstance(enemy, Jonathan):
                    # If player has an egg, Jonathan takes it and returns to classroom
                    if self.player.inventory["egg"]:
                        enemy.egg_eaten = True
                        enemy.eating_timer = 10.0  # Takes 10 seconds to eat the egg
                        enemy.state = "returning_to_classroom"
                        self.player.inventory["egg"] = False
                        self.show_message("Jo-nathan took your egg and went to eat it!", 3.0)
                        
                        # Particle effect
                        ex, ey = enemy.get_center()
                        self.particle_system.emit(ex, ey, GREEN, 20, 100, 1.0)
                    else:
                        # No egg = player dies
                        self.switch_state(GameState.GAME_OVER)
                        self.screen_shake(20)
                        px, py = self.player.get_center()
                        self.particle_system.emit(px, py, RED, 30, 150, 2.0)
                
                # Jeromathy only kills when angry
                elif isinstance(enemy, Jeromathy):
                    if enemy.is_angry and enemy.state == "chasing":
                        self.switch_state(GameState.GAME_OVER)
                        self.screen_shake(20)
                        px, py = self.player.get_center()
                        self.particle_system.emit(px, py, RED, 30, 150, 2.0)
                
                # Angellica only kills when chasing (player on YouTube)
                elif isinstance(enemy, Angellica):
                    if enemy.state == "chasing" and self.player.on_youtube:
                        self.switch_state(GameState.GAME_OVER)
                        self.screen_shake(20)
                        px, py = self.player.get_center()
                        self.particle_system.emit(px, py, RED, 30, 150, 2.0)
    
    def update(self, dt: float):
        if self.state == GameState.MENU:
            self.update_menu(dt)
        elif self.state == GameState.PLAYING:
            self.update_playing(dt)
        elif self.state == GameState.CAMERA:
            self.update_camera(dt)
        elif self.state == GameState.GAME_OVER:
            self.update_game_over(dt)
        elif self.state == GameState.VICTORY:
            self.update_victory(dt)
        elif self.state == GameState.TUTORIAL:
            self.update_tutorial(dt)
        
        # Update particles
        self.particle_system.update(dt)
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
        
        # Update shake
        if self.shake_intensity > 0:
            self.shake_intensity = max(0, self.shake_intensity - dt * 30)
    
    def update_menu(self, dt: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.show_tutorial:
                self.switch_state(GameState.TUTORIAL)
            else:
                self.switch_state(GameState.PLAYING)
    
    def update_tutorial(self, dt: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.show_tutorial = False
            self.switch_state(GameState.PLAYING)
    
    def update_playing(self, dt: float):
        if not self.player:
            return
        
        # Update time
        time_multiplier = 3.0 if self.player.on_youtube else 1.0
        self.current_time += (dt / 60.0) * self.time_speed * time_multiplier
        
        # Check victory condition
        if self.current_time >= self.target_time:
            if self.current_day >= self.max_days:
                self.switch_state(GameState.VICTORY)
            else:
                self.current_day += 1
                self.current_time = 9.0
                self.battery = self.max_battery
                self.show_message(f"Day {self.current_day - 1} Complete! Starting Day {self.current_day}", 3.0)
                
                # Reset game state for new day
                self._init_game()
        
        # Player movement
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        
        # Save old position
        old_x, old_y = self.player.x, self.player.y
        
        # Move player
        self.player.move(dx, dy, dt)
        
        # Check wall collision
        if self.check_collision_with_walls(self.player):
            self.player.x, self.player.y = old_x, old_y
        
        # Check door transitions
        self.check_door_transitions()
        
        # Handle interactions
        if keys[pygame.K_e]:
            current_room = self.rooms[self.current_room]
            for interactable in current_room.interactables:
                if interactable.can_interact(self.player):
                    msg = interactable.interact(self.player, self)
                    if msg:
                        self.show_message(msg, 2.0)
        
        # Laptop special controls
        current_room = self.rooms[self.current_room]
        for interactable in current_room.interactables:
            if interactable.type == InteractableType.LAPTOP:
                if interactable.can_interact(self.player):
                    if keys[pygame.K_y]:
                        self.player.on_youtube = True
                        self.show_message("Watching YouTube... (Time moves faster!)", 2.0)
                    elif keys[pygame.K_c]:
                        self.player.on_youtube = False
                        self.show_message("Working on coding project", 2.0)
        
        # Update interactables
        for interactable in current_room.interactables:
            interactable.update(dt)
        
        # Update enemies
        snacks_depleted = self.player.inventory["snacks"] == 0
        breakroom = self.rooms[RoomType.BREAK_ROOM]
        breakroom_center = (breakroom.x + breakroom.width // 2, breakroom.y + breakroom.height // 2)
        
        for enemy in self.enemies:
            old_x, old_y = None, None
            
            if isinstance(enemy, Jonathan):
                result = enemy.update(dt, self.player, self.rooms, self.current_room)
                if result:
                    old_x, old_y = result
            elif isinstance(enemy, Jeromathy):
                result = enemy.update(dt, self.player, snacks_depleted, self.rooms)
                if result:
                    old_x, old_y = result
            elif isinstance(enemy, Angellica):
                result = enemy.update(dt, self.player, self.rooms)
                if result:
                    old_x, old_y = result
            elif isinstance(enemy, NextGenIntern):
                result = enemy.update(dt, self.player, breakroom_center, self)
                if result:
                    old_x, old_y = result
            
            # Check if enemy hit a wall in their room
            if old_x is not None and self.check_enemy_collision_with_walls(enemy):
                enemy.x = old_x
                enemy.y = old_y
        
        # Check for enemy room transitions
        self.check_enemy_room_transitions()
        
        # Check enemy collisions
        self.check_enemy_collisions()
        
        # Note: Pause is now handled in handle_events() via KEYDOWN
    
    def update_camera(self, dt: float):
        # Drain battery
        self.battery -= self.battery_drain_rate * dt
        if self.battery <= 0:
            self.battery = 0
            self.switch_state(GameState.GAME_OVER)
            self.show_message("Battery depleted!", 3.0)
            return
        
        # Switch between camera views
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_1]:
            self.camera_selected_room = RoomType.OFFICE
        elif keys[pygame.K_2]:
            self.camera_selected_room = RoomType.BREAK_ROOM
        elif keys[pygame.K_3]:
            self.camera_selected_room = RoomType.MEETING_ROOM
        elif keys[pygame.K_4]:
            self.camera_selected_room = RoomType.CLASSROOM
        elif keys[pygame.K_5]:
            self.camera_selected_room = RoomType.HALLWAY
        
        # Note: Camera close is now handled in handle_events() via KEYDOWN
    
    def update_game_over(self, dt: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Restart day
            self.current_time = 9.0
            self.battery = self.max_battery
            self._init_game()
            self.switch_state(GameState.PLAYING)
    
    def update_victory(self, dt: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Restart game
            self.current_day = 1
            self.current_time = 9.0
            self.battery = self.max_battery
            self._init_game()
            self.switch_state(GameState.MENU)
    
    def get_camera_offset(self) -> Tuple[int, int]:
        """Calculate camera offset to center on player"""
        if not self.player:
            return (0, 0)
        
        px, py = self.player.get_center()
        offset_x = px - SCREEN_WIDTH // 2
        offset_y = py - SCREEN_HEIGHT // 2
        
        # Add shake
        if self.shake_intensity > 0:
            offset_x += random.uniform(-self.shake_intensity, self.shake_intensity)
            offset_y += random.uniform(-self.shake_intensity, self.shake_intensity)
        
        return (int(offset_x), int(offset_y))
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_playing()
        elif self.state == GameState.CAMERA:
            self.draw_camera()
        elif self.state == GameState.PAUSED:
            self.draw_paused()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        elif self.state == GameState.TUTORIAL:
            self.draw_tutorial()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Title
        title_font = pygame.font.Font(None, 80)
        title_surf = title_font.render("Five Nights at Rocket", True, ORANGE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_surf = subtitle_font.render("Survive the office until 5pm", True, WHITE)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(subtitle_surf, subtitle_rect)
        
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
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text_surf, text_rect)
            y += 40
    
    def draw_tutorial(self):
        # Background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 56)
        title_surf = title_font.render("How to Survive", True, YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)
        
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
            text_rect = text_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y)
            self.screen.blit(text_surf, text_rect)
            y += 45
    
    def draw_playing(self):
        camera_offset = self.get_camera_offset()
        
        # Draw ALL rooms at once
        for room in self.rooms.values():
            room.draw(self.screen, camera_offset)
        
        # Draw ALL enemies (they're constrained to their rooms by walls anyway)
        for enemy in self.enemies:
            enemy.draw(self.screen, camera_offset)
        
        # Draw player
        if self.player:
            self.player.draw(self.screen, camera_offset)
        
        # Draw particles
        self.particle_system.draw(self.screen, camera_offset)
        
        # Draw UI
        self.draw_ui()
        
        # Draw message
        if self.message:
            self.draw_message()
    
    def draw_ui(self):
        # UI Panel
        panel_height = 100
        panel = pygame.Surface((SCREEN_WIDTH, panel_height), pygame.SRCALPHA)
        panel.fill(UI_BG)
        self.screen.blit(panel, (0, SCREEN_HEIGHT - panel_height))
        
        font = pygame.font.Font(None, 32)
        y = SCREEN_HEIGHT - panel_height + 15
        
        # Time
        hours = int(self.current_time)
        minutes = int((self.current_time - hours) * 60)
        am_pm = "AM" if hours < 12 else "PM"
        display_hours = hours if hours <= 12 else hours - 12
        time_text = f"Time: {display_hours}:{minutes:02d} {am_pm}"
        time_surf = font.render(time_text, True, YELLOW)
        self.screen.blit(time_surf, (20, y))
        
        # Battery
        battery_text = f"Battery: {int(self.battery)}%"
        battery_color = GREEN if self.battery > 50 else (ORANGE if self.battery > 20 else RED)
        battery_surf = font.render(battery_text, True, battery_color)
        self.screen.blit(battery_surf, (250, y))
        
        # Battery bar
        bar_x = 250
        bar_y = y + 35
        bar_width = 150
        bar_height = 20
        
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        fill_width = int((self.battery / self.max_battery) * bar_width)
        pygame.draw.rect(self.screen, battery_color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Day
        day_text = f"Day: {self.current_day}/5"
        day_surf = font.render(day_text, True, WHITE)
        self.screen.blit(day_surf, (480, y))
        
        # Inventory
        if self.player:
            inv_text = f"Snacks: {self.player.inventory['snacks']}"
            inv_surf = font.render(inv_text, True, WHITE)
            self.screen.blit(inv_surf, (650, y))
            
            # Egg inventory with visual icon
            if self.player.inventory["egg"]:
                # Draw egg icon
                egg_x = 820
                egg_y = y + 8
                pygame.draw.ellipse(self.screen, (240, 230, 200), (egg_x, egg_y, 24, 30))
                pygame.draw.ellipse(self.screen, (220, 210, 180), (egg_x, egg_y, 24, 30), 2)
                
                # Label
                egg_text = "Egg"
                egg_surf = font.render(egg_text, True, GREEN)
                self.screen.blit(egg_surf, (850, y))
            
            if self.player.on_youtube:
                yt_text = "YouTube ON"
                yt_surf = font.render(yt_text, True, RED)
                self.screen.blit(yt_surf, (950, y))
        
        # Current room
        room_text = f"Room: {self.current_room.value}"
        room_surf = font.render(room_text, True, LIGHT_GRAY)
        self.screen.blit(room_surf, (20, y + 35))
        
        # Interaction hint
        if self.player:
            current_room = self.rooms[self.current_room]
            for interactable in current_room.interactables:
                if interactable.can_interact(self.player):
                    hint = "[E] to interact"
                    if interactable.type == InteractableType.LAPTOP:
                        hint = "[E] interact, [Y] YouTube, [C] Code"
                    
                    hint_surf = font.render(hint, True, UI_HIGHLIGHT)
                    hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, y + 45))
                    self.screen.blit(hint_surf, hint_rect)
                    break
    
    def draw_message(self):
        font = pygame.font.Font(None, 40)
        text_surf = font.render(self.message, True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
        
        # Background
        bg_rect = text_rect.inflate(40, 20)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 200))
        self.screen.blit(bg_surf, bg_rect)
        
        # Border
        pygame.draw.rect(self.screen, YELLOW, bg_rect, 3, border_radius=5)
        
        self.screen.blit(text_surf, text_rect)
    
    def draw_camera(self):
        # Background
        self.screen.fill(BLACK)
        
        # Camera feed
        if self.camera_selected_room:
            room = self.rooms[self.camera_selected_room]
            
            # Scale and center the room view
            room_surface = pygame.Surface((room.width, room.height))
            room_surface.fill((80, 80, 90))
            
            # Draw room elements relative to room position
            temp_offset = (room.x, room.y)
            
            # Draw interactables
            for interactable in room.interactables:
                interactable.draw(room_surface, temp_offset)
            
            # Draw enemies in this room
            for enemy in self.enemies:
                if enemy.current_room == self.camera_selected_room:
                    enemy.draw(room_surface, temp_offset)
            
            # Draw player if in this room
            if self.player and self.current_room == self.camera_selected_room:
                self.player.draw(room_surface, temp_offset)
            
            # Scale to fit screen
            scale_factor = min(SCREEN_WIDTH * 0.7 / room.width, SCREEN_HEIGHT * 0.6 / room.height)
            scaled_width = int(room.width * scale_factor)
            scaled_height = int(room.height * scale_factor)
            scaled_surface = pygame.transform.scale(room_surface, (scaled_width, scaled_height))
            
            # Center on screen
            x = (SCREEN_WIDTH - scaled_width) // 2
            y = (SCREEN_HEIGHT - scaled_height) // 2 - 30
            self.screen.blit(scaled_surface, (x, y))
            
            # Camera border
            pygame.draw.rect(self.screen, GREEN, (x - 5, y - 5, scaled_width + 10, scaled_height + 10), 5)
            
            # Room label
            label_font = pygame.font.Font(None, 48)
            label_surf = label_font.render(self.camera_selected_room.value, True, GREEN)
            label_rect = label_surf.get_rect(centerx=SCREEN_WIDTH // 2, y=y - 50)
            self.screen.blit(label_surf, label_rect)
        
        # Camera selection UI
        font = pygame.font.Font(None, 28)
        y = SCREEN_HEIGHT - 120
        
        instructions = "Select Camera: [1]Office [2]Break Room [3]Meeting [4]Classroom [5]Hallway  [ESC]Close"
        inst_surf = font.render(instructions, True, WHITE)
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.screen.blit(inst_surf, inst_rect)
        
        # Battery warning
        battery_font = pygame.font.Font(None, 36)
        battery_text = f"BATTERY: {int(self.battery)}%"
        battery_color = GREEN if self.battery > 50 else (ORANGE if self.battery > 20 else RED)
        battery_surf = battery_font.render(battery_text, True, battery_color)
        battery_rect = battery_surf.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
        self.screen.blit(battery_surf, battery_rect)
        
        # Static effect for camera
        if random.random() < 0.1:
            static = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                size = random.randint(1, 3)
                alpha = random.randint(50, 150)
                color = (200, 200, 200, alpha)
                pygame.draw.circle(static, color, (x, y), size)
            self.screen.blit(static, (0, 0))
    
    def draw_paused(self):
        # Draw game behind pause menu
        self.draw_playing()
        
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        font = pygame.font.Font(None, 80)
        text_surf = font.render("PAUSED", True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text_surf, text_rect)
        
        # Resume instruction
        small_font = pygame.font.Font(None, 36)
        resume_surf = small_font.render("Press ESC to resume", True, LIGHT_GRAY)
        resume_rect = resume_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(resume_surf, resume_rect)
    
    def draw_game_over(self):
        # Red overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((139, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        font = pygame.font.Font(None, 100)
        text_surf = font.render("GAME OVER", True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text_surf, text_rect)
        
        # Reason
        reason_font = pygame.font.Font(None, 40)
        reason_text = "You didn't survive the night"
        reason_surf = reason_font.render(reason_text, True, LIGHT_GRAY)
        reason_rect = reason_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(reason_surf, reason_rect)
        
        # Restart instruction
        restart_font = pygame.font.Font(None, 32)
        restart_surf = restart_font.render("Press SPACE to restart day", True, WHITE)
        restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_surf, restart_rect)
    
    def draw_victory(self):
        # Golden overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        font = pygame.font.Font(None, 100)
        text_surf = font.render("VICTORY!", True, YELLOW)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text_surf, text_rect)
        
        # Message
        msg_font = pygame.font.Font(None, 40)
        msg_text = "You survived all 5 days at Rocket!"
        msg_surf = msg_font.render(msg_text, True, WHITE)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(msg_surf, msg_rect)
        
        # Restart instruction
        restart_font = pygame.font.Font(None, 32)
        restart_surf = restart_font.render("Press SPACE to return to menu", True, WHITE)
        restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_surf, restart_rect)
        
        # Particle celebration
        if random.random() < 0.3:
            x = random.randint(0, SCREEN_WIDTH)
            self.particle_system.emit(x, 0, random.choice([YELLOW, ORANGE, GREEN]), 5, 50, 3.0)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                # Pause toggle
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PAUSED:
                        self.switch_state(GameState.PLAYING)
                    elif self.state == GameState.PLAYING:
                        self.switch_state(GameState.PAUSED)
                    elif self.state == GameState.CAMERA:
                        self.switch_state(GameState.PLAYING)
                
                # Camera close with E
                if event.key == pygame.K_e and self.state == GameState.CAMERA:
                    self.switch_state(GameState.PLAYING)
    
    async def run(self):
        """Main game loop for pygbag compatibility"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            # Required for pygbag
            await asyncio.sleep(0)
        
        pygame.quit()


# ============================================================
# MAIN ENTRY POINT
# ============================================================

async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
