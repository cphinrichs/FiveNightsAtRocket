"""
MODEL LAYER - Game Data and Business Logic
===========================================
This module contains all game entities, their data, and behavior logic.
Models are responsible for:
- Storing game state (positions, health, inventory, etc.)
- Entity behavior (movement, pathfinding, AI logic)
- Game rules and validation
- No rendering or input handling (that's View and Controller)
"""

import pygame
import math
import random
from enum import Enum
from typing import Dict, List, Tuple, Optional


# ============================================================
# ENUMERATIONS - Define game constants and types
# ============================================================

class GameState(Enum):
    """Represents the current state/screen of the game"""
    MENU = 1           # Main menu screen
    PLAYING = 2        # Active gameplay
    CAMERA = 3         # Camera view mode
    PAUSED = 4         # Game paused
    GAME_OVER = 5      # Player lost
    VICTORY = 6        # Player won
    TUTORIAL = 7       # Tutorial/help screen


class RoomType(Enum):
    """Types of rooms in the office building"""
    OFFICE = "Office"
    BREAK_ROOM = "Break Room"
    MEETING_ROOM = "Meeting Room"
    CLASSROOM = "Classroom"
    HALLWAY = "Hallway"


class Direction(Enum):
    """Cardinal directions for entity movement and facing"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class InteractableType(Enum):
    """Types of objects the player can interact with"""
    REFRIGERATOR = "refrigerator"  # Gives eggs
    CABINET = "cabinet"            # Gives snacks
    CAMERA = "camera"              # Opens camera view
    LAPTOP = "laptop"              # For YouTube/coding
    DESK = "desk"                  # Just decoration
    DOOR = "door"                  # Room transitions


# ============================================================
# PARTICLE SYSTEM - Visual effects particles
# ============================================================

class Particle:
    """
    Represents a single particle for visual effects.
    Particles move, fade out, and disappear after their lifetime expires.
    """
    
    def __init__(self, x: float, y: float, dx: float, dy: float, 
                 color: Tuple[int, int, int], lifetime: float, size: float = 4):
        """
        Initialize a particle.
        
        Args:
            x, y: Starting position
            dx, dy: Velocity (pixels per second)
            color: RGB color tuple
            lifetime: How long particle exists (seconds)
            size: Radius of particle circle
        """
        self.x = x
        self.y = y
        self.dx = dx  # Velocity in X
        self.dy = dy  # Velocity in Y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255  # Transparency (255 = opaque, 0 = invisible)

    def update(self, dt: float):
        """
        Update particle position and lifetime.
        
        Args:
            dt: Delta time (time since last frame in seconds)
        """
        # Move particle
        self.x += self.dx * dt
        self.y += self.dy * dt
        
        # Reduce lifetime
        self.lifetime -= dt
        
        # Fade out as lifetime decreases
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Apply friction/damping to velocity
        self.dx *= 0.95
        self.dy *= 0.95

    def is_alive(self) -> bool:
        """Check if particle should still exist"""
        return self.lifetime > 0


class ParticleEmitter:
    """
    Manages a collection of particles.
    Creates particle effects at specified locations.
    """
    
    def __init__(self):
        """Initialize the particle system"""
        self.particles: List[Particle] = []

    def emit(self, x: float, y: float, color: Tuple[int, int, int], 
             count: int = 10, spread: float = 100, lifetime: float = 1.0):
        """
        Create a burst of particles.
        
        Args:
            x, y: Position to emit from
            color: Color of particles
            count: Number of particles to create
            spread: Maximum velocity of particles
            lifetime: How long particles live
        """
        for _ in range(count):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, spread)
            
            # Convert polar to cartesian
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            
            # Random size
            size = random.uniform(2, 6)
            
            # Create and add particle
            particle = Particle(x, y, dx, dy, color, lifetime, size)
            self.particles.append(particle)

    def update(self, dt: float):
        """
        Update all particles and remove dead ones.
        
        Args:
            dt: Delta time
        """
        # Update each particle
        for particle in self.particles[:]:  # Copy list to safely remove during iteration
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)


# ============================================================
# BASE ENTITY CLASS - Foundation for all game objects
# ============================================================

class Entity:
    """
    Base class for all game entities (player, enemies, interactables).
    Provides common functionality like position, size, and collision.
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 color: Tuple[int, int, int]):
        """
        Initialize an entity.
        
        Args:
            x, y: Position in world coordinates
            width, height: Size of entity
            color: RGB color for rendering
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 150  # Default movement speed (pixels/second)
        self.direction = Direction.DOWN  # Default facing direction
        
    def get_rect(self) -> pygame.Rect:
        """
        Get the collision rectangle for this entity.
        
        Returns:
            pygame.Rect: Rectangle for collision detection
        """
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def get_center(self) -> Tuple[float, float]:
        """
        Get the center point of this entity.
        
        Returns:
            Tuple of (center_x, center_y)
        """
        return (self.x + self.width / 2, self.y + self.height / 2)


# ============================================================
# PLAYER MODEL - Represents the player character
# ============================================================

class Player(Entity):
    """
    The player character controlled by the user.
    Manages inventory, movement, and interaction state.
    """
    
    def __init__(self, x: float, y: float):
        """
        Initialize the player.
        
        Args:
            x, y: Starting position
        """
        super().__init__(x, y, 40, 40, (50, 150, 220))  # Blue color
        
        # Player-specific attributes
        self.inventory = {
            "snacks": 5,    # Food for Jeromathy (starts full)
            "egg": False    # Egg for Jo-nathan (boolean flag)
        }
        self.on_youtube = False  # Is player watching YouTube?
        self.speed = 200         # Player moves faster than enemies
        
    def move(self, dx: float, dy: float, dt: float):
        """
        Move the player by a given direction vector.
        Normalizes diagonal movement to prevent faster diagonal speed.
        
        Args:
            dx, dy: Direction vector (-1 to 1)
            dt: Delta time for frame-rate independent movement
        """
        if dx != 0 or dy != 0:
            # Normalize diagonal movement
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
            
            # Apply movement
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
            
            # Update facing direction (prioritize horizontal)
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            elif dy != 0:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP


# ============================================================
# ENEMY MODELS - AI-controlled antagonists
# ============================================================

class Enemy(Entity):
    """
    Base class for all enemy types.
    Enemies chase the player, navigate rooms, and have different behaviors.
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 color: Tuple[int, int, int], name: str):
        """
        Initialize an enemy.
        
        Args:
            x, y: Starting position
            width, height: Size
            color: RGB color
            name: Display name
        """
        super().__init__(x, y, width, height, color)
        self.name = name
        self.speed = 80
        self.state = "idle"  # Current behavior state
        self.target_pos: Optional[Tuple[float, float]] = None  # Where enemy is moving to
        self.wait_timer = 0  # Time before next action
        self.path_timer = 0  # Time since last pathfinding update
        self.current_room: RoomType = RoomType.OFFICE  # Which room enemy is in


