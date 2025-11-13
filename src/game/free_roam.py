import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1000, 600  # Wider for longer hallway
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Office Nightmare")

# Create surfaces for caching
cached_surfaces = {}

# Print to console
print("Hello World")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (60, 60, 60)
BLUE = (50, 120, 200)
GREEN = (50, 200, 50)
BROWN = (139, 69, 19)
BEIGE = (245, 222, 179)
DARK_BROWN = (101, 67, 33)
RED = (200, 50, 50)
YELLOW = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 140, 0)
PURPLE = (128, 0, 128)

# Spooky color scheme - Abandoned Office
DARK_FLOOR = (25, 25, 28)
WALL_DARK = (45, 45, 50)
WALL_ACCENT = (55, 55, 60)
BLOOD_RED = (120, 20, 20)
SICKLY_GREEN = (40, 60, 40)
RUSTY_BROWN = (60, 50, 40)
SHADOW_BLACK = (12, 12, 15)
DIM_YELLOW = (80, 80, 50)
EERIE_PURPLE = (70, 50, 80)
FLICKERING_LIGHT = (255, 240, 200)
OFFICE_GRAY = (50, 55, 60)
DESK_BROWN = (55, 45, 35)
CARPET_BLUE = (30, 35, 45)

# Player settings
player_size = 40
player_x = 150  # Start away from furniture
player_y = 50   # Top area of office
player_speed = 4  # Smoother speed
player_color = (70, 130, 180)  # Steel blue for office worker

# Game mode
game_mode = "camera"  # "camera" or "walk"
selected_camera = 0  # Which room camera is viewing

# Particle System
class Particle:
    def __init__(self, x, y, color, lifetime=60, vel_x=0, vel_y=0, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.size = size
        self.gravity = 0.1
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color_with_alpha = (*self.color[:3], alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))

particles = []

# Sprite Classes
class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.base_color = color
        self.width = width
        self.height = height
        self.create_sprite()
    
    def create_sprite(self):
        # Override in subclasses
        self.image.fill(self.base_color)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, (70, 130, 180))
        self.speed = 4
        self.animation_frame = 0
    
    def create_sprite(self):
        # Create player sprite with detail
        self.image.fill((0, 0, 0, 0))
        
        # Body (rounded rectangle with gradient effect)
        for i in range(self.width):
            intensity = int(255 * (1 - abs(i - self.width/2) / (self.width/2)) * 0.3)
            color = tuple(min(255, c + intensity) for c in self.base_color)
            pygame.draw.rect(self.image, color, (i, 8, 1, 24))
        
        # Head
        head_color = (90, 150, 200)
        pygame.draw.circle(self.image, head_color, (20, 10), 8)
        # Eyes
        pygame.draw.circle(self.image, (20, 20, 40), (17, 9), 2)
        pygame.draw.circle(self.image, (20, 20, 40), (23, 9), 2)
        
        # Shadow beneath
        shadow = pygame.Surface((self.width + 10, 5), pygame.SRCALPHA)
        for y in range(5):
            alpha = int(40 * (1 - y/5))
            pygame.draw.ellipse(shadow, (0, 0, 0, alpha), (0, y, self.width + 10, 5 - y))
        self.shadow = shadow
    
    def update_animation(self, moving):
        if moving:
            self.animation_frame = (self.animation_frame + 1) % 20
            # Simple bobbing effect
            offset = int(math.sin(self.animation_frame / 10 * math.pi) * 2)
            self.create_sprite()

class Jerome(Entity):
    def __init__(self, x, y):
        self.animation_frame = 0
        self.glow_intensity = 0
        super().__init__(x, y, 45, 45, (60, 40, 70))
    
    def create_sprite(self):
        self.image.fill((0, 0, 0, 0))
        
        # Body with menacing appearance
        for i in range(self.width):
            darkness = int(30 * abs(i - self.width/2) / (self.width/2))
            color = tuple(max(0, c - darkness) for c in self.base_color)
            pygame.draw.rect(self.image, color, (i, 10, 1, 28))
        
        # Head (angular, threatening)
        head_points = [(22, 5), (15, 15), (30, 15)]
        pygame.draw.polygon(self.image, (80, 60, 90), head_points)
        
        # Glowing red eyes
        eye_glow = int(abs(math.sin(self.animation_frame / 10)) * 50) + 100
        eye_color = (min(255, eye_glow), 20, 20)
        pygame.draw.circle(self.image, eye_color, (17, 12), 3)
        pygame.draw.circle(self.image, eye_color, (27, 12), 3)
        
        # Shadow
        shadow = pygame.Surface((self.width + 15, 8), pygame.SRCALPHA)
        for y in range(8):
            alpha = int(60 * (1 - y/8))
            pygame.draw.ellipse(shadow, (0, 0, 0, alpha), (0, y, self.width + 15, 8 - y))
        self.shadow = shadow
    
    def update_animation(self):
        self.animation_frame = (self.animation_frame + 1) % 60
        self.create_sprite()
        
        # Create menacing particles
        if self.animation_frame % 15 == 0:
            particles.append(Particle(
                self.rect.centerx + random.randint(-10, 10),
                self.rect.bottom - 5,
                (80, 20, 20),
                lifetime=30,
                vel_x=random.uniform(-0.5, 0.5),
                vel_y=random.uniform(-1, -0.5),
                size=2
            ))

