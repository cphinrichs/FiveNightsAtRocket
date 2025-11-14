"""
Five Nights at Rocket - Enemy Classes
Contains all enemy AI and behaviors
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional
from entities import Entity
from enums import Direction, RoomType
from constants import *
from sprites import create_enemy_sprite, create_name_tag


def simple_pathfind(enemy_pos: Tuple[float, float], target_pos: Tuple[float, float], 
                   walls: List[pygame.Rect], room_bounds: pygame.Rect) -> Tuple[float, float]:
    """
    Simple pathfinding that tries to navigate around walls.
    Returns a direction (dx, dy) to move towards.
    
    Args:
        enemy_pos: Current enemy position (x, y)
        target_pos: Target position (x, y)
        walls: List of wall rectangles to avoid
        room_bounds: Boundary rectangle of the room
        
    Returns:
        Tuple of (dx, dy) direction to move
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


class Enemy(Entity):
    """
    Base class for all enemy types.
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 color: Tuple[int, int, int], name: str):
        """
        Initialize an enemy.
        
        Args:
            x: Initial x position
            y: Initial y position
            width: Width of the enemy
            height: Height of the enemy
            color: RGB color tuple
            name: Name of the enemy
        """
        super().__init__(x, y, width, height, color)
        self.name = name
        self.speed = 80
        self.state = "idle"
        self.target_pos: Optional[Tuple[float, float]] = None
        self.wait_timer = 0
        self.path_timer = 0
        self.current_room: RoomType = RoomType.OFFICE  # Track which room enemy is in
        self.sprite_cache = {}  # Cache sprites for different states
        self.name_tag = create_name_tag(name)
        self.last_state = None  # Track state changes for sprite cache
        
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """
        Draw the enemy to the screen.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: Camera offset (x, y)
        """
        rect = self.get_rect()
        screen_x = rect.x - camera_offset[0]
        screen_y = rect.y - camera_offset[1]
        
        # Get or create sprite for current state
        if self.state != self.last_state:
            # Generate new sprite if state changed
            intern_id = getattr(self, 'intern_id', 1)  # Get intern_id if it exists, default to 1
            self.sprite_cache[self.state] = create_enemy_sprite(self.width, self.height, 
                                                                 self.color, self.state,
                                                                 self.name, intern_id)
            self.last_state = self.state
        
        sprite = self.sprite_cache.get(self.state)
        if not sprite:
            # Fallback: create sprite if not in cache
            intern_id = getattr(self, 'intern_id', 1)
            sprite = create_enemy_sprite(self.width, self.height, self.color, self.state,
                                        self.name, intern_id)
            self.sprite_cache[self.state] = sprite
        
        surface.blit(sprite, (screen_x, screen_y))
        
        # Draw name tag
        name_x = screen_x + self.width // 2 - self.name_tag.get_width() // 2
        name_y = screen_y - self.name_tag.get_height() - 5
        surface.blit(self.name_tag, (name_x, name_y))


class Jonathan(Enemy):
    """
    Jo-nathan: Chases the player constantly. Can be delayed by feeding him eggs.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize Jo-nathan at classroom position."""
        super().__init__(x, y, 38, 38, (200, 100, 50), "Jo-nathan")
        self.speed = 60  # Reduced from 90
        self.egg_eaten = False
        self.eating_timer = 0
        self.activation_delay = 30.0  # Wait 30 seconds before starting to chase (increased from 15)
        self.classroom_pos = (x, y)  # Remember classroom position
        
    def update(self, dt: float, player, rooms: Dict, current_room: str):
        """
        Update Jo-nathan's AI.
        
        Args:
            dt: Delta time (seconds)
            player: Player object
            rooms: Dictionary of room objects
            current_room: Current room name
            
        Returns:
            Tuple of old (x, y) position for collision detection
        """
        # Activation delay - Jo-nathan doesn't chase immediately
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return None, None  # Return tuple for consistency
        
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
            return None, None  # Return tuple for consistency
        
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
    """
    Jeromathy: Patrols the office. Gets angry when snacks are depleted.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize Jeromathy at his desk position."""
        super().__init__(x, y, 38, 38, (100, 150, 200), "Jeromathy")
        self.speed = 50  # Reduced from 70
        self.patrol_points = []
        self.current_patrol_index = 0
        self.check_snacks_timer = 0
        self.is_angry = False
        self.desk_pos = (x, y)
        self.at_desk_timer = 0
        self.activation_delay = 8.0  # Wait 8 seconds before starting patrol
        
    def update(self, dt: float, player, snacks_depleted: bool, rooms: Dict):
        """
        Update Jeromathy's AI.
        
        Args:
            dt: Delta time (seconds)
            player: Player object
            snacks_depleted: Whether snacks are depleted
            rooms: Dictionary of room objects
            
        Returns:
            Tuple of old (x, y) position for collision detection
        """
        # Activation delay - Jeromathy stays at desk initially
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return None, None  # Return tuple for consistency
        
        # Save old position
        old_x, old_y = self.x, self.y
        
        self.check_snacks_timer += dt
        
        # Check snacks periodically, not immediately
        if snacks_depleted and not self.is_angry and self.check_snacks_timer > 10.0:
            self.is_angry = True
            self.state = "chasing"
            self.speed = 85  # Reduced from 110
        
        # Calm down if snacks are refilled
        if not snacks_depleted and self.is_angry:
            self.is_angry = False
            self.state = "returning_to_desk"
            self.speed = 50  # Return to normal speed
        
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
    """
    Angellica: Gets angry when the player plays Solitaire.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize Angellica at her desk position."""
        super().__init__(x, y, 38, 38, (200, 100, 200), "Angellica")
        self.speed = 70  # Reduced from 100
        self.watching_solitaire = False
        self.desk_pos = (x, y)
        self.at_desk_timer = 0
        self.patrol_timer = 0
        self.activation_delay = 10.0  # Wait 10 seconds before becoming active
        
    def update(self, dt: float, player, rooms: Dict, last_coding_time: float):
        """
        Update Angellica's AI.
        
        Args:
            dt: Delta time (seconds)
            player: Player object
            rooms: Dictionary of room objects
            last_coding_time: Time since player last coded
            
        Returns:
            Tuple of old (x, y) position for collision detection
        """
        # Activation delay - Angellica stays at desk initially
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return None, None  # Return tuple for consistency
        
        # Save old position
        old_x, old_y = self.x, self.y
        
        # Chase player if playing Solitaire OR hasn't coded in 30+ seconds
        if player.on_solitaire or last_coding_time > 30.0:
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
    """
    NextGenIntern: Periodically goes to the break room to steal snacks.
    Doesn't harm the player directly.
    """
    
    # Class variable to track intern count for unique images
    _intern_counter = 0
    
    def __init__(self, x: float, y: float):
        """Initialize NextGenIntern at classroom position."""
        super().__init__(x, y, 38, 38, (100, 200, 100), "NextGen Intern")
        
        # Assign unique intern ID (cycles through 1, 2, 3)
        NextGenIntern._intern_counter += 1
        self.intern_id = ((NextGenIntern._intern_counter - 1) % 3) + 1
        
        self.speed = 60
        self.state = "idle"
        self.snack_timer = 0
        self.going_for_snack = False
        self.returning_to_classroom = False
        self.breakroom_pos: Optional[Tuple[float, float]] = None
        self.classroom_pos = (x, y)
        self.activation_delay = 15.0  # Wait 15 seconds before first snack trip
        
    def update(self, dt: float, player, breakroom_pos: Tuple[float, float], 
               game_instance, rooms: Dict):
        """
        Update NextGenIntern's AI.
        
        Args:
            dt: Delta time (seconds)
            player: Player object
            breakroom_pos: Position of the break room
            game_instance: Reference to Game instance for showing messages
            rooms: Dictionary of room objects
            
        Returns:
            Tuple of old (x, y) position for collision detection
        """
        # Activation delay
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return None, None  # Return tuple for consistency
        
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
                # Use pathfinding to navigate around walls
                current_room_obj = rooms.get(self.current_room)
                if current_room_obj:
                    dx, dy = simple_pathfind((ex, ey), (bx, by), 
                                            current_room_obj.walls, 
                                            current_room_obj.get_rect())
                    
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
                # Use pathfinding to navigate around walls
                current_room_obj = rooms.get(self.current_room)
                if current_room_obj:
                    dx, dy = simple_pathfind((ex, ey), (cx, cy), 
                                            current_room_obj.walls, 
                                            current_room_obj.get_rect())
                    
                    self.x += dx * self.speed * dt
                    self.y += dy * self.speed * dt
                    
                    if abs(dx) > abs(dy):
                        self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                    else:
                        self.direction = Direction.DOWN if dy > 0 else Direction.UP
        else:
            self.state = "idle"
        
        return old_x, old_y


class Runnit(Enemy):
    """
    Runnit: A fast, unpredictable enemy that randomly sprints through rooms.
    Only dangerous when sprinting. Uses hit-and-run tactics.
    """
    
    def __init__(self, x: float, y: float):
        """Initialize Runnit at meeting room position."""
        super().__init__(x, y, 35, 35, (180, 50, 200), "Runnit")
        self.speed = 40  # Normal speed
        self.sprint_speed = 200  # Very fast when sprinting
        self.is_sprinting = False
        self.sprint_timer = 0
        self.sprint_duration = 3.0  # Sprints for 3 seconds
        self.sprint_cooldown = 0
        self.sprint_cooldown_duration = 10.0  # 10 seconds between sprints
        self.activation_delay = 20.0  # Wait 20 seconds before first sprint
        self.home_pos = (x, y)  # Meeting room home position
        self.sprint_target = None  # Where to sprint to
        
    def update(self, dt: float, player, rooms: Dict):
        """
        Update Runnit's AI.
        
        Args:
            dt: Delta time (seconds)
            player: Player object
            rooms: Dictionary of room objects
            
        Returns:
            Tuple of old (x, y) position for collision detection
        """
        old_x, old_y = self.x, self.y
        
        # Activation delay
        if self.activation_delay > 0:
            self.activation_delay -= dt
            self.state = "idle"
            return old_x, old_y
        
        # Update sprint cooldown
        if self.sprint_cooldown > 0:
            self.sprint_cooldown -= dt
        
        # Check if should start sprinting
        if not self.is_sprinting and self.sprint_cooldown <= 0:
            # Pick a random room to sprint to
            import random
            target_rooms = [RoomType.OFFICE, RoomType.HALLWAY, RoomType.CLASSROOM, RoomType.BREAK_ROOM]
            target_room = random.choice(target_rooms)
            target_room_obj = rooms.get(target_room)
            
            if target_room_obj:
                # Pick random position in that room
                self.sprint_target = (
                    target_room_obj.x + target_room_obj.width // 2,
                    target_room_obj.y + target_room_obj.height // 2
                )
                self.is_sprinting = True
                self.sprint_timer = self.sprint_duration
                self.state = "sprinting"
        
        # Sprinting behavior
        if self.is_sprinting:
            self.sprint_timer -= dt
            
            if self.sprint_timer <= 0:
                # Sprint over, return home
                self.is_sprinting = False
                self.sprint_cooldown = self.sprint_cooldown_duration
                self.sprint_target = self.home_pos
                self.state = "returning_home"
            else:
                # Sprint towards target
                if self.sprint_target:
                    ex, ey = self.get_center()
                    tx, ty = self.sprint_target
                    
                    dx = tx - ex
                    dy = ty - ey
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    if dist > 10:
                        dx /= dist
                        dy /= dist
                        
                        # Use pathfinding
                        current_room_obj = rooms.get(self.current_room)
                        if current_room_obj:
                            dx, dy = simple_pathfind((ex, ey), (tx, ty),
                                                    current_room_obj.walls,
                                                    current_room_obj.get_rect())
                        
                        self.x += dx * self.sprint_speed * dt
                        self.y += dy * self.sprint_speed * dt
                        
                        if abs(dx) > abs(dy):
                            self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                        else:
                            self.direction = Direction.DOWN if dy > 0 else Direction.UP
                    else:
                        # Reached target, pick new target
                        import random
                        target_rooms = [RoomType.OFFICE, RoomType.HALLWAY, RoomType.CLASSROOM, RoomType.BREAK_ROOM]
                        target_room = random.choice(target_rooms)
                        target_room_obj = rooms.get(target_room)
                        if target_room_obj:
                            self.sprint_target = (
                                target_room_obj.x + target_room_obj.width // 2,
                                target_room_obj.y + target_room_obj.height // 2
                            )
        
        # Returning home
        elif self.state == "returning_home":
            ex, ey = self.get_center()
            hx, hy = self.home_pos
            
            dx = hx - ex
            dy = hy - ey
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < 20:
                # Back home, idle
                self.state = "idle"
            else:
                dx /= dist
                dy /= dist
                
                # Use pathfinding
                current_room_obj = rooms.get(self.current_room)
                if current_room_obj:
                    dx, dy = simple_pathfind((ex, ey), (hx, hy),
                                            current_room_obj.walls,
                                            current_room_obj.get_rect())
                
                self.x += dx * self.speed * dt
                self.y += dy * self.speed * dt
                
                if abs(dx) > abs(dy):
                    self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
                else:
                    self.direction = Direction.DOWN if dy > 0 else Direction.UP
        else:
            # Idle at home
            self.state = "idle"
        
        return old_x, old_y