class Jonathan(Enemy):
    """
    Jo-nathan: The relentless chaser.
    Always pursues the player unless given an egg to eat.
    Takes eggs back to classroom before resuming chase.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize Jo-nathan in the classroom"""
        super().__init__(x, y, 38, 38, (200, 100, 50), "Jo-nathan")
        self.speed = 60  # Slower than player but persistent
        self.egg_eaten = False  # Has he been fed recently?
        self.eating_timer = 0   # Time remaining while eating
        self.activation_delay = 15.0  # Seconds before he starts chasing
        self.classroom_pos = (x, y)   # Remember home position
        
    def update(self, dt: float, player: Player, rooms: Dict, current_room: str):
        """
        Update Jo-nathan's behavior each frame.
        
        Args:
            dt: Delta time
            player: Player reference for chasing
            rooms: Dictionary of all rooms for pathfinding
            current_room: Current room identifier
        """
        # Activation delay - don't chase immediately at game start
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return
        
        # If returning to classroom to eat egg
        if self.state == "returning_to_classroom":
            old_x, old_y = self.x, self.y
            
            # Move toward classroom
            cx, cy = self.classroom_pos
            ex, ey = self.get_center()
            
            dx = cx - ex
            dy = cy - ey
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 10:
                # Still moving toward classroom
                dx /= dist
                dy /= dist
                self.x += dx * self.speed * 1.5 * dt  # Move faster when returning
                self.y += dy * self.speed * 1.5 * dt
                
                # Update facing direction
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
            else:
                # Reached classroom, start eating
                self.state = "eating"
                self.eating_timer = 10.0  # Takes 10 seconds to eat
            
            return old_x, old_y
        
        # If eating an egg, stay in classroom
        if self.eating_timer > 0:
            self.eating_timer -= dt
            self.state = "eating"
            if self.eating_timer <= 0:
                self.egg_eaten = False  # Can be fed again after eating
            return
        
        # Save old position for collision revert
        old_x, old_y = self.x, self.y
        
        # Default behavior: always chase the player
        self.state = "chasing"
        
        # Use pathfinding to chase player
        px, py = player.get_center()
        ex, ey = self.get_center()
        
        # Get current room for pathfinding
        current_room_obj = rooms.get(self.current_room)
        if current_room_obj:
            # Use pathfinding to navigate around walls
            from pathfinding import simple_pathfind
            dx, dy = simple_pathfind((ex, ey), (px, py), 
                                    current_room_obj.walls, 
                                    current_room_obj.get_rect())
            
            # Apply movement
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt
            
            # Update direction
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
        
        return old_x, old_y  # Return old position for collision handling


