"""
Nine to Five at Rocket - A survival game with strategy and time management
Navigate the office, avoid enemies, manage resources, and survive until 5pm
"""

import asyncio
import pygame
import sys
from typing import Dict, List, Tuple, Optional
import math
import random

# Import from our modules
from enums import GameState, RoomType, Direction, InteractableType
from constants import *
from sprites import create_player_sprite, create_enemy_sprite, create_interactable_sprite, create_name_tag
from particles import Particle, ParticleSystem
from entities import Entity, Player
from enemies import Enemy, Jonathan, Jeromathy, Angellica, NextGenIntern, simple_pathfind
from interactable import Interactable
from room import Room

# Initialize Pygame
pygame.init()


# ============================================================
# GAME CLASS
# ============================================================

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nine to Five at Rocket")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Game time
        self.current_time = 9.0  # 9:00 AM
        self.target_time = 17.0  # 5:00 PM
        self.time_speed = 1.0  # Hours per real second
        
        # Bandwidth
        self.bandwidth = 100
        self.max_bandwidth = 100
        self.bandwidth_drain_rate = 2  # Per second when cameras open (reduced from 5)
        self.bandwidth_refill_rate = 0.5  # Per second when cameras closed (1/20 of original)
        
        # Day progression
        self.current_day = 1
        self.max_days = 1  # Changed from 5 to 1 - single day only
        
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
        
        # Hallway camera background
        self.hallway_bg_image = None
        self.hallway_bg_offset = 0.0
        self.load_hallway_background()
        
        # Break room camera background
        self.breakroom_bg_image = None
        self.breakroom_bg_offset = 0.0
        self.load_breakroom_background()
        
        # Office camera background
        self.office_bg_image = None
        self.office_bg_offset = 0.0
        self.load_office_background()
        
        # Classroom camera background
        self.classroom_bg_image = None
        self.classroom_bg_offset = 0.0
        self.load_classroom_background()
        
        # Tutorial
        self.show_tutorial = True
        
        # Room transition tracking (to prevent jitter)
        self.room_transition_cooldown = 0.0
        
        # Angellica's timer for coding requirement
        self.last_coding_time = 0.0
        
        self._init_game()
    
    def load_hallway_background(self):
        """Load the hallway background image for camera view"""
        try:
            # Pygbag-compatible path handling
            try:
                # Try relative path first (works in pygbag)
                self.hallway_bg_image = pygame.image.load('images/hallway.jpg').convert()
                print(f"Loaded hallway background from images/hallway.jpg")
            except:
                # Fallback to absolute path (works in desktop)
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(current_dir, 'images', 'hallway.jpg')
                self.hallway_bg_image = pygame.image.load(image_path).convert()
                print(f"Loaded hallway background from {image_path}")
        except Exception as e:
            print(f"Error loading hallway background: {e}")
            self.hallway_bg_image = None
    
    def load_breakroom_background(self):
        """Load the break room background image for camera view"""
        try:
            # Pygbag-compatible path handling
            try:
                # Try relative path first (works in pygbag)
                self.breakroom_bg_image = pygame.image.load('images/break_room.jpg').convert()
                print(f"Loaded break room background from images/break_room.jpg")
            except:
                # Fallback to absolute path (works in desktop)
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(current_dir, 'images', 'break_room.jpg')
                self.breakroom_bg_image = pygame.image.load(image_path).convert()
                print(f"Loaded break room background from {image_path}")
        except Exception as e:
            print(f"Error loading break room background: {e}")
            self.breakroom_bg_image = None
    
    def load_office_background(self):
        """Load the office background image for camera view"""
        try:
            # Pygbag-compatible path handling
            try:
                # Try relative path first (works in pygbag)
                self.office_bg_image = pygame.image.load('images/office.jpg').convert()
                print(f"Loaded office background from images/office.jpg")
            except:
                # Fallback to absolute path (works in desktop)
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(current_dir, 'images', 'office.jpg')
                self.office_bg_image = pygame.image.load(image_path).convert()
                print(f"Loaded office background from {image_path}")
        except Exception as e:
            print(f"Error loading office background: {e}")
            self.office_bg_image = None
    
    def load_classroom_background(self):
        """Load the classroom background image for camera view"""
        try:
            # Pygbag-compatible path handling
            try:
                # Try relative path first (works in pygbag)
                self.classroom_bg_image = pygame.image.load('images/classroom.jpg').convert()
                print(f"Loaded classroom background from images/classroom.jpg")
            except:
                # Fallback to absolute path (works in desktop)
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(current_dir, 'images', 'classroom.jpg')
                self.classroom_bg_image = pygame.image.load(image_path).convert()
                print(f"Loaded classroom background from {image_path}")
        except Exception as e:
            print(f"Error loading classroom background: {e}")
            self.classroom_bg_image = None
    
    def _init_game(self):
        """Initialize game objects"""
        # Create rooms with proper layout
        # Layout: Break Room <- Office <- Hallway -> Classroom
        #                                     |
        #                                Meeting Room
        
        room_width = 450
        room_height = 400
        hallway_width = 550  # Wider hallway
        hallway_height = 300  # Thinner height for hallway (reduced from 400)
        meeting_room_width = 400  # Thinner width for meeting room (reduced from 550)
        meeting_room_height = 250  # Thinner height for Meeting Room
        break_room_width = 200  # Thin width for tall Break Room
        break_room_height = 400  # Tall Break Room
        
        # Horizontal layout for main path
        self.rooms[RoomType.BREAK_ROOM] = Room(RoomType.BREAK_ROOM, -100, 100, break_room_width, break_room_height)
        self.rooms[RoomType.OFFICE] = Room(RoomType.OFFICE, 100, 100, room_width, room_height)
        self.rooms[RoomType.HALLWAY] = Room(RoomType.HALLWAY, 550, 100, hallway_width, hallway_height)
        self.rooms[RoomType.CLASSROOM] = Room(RoomType.CLASSROOM, 1100, 100, room_width, room_height)
        self.rooms[RoomType.MEETING_ROOM] = Room(RoomType.MEETING_ROOM, 625, 400, meeting_room_width, meeting_room_height)
        
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
        self.rooms[RoomType.HALLWAY].add_walls_with_doorway("bottom", 150, 350)  # Doorway to Meeting (centered, 200px wide)
        
        # Classroom: doorway on left to Hallway
        self.rooms[RoomType.CLASSROOM].add_solid_wall("top")
        self.rooms[RoomType.CLASSROOM].add_solid_wall("right")
        self.rooms[RoomType.CLASSROOM].add_solid_wall("bottom")
        self.rooms[RoomType.CLASSROOM].add_walls_with_doorway("left", 150, 250)  # Doorway to Hallway
        
        # Meeting Room: doorway on top to Hallway (aligned with hallway's bottom doorway)
        self.rooms[RoomType.MEETING_ROOM].add_walls_with_doorway("top", 75, 275)  # Doorway to Hallway (200px wide, centered)
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
        
        # Hallway connections (adjusted for hallway at y=100, meeting room at y=400)
        self.rooms[RoomType.HALLWAY].add_door(RoomType.OFFICE, door_office_hall)
        door_hall_classroom = pygame.Rect(1095, 250, 10, 100)
        door_hall_meeting = pygame.Rect(700, 395, 200, 10)  # Centered between x=700-900, at y=400 junction
        self.rooms[RoomType.HALLWAY].add_door(RoomType.CLASSROOM, door_hall_classroom)
        self.rooms[RoomType.HALLWAY].add_door(RoomType.MEETING_ROOM, door_hall_meeting)
        
        # Classroom connections
        self.rooms[RoomType.CLASSROOM].add_door(RoomType.HALLWAY, door_hall_classroom)
        
        # Meeting Room connections
        self.rooms[RoomType.MEETING_ROOM].add_door(RoomType.HALLWAY, door_hall_meeting)
        
        # Create player in classroom near the laptop
        classroom = self.rooms[RoomType.CLASSROOM]
        # Laptop is at x + width/2 - 30, y + height/2 - 20
        # Position player slightly to the right of the laptop
        laptop_x = classroom.x + classroom.width // 2 - 30
        laptop_y = classroom.y + classroom.height // 2 - 20
        self.player = Player(laptop_x + 100, laptop_y + 20)
        self.current_room = RoomType.CLASSROOM
        
        # Create enemies - ONE OF EACH
        # Only create if not already in the list (prevents duplicates on day reset)
        if not self.enemies:
            # Jo-nathan in Classroom (bottom left corner at his desk)
            classroom = self.rooms[RoomType.CLASSROOM]
            jonathan = Jonathan(classroom.x + 60, classroom.y + classroom.height - 80)
            jonathan.current_room = RoomType.CLASSROOM
            self.enemies.append(jonathan)
            
            # Jeromathy in Office
            office = self.rooms[RoomType.OFFICE]
            jeromathy = Jeromathy(office.x + 150, office.y + 150)
            jeromathy.desk_pos = (office.x + 120, office.y + 110)
            jeromathy.current_room = RoomType.OFFICE
            self.enemies.append(jeromathy)
            
            # Angellica in Hallway (at her desk - moved down and left)
            hallway = self.rooms[RoomType.HALLWAY]
            angellica = Angellica(hallway.x + 210, hallway.y + 160)
            angellica.desk_pos = (hallway.x + 200, hallway.y + 150)
            angellica.current_room = RoomType.HALLWAY
            self.enemies.append(angellica)
            
            # NextGen Intern #1 in Classroom (to the right of laptop)
            classroom = self.rooms[RoomType.CLASSROOM]
            laptop_x = classroom.x + classroom.width // 2 - 30
            intern1 = NextGenIntern(laptop_x + 100, classroom.y + classroom.height // 2 - 20)
            intern1.current_room = RoomType.CLASSROOM
            intern1.activation_delay = 15.0  # First intern activates at 15 seconds
            self.enemies.append(intern1)
            
            # NextGen Intern #2 in Classroom (top right corner)
            intern2 = NextGenIntern(classroom.x + classroom.width - 80, classroom.y + 60)
            intern2.current_room = RoomType.CLASSROOM
            intern2.activation_delay = 25.0  # Second intern activates at 25 seconds
            self.enemies.append(intern2)
            
            # NextGen Intern #3 in Classroom (bottom right corner)
            intern3 = NextGenIntern(classroom.x + classroom.width - 80, classroom.y + classroom.height - 80)
            intern3.current_room = RoomType.CLASSROOM
            intern3.activation_delay = 35.0  # Third intern activates at 35 seconds
            self.enemies.append(intern3)
        else:
            # Reset enemy positions for new day
            intern_count = 0
            classroom = self.rooms[RoomType.CLASSROOM]
            laptop_x = classroom.x + classroom.width // 2 - 30
            
            for enemy in self.enemies:
                if isinstance(enemy, Jonathan):
                    enemy.x = classroom.x + 60
                    enemy.y = classroom.y + classroom.height - 80
                    enemy.current_room = RoomType.CLASSROOM
                    enemy.activation_delay = 30.0
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
                    enemy.x = hallway.x + 210
                    enemy.y = hallway.y + 160
                    enemy.desk_pos = (hallway.x + 200, hallway.y + 150)
                    enemy.current_room = RoomType.HALLWAY
                    enemy.activation_delay = 10.0
                elif isinstance(enemy, NextGenIntern):
                    # Position each intern differently with different activation delays
                    if intern_count == 0:
                        enemy.x = laptop_x + 100
                        enemy.y = classroom.y + classroom.height // 2 - 20
                        enemy.activation_delay = 15.0  # First intern
                    elif intern_count == 1:
                        enemy.x = classroom.x + classroom.width - 80
                        enemy.y = classroom.y + 60
                        enemy.activation_delay = 25.0  # Second intern
                    elif intern_count == 2:
                        enemy.x = classroom.x + classroom.width - 80
                        enemy.y = classroom.y + classroom.height - 80
                        enemy.activation_delay = 35.0  # Third intern
                    
                    enemy.current_room = RoomType.CLASSROOM
                    enemy.snack_timer = 0
                    enemy.going_for_snack = False
                    enemy.returning_to_classroom = False
                    intern_count += 1
    
    def switch_state(self, new_state: GameState):
        self.state = new_state
        
        if new_state == GameState.CAMERA:
            self.camera_selected_room = RoomType.BREAK_ROOM
        elif new_state == GameState.PLAYING:
            self.player.on_youtube = False
    
    def show_message(self, message: str, duration: float = 2.0):
        self.message = message
        self.message_timer = duration
    
    def screen_shake(self, intensity: float = 10):
        self.shake_intensity = intensity
    
    def check_collision_with_walls(self, entity: Entity) -> bool:
        """Check if entity collides with walls in ANY room (not just current room)"""
        entity_rect = entity.get_rect()
        
        # Check walls in ALL rooms to prevent walking through walls
        for room in self.rooms.values():
            for wall in room.walls:
                if entity_rect.colliderect(wall):
                    # Check if we're in a doorway - if so, allow movement
                    in_doorway = False
                    for doorway in room.doorways:
                        if entity_rect.colliderect(doorway):
                            in_doorway = True
                            break
                    
                    if not in_doorway:
                        return True
        
        return False
    
    def check_enemy_collision_with_walls(self, enemy: Enemy) -> bool:
        """Check if enemy collides with walls in ANY room"""
        enemy_rect = enemy.get_rect()
        
        # Check walls in ALL rooms to prevent walking through walls
        for room in self.rooms.values():
            for wall in room.walls:
                if enemy_rect.colliderect(wall):
                    # Check if we're in a doorway - if so, allow movement
                    in_doorway = False
                    for doorway in room.doorways:
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
        player_center = self.player.get_center()
        
        # First, verify the player is actually in their current room
        # If not, find which room they're in
        current_room_obj = self.rooms[self.current_room]
        if not current_room_obj.get_rect().collidepoint(player_center):
            # Player is not in their "current room", find the correct room
            for room_type, room_obj in self.rooms.items():
                if room_obj.get_rect().collidepoint(player_center):
                    self.current_room = room_type
                    self.room_transition_cooldown = 0.3  # Reset cooldown
                    break
            return  # Don't check door transitions this frame
        
        # Skip transition if cooldown active (prevents jitter at room borders)
        if self.room_transition_cooldown > 0:
            return
        
        # Check for door transitions
        for to_room_type, door_rect in current_room_obj.connections:
            if player_rect.colliderect(door_rect):
                # Transition to new room (silently, no effects)
                self.current_room = to_room_type
                self.room_transition_cooldown = 0.3  # 0.3 second cooldown
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
                    # Only dangerous when chasing (angry/mad)
                    if enemy.state == "chasing":
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
                
                # Angellica kills when chasing (player on YouTube OR not coding for 15+ seconds)
                elif isinstance(enemy, Angellica):
                    if enemy.state == "chasing":
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
        
        # Update room transition cooldown
        if self.room_transition_cooldown > 0:
            self.room_transition_cooldown -= dt
        
        # Update last coding time
        self.last_coding_time += dt
        
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
                self.bandwidth = self.max_bandwidth
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
        
        # Move player (but check collisions separately for X and Y to prevent diagonal clipping)
        if dx != 0 or dy != 0:
            # Normalize diagonal movement
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
            
            # Save original position
            original_x = self.player.x
            original_y = self.player.y
            
            # Try moving X first
            self.player.x += dx * self.player.speed * dt
            if self.check_collision_with_walls(self.player):
                self.player.x = original_x  # Revert X if collision
            
            # Save X position after it's been validated
            validated_x = self.player.x
            
            # Then try moving Y
            self.player.y += dy * self.player.speed * dt
            if self.check_collision_with_walls(self.player):
                self.player.y = original_y  # Revert Y if collision
            
            # Final check: if somehow still colliding (corner case), revert everything
            if self.check_collision_with_walls(self.player):
                self.player.x = original_x
                self.player.y = original_y
            
            # Update direction based on movement
            if abs(dx) > abs(dy):
                self.player.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            elif dy != 0:
                self.player.direction = Direction.DOWN if dy > 0 else Direction.UP
        
        # Check door transitions
        self.check_door_transitions()
        
        # Laptop special controls (continuous check for Y and C keys)
        current_room = self.rooms[self.current_room]
        for interactable in current_room.interactables:
            if interactable.type == InteractableType.LAPTOP:
                if interactable.can_interact(self.player):
                    if keys[pygame.K_y]:
                        self.player.on_youtube = True
                        self.show_message("Watching YouTube... (Time moves faster!)", 2.0)
                    elif keys[pygame.K_c]:
                        self.player.on_youtube = False
                        self.last_coding_time = 0.0  # Reset timer when coding
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
                result = enemy.update(dt, self.player, self.rooms, self.last_coding_time)
                if result:
                    old_x, old_y = result
            elif isinstance(enemy, NextGenIntern):
                result = enemy.update(dt, self.player, breakroom_center, self, self.rooms)
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
        
        # Refill bandwidth when not using camera
        if self.bandwidth < self.max_bandwidth:
            self.bandwidth += self.bandwidth_refill_rate * dt
            if self.bandwidth > self.max_bandwidth:
                self.bandwidth = self.max_bandwidth
        
        # Note: Pause is now handled in handle_events() via KEYDOWN
    
    def update_camera(self, dt: float):
        # Drain bandwidth
        self.bandwidth -= self.bandwidth_drain_rate * dt
        if self.bandwidth <= 0:
            self.bandwidth = 0
            self.switch_state(GameState.GAME_OVER)
            self.show_message("Bandwidth depleted!", 3.0)
            return
        
        # Update hallway background panning when viewing hallway
        if self.camera_selected_room == RoomType.HALLWAY and self.hallway_bg_image:
            self.hallway_bg_offset += 5 * dt  # Very slow panning speed
            # Reset offset before the edge becomes visible (reset at 80% to prevent tiling)
            max_offset = SCREEN_WIDTH * 0.8
            if self.hallway_bg_offset >= max_offset:
                self.hallway_bg_offset = 0
        
        # Update break room background panning when viewing break room
        if self.camera_selected_room == RoomType.BREAK_ROOM and self.breakroom_bg_image:
            self.breakroom_bg_offset += 5 * dt  # Very slow panning speed
            # Reset offset before the edge becomes visible (reset at 80% to prevent tiling)
            max_offset = SCREEN_WIDTH * 0.8
            if self.breakroom_bg_offset >= max_offset:
                self.breakroom_bg_offset = 0
        
        # Update office background panning when viewing office
        if self.camera_selected_room == RoomType.OFFICE and self.office_bg_image:
            self.office_bg_offset += 5 * dt  # Very slow panning speed
            # Reset offset before the edge becomes visible (reset at 80% to prevent tiling)
            max_offset = SCREEN_WIDTH * 0.8
            if self.office_bg_offset >= max_offset:
                self.office_bg_offset = 0
        
        # Update classroom background panning when viewing classroom
        if self.camera_selected_room == RoomType.CLASSROOM and self.classroom_bg_image:
            self.classroom_bg_offset += 5 * dt  # Very slow panning speed
            # Reset offset before the edge becomes visible (reset at 80% to prevent tiling)
            max_offset = SCREEN_WIDTH * 0.8
            if self.classroom_bg_offset >= max_offset:
                self.classroom_bg_offset = 0
        
        # Switch between camera views (skip Meeting Room - that's where the player is)
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_1]:
            self.camera_selected_room = RoomType.BREAK_ROOM
        elif keys[pygame.K_2]:
            self.camera_selected_room = RoomType.OFFICE
        elif keys[pygame.K_3]:
            self.camera_selected_room = RoomType.HALLWAY
        elif keys[pygame.K_4]:
            self.camera_selected_room = RoomType.CLASSROOM
        
        # Note: Camera close is now handled in handle_events() via KEYDOWN
    
    def update_game_over(self, dt: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Restart day
            self.current_time = 9.0
            self.bandwidth = self.max_bandwidth
            self._init_game()
            self.switch_state(GameState.PLAYING)
    
    def update_victory(self, dt: float):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Restart game
            self.current_day = 1
            self.current_time = 9.0
            self.bandwidth = self.max_bandwidth
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
        title_surf = title_font.render("Nine to Five at Rocket", True, ORANGE)
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
            "• Survive from 9am to 5pm - just one workday!",
            "• Enemies take time to activate - use this to prepare!",
            "• Jo-nathan ALWAYS chases you relentlessly",
            "• Give Jo-nathan an egg to distract him for 10 seconds",
            "• Jeromathy hunts you down if snacks hit 0",
            "• Angellica pursues you if you watch YouTube or don't code for 30s",
            "• Enemies navigate around walls to catch you!",
            "• NextGen Intern takes snacks but is harmless",
            "• Use cameras to track enemies (drains bandwidth, refills slowly when off)",
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
        
        # Determine which rooms to draw based on player position
        rooms_to_draw = set()
        
        if self.player:
            player_rect = self.player.get_rect()
            
            # Check all rooms to see if player is in or near them
            for room_type, room in self.rooms.items():
                room_rect = pygame.Rect(room.x, room.y, room.width, room.height)
                
                # Draw room if player is inside it or very close to it (within 30 pixels)
                expanded_room = room_rect.inflate(60, 60)  # 30 pixels on each side
                if expanded_room.colliderect(player_rect):
                    rooms_to_draw.add(room_type)
        
        # If no rooms detected, at least draw the current room
        if not rooms_to_draw:
            rooms_to_draw.add(self.current_room)
        
        # Draw all visible rooms
        for room_type in rooms_to_draw:
            room = self.rooms.get(room_type)
            if room:
                room.draw(self.screen, camera_offset)
        
        # Draw enemies in any visible room
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            
            # Check if enemy is in any visible room
            for room_type in rooms_to_draw:
                room = self.rooms.get(room_type)
                if room:
                    room_rect = pygame.Rect(room.x, room.y, room.width, room.height)
                    if room_rect.colliderect(enemy_rect):
                        enemy.draw(self.screen, camera_offset)
                        break  # Only draw once
        
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
        
        # Bandwidth
        bandwidth_text = f"Bandwidth: {int(self.bandwidth)}%"
        bandwidth_color = GREEN if self.bandwidth > 50 else (ORANGE if self.bandwidth > 20 else RED)
        bandwidth_surf = font.render(bandwidth_text, True, bandwidth_color)
        self.screen.blit(bandwidth_surf, (250, y))
        
        # Bandwidth bar
        bar_x = 250
        bar_y = y + 35
        bar_width = 150
        bar_height = 20
        
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        fill_width = int((self.bandwidth / self.max_bandwidth) * bar_width)
        pygame.draw.rect(self.screen, bandwidth_color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Inventory (removed day counter since it's only 1 day)
        # Only show snacks if in break room or viewing break room on camera
        if self.player:
            show_snacks = (self.current_room == RoomType.BREAK_ROOM or 
                          (self.state == GameState.CAMERA and self.camera_selected_room == RoomType.BREAK_ROOM))
            
            if show_snacks:
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
                # Skip desks - they're not interactable
                if interactable.type == InteractableType.DESK:
                    continue
                    
                if interactable.can_interact(self.player):
                    hint = "[E] to interact"
                    if interactable.type == InteractableType.LAPTOP:
                        hint = "[Y] YouTube, [C] Code"
                    
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
        
        # Draw full-screen panning background for hallway FIRST (behind everything)
        if self.camera_selected_room == RoomType.HALLWAY and self.hallway_bg_image:
            # Scale the background image to be much larger (3x zoomed in)
            zoom_factor = 3.0
            bg_width = int(SCREEN_WIDTH * zoom_factor)
            bg_height = int(SCREEN_HEIGHT * zoom_factor)
            bg_scaled = pygame.transform.scale(self.hallway_bg_image, (bg_width, bg_height))
            
            # Draw single copy with offset, no tiling
            offset = int(self.hallway_bg_offset)
            # Center the image vertically and pan horizontally
            y_offset = -(bg_height - SCREEN_HEIGHT) // 2
            # Use subsurface to get the visible portion of the scaled image
            source_rect = pygame.Rect(offset, -y_offset, SCREEN_WIDTH, SCREEN_HEIGHT)
            # Make sure the source rect is within bounds
            if source_rect.right <= bg_width and source_rect.bottom <= bg_height:
                visible_section = bg_scaled.subsurface(source_rect)
                self.screen.blit(visible_section, (0, 0))
        
        # Draw full-screen panning background for break room FIRST (behind everything)
        if self.camera_selected_room == RoomType.BREAK_ROOM and self.breakroom_bg_image:
            # Scale the background image to be much larger (3x zoomed in)
            zoom_factor = 3.0
            bg_width = int(SCREEN_WIDTH * zoom_factor)
            bg_height = int(SCREEN_HEIGHT * zoom_factor)
            bg_scaled = pygame.transform.scale(self.breakroom_bg_image, (bg_width, bg_height))
            
            # Draw single copy with offset, no tiling
            offset = int(self.breakroom_bg_offset)
            # Center the image vertically and pan horizontally
            y_offset = -(bg_height - SCREEN_HEIGHT) // 2
            # Use subsurface to get the visible portion of the scaled image
            source_rect = pygame.Rect(offset, -y_offset, SCREEN_WIDTH, SCREEN_HEIGHT)
            # Make sure the source rect is within bounds
            if source_rect.right <= bg_width and source_rect.bottom <= bg_height:
                visible_section = bg_scaled.subsurface(source_rect)
                self.screen.blit(visible_section, (0, 0))
        
        # Draw full-screen panning background for office FIRST (behind everything)
        if self.camera_selected_room == RoomType.OFFICE and self.office_bg_image:
            # Scale the background image to be much larger (3x zoomed in)
            zoom_factor = 3.0
            bg_width = int(SCREEN_WIDTH * zoom_factor)
            bg_height = int(SCREEN_HEIGHT * zoom_factor)
            bg_scaled = pygame.transform.scale(self.office_bg_image, (bg_width, bg_height))
            
            # Draw single copy with offset, no tiling
            offset = int(self.office_bg_offset)
            # Center the image vertically and pan horizontally
            y_offset = -(bg_height - SCREEN_HEIGHT) // 2
            # Use subsurface to get the visible portion of the scaled image
            source_rect = pygame.Rect(offset, -y_offset, SCREEN_WIDTH, SCREEN_HEIGHT)
            # Make sure the source rect is within bounds
            if source_rect.right <= bg_width and source_rect.bottom <= bg_height:
                visible_section = bg_scaled.subsurface(source_rect)
                self.screen.blit(visible_section, (0, 0))
        
        # Draw full-screen panning background for classroom FIRST (behind everything)
        if self.camera_selected_room == RoomType.CLASSROOM and self.classroom_bg_image:
            # Scale the background image to be much larger (3x zoomed in)
            zoom_factor = 3.0
            bg_width = int(SCREEN_WIDTH * zoom_factor)
            bg_height = int(SCREEN_HEIGHT * zoom_factor)
            bg_scaled = pygame.transform.scale(self.classroom_bg_image, (bg_width, bg_height))
            
            # Draw single copy with offset, no tiling
            offset = int(self.classroom_bg_offset)
            # Center the image vertically and pan horizontally
            y_offset = -(bg_height - SCREEN_HEIGHT) // 2
            # Use subsurface to get the visible portion of the scaled image
            source_rect = pygame.Rect(offset, -y_offset, SCREEN_WIDTH, SCREEN_HEIGHT)
            # Make sure the source rect is within bounds
            if source_rect.right <= bg_width and source_rect.bottom <= bg_height:
                visible_section = bg_scaled.subsurface(source_rect)
                self.screen.blit(visible_section, (0, 0))
        
        # Camera feed
        if self.camera_selected_room:
            room = self.rooms[self.camera_selected_room]
            
            # Calculate scaled dimensions
            scale_factor = min(SCREEN_WIDTH * 0.7 / room.width, SCREEN_HEIGHT * 0.6 / room.height)
            scaled_width = int(room.width * scale_factor)
            scaled_height = int(room.height * scale_factor)
            
            # Center on screen coordinates
            x = (SCREEN_WIDTH - scaled_width) // 2
            y = (SCREEN_HEIGHT - scaled_height) // 2 - 30
            
            # Create room surface
            room_surface = pygame.Surface((room.width, room.height), pygame.SRCALPHA)
            if self.camera_selected_room != RoomType.HALLWAY or not self.hallway_bg_image:
                room_surface.fill((80, 80, 90))  # Only fill if no background image
            
            # Draw room elements relative to room position
            temp_offset = (room.x, room.y)
            
            # Draw interactables
            for interactable in room.interactables:
                interactable.draw(room_surface, temp_offset)
            
            # Draw enemies in this room (check by position)
            room_rect = pygame.Rect(room.x, room.y, room.width, room.height)
            for enemy in self.enemies:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if room_rect.colliderect(enemy_rect):
                    enemy.draw(room_surface, temp_offset)
            
            # Draw player if in this room
            if self.player and self.current_room == self.camera_selected_room:
                self.player.draw(room_surface, temp_offset)
            
            # Scale room content
            scaled_surface = pygame.transform.scale(room_surface, (scaled_width, scaled_height))
            self.screen.blit(scaled_surface, (x, y))
            
            # Add film grain effect
            grain_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            for _ in range(int(scaled_width * scaled_height * 0.02)):  # 2% coverage
                gx = random.randint(0, scaled_width - 1)
                gy = random.randint(0, scaled_height - 1)
                grain_intensity = random.randint(20, 80)
                grain_color = (grain_intensity, grain_intensity, grain_intensity, random.randint(30, 100))
                grain_surface.set_at((gx, gy), grain_color)
            self.screen.blit(grain_surface, (x, y))
            
            # Add slight vignette/darkening for camera effect
            vignette = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            vignette.fill((0, 0, 0, 30))
            self.screen.blit(vignette, (x, y))
            
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
        
        instructions = "Select Camera: [1]Break Room [2]Office [3]Hallway [4]Classroom  [ESC]Close"
        inst_surf = font.render(instructions, True, WHITE)
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.screen.blit(inst_surf, inst_rect)
        
        # Bandwidth warning
        bandwidth_font = pygame.font.Font(None, 36)
        bandwidth_text = f"BANDWIDTH: {int(self.bandwidth)}%"
        bandwidth_color = GREEN if self.bandwidth > 50 else (ORANGE if self.bandwidth > 20 else RED)
        bandwidth_surf = bandwidth_font.render(bandwidth_text, True, bandwidth_color)
        bandwidth_rect = bandwidth_surf.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
        self.screen.blit(bandwidth_surf, bandwidth_rect)
        
        # Show snack count when viewing break room camera
        if self.camera_selected_room == RoomType.BREAK_ROOM and self.player:
            snack_font = pygame.font.Font(None, 32)
            snack_text = f"Snacks: {self.player.inventory['snacks']}"
            snack_surf = snack_font.render(snack_text, True, WHITE)
            snack_rect = snack_surf.get_rect(center=(SCREEN_WIDTH // 2, y + 80))
            self.screen.blit(snack_surf, snack_rect)
        
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
        reason_text = "You didn't survive your shift"
        reason_surf = reason_font.render(reason_text, True, LIGHT_GRAY)
        reason_rect = reason_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(reason_surf, reason_rect)
        
        # Restart instruction
        restart_font = pygame.font.Font(None, 32)
        restart_surf = restart_font.render("Press SPACE to restart", True, WHITE)
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
        msg_text = "You survived your workday at Rocket!"
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
                
                # Interaction with E in playing state
                if event.key == pygame.K_e and self.state == GameState.PLAYING:
                    current_room = self.rooms[self.current_room]
                    for interactable in current_room.interactables:
                        # Skip desks and laptops - they're not interactable with E
                        if interactable.type in [InteractableType.DESK, InteractableType.LAPTOP]:
                            continue
                            
                        if interactable.can_interact(self.player):
                            msg = interactable.interact(self.player, self)
                            if msg:
                                self.show_message(msg, 2.0)
                            break  # Only interact with one object at a time
    
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