class Furniture(Entity):
    def __init__(self, x, y, width, height, color, ftype="desk"):
        self.ftype = ftype
        super().__init__(x, y, width, height, color)
    
    def create_sprite(self):
        self.image.fill((0, 0, 0, 0))
        
        # Create textured furniture
        if self.ftype == "supply":
            # Supply station with glowing effect
            # Base
            pygame.draw.rect(self.image, self.base_color, (0, 0, self.width, self.height))
            # Highlight
            pygame.draw.rect(self.image, tuple(min(255, c + 30) for c in self.base_color), 
                           (2, 2, self.width - 4, self.height - 4))
            # Grid pattern
            for i in range(0, self.width, 8):
                pygame.draw.line(self.image, tuple(max(0, c - 20) for c in self.base_color),
                               (i, 0), (i, self.height), 1)
            for i in range(0, self.height, 8):
                pygame.draw.line(self.image, tuple(max(0, c - 20) for c in self.base_color),
                               (0, i), (self.width, i), 1)
        else:
            # Regular furniture with wood grain effect
            for y in range(self.height):
                noise = random.randint(-5, 5) if y % 3 == 0 else 0
                color = tuple(max(0, min(255, c + noise)) for c in self.base_color)
                pygame.draw.line(self.image, color, (0, y), (self.width, y))
            
            # 3D effect
            pygame.draw.rect(self.image, tuple(min(255, c + 20) for c in self.base_color),
                           (0, 0, self.width, 3))
            pygame.draw.rect(self.image, tuple(max(0, c - 30) for c in self.base_color),
                           (0, self.height - 3, self.width, 3))
        
        # Shadow
        shadow = pygame.Surface((self.width + 8, 8), pygame.SRCALPHA)
        for y in range(8):
            alpha = int(50 * (1 - y/8))
            pygame.draw.rect(shadow, (0, 0, 0, alpha), (0, y, self.width + 8, 8 - y))
        self.shadow = shadow

# Sprite groups
all_sprites = pygame.sprite.Group()
furniture_sprites = pygame.sprite.Group()

# Player sprite
player_sprite = None
jerome_sprite = None

# Timer settings (in seconds)
timer_duration = 15  # 15 seconds until Manager gets angry (more time to learn)
start_time = pygame.time.get_ticks()
announcement_made = False
announcement_text = ""
announcement_timer = 0

# Supply restocking
supplies_stocked = 3  # Start with full supplies
supplies_needed = 3  # Total supplies needed
last_restock_time = 0

# Jerome (enemy) settings
jerome_active = False
jerome_x = 0
jerome_y = 0
jerome_size = 45
jerome_speed = 2  # Slightly slower for better gameplay
jerome_color = (60, 40, 70)  # Dark purple/gray
jerome_room = 1  # Track which room Jerome is in
jerome_spawn_time = 0
jerome_chase_duration = 12000  # 12 seconds chase (longer)
jerome_recovery_duration = 8000  # 8 seconds recovery (shorter)
jerome_in_recovery = False
jerome_recovery_start = 0

# Audio cues (visual since we don't have sound)
danger_flash = 0
warning_text = ""
warning_timer = 0

# Current room
current_room = 0