class Jeromathy(Enemy):
    """
    Jeromathy: The snack thief.
    Steals snacks from cabinet. Chases player when snacks run out.
    Returns to desk when snacks are replenished.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize Jeromathy at his desk"""
        super().__init__(x, y, 38, 38, (100, 180, 100), "Jeromathy")
        self.speed = 70
        self.activation_delay = 20.0  # Wait 20 seconds before activating
        self.desk_pos = (x, y)        # Remember desk position
        self.at_desk = True           # Starts at desk
        self.target_snacks = 0        # Snacks level that triggers him
        
    def update(self, dt: float, player: Player, rooms: Dict, current_room: str):
        """
        Update Jeromathy's behavior.
        Activates when snacks hit 0, returns to desk when snacks > 0.
        """
        # Activation delay
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "at_desk"
            return
        
        # Check if should chase or return to desk
        if player.inventory["snacks"] <= 0 and not self.at_desk:
            # Chase player when out of snacks
            self.state = "chasing"
            old_x, old_y = self.x, self.y
            
            # Pathfind toward player
            px, py = player.get_center()
            ex, ey = self.get_center()
            
            current_room_obj = rooms.get(self.current_room)
            if current_room_obj:
                from pathfinding import simple_pathfind
                dx, dy = simple_pathfind((ex, ey), (px, py), 
                                        current_room_obj.walls, 
                                        current_room_obj.get_rect())
                
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
            
            return old_x, old_y
            
        elif player.inventory["snacks"] > 0 and not self.at_desk:
            # Return to desk when snacks available
            self.state = "returning"
            old_x, old_y = self.x, self.y
            
            dx_desk, dy_desk = self.desk_pos
            ex, ey = self.get_center()
            
            dx = dx_desk - ex
            dy = dy_desk - ey
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 10:
                dx /= dist
                dy /= dist
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
            else:
                self.at_desk = True
                self.state = "at_desk"
            
            return old_x, old_y
        else:
            # Stay at desk
            self.state = "at_desk"
            self.at_desk = True


