"""
CONTROLLER LAYER - Game Logic and Coordination
==============================================
This module coordinates between Model and View layers.
Controllers are responsible for:
- Game loop execution
- Input handling (keyboard, mouse)
- Updating model state
- Triggering view rendering
- Collision detection and response
- Game state transitions
"""

import asyncio
import pygame
import sys
from typing import Dict, List, Optional
import random

# Import models
from models import (
    Player, Enemy, Jonathan, Jeromathy, Angellica, NextGenIntern,
    Room, Interactable, ParticleEmitter,
    GameState, RoomType, Direction, InteractableType
)

# Import views
from views import (
    PlayerRenderer, EnemyRenderer, InteractableRenderer, RoomRenderer,
    HUDRenderer, MenuRenderer, CameraRenderer, ParticleRenderer,
    BLACK, WHITE, RED, GREEN, YELLOW
)


# ============================================================
# GAME CONFIGURATION
# ============================================================

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Game timing constants
GAME_DAY_LENGTH = 480.0  # Seconds per in-game day (8 minutes = 480s real time)
TOTAL_DAYS = 5  # Must survive 5 days


# ============================================================
# MAIN GAME CONTROLLER
# ============================================================

class GameController:
    """
    Main game controller that manages the entire game loop.
    Coordinates input, game logic, and rendering.
    """
    
    def __init__(self):
        """Initialize the game controller and all subsystems"""
        # Initialize Pygame
        pygame.init()
        
        # Create display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Five Nights at Rocket")
        
        # Clock for frame rate control
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = GameState.MENU
        self.show_tutorial = True  # Show tutorial on first play
        
        # Initialize subsystems
        self._init_renderers()
        self._init_game()
    
    def _init_renderers(self):
        """
        Initialize all view renderers.
        Renderers handle drawing different game elements.
        """
        self.player_renderer = PlayerRenderer()
        self.enemy_renderer = EnemyRenderer()
        self.interactable_renderer = InteractableRenderer()
        self.particle_renderer = ParticleRenderer()
    
    def _init_game(self):
        """
        Initialize/reset all game state for a new game.
        Sets up rooms, player, enemies, and game variables.
        """
        # Time tracking
        self.current_day = 1
        self.day_progress = 0.0  # 0.0 = 9am, 1.0 = 5pm
        
        # Battery for camera usage
        self.battery = 100.0  # Starts full
        self.max_battery = 100.0
        self.battery_drain_rate = 5.0  # % per second when using camera
        
        # UI state
        self.message = ""  # Temporary message to display
        self.message_timer = 0  # How long to show message
        self.game_over_reason = ""  # Why player died
        
        # Camera view
        self.current_camera_room = RoomType.OFFICE
        
        # Initialize rooms
        self._init_rooms()
        
        # Initialize player
        office = self.rooms[RoomType.OFFICE]
        self.player = Player(
            office.x + office.width // 2 - 20,
            office.y + office.height // 2
        )
        self.player.current_room = RoomType.OFFICE
        
        # Initialize enemies
        self._init_enemies()
        
        # Particle system
        self.particle_emitter = ParticleEmitter()
    
    def _init_rooms(self):
        """
        Create all rooms in the office building.
        Define room positions, sizes, and connections.
        """
        # Create rooms with specific layouts
        # Room positions create a connected office space
        self.rooms: Dict[RoomType, Room] = {
            # Break Room: Left of Office (tall, thin room)
            RoomType.BREAK_ROOM: Room(RoomType.BREAK_ROOM, -100, 100, 200, 400),
            
            # Office: Center-left (player starting area)
            RoomType.OFFICE: Room(RoomType.OFFICE, 100, 100, 450, 400),
            
            # Hallway: Center-right (connects multiple rooms)
            RoomType.HALLWAY: Room(RoomType.HALLWAY, 550, 100, 550, 400),
            
            # Classroom: Far right
            RoomType.CLASSROOM: Room(RoomType.CLASSROOM, 1100, 100, 450, 400),
            
            # Meeting Room: Below Hallway
            RoomType.MEETING_ROOM: Room(RoomType.MEETING_ROOM, 550, 500, 550, 250),
        }
        
        # Add walls to rooms (with doorway breaks)
        self._setup_walls()
        
        # Connect rooms via doorways
        self._connect_rooms()
    
    def _setup_walls(self):
        """
        Add wall collision rectangles to each room.
        Walls have breaks for doorways between rooms.
        """
        # Wall thickness
        WALL_THICKNESS = 15
        
        for room_type, room in self.rooms.items():
            x, y, w, h = room.x, room.y, room.width, room.height
            
            # Add walls based on room connections
            # Top wall
            if room_type != RoomType.BREAK_ROOM:
                room.add_wall(pygame.Rect(x, y, w, WALL_THICKNESS))
            
            # Bottom wall
            if room_type != RoomType.MEETING_ROOM:
                room.add_wall(pygame.Rect(x, y + h - WALL_THICKNESS, w, WALL_THICKNESS))
            
            # Left and right walls with doorway breaks
            if room_type == RoomType.BREAK_ROOM:
                # Right wall with doorway to Office
                doorway_y = 150
                doorway_height = 100
                # Wall above doorway
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, y, WALL_THICKNESS, doorway_y - y))
                # Wall below doorway
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, doorway_y + doorway_height, 
                                         WALL_THICKNESS, h - (doorway_y + doorway_height)))
            
            elif room_type == RoomType.OFFICE:
                # Left wall with doorway from Break Room
                doorway_y = 150
                doorway_height = 100
                room.add_wall(pygame.Rect(x, y, WALL_THICKNESS, doorway_y - y))
                room.add_wall(pygame.Rect(x, doorway_y + doorway_height, 
                                         WALL_THICKNESS, h - (doorway_y + doorway_height)))
                
                # Right wall with doorway to Hallway
                doorway_y = 200
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, y, WALL_THICKNESS, doorway_y - y))
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, doorway_y + doorway_height,
                                         WALL_THICKNESS, h - (doorway_y + doorway_height)))
            
            elif room_type == RoomType.HALLWAY:
                # Left wall with doorway from Office
                doorway_y = 200
                doorway_height = 100
                room.add_wall(pygame.Rect(x, y, WALL_THICKNESS, doorway_y - y))
                room.add_wall(pygame.Rect(x, doorway_y + doorway_height,
                                         WALL_THICKNESS, h - (doorway_y + doorway_height)))
                
                # Right wall with doorway to Classroom
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, y, WALL_THICKNESS, doorway_y - y))
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, doorway_y + doorway_height,
                                         WALL_THICKNESS, h - (doorway_y + doorway_height)))
                
                # Bottom wall with doorway to Meeting Room
                doorway_x = 200
                doorway_width = 150
                room.add_wall(pygame.Rect(x, y + h - WALL_THICKNESS, doorway_x, WALL_THICKNESS))
                room.add_wall(pygame.Rect(x + doorway_x + doorway_width, y + h - WALL_THICKNESS,
                                         w - (doorway_x + doorway_width), WALL_THICKNESS))
            
            elif room_type == RoomType.CLASSROOM:
                # Left wall with doorway from Hallway
                doorway_y = 200
                doorway_height = 100
                room.add_wall(pygame.Rect(x, y, WALL_THICKNESS, doorway_y - y))
                room.add_wall(pygame.Rect(x, doorway_y + doorway_height,
                                         WALL_THICKNESS, h - (doorway_y + doorway_height)))
                
                # Right wall (no connections)
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, y, WALL_THICKNESS, h))
            
            elif room_type == RoomType.MEETING_ROOM:
                # Top wall with doorway from Hallway
                doorway_x = 200
                doorway_width = 150
                room.add_wall(pygame.Rect(x, y, doorway_x, WALL_THICKNESS))
                room.add_wall(pygame.Rect(x + doorway_x + doorway_width, y,
                                         w - (doorway_x + doorway_width), WALL_THICKNESS))
                
                # Left and right walls (full walls, no doors)
                room.add_wall(pygame.Rect(x, y, WALL_THICKNESS, h))
                room.add_wall(pygame.Rect(x + w - WALL_THICKNESS, y, WALL_THICKNESS, h))
        
        # Add missing walls for Break Room
        break_room = self.rooms[RoomType.BREAK_ROOM]
        # Left wall (full)
        break_room.add_wall(pygame.Rect(break_room.x, break_room.y, WALL_THICKNESS, break_room.height))
        # Top wall
        break_room.add_wall(pygame.Rect(break_room.x, break_room.y, break_room.width, WALL_THICKNESS))
    
    def _connect_rooms(self):
        """Define which rooms connect to which other rooms"""
        # Define doorway connections
        self.rooms[RoomType.BREAK_ROOM].add_connection(
            RoomType.OFFICE, pygame.Rect(100, 150, 50, 100)
        )
        self.rooms[RoomType.OFFICE].add_connection(
            RoomType.BREAK_ROOM, pygame.Rect(-100, 150, 50, 100)
        )
        self.rooms[RoomType.OFFICE].add_connection(
            RoomType.HALLWAY, pygame.Rect(550, 200, 50, 100)
        )
        self.rooms[RoomType.HALLWAY].add_connection(
            RoomType.OFFICE, pygame.Rect(550, 200, 50, 100)
        )
        self.rooms[RoomType.HALLWAY].add_connection(
            RoomType.CLASSROOM, pygame.Rect(1100, 200, 50, 100)
        )
        self.rooms[RoomType.CLASSROOM].add_connection(
            RoomType.HALLWAY, pygame.Rect(1100, 200, 50, 100)
        )
        self.rooms[RoomType.HALLWAY].add_connection(
            RoomType.MEETING_ROOM, pygame.Rect(750, 500, 150, 50)
        )
        self.rooms[RoomType.MEETING_ROOM].add_connection(
            RoomType.HALLWAY, pygame.Rect(750, 485, 150, 50)
        )
    
    def _init_enemies(self):
        """
        Create all enemy characters.
        Each enemy starts in a specific room.
        """
        classroom = self.rooms[RoomType.CLASSROOM]
        office = self.rooms[RoomType.OFFICE]
        meeting = self.rooms[RoomType.MEETING_ROOM]
        hallway = self.rooms[RoomType.HALLWAY]
        
        self.enemies: List[Enemy] = [
            # Jo-nathan: Starts in classroom, always chases
            Jonathan(
                classroom.x + classroom.width // 2 - 20,
                classroom.y + classroom.height // 2
            ),
            
            # Jeromathy: Starts at his desk in the office
            Jeromathy(
                office.x + office.width - 80,
                office.y + 80
            ),
            
            # Angellica: Starts in meeting room
            Angellica(
                meeting.x + meeting.width // 2 - 20,
                meeting.y + meeting.height // 2
            ),
            
            # NextGen Intern: Starts in hallway
            NextGenIntern(
                hallway.x + hallway.width // 2 - 20,
                hallway.y + hallway.height // 2
            ),
        ]
        
        # Set initial rooms for enemies
        self.enemies[0].current_room = RoomType.CLASSROOM
        self.enemies[1].current_room = RoomType.OFFICE
        self.enemies[2].current_room = RoomType.MEETING_ROOM
        self.enemies[3].current_room = RoomType.HALLWAY
    
    def switch_state(self, new_state: GameState):
        """
        Switch to a different game state.
        
        Args:
            new_state: The state to switch to
        """
        self.state = new_state
        
        # Reset tutorial flag after showing once
        if new_state == GameState.PLAYING:
            self.show_tutorial = False
    
    def show_message(self, message: str, duration: float = 2.0):
        """
        Display a temporary message to the player.
        
        Args:
            message: Text to display
            duration: How long to show message (seconds)
        """
        self.message = message
        self.message_timer = duration
    
    def game_over(self, reason: str):
        """
        Trigger game over.
        
        Args:
            reason: Why the player died
        """
        self.game_over_reason = reason
        self.switch_state(GameState.GAME_OVER)
        
        # Particle burst at player location
        px, py = self.player.get_center()
        self.particle_emitter.emit(px, py, RED, count=50, spread=200, lifetime=2.0)
    
    def check_victory(self):
        """Check if player has won (survived all days)"""
        if self.current_day > TOTAL_DAYS:
            self.switch_state(GameState.VICTORY)
            
            # Victory particle effect
            px, py = self.player.get_center()
            self.particle_emitter.emit(px, py, YELLOW, count=100, spread=300, lifetime=3.0)
    
    def advance_day(self):
        """
        Progress to the next day.
        Resets day progress and battery.
        """
        self.current_day += 1
        self.day_progress = 0.0
        self.battery = self.max_battery
        
        # Show day transition message
        self.show_message(f"Day {self.current_day} begins!", 3.0)
        
        # Check for victory
        self.check_victory()
    
    async def run(self):
        """
        Main game loop.
        Handles input, updates game state, and renders everything.
        Uses async for pygbag browser compatibility.
        """
        while self.running:
            # Delta time for frame-rate independent movement
            dt = self.clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
            
            # Handle input
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render everything
            self.render()
            
            # Update display
            pygame.display.flip()
            
            # Yield control for async (required for pygbag)
            await asyncio.sleep(0)
        
        # Cleanup
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """
        Process all input events (keyboard, mouse, window).
        Routes events based on current game state.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Route to appropriate handler based on state
                if self.state == GameState.MENU:
                    self.handle_menu_input(event)
                elif self.state == GameState.TUTORIAL:
                    self.handle_tutorial_input(event)
                elif self.state == GameState.PLAYING:
                    self.handle_playing_input(event)
                elif self.state == GameState.CAMERA:
                    self.handle_camera_input(event)
                elif self.state == GameState.PAUSED:
                    self.handle_paused_input(event)
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    self.handle_end_screen_input(event)
    
    def handle_menu_input(self, event):
        """Handle input on main menu"""
        if event.key == pygame.K_SPACE:
            if self.show_tutorial:
                self.switch_state(GameState.TUTORIAL)
            else:
                self.switch_state(GameState.PLAYING)
    
    def handle_tutorial_input(self, event):
        """Handle input on tutorial screen"""
        if event.key == pygame.K_SPACE:
            self.switch_state(GameState.PLAYING)
    
    def handle_playing_input(self, event):
        """Handle input during active gameplay"""
        if event.key == pygame.K_ESCAPE:
            # Toggle pause
            self.switch_state(GameState.PAUSED)
        
        elif event.key == pygame.K_e:
            # Try to interact with nearby objects
            self.try_interact()
        
        elif event.key == pygame.K_y:
            # Watch YouTube (triggers Angellica)
            self.player.on_youtube = True
            self.show_message("Watching YouTube...", 1.0)
        
        elif event.key == pygame.K_c:
            # Code/work (stops YouTube)
            self.player.on_youtube = False
            self.show_message("Back to work!", 1.0)
    
    def handle_camera_input(self, event):
        """Handle input while in camera view"""
        if event.key == pygame.K_ESCAPE:
            # Close camera
            self.switch_state(GameState.PLAYING)
        
        # Number keys to switch camera views
        elif event.key == pygame.K_1:
            self.current_camera_room = RoomType.OFFICE
        elif event.key == pygame.K_2:
            self.current_camera_room = RoomType.BREAK_ROOM
        elif event.key == pygame.K_3:
            self.current_camera_room = RoomType.MEETING_ROOM
        elif event.key == pygame.K_4:
            self.current_camera_room = RoomType.CLASSROOM
        elif event.key == pygame.K_5:
            self.current_camera_room = RoomType.HALLWAY
    
    def handle_paused_input(self, event):
        """Handle input while game is paused"""
        if event.key == pygame.K_ESCAPE:
            # Unpause
            self.switch_state(GameState.PLAYING)
    
    def handle_end_screen_input(self, event):
        """Handle input on game over or victory screen"""
        if event.key == pygame.K_SPACE:
            # Restart game
            self._init_game()
            self.switch_state(GameState.MENU)
    
    def try_interact(self):
        """
        Try to interact with objects near the player.
        Checks all interactables in current room.
        """
        current_room = self.rooms.get(self.player.current_room)
        if not current_room:
            return
        
        # Check each interactable in the room
        for interactable in current_room.interactables:
            if interactable.can_interact(self.player):
                # Perform interaction
                message = interactable.interact(self.player, self)
                if message:
                    self.show_message(message, 2.0)
                
                # Particle effect at interaction point
                ix, iy = interactable.get_rect().center
                self.particle_emitter.emit(ix, iy, GREEN, count=10, spread=50, lifetime=0.5)
                break
    
    def update(self, dt: float):
        """
        Update all game logic.
        Routes to appropriate update method based on state.
        
        Args:
            dt: Delta time (time since last frame)
        """
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
        
        # Update particles (always active for effects)
        self.particle_emitter.update(dt)
        
        # Route to state-specific update
        if self.state == GameState.PLAYING:
            self.update_playing(dt)
        elif self.state == GameState.CAMERA:
            self.update_camera(dt)
    
    def update_playing(self, dt: float):
        """
        Update game state during active gameplay.
        Handles player movement, enemy AI, collisions, time progression.
        
        Args:
            dt: Delta time
        """
        # Update day progress (time of day)
        self.day_progress += dt / GAME_DAY_LENGTH
        
        # Check if day ended
        if self.day_progress >= 1.0:
            self.advance_day()
        
        # Handle continuous player movement (WASD)
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
        
        # Move player
        if dx != 0 or dy != 0:
            old_x, old_y = self.player.x, self.player.y
            self.player.move(dx, dy, dt)
            
            # Check collision with walls
            if self.check_wall_collision(self.player):
                # Revert movement
                self.player.x = old_x
                self.player.y = old_y
            else:
                # Update which room player is in
                self.update_entity_room(self.player)
        
        # Update all enemies
        for enemy in self.enemies:
            # Enemy-specific update logic
            old_pos = enemy.update(dt, self.player, self.rooms, enemy.current_room)
            
            # Check collision with walls
            if old_pos and self.check_wall_collision(enemy):
                # Revert enemy movement
                enemy.x, enemy.y = old_pos
            else:
                # Update which room enemy is in
                self.update_entity_room(enemy)
        
        # Update all interactables (cooldowns)
        for room in self.rooms.values():
            for interactable in room.interactables:
                interactable.update(dt)
        
        # Check enemy collisions with player
        self.check_enemy_collisions()
    
    def update_camera(self, dt: float):
        """
        Update while in camera view.
        Drains battery while cameras are active.
        
        Args:
            dt: Delta time
        """
        # Drain battery
        self.battery -= self.battery_drain_rate * dt
        
        # Clamp battery
        if self.battery <= 0:
            self.battery = 0
            # Auto-close camera when battery dies
            self.show_message("Battery dead!", 2.0)
            self.switch_state(GameState.PLAYING)
    
    def check_wall_collision(self, entity) -> bool:
        """
        Check if entity is colliding with any walls.
        
        Args:
            entity: Entity to check (Player or Enemy)
            
        Returns:
            True if colliding with a wall
        """
        entity_rect = entity.get_rect()
        current_room = self.rooms.get(entity.current_room)
        
        if current_room:
            for wall in current_room.walls:
                if entity_rect.colliderect(wall):
                    return True
        
        return False
    
    def update_entity_room(self, entity):
        """
        Update which room an entity is currently in.
        
        Args:
            entity: Entity to update
        """
        entity_rect = entity.get_rect()
        
        # Check all rooms
        for room_type, room in self.rooms.items():
            if entity_rect.colliderect(room.get_rect()):
                entity.current_room = room_type
                break
    
    def check_enemy_collisions(self):
        """
        Check if any enemies are touching the player.
        Handles different collision behaviors per enemy type.
        """
        player_rect = self.player.get_rect()
        
        for enemy in self.enemies:
            enemy_rect = enemy.get_rect()
            
            # Check collision
            if player_rect.colliderect(enemy_rect):
                # Handle different enemy types
                if isinstance(enemy, Jonathan):
                    # Jo-nathan: Only dangerous when chasing (mad)
                    if enemy.state == "chasing":
                        # Check for egg
                        if self.player.inventory["egg"]:
                            # Take egg and return to classroom
                            self.player.inventory["egg"] = False
                            enemy.state = "returning_to_classroom"
                            enemy.eating_timer = 10.0
                            self.show_message("Jo-nathan took your egg!", 2.0)
                            
                            # Particle effect
                            ex, ey = enemy.get_center()
                            self.particle_emitter.emit(ex, ey, YELLOW, count=20, spread=100, lifetime=1.0)
                        else:
                            # No egg = death
                            self.game_over("Caught by Jo-nathan!")
                
                elif isinstance(enemy, Jeromathy):
                    # Jeromathy: Always kills if chasing
                    if enemy.state == "chasing":
                        self.game_over("Caught by Jeromathy!")
                
                elif isinstance(enemy, Angellica):
                    # Angellica: Kills if chasing
                    if enemy.state == "chasing":
                        self.game_over("Caught by Angellica!")
                
                # NextGenIntern is harmless, just steals snacks
    
    def get_camera_offset(self) -> tuple[int, int]:
        """
        Calculate camera offset to center view on player.
        
        Returns:
            Tuple of (offset_x, offset_y)
        """
        px, py = self.player.get_center()
        
        # Center camera on player
        offset_x = int(px - SCREEN_WIDTH // 2)
        offset_y = int(py - SCREEN_HEIGHT // 2)
        
        return (offset_x, offset_y)
    
    def render(self):
        """
        Render everything to the screen.
        Routes to appropriate render method based on state.
        """
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            MenuRenderer.draw_main_menu(self.screen)
        
        elif self.state == GameState.TUTORIAL:
            MenuRenderer.draw_tutorial(self.screen)
        
        elif self.state == GameState.PLAYING:
            self.render_playing()
        
        elif self.state == GameState.CAMERA:
            self.render_camera()
        
        elif self.state == GameState.PAUSED:
            # Render game, then overlay pause menu
            self.render_playing()
            self.render_pause_overlay()
        
        elif self.state == GameState.GAME_OVER:
            MenuRenderer.draw_game_over(self.screen, self.game_over_reason)
        
        elif self.state == GameState.VICTORY:
            MenuRenderer.draw_victory(self.screen)
    
    def render_playing(self):
        """Render the main gameplay view"""
        camera_offset = self.get_camera_offset()
        
        # Draw all rooms
        for room in self.rooms.values():
            RoomRenderer.draw(room, self.screen, camera_offset)
        
        # Draw all interactables
        for room in self.rooms.values():
            for interactable in room.interactables:
                self.interactable_renderer.draw(interactable, self.screen, camera_offset)
        
        # Draw all enemies
        for enemy in self.enemies:
            self.enemy_renderer.draw(enemy, self.screen, camera_offset)
        
        # Draw player
        self.player_renderer.draw(self.player, self.screen, camera_offset)
        
        # Draw particles
        ParticleRenderer.draw_particles(self.particle_emitter.particles, 
                                       self.screen, camera_offset)
        
        # Draw HUD
        hud_data = {
            'inventory': self.player.inventory,
            'current_time': self.day_progress,
            'current_day': self.current_day,
            'battery': self.battery,
            'message': self.message
        }
        HUDRenderer.draw(self.screen, hud_data)
    
    def render_camera(self):
        """Render the security camera view"""
        CameraRenderer.draw(self.screen, self.rooms, self.enemies, self.current_camera_room)
        
        # Show battery level
        hud_data = {
            'inventory': {},
            'battery': self.battery,
            'message': "Using cameras..."
        }
        HUDRenderer.draw(self.screen, hud_data)
    
    def render_pause_overlay(self):
        """Render the pause menu overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        font = pygame.font.Font(None, 72)
        text_surf = font.render("PAUSED", True, WHITE)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text_surf, text_rect)
        
        # Instructions
        small_font = pygame.font.Font(None, 36)
        inst_surf = small_font.render("Press ESC to resume", True, WHITE)
        inst_rect = inst_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(inst_surf, inst_rect)


# ============================================================
# ENTRY POINT
# ============================================================

async def main():
    """
    Entry point for the game.
    Creates controller and starts game loop.
    """
    game = GameController()
    await game.run()


if __name__ == "__main__":
    # Run the async game loop
    asyncio.run(main())