# Define rooms with walls and transitions
# Each room has: walls list, floor color, transitions, and furniture/objects
rooms = {
    0: {  # Office Room - Abandoned workspace
        'walls': [
            pygame.Rect(0, 0, width, 20),                    # Top wall
            pygame.Rect(0, 0, 20, height),                   # Left wall
            pygame.Rect(0, height - 20, width, 20),          # Bottom wall
            pygame.Rect(width - 20, 0, 20, height // 2 - 60),           # Right wall top part
            pygame.Rect(width - 20, height // 2 + 60, 20, height // 2 - 60), # Right wall bottom part
        ],
        'floor_color': CARPET_BLUE,
        'furniture': [
            # Longer desk rows (4 rows of long desks)
            {'rect': pygame.Rect(80, 100, 200, 50), 'color': DESK_BROWN, 'label': None},
            {'rect': pygame.Rect(320, 100, 200, 50), 'color': DESK_BROWN, 'label': None},
            
            {'rect': pygame.Rect(80, 180, 200, 50), 'color': DESK_BROWN, 'label': None},
            {'rect': pygame.Rect(320, 180, 200, 50), 'color': DESK_BROWN, 'label': None},
            
            {'rect': pygame.Rect(80, 260, 200, 50), 'color': DESK_BROWN, 'label': None},
            {'rect': pygame.Rect(320, 260, 200, 50), 'color': DESK_BROWN, 'label': None},
            
            {'rect': pygame.Rect(80, 340, 200, 50), 'color': DESK_BROWN, 'label': None},
            {'rect': pygame.Rect(320, 340, 200, 50), 'color': DESK_BROWN, 'label': None},
            
            # Manager's desk
            {'rect': pygame.Rect(150, 450, 150, 80), 'color': RUSTY_BROWN, 'label': "Manager"},
        ],
        'transitions': [
            # Exit to hallway
            (pygame.Rect(width - 20, height // 2 - 60, 20, 120), 1, 40, height // 2),
        ]
    },
    1: {  # Hallway - Dark corporate corridor
        'walls': [
            pygame.Rect(0, 0, width, 20),                    # Top wall
            pygame.Rect(0, 0, 20, height // 2 - 60),                    # Left wall top part
            pygame.Rect(0, height // 2 + 60, 20, height // 2 - 60),     # Left wall bottom part
            pygame.Rect(0, height - 20, width, 20),          # Bottom wall
            pygame.Rect(width - 20, 0, 20, height // 2 - 60),           # Right wall top part
            pygame.Rect(width - 20, height // 2 + 60, 20, height // 2 - 60), # Right wall bottom part
        ],
        'floor_color': DARK_FLOOR,
        'furniture': [
            # Filing cabinets and storage
            {'rect': pygame.Rect(50, 50, 35, 80), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(50, 150, 35, 80), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(50, 470, 35, 80), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(width - 85, 50, 35, 80), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(width - 85, 150, 35, 80), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(width - 85, 470, 35, 80), 'color': OFFICE_GRAY, 'label': None},
        ],
        'transitions': [
            # Back to office
            (pygame.Rect(0, height // 2 - 60, 20, 120), 0, width - 60, height // 2),
            # To breakroom
            (pygame.Rect(width - 20, height // 2 - 60, 20, 120), 2, 40, height // 2),
        ]
    },
    2: {  # Breakroom - Neglected employee lounge
        'walls': [
            pygame.Rect(0, 0, width, 20),                    # Top wall
            pygame.Rect(0, 0, 20, height // 2 - 60),                    # Left wall top part
            pygame.Rect(0, height // 2 + 60, 20, height // 2 - 60),     # Left wall bottom part
            pygame.Rect(0, height - 20, width, 20),          # Bottom wall
            pygame.Rect(width - 20, 0, 20, height),          # Right wall
        ],
        'floor_color': CARPET_BLUE,
        'furniture': [
            # Break table
            {'rect': pygame.Rect(width // 2 - 100, height // 2 - 75, 200, 150), 'color': DESK_BROWN, 'label': None},
            
            # Supply stations (interactive) - SEPARATE from table, more visible
            {'rect': pygame.Rect(width // 2 - 80, height // 2 - 30, 40, 40), 'color': RUSTY_BROWN, 'label': "SUPPLY 1", 'type': 'supply'},
            {'rect': pygame.Rect(width // 2 - 20, height // 2 - 30, 40, 40), 'color': DIM_YELLOW, 'label': "SUPPLY 2", 'type': 'supply'},
            {'rect': pygame.Rect(width // 2 + 40, height // 2 - 30, 40, 40), 'color': SICKLY_GREEN, 'label': "SUPPLY 3", 'type': 'supply'},
            
            # Office chairs
            {'rect': pygame.Rect(width // 2 - 180, height // 2 - 30, 40, 40), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(width // 2 + 140, height // 2 - 30, 40, 40), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(width // 2 - 20, height // 2 - 140, 40, 40), 'color': OFFICE_GRAY, 'label': None},
            {'rect': pygame.Rect(width // 2 - 20, height // 2 + 100, 40, 40), 'color': OFFICE_GRAY, 'label': None},
            
            # Old vending machine
            {'rect': pygame.Rect(50, 50, 60, 100), 'color': WALL_DARK, 'label': "Broken"},
        ],
        'transitions': [
            # Back to hallway
            (pygame.Rect(0, height // 2 - 60, 20, 120), 1, width - 60, height // 2),
        ]
    }
}

walls = rooms[current_room]['walls']
transitions = rooms[current_room]['transitions']

# Initialize sprites
def init_sprites():
    global player_sprite, jerome_sprite, furniture_sprites, all_sprites
    
    # Clear existing sprites
    all_sprites.empty()
    furniture_sprites.empty()
    
    # Create player sprite
    player_sprite = Player(player_x, player_y)
    all_sprites.add(player_sprite)
    
    # Create Jerome sprite
    jerome_sprite = Jerome(jerome_x, jerome_y)
    all_sprites.add(jerome_sprite)
    
    # Create furniture sprites for all rooms (cache them)
    for room_id, room_data in rooms.items():
        for furn in room_data['furniture']:
            ftype = furn.get('type', 'desk')
            f_sprite = Furniture(furn['rect'].x, furn['rect'].y, 
                               furn['rect'].width, furn['rect'].height,
                               furn['color'], ftype)
            f_sprite.room = room_id
            f_sprite.label = furn.get('label')
            f_sprite.furniture_data = furn
            furniture_sprites.add(f_sprite)

init_sprites()

# Enhanced rendering functions
def draw_floor_with_texture(surface, color, room_id):
    """Draw textured floor"""
    surface.fill(color)
    
    # Add subtle noise texture
    noise_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(-10, 10)
        pixel_color = tuple(max(0, min(255, color[i] + brightness)) for i in range(3))
        pygame.draw.rect(noise_surface, (*pixel_color, 30), (x, y, 2, 2))
    surface.blit(noise_surface, (0, 0))
    
    # Tile pattern for office rooms
    if room_id == 0:
        for x in range(0, width, 100):
            pygame.draw.line(surface, tuple(max(0, c - 5) for c in color), 
                           (x, 0), (x, height), 1)
        for y in range(0, height, 100):
            pygame.draw.line(surface, tuple(max(0, c - 5) for c in color),
                           (0, y), (width, y), 1)

def draw_wall_with_texture(surface, rect, color):
    """Draw textured wall with depth"""
    # Base wall
    pygame.draw.rect(surface, color, rect)
    
    # Highlight edge
    highlight_color = tuple(min(255, c + 15) for c in color)
    if rect.width > rect.height:  # Horizontal wall
        pygame.draw.rect(surface, highlight_color, (rect.x, rect.y, rect.width, 2))
    else:  # Vertical wall
        pygame.draw.rect(surface, highlight_color, (rect.x, rect.y, 2, rect.height))
    
    # Shadow edge
    shadow_color = tuple(max(0, c - 25) for c in color)
    if rect.width > rect.height:
        pygame.draw.rect(surface, shadow_color, (rect.x, rect.bottom - 3, rect.width, 3))
    else:
        pygame.draw.rect(surface, shadow_color, (rect.right - 3, rect.y, 3, rect.height))

def create_glow_effect(x, y, radius, color, intensity=100):
    """Create a glowing particle effect"""
    glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    for i in range(radius, 0, -1):
        alpha = int(intensity * (1 - i / radius))
        pygame.draw.circle(glow_surf, (*color[:3], alpha), (radius * 2, radius * 2), i)
    return glow_surf, (x - radius * 2, y - radius * 2)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle key presses for camera switching and mode toggle
        if event.type == pygame.KEYDOWN:
            if game_mode == "camera":
                if event.key == pygame.K_1:
                    selected_camera = 0
                elif event.key == pygame.K_2:
                    selected_camera = 1
                elif event.key == pygame.K_3:
                    selected_camera = 2
                elif event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    # Switch to walk mode
                    game_mode = "walk"
                    current_room = 0  # Start in office room
                    player_x = 150  # Safe spawn position
                    player_y = 50
                    walls = rooms[current_room]['walls']
                    transitions = rooms[current_room]['transitions']
            elif game_mode == "walk":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_c:
                    # Switch back to camera mode
                    game_mode = "camera"
    
    # Check timer for Jerome's announcement
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) / 1000  # Convert to seconds
    
    # Check if supplies are low
    if supplies_stocked == 0 and not announcement_made:
        warning_text = "SUPPLIES CRITICALLY LOW!"
        warning_timer = current_time
        danger_flash = 30
    
    # Initial announcement and spawn
    if elapsed_time >= timer_duration and not announcement_made:
        announcement_made = True
        announcement_text = "The office manager demands supplies be restocked immediately..."
        announcement_timer = current_time
        jerome_active = True
        jerome_spawn_time = current_time
        # Spawn Jerome in the hallway (room 1)
        jerome_x = width // 2
        jerome_y = height // 2
        jerome_room = 1
    
    # Jerome chase/recovery cycle
    if announcement_made:
        if jerome_active:
            # Check if chase duration is over
            if current_time - jerome_spawn_time >= jerome_chase_duration:
                jerome_active = False
                jerome_in_recovery = True
                jerome_recovery_start = current_time
        elif jerome_in_recovery:
            # Check if recovery period is over
            if current_time - jerome_recovery_start >= jerome_recovery_duration:
                jerome_in_recovery = False
                jerome_active = True
                jerome_spawn_time = current_time
                # Respawn Jerome at his last position
                if jerome_room == current_room:
                    # If in same room, spawn at opposite side
                    jerome_x = width - player_x
                    jerome_y = height - player_y
    
    # Get key presses
    keys = pygame.key.get_pressed()
    
    # Initialize player_rect for collision detection (needed even in camera mode for Jerome AI)
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    
    # Track if player is moving for animation
    player_moving = False
    
    # Only process movement in walk mode
    if game_mode == "walk":
        # Store old position
        old_x = player_x
        old_y = player_y
        
        # Move player based on input (separate X and Y for smooth sliding)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed
            player_moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed
            player_moving = True
        
        # Create player rect and check X-axis collision with walls
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for wall in walls:
            if player_rect.colliderect(wall):
                player_x = old_x
                break
        
        # Check X-axis collision with furniture
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for furniture in rooms[current_room]['furniture']:
            if player_rect.colliderect(furniture['rect']):
                player_x = old_x
                break
        
        # Update player position for Y-axis
        if keys[pygame.K_UP]:
            player_y -= player_speed
            player_moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_y += player_speed
            player_moving = True
        
        # Check Y-axis collision with walls
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for wall in walls:
            if player_rect.colliderect(wall):
                player_y = old_y
                break
        
        # Check Y-axis collision with furniture
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for furniture in rooms[current_room]['furniture']:
            if player_rect.colliderect(furniture['rect']):
                player_y = old_y
                break
        
        # Update final player rect
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        
        # Update player sprite position and animation
        player_sprite.rect.topleft = (player_x, player_y)
        player_sprite.update_animation(player_moving)
        
        # Create footstep particles when moving
        if player_moving and random.randint(0, 5) == 0:
            particles.append(Particle(
                player_x + player_size // 2 + random.randint(-5, 5),
                player_y + player_size,
                tuple(max(0, c - 20) for c in rooms[current_room]['floor_color']),
                lifetime=20,
                vel_x=random.uniform(-0.3, 0.3),
                vel_y=random.uniform(-0.5, 0),
                size=2
            ))
        
        # Check for supply restocking (E key near supplies in breakroom)
        if (keys[pygame.K_e] or keys[pygame.K_SPACE]) and current_room == 2:
            # Check if near any supply station
            for furniture in rooms[2]['furniture']:
                if furniture.get('type') == 'supply':
                    if player_rect.colliderect(furniture['rect'].inflate(50, 50)):
                        # Restock if not recently done
                        if current_time - last_restock_time > 1000:  # 1 second cooldown
                            if supplies_stocked < supplies_needed:
                                supplies_stocked += 1
                                last_restock_time = current_time
                                warning_text = f"Restocked! {supplies_stocked}/{supplies_needed}"
                                warning_timer = current_time
                        break
    
    # Supplies deplete over time
    if current_time % 5000 < 50 and supplies_stocked > 0:  # Every 5 seconds
        supplies_stocked = max(0, supplies_stocked - 1)
    
    # Jerome AI - chase the player (follows through rooms)
    if jerome_active:
        old_jerome_x = jerome_x
        old_jerome_y = jerome_y
        
        # Update Jerome's animation
        jerome_sprite.update_animation()
        
        # Only chase if Jerome is in the same room as player
        if jerome_room == current_room:
            # Move towards player (simple chase AI)
            if jerome_x < player_x:
                jerome_x += jerome_speed
            elif jerome_x > player_x:
                jerome_x -= jerome_speed
            
            # Check X collision for Jerome
            jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
            for wall in walls:
                if jerome_rect.colliderect(wall):
                    jerome_x = old_jerome_x
                    break
            
            for furniture in rooms[current_room]['furniture']:
                if jerome_rect.colliderect(furniture['rect']):
                    jerome_x = old_jerome_x
                    break
            
            # Move Y axis
            if jerome_y < player_y:
                jerome_y += jerome_speed
            elif jerome_y > player_y:
                jerome_y -= jerome_speed
            
            # Check Y collision for Jerome
            jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
            for wall in walls:
                if jerome_rect.colliderect(wall):
                    jerome_y = old_jerome_y
                    break
            
            for furniture in rooms[current_room]['furniture']:
                if jerome_rect.colliderect(furniture['rect']):
                    jerome_y = old_jerome_y
                    break
            
            # Update Jerome rect
            jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
            
            # Update Jerome sprite position
            jerome_sprite.rect.topleft = (jerome_x, jerome_y)
            
            # Check if Jerome caught the player
            if player_rect.colliderect(jerome_rect):
                # Create explosion particles
                for _ in range(30):
                    particles.append(Particle(
                        player_x + player_size // 2,
                        player_y + player_size // 2,
                        (200, 50, 50),
                        lifetime=40,
                        vel_x=random.uniform(-3, 3),
                        vel_y=random.uniform(-3, 3),
                        size=random.randint(2, 5)
                    ))
                
                # Reset player to starting position (safe spot)
                player_x = 150
                player_y = 50
                current_room = 0
                walls = rooms[current_room]['walls']
                transitions = rooms[current_room]['transitions']
                player_sprite.rect.topleft = (player_x, player_y)
        else:
            # Jerome tries to follow player to their room through doorways
            # Check if Jerome can transition to follow player
            for transition_rect, destination_room, spawn_x, spawn_y in rooms[jerome_room]['transitions']:
                jerome_transition_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
                if jerome_transition_rect.colliderect(transition_rect) and destination_room == current_room:
                    # Jerome follows through the door
                    jerome_room = destination_room
                    jerome_x = spawn_x
                    jerome_y = spawn_y
                    break
            
            # Move Jerome towards the transition that leads to player's room
            for transition_rect, destination_room, _, _ in rooms[jerome_room]['transitions']:
                if destination_room == current_room:
                    # Move towards this transition
                    transition_center_x = transition_rect.centerx
                    transition_center_y = transition_rect.centery
                    
                    if jerome_x < transition_center_x:
                        jerome_x += jerome_speed
                    elif jerome_x > transition_center_x:
                        jerome_x -= jerome_speed
                    
                    # Check X collision
                    jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
                    for wall in rooms[jerome_room]['walls']:
                        if jerome_rect.colliderect(wall):
                            jerome_x = old_jerome_x
                            break
                    
                    for furniture in rooms[jerome_room]['furniture']:
                        if jerome_rect.colliderect(furniture['rect']):
                            jerome_x = old_jerome_x
                            break
                    
                    if jerome_y < transition_center_y:
                        jerome_y += jerome_speed
                    elif jerome_y > transition_center_y:
                        jerome_y -= jerome_speed
                    
                    # Check Y collision
                    jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
                    for wall in rooms[jerome_room]['walls']:
                        if jerome_rect.colliderect(wall):
                            jerome_y = old_jerome_y
                            break
                    
                    for furniture in rooms[jerome_room]['furniture']:
                        if jerome_rect.colliderect(furniture['rect']):
                            jerome_y = old_jerome_y
                            break
                    break
    
    # Update particles
    particles[:] = [p for p in particles if p.update()]
    
    # Check for room transitions (only in walk mode)
    if game_mode == "walk":
        for transition_rect, destination_room, spawn_x, spawn_y in transitions:
            if player_rect.colliderect(transition_rect):
                current_room = destination_room
                player_x = spawn_x
                player_y = spawn_y
                walls = rooms[current_room]['walls']
                transitions = rooms[current_room]['transitions']
                break
    
    # Draw based on mode
    if game_mode == "camera":
        # Camera mode - show selected room with FNAF-style camera effect
        screen.fill(BLACK)
        
        # Draw the selected room view
        camera_room = selected_camera
        room_surface = pygame.Surface((width - 100, height - 150))
        
        # Draw textured floor
        draw_floor_with_texture(room_surface, rooms[camera_room]['floor_color'], camera_room)
        
        # Draw walls with texture
        for wall in rooms[camera_room]['walls']:
            draw_wall_with_texture(room_surface, wall, WALL_ACCENT)
        
        # Draw furniture sprites for this room
        for furn_sprite in furniture_sprites:
            if furn_sprite.room == camera_room:
                # Draw shadow first
                shadow_pos = (furn_sprite.rect.x + 4, furn_sprite.rect.bottom)
                room_surface.blit(furn_sprite.shadow, shadow_pos)
                
                # Draw furniture
                room_surface.blit(furn_sprite.image, furn_sprite.rect)
                
                # Highlight supply stations with glow
                if furn_sprite.furniture_data.get('type') == 'supply':
                    supply_color = (100, 255, 100) if supplies_stocked > 1 else (255, 100, 100)
                    glow_surf, glow_pos = create_glow_effect(
                        furn_sprite.rect.centerx, furn_sprite.rect.centery,
                        25, supply_color, 80
                    )
                    room_surface.blit(glow_surf, glow_pos)
                    pygame.draw.rect(room_surface, supply_color, furn_sprite.rect, 3)
                
                # Draw labels
                if furn_sprite.label:
                    font = pygame.font.Font(None, 16)
                    text = font.render(furn_sprite.label, True, BLOOD_RED)
                    text_rect = text.get_rect(center=furn_sprite.rect.center)
                    room_surface.blit(text, text_rect)
        
        # Draw Jerome if he's in this camera view
        if jerome_active and jerome_room == camera_room:
            # Draw Jerome's shadow
            shadow_pos = (jerome_x + 4, jerome_y + jerome_size)
            room_surface.blit(jerome_sprite.shadow, shadow_pos)
            
            # Draw ominous glow around Jerome
            glow_surf, glow_pos = create_glow_effect(
                jerome_x + jerome_size // 2, jerome_y + jerome_size // 2,
                30, (120, 20, 20), 60
            )
            room_surface.blit(glow_surf, glow_pos)
            
            # Draw Jerome sprite
            jerome_sprite.rect.topleft = (jerome_x, jerome_y)
            room_surface.blit(jerome_sprite.image, jerome_sprite.rect)
        
        # Apply static/noise effect
        static_surface = pygame.Surface((width - 100, height - 150), pygame.SRCALPHA)
        for _ in range(200):
            x = random.randint(0, width - 100)
            y = random.randint(0, height - 150)
            size = random.randint(1, 3)
            alpha = random.randint(30, 100)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255), alpha)
            pygame.draw.rect(static_surface, color, (x, y, size, size))
        
        room_surface.blit(static_surface, (0, 0))
        
        # Add scanlines
        for y in range(0, height - 150, 4):
            pygame.draw.line(room_surface, (0, 0, 0, 30), (0, y), (width - 100, y), 1)
        
        # Draw vignette (darker edges)
        vignette = pygame.Surface((width - 100, height - 150), pygame.SRCALPHA)
        for i in range(50):
            alpha = int((i / 50) * 100)
            pygame.draw.rect(vignette, (0, 0, 0, alpha), (i, i, width - 100 - i * 2, height - 150 - i * 2), 2)
        room_surface.blit(vignette, (0, 0))
        
        # Blit camera view to screen
        screen.blit(room_surface, (50, 75))
        
        # Draw camera frame/border
        pygame.draw.rect(screen, WALL_DARK, (45, 70, width - 90, height - 140), 5)
        
        # Camera UI
        camera_names = ["CAM 1: Office", "CAM 2: Hallway", "CAM 3: Breakroom"]
        ui_font = pygame.font.Font(None, 28)
        title_text = ui_font.render(camera_names[selected_camera], True, (150, 255, 150))
        screen.blit(title_text, (60, 30))
        
        # Supply status indicator
        supply_font = pygame.font.Font(None, 24)
        supply_color = (100, 255, 100) if supplies_stocked >= 2 else (255, 100, 100) if supplies_stocked == 1 else (255, 50, 50)
        supply_text = supply_font.render(f"Supplies: {supplies_stocked}/{supplies_needed}", True, supply_color)
        screen.blit(supply_text, (width - 200, 30))
        
        # Instructions
        inst_font = pygame.font.Font(None, 22)
        instructions = [
            "1,2,3 - Switch Cameras",
            "SPACE/W - Walk Mode"
        ]
        for i, inst in enumerate(instructions):
            text = inst_font.render(inst, True, (180, 180, 180))
            screen.blit(text, (60, height - 70 + i * 25))
        
        # Camera indicator boxes
        for i in range(3):
            box_x = width - 150
            box_y = 100 + i * 60
            box_color = (100, 200, 100) if i == selected_camera else (80, 80, 80)
            pygame.draw.rect(screen, box_color, (box_x, box_y, 120, 40))
            pygame.draw.rect(screen, WHITE, (box_x, box_y, 120, 40), 2)
            cam_text = inst_font.render(f"CAM {i+1}", True, WHITE)
            screen.blit(cam_text, (box_x + 20, box_y + 10))
    
    else:  # walk mode
        # Draw textured floor
        draw_floor_with_texture(screen, rooms[current_room]['floor_color'], current_room)
        
        # Draw walls with texture
        for wall in walls:
            draw_wall_with_texture(screen, wall, WALL_ACCENT)
        
        # Draw furniture sprites for current room
        for furn_sprite in furniture_sprites:
            if furn_sprite.room == current_room:
                # Draw shadow
                shadow_pos = (furn_sprite.rect.x + 4, furn_sprite.rect.bottom)
                screen.blit(furn_sprite.shadow, shadow_pos)
                
                # Check if near player for highlighting
                if furn_sprite.furniture_data.get('type') == 'supply' and player_rect.colliderect(furn_sprite.rect.inflate(50, 50)):
                    # Pulse effect - no color mod needed, using glow instead
                    
                    # Enhanced glow for nearby supply
                    glow_surf, glow_pos = create_glow_effect(
                        furn_sprite.rect.centerx, furn_sprite.rect.centery,
                        35, (100, 255, 100), 120
                    )
                    screen.blit(glow_surf, glow_pos)
                    
                    # Draw interaction hint
                    hint_font = pygame.font.Font(None, 20)
                    hint_text = hint_font.render("Press E or SPACE", True, (200, 255, 200))
                    hint_bg = pygame.Surface((hint_text.get_width() + 10, hint_text.get_height() + 6), pygame.SRCALPHA)
                    pygame.draw.rect(hint_bg, (0, 0, 0, 180), hint_bg.get_rect(), border_radius=5)
                    hint_bg.blit(hint_text, (5, 3))
                    screen.blit(hint_bg, (furn_sprite.rect.centerx - hint_bg.get_width() // 2, 
                                         furn_sprite.rect.y - 35))
                
                # Draw furniture sprite
                screen.blit(furn_sprite.image, furn_sprite.rect)
                
                # Always draw supply station borders in bright color
                if furn_sprite.furniture_data.get('type') == 'supply':
                    supply_border_color = (100, 255, 100) if supplies_stocked > 1 else (255, 100, 100)
                    pygame.draw.rect(screen, supply_border_color, furn_sprite.rect, 4)
                    
                    # Subtle glow
                    glow_surf, glow_pos = create_glow_effect(
                        furn_sprite.rect.centerx, furn_sprite.rect.centery,
                        25, supply_border_color, 60
                    )
                    screen.blit(glow_surf, glow_pos)
                
                # Draw label if exists
                if furn_sprite.label:
                    font = pygame.font.Font(None, 16)
                    text = font.render(furn_sprite.label, True, WHITE)
                    text_rect = text.get_rect(center=furn_sprite.rect.center)
                    # Draw text background
                    bg_rect = text_rect.inflate(8, 4)
                    pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect, border_radius=3)
                    screen.blit(text, text_rect)
        
        # Draw transition zones (darker, ominous doorways)
        for transition_rect, _, _, _ in transitions:
            pygame.draw.rect(screen, SHADOW_BLACK, transition_rect)
            pygame.draw.rect(screen, BLOOD_RED, transition_rect, 2)
            
            # Add subtle red glow to doorways
            glow_surf, glow_pos = create_glow_effect(
                transition_rect.centerx, transition_rect.centery,
                20, BLOOD_RED, 40
            )
            screen.blit(glow_surf, glow_pos)
        
        # Draw particles
        for particle in particles:
            particle.draw(screen)
        
        # Draw player shadow
        shadow_pos = (player_x - 5, player_y + player_size)
        screen.blit(player_sprite.shadow, shadow_pos)
        
        # Draw player sprite
        screen.blit(player_sprite.image, player_sprite.rect)
        
        # Draw Jerome if active (only if in the same room as player)
        if jerome_active and jerome_room == current_room:
            # Draw Jerome's shadow
            shadow_pos = (jerome_x + 4, jerome_y + jerome_size)
            screen.blit(jerome_sprite.shadow, shadow_pos)
            
            # Draw ominous red glow around Jerome
            glow_surf, glow_pos = create_glow_effect(
                jerome_x + jerome_size // 2, jerome_y + jerome_size // 2,
                40, (120, 20, 20), 100
            )
            screen.blit(glow_surf, glow_pos)
            
            # Draw Jerome sprite
            screen.blit(jerome_sprite.image, jerome_sprite.rect)
            
            # Draw clipboard/papers
            angle_to_player = math.atan2(player_y - jerome_y, player_x - jerome_x)
            clipboard_length = 35
            clipboard_end_x = jerome_x + jerome_size // 2 + math.cos(angle_to_player) * clipboard_length
            clipboard_end_y = jerome_y + jerome_size // 2 + math.sin(angle_to_player) * clipboard_length
            # Draw clipboard with shadow effect
            pygame.draw.line(screen, (30, 30, 35), 
                            (jerome_x + jerome_size // 2 + 2, jerome_y + jerome_size // 2 + 2),
                            (clipboard_end_x + 2, clipboard_end_y + 2), 9)
            pygame.draw.line(screen, OFFICE_GRAY, 
                            (jerome_x + jerome_size // 2, jerome_y + jerome_size // 2),
                            (clipboard_end_x, clipboard_end_y), 8)
            
            # Draw Jerome's title with glow
            font_small = pygame.font.Font(None, 20)
            name_text = font_small.render("Manager", True, (200, 150, 150))
            name_bg = pygame.Surface((name_text.get_width() + 8, name_text.get_height() + 4), pygame.SRCALPHA)
            pygame.draw.rect(name_bg, (80, 20, 20, 200), name_bg.get_rect(), border_radius=4)
            name_bg.blit(name_text, (4, 2))
            screen.blit(name_bg, (jerome_x - 5, jerome_y - 25))
        
        # Walk mode instructions
        walk_inst_font = pygame.font.Font(None, 20)
        walk_text = walk_inst_font.render("ESC/C - Cameras", True, (180, 180, 180))
        screen.blit(walk_text, (10, height - 25))
        
        # Supply indicator in walk mode
        supply_status_font = pygame.font.Font(None, 24)
        supply_status_color = (100, 255, 100) if supplies_stocked >= 2 else (255, 255, 100) if supplies_stocked == 1 else (255, 50, 50)
        supply_status_text = supply_status_font.render(f"Supplies: {supplies_stocked}/{supplies_needed}", True, supply_status_color)
        screen.blit(supply_status_text, (10, 10))
    
    # Draw timer
    time_left = max(0, timer_duration - elapsed_time)
    font = pygame.font.Font(None, 32)
    
    if not announcement_made:
        timer_text = font.render(f"Time: {int(time_left)}s", True, (150, 130, 130))
    elif jerome_active:
        chase_time_left = (jerome_chase_duration - (current_time - jerome_spawn_time)) / 1000
        if jerome_room == current_room and game_mode == "walk":
            timer_text = font.render(f"DANGER: {max(0, int(chase_time_left))}s", True, BLOOD_RED)
            danger_flash = 20
        elif jerome_room == current_room:
            timer_text = font.render(f"Manager here: {max(0, int(chase_time_left))}s", True, (200, 100, 100))
        else:
            timer_text = font.render(f"Manager nearby: {max(0, int(chase_time_left))}s", True, (150, 100, 100))
    elif jerome_in_recovery:
        recovery_time_left = (jerome_recovery_duration - (current_time - jerome_recovery_start)) / 1000
        timer_text = font.render(f"Break: {max(0, int(recovery_time_left))}s", True, SICKLY_GREEN)
    
    # Draw timer with office-style background
    timer_bg_width = timer_text.get_width() + 20
    timer_bg = pygame.Surface((timer_bg_width, 45))
    timer_bg.fill(SHADOW_BLACK)
    timer_bg.set_alpha(180)
    
    # Position based on mode
    timer_x = 5 if game_mode == "walk" else width // 2 - timer_bg_width // 2
    timer_y = 40 if game_mode == "walk" else 5
    
    screen.blit(timer_bg, (timer_x, timer_y))
    screen.blit(timer_text, (timer_x + 10, timer_y + 10))
    
    # Warning/danger flash
    if danger_flash > 0:
        danger_flash -= 1
        flash_alpha = danger_flash * 3
        flash_surface = pygame.Surface((width, height))
        flash_surface.fill((255, 0, 0))
        flash_surface.set_alpha(flash_alpha)
        screen.blit(flash_surface, (0, 0))
    
    # Warning text
    if warning_text and (current_time - warning_timer) < 3000:
        warning_font = pygame.font.Font(None, 28)
        warning_surface = warning_font.render(warning_text, True, (255, 200, 100))
        warning_bg = pygame.Surface((warning_surface.get_width() + 20, 40))
        warning_bg.fill(SHADOW_BLACK)
        warning_bg.set_alpha(200)
        screen.blit(warning_bg, (width // 2 - warning_surface.get_width() // 2 - 10, height - 60))
        screen.blit(warning_surface, (width // 2 - warning_surface.get_width() // 2, height - 55))
    
    # Draw announcement if made (show for 5 seconds)
    if announcement_made and (current_time - announcement_timer) < 5000:
        announcement_font = pygame.font.Font(None, 24)
        # Word wrap the announcement
        words = announcement_text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if announcement_font.size(test_line)[0] < width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        # Draw subtle announcement box
        box_height = len(lines) * 30 + 20
        pygame.draw.rect(screen, SHADOW_BLACK, (10, height - box_height - 10, width - 20, box_height))
        pygame.draw.rect(screen, OFFICE_GRAY, (10, height - box_height - 10, width - 20, box_height), 3)
        
        # Draw text lines
        for i, line in enumerate(lines):
            text_color = (180, 160, 160)
            text_surface = announcement_font.render(line.strip(), True, text_color)
            screen.blit(text_surface, (20, height - box_height + i * 30))
    
    # Update the display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