class Angellica(Enemy):
    """
    Angellica: The productivity monitor.
    Activates when player watches YouTube instead of working.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize Angellica in the meeting room"""
        super().__init__(x, y, 38, 38, (180, 100, 180), "Angellica")
        self.speed = 85
        self.activation_delay = 25.0  # Wait 25 seconds
        self.youtube_trigger_time = 5.0  # Activates after 5 seconds of YouTube
        self.youtube_timer = 0  # How long player has been on YouTube
        
    def update(self, dt: float, player: Player, rooms: Dict, current_room: str):
        """
        Update Angellica's behavior.
        Tracks YouTube usage and chases player if they watch too long.
        """
        # Activation delay
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return
        
        # Track YouTube time
        if player.on_youtube:
            self.youtube_timer += dt
        else:
            # Reset timer if player stops watching
            self.youtube_timer = max(0, self.youtube_timer - dt * 2)  # Forgiveness decay
        
        # Activate if player watches too long
        if self.youtube_timer >= self.youtube_trigger_time:
            self.state = "chasing"
            old_x, old_y = self.x, self.y
            
            # Chase player
            px, py = player.get_center()
            ex, ey = self.get_center()
            
            current_room_obj = rooms.get(self.current_room)
            if current_room_obj:
                from pathfinding import simple_pathfind
                dx, dy = simple_pathfind((ex, ey), (px, py), 
                                        current_room_obj.walls, 
                                        current_room_obj.get_rect())
                
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
            
            return old_x, old_y
        else:
            self.state = "idle"


class NextGenIntern(Enemy):
    """
    NextGen Intern: The snack thief.
    Randomly takes snacks but doesn't harm the player.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize the intern in a random room"""
        super().__init__(x, y, 35, 35, (255, 200, 100), "NextGen Intern")
        self.speed = 100  # Fast but harmless
        self.activation_delay = 10.0
        self.snack_timer = 0
        self.snack_interval = random.uniform(15, 30)  # Time between snack attempts
        
    def update(self, dt: float, player: Player, rooms: Dict, current_room: str):
        """
        Update intern behavior.
        Randomly steals snacks from player.
        """
        # Activation delay
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return
        
        # Snack stealing timer
        self.snack_timer += dt
        if self.snack_timer >= self.snack_interval:
            # Try to steal a snack
            if player.inventory["snacks"] > 0:
                player.inventory["snacks"] -= 1
                # Reset timer with new random interval
                self.snack_interval = random.uniform(15, 30)
            self.snack_timer = 0
        
        # Just wander around (idle behavior)
        self.state = "idle"


# ============================================================
# INTERACTABLE OBJECTS - Things player can interact with
# ============================================================

class Interactable:
    """
    Objects in the game world that the player can interact with.
    Examples: refrigerator, cabinet, camera, laptop, desk.
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 obj_type: InteractableType, color: Tuple[int, int, int]):
        """
        Initialize an interactable object.
        
        Args:
            x, y: Position in world
            width, height: Size
            obj_type: Type of interactable
            color: RGB color
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obj_type
        self.color = color
        self.cooldown = 0  # Prevent spam interaction
        self.label: Optional[str] = None  # Custom label for desks
        self.sprite = None  # Sprite will be generated by view
        
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle"""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def can_interact(self, player: Player) -> bool:
        """
        Check if player is close enough to interact.
        
        Args:
            player: Player entity
            
        Returns:
            True if player can interact with this object
        """
        player_rect = player.get_rect()
        obj_rect = self.get_rect()
        # Check if player is within interaction range (inflated by 20 pixels)
        return player_rect.colliderect(obj_rect.inflate(20, 20)) and self.cooldown <= 0
    
    def interact(self, player: Player, game) -> str:
        """
        Perform the interaction.
        
        Args:
            player: Player entity
            game: Game controller reference
            
        Returns:
            Message to display to player
        """
        self.cooldown = 1.0  # 1 second cooldown
        
        if self.type == InteractableType.REFRIGERATOR:
            # Give egg if player doesn't have one
            if not player.inventory["egg"]:
                player.inventory["egg"] = True
                return "Got an egg!"
            return "Already have an egg"
        
        elif self.type == InteractableType.CABINET:
            # Give snacks (max 5)
            player.inventory["snacks"] = min(5, player.inventory["snacks"] + 1)
            return f"Grabbed snacks! ({player.inventory['snacks']}/5)"
        
        elif self.type == InteractableType.CAMERA:
            # Switch to camera view
            game.switch_state(GameState.CAMERA)
            return "Opening cameras..."
        
        elif self.type == InteractableType.LAPTOP:
            # Laptop interaction message
            return "Use [Y] for YouTube, [C] for coding"
        
        elif self.type == InteractableType.DESK:
            # Just a desk
            return "Jeromathy's desk"
        
        return ""
    
    def update(self, dt: float):
        """
        Update cooldown timer.
        
        Args:
            dt: Delta time
        """
        if self.cooldown > 0:
            self.cooldown -= dt


# ============================================================
# ROOM MODEL - Represents a room in the office
# ============================================================

class Room:
    """
    A room in the office building.
    Contains walls, doorways, and interactable objects.
    """
    
    def __init__(self, room_type: RoomType, x: int, y: int, width: int, height: int):
        """
        Initialize a room.
        
        Args:
            room_type: Type of room (Office, Classroom, etc.)
            x, y: Position in world coordinates
            width, height: Size of room
        """
        self.type = room_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.connections: List[Tuple[RoomType, pygame.Rect]] = []  # Connected rooms
        self.interactables: List[Interactable] = []  # Objects in this room
        self.walls: List[pygame.Rect] = []  # Wall collision rectangles
        self.doorways: List[pygame.Rect] = []  # Doorway positions (no walls)
        self._setup_room()
    
    def _setup_room(self):
        """
        Setup room-specific interactables.
        Walls are added later by the game controller.
        """
        # Add interactables based on room type
        if self.type == RoomType.BREAK_ROOM:
            # Refrigerator (gives eggs)
            self.interactables.append(Interactable(
                self.x + 40, self.y + 50, 60, 80, 
                InteractableType.REFRIGERATOR, (200, 200, 220)
            ))
            # Cabinet (gives snacks)
            self.interactables.append(Interactable(
                self.x + 40, self.y + 280, 60, 60, 
                InteractableType.CABINET, (139, 90, 60)
            ))
        
        elif self.type == RoomType.MEETING_ROOM:
            # Camera system
            self.interactables.append(Interactable(
                self.x + self.width // 2 - 40, self.y + 50, 80, 60, 
                InteractableType.CAMERA, (64, 64, 64)
            ))
        
        elif self.type == RoomType.CLASSROOM:
            # Laptop for YouTube/coding
            self.interactables.append(Interactable(
                self.x + 50, self.y + 50, 80, 60, 
                InteractableType.LAPTOP, (40, 40, 60)
            ))
        
        elif self.type == RoomType.OFFICE:
            # Jeromathy's desk
            desk = Interactable(
                self.x + self.width - 120, self.y + 50, 80, 60, 
                InteractableType.DESK, (101, 67, 33)
            )
            desk.label = "Jeromathy"
            self.interactables.append(desk)
    
    def get_rect(self) -> pygame.Rect:
        """Get the bounding rectangle of the room"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def add_wall(self, wall_rect: pygame.Rect):
        """Add a wall collision rectangle to this room"""
        self.walls.append(wall_rect)
    
    def add_doorway(self, doorway_rect: pygame.Rect):
        """Add a doorway (opening) to this room"""
        self.doorways.append(doorway_rect)
    
    def add_connection(self, other_room: RoomType, doorway: pygame.Rect):
        """
        Connect this room to another room via a doorway.
        
        Args:
            other_room: The connected room type
            doorway: Rectangle representing the doorway position
        """
        self.connections.append((other_room, doorway))
