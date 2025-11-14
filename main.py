import pygame
import sys
import random
import math
import threading
import os
from openai import OpenAI

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 1000, 600  # Wider for longer hallway
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Office Nightmare")

# Create surfaces for caching
cached_surfaces = {}

# Load camera images
camera_images = [
    pygame.image.load("entrance.jpg"),
    pygame.image.load("hallway.jpg"),
    pygame.image.load("break_room.jpg")
]

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
game_mode = "tutorial"  # "tutorial", "camera", "walk"
selected_camera = 0  # Which room camera is viewing

# Game state
game_state = "playing"  # "playing", "game_over"

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
start_time = pygame.time.get_ticks()

# Snack stocking system
snacks_stocked = 0
snacks_needed = 5
snack_check_timer = 0
snack_check_interval = 15000  # Check every 15 seconds

# Difficulty scaling - snack consumption gets faster over time
snack_consumption_interval = 12000  # Start at 12 seconds
snack_consumption_min = 4000  # Minimum 4 seconds
snack_consumption_last = 0
difficulty_increase_rate = 200  # Decrease interval by 200ms each consumption

# Dynamic supply spawning
active_supplies = []  # List of active supply stations
max_supplies = 2  # Max number of supplies active at once

# Player inventory
carrying_snack = False

# Jerome (enemy) settings
jerome_active = True  # Jerome is always present, walking around
jerome_x = width // 2
jerome_y = height // 2
jerome_size = 45
jerome_patrol_speed = 1.0  # Slow patrol speed
jerome_angry_speed = 3.0  # Fast chase speed
jerome_color = (60, 40, 70)  # Dark purple/gray
jerome_room = 1  # Starts in hallway
jerome_state = "patrolling"  # "patrolling", "angry"
jerome_patience = 100  # Patience meter (depletes when snacks are low)
jerome_target_x = 0
jerome_target_y = 0
jerome_patrol_timer = 0

# Patrol waypoints for each room
patrol_waypoints = {
    0: [(200, 100), (400, 200), (300, 400), (150, 300)],  # Office
    1: [(200, 200), (500, 300), (800, 200), (500, 400)],  # Hallway
    2: [(300, 150), (600, 250), (400, 450)]  # Breakroom
}
current_waypoint_index = 0

# MMO-style UI variables
player_health = 100
player_max_health = 100
player_stamina = 100
player_max_stamina = 100
stamina_regen_rate = 0.5
sprint_drain_rate = 2.0
is_sprinting = False

# Visual feedback
danger_flash = 0
warning_text = ""
warning_timer = 0
objective_text = "Stock the Break Room with 5 snacks to keep Jerome happy!"
show_tutorial = True
last_patience_warning = 0
warning_timer = 0

# ChatGPT Joke System
joke_text = "Loading joke..."
joke_timer = 0
joke_fetch_timer = 0
joke_fetch_interval = 30000  # Fetch new joke every 30 seconds
is_fetching_joke = False

# Initialize OpenAI client (set your API key as environment variable OPENAI_API_KEY)
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    chatgpt_available = True
except:
    client = None
    chatgpt_available = False
    joke_text = "Set OPENAI_API_KEY environment variable to enable jokes!"

def fetch_joke_from_chatgpt():
    """Fetch a joke from ChatGPT in a separate thread"""
    global joke_text, is_fetching_joke
    
    if not chatgpt_available:
        return
    
    is_fetching_joke = True
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a comedian. Tell short, funny jokes (2-3 sentences max)."},
                {"role": "user", "content": "Tell me a random funny joke."}
            ],
            max_tokens=100,
            temperature=0.9
        )
        
        new_joke = response.choices[0].message.content.strip()
        joke_text = new_joke
        
    except Exception as e:
        joke_text = f"Joke error: {str(e)[:50]}..."
    
    is_fetching_joke = False

def start_joke_fetch():
    """Start fetching a joke in a background thread"""
    if not is_fetching_joke:
        thread = threading.Thread(target=fetch_joke_from_chatgpt, daemon=True)
        thread.start()

# Fetch first joke on startup
if chatgpt_available:
    start_joke_fetch()

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
            
            # Jerome's desk
            {'rect': pygame.Rect(150, 450, 150, 80), 'color': RUSTY_BROWN, 'label': "Jerome's Desk"},
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
            # Long break table with snacks (table is non-collidable decoration)
            {'rect': pygame.Rect(width // 2 - 150, height // 2 - 40, 300, 80), 'color': DESK_BROWN, 'label': None, 'type': 'table_with_snacks'},
            
            # Old vending machine
            {'rect': pygame.Rect(50, 50, 60, 100), 'color': WALL_DARK, 'label': "Broken"},
        ],
        'decorations': [
            # Snacks on the table (non-collidable)
            {'rect': pygame.Rect(width // 2 - 120, height // 2 - 10, 30, 20), 'color': RED, 'label': "Chips"},
            {'rect': pygame.Rect(width // 2 - 70, height // 2 - 10, 25, 20), 'color': ORANGE, 'label': "Cookies"},
            {'rect': pygame.Rect(width // 2 - 20, height // 2 - 10, 35, 20), 'color': YELLOW, 'label': "Crackers"},
            {'rect': pygame.Rect(width // 2 + 30, height // 2 - 10, 28, 20), 'color': PURPLE, 'label': "Candy"},
            {'rect': pygame.Rect(width // 2 + 80, height // 2 - 10, 30, 20), 'color': GREEN, 'label': "Fruit"},
        ],
        'transitions': [
            # Back to hallway
            (pygame.Rect(0, height // 2 - 60, 20, 120), 1, width - 60, height // 2),
        ]
    }
}

walls = rooms[current_room]['walls']
transitions = rooms[current_room]['transitions']

# Function to spawn a new supply station in a random valid location
def spawn_new_supply():
    """Spawn a supply station in a random room at a random valid position"""
    if len(active_supplies) >= max_supplies:
        return
    
    # Pick a random room
    room_id = random.randint(0, 2)
    
    # Define safe spawn areas for each room (avoiding walls and furniture)
    safe_areas = {
        0: [(100, 60, 400, 380)],  # Office - between desks
        1: [(120, 80, 860, 440)],  # Hallway - center corridor
        2: [(100, 60, 300, 200), (600, 60, 300, 200)]  # Breakroom - sides
    }
    
    # Pick a random safe area in the room
    areas = safe_areas[room_id]
    area = random.choice(areas)
    
    # Random position within the area
    x = random.randint(area[0], area[0] + area[2] - 50)
    y = random.randint(area[1], area[1] + area[3] - 50)
    
    # Random color for variety
    colors = [RUSTY_BROWN, DIM_YELLOW, SICKLY_GREEN, ORANGE, PURPLE]
    color = random.choice(colors)
    
    active_supplies.append({
        'x': x,
        'y': y,
        'room': room_id,
        'color': color
    })

# Initialize starting supplies
for _ in range(max_supplies):
    spawn_new_supply()

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

def draw_mmo_ui(surface, current_time):
    """Draw MMO-style UI elements"""
    # Health bar (top left)
    health_bar_width = 200
    health_bar_height = 25
    health_bar_x = 10
    health_bar_y = 10
    
    # Health bar background
    pygame.draw.rect(surface, (40, 40, 40), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), border_radius=5)
    
    # Health bar fill (gradient from green to red)
    health_percent = player_health / player_max_health
    health_fill_width = int(health_bar_width * health_percent)
    if health_percent > 0.5:
        health_color = (50, 200, 50)
    elif health_percent > 0.25:
        health_color = (200, 200, 50)
    else:
        health_color = (200, 50, 50)
    
    if health_fill_width > 0:
        pygame.draw.rect(surface, health_color, (health_bar_x, health_bar_y, health_fill_width, health_bar_height), border_radius=5)
    
    # Health bar border
    pygame.draw.rect(surface, (200, 200, 200), (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2, border_radius=5)
    
    # Health text
    health_font = pygame.font.Font(None, 18)
    health_text = health_font.render(f"HP: {int(player_health)}/{player_max_health}", True, WHITE)
    surface.blit(health_text, (health_bar_x + health_bar_width // 2 - health_text.get_width() // 2, health_bar_y + 5))
    
    # Stamina bar (below health)
    stamina_bar_y = health_bar_y + health_bar_height + 5
    pygame.draw.rect(surface, (40, 40, 40), (health_bar_x, stamina_bar_y, health_bar_width, 20), border_radius=4)
    
    stamina_percent = player_stamina / player_max_stamina
    stamina_fill_width = int(health_bar_width * stamina_percent)
    stamina_color = (100, 180, 255) if player_stamina > 30 else (100, 100, 150)
    
    if stamina_fill_width > 0:
        pygame.draw.rect(surface, stamina_color, (health_bar_x, stamina_bar_y, stamina_fill_width, 20), border_radius=4)
    
    pygame.draw.rect(surface, (150, 180, 200), (health_bar_x, stamina_bar_y, health_bar_width, 20), 2, border_radius=4)
    
    stamina_text = health_font.render(f"Stamina: {int(player_stamina)}", True, WHITE)
    surface.blit(stamina_text, (health_bar_x + health_bar_width // 2 - stamina_text.get_width() // 2, stamina_bar_y + 2))
    
    # Request/Objective status (right side)
    status_box_width = 220
    status_box_x = width - status_box_width - 10
    status_box_y = 10
    
    pygame.draw.rect(surface, (40, 40, 40), (status_box_x, status_box_y, status_box_width, 90), border_radius=5)
    pygame.draw.rect(surface, (100, 100, 100), (status_box_x, status_box_y, status_box_width, 90), 2, border_radius=5)
    
    status_title = health_font.render("SNACK STATUS", True, (200, 200, 200))
    surface.blit(status_title, (status_box_x + status_box_width // 2 - status_title.get_width() // 2, status_box_y + 5))
    
    # Show snack count with visual icons
    snack_font = pygame.font.Font(None, 28)
    snack_text = snack_font.render(f"{snacks_stocked} / {snacks_needed}", True, WHITE)
    surface.blit(snack_text, (status_box_x + status_box_width // 2 - snack_text.get_width() // 2, status_box_y + 30))
    
    # Snack icons
    icon_y = status_box_y + 62
    icon_size = 12
    for i in range(snacks_needed):
        icon_x = status_box_x + 40 + i * 30
        if i < snacks_stocked:
            # Filled snack (colorful)
            snack_colors = [RED, ORANGE, YELLOW, PURPLE, GREEN]
            pygame.draw.circle(surface, snack_colors[i % len(snack_colors)], (icon_x, icon_y), icon_size)
            pygame.draw.circle(surface, WHITE, (icon_x, icon_y), icon_size, 2)
        else:
            # Empty slot
            pygame.draw.circle(surface, (80, 80, 80), (icon_x, icon_y), icon_size)
            pygame.draw.circle(surface, (120, 120, 120), (icon_x, icon_y), icon_size, 2)
    
    # Jerome's Patience meter
    patience_bar_y = status_box_y + 95
    patience_bar_width = status_box_width - 20
    
    patience_title_font = pygame.font.Font(None, 16)
    patience_title = patience_title_font.render("Jerome's Patience:", True, (200, 200, 200))
    surface.blit(patience_title, (status_box_x + 10, patience_bar_y - 15))
    
    pygame.draw.rect(surface, (60, 60, 60), (status_box_x + 10, patience_bar_y, patience_bar_width, 14), border_radius=3)
    
    if jerome_patience > 0:
        patience_fill = int(patience_bar_width * (jerome_patience / 100))
        if jerome_patience > 60:
            patience_color = (100, 255, 100)
        elif jerome_patience > 30:
            patience_color = (255, 255, 100)
        else:
            patience_color = (255, 100, 100)
        pygame.draw.rect(surface, patience_color, (status_box_x + 10, patience_bar_y, patience_fill, 14), border_radius=3)
    
    patience_label = pygame.font.Font(None, 14).render(f"{int(jerome_patience)}%", True, WHITE)
    surface.blit(patience_label, (status_box_x + patience_bar_width // 2 + 10 - patience_label.get_width() // 2, patience_bar_y + 1))
    
    # Adjust box height to fit patience meter
    pygame.draw.rect(surface, (40, 40, 40), (status_box_x, status_box_y, status_box_width, 120), border_radius=5)
    pygame.draw.rect(surface, (100, 100, 100), (status_box_x, status_box_y, status_box_width, 120), 2, border_radius=5)
    
    # Redraw title and content over adjusted box
    surface.blit(status_title, (status_box_x + status_box_width // 2 - status_title.get_width() // 2, status_box_y + 5))
    surface.blit(snack_text, (status_box_x + status_box_width // 2 - snack_text.get_width() // 2, status_box_y + 30))
    for i in range(snacks_needed):
        icon_x = status_box_x + 40 + i * 30
        if i < snacks_stocked:
            snack_colors = [RED, ORANGE, YELLOW, PURPLE, GREEN]
            pygame.draw.circle(surface, snack_colors[i % len(snack_colors)], (icon_x, icon_y), icon_size)
            pygame.draw.circle(surface, WHITE, (icon_x, icon_y), icon_size, 2)
        else:
            pygame.draw.circle(surface, (80, 80, 80), (icon_x, icon_y), icon_size)
            pygame.draw.circle(surface, (120, 120, 120), (icon_x, icon_y), icon_size, 2)
    surface.blit(patience_title, (status_box_x + 10, patience_bar_y - 15))
    pygame.draw.rect(surface, (60, 60, 60), (status_box_x + 10, patience_bar_y, patience_bar_width, 14), border_radius=3)
    if jerome_patience > 0:
        patience_fill = int(patience_bar_width * (jerome_patience / 100))
        if jerome_patience > 60:
            patience_color = (100, 255, 100)
        elif jerome_patience > 30:
            patience_color = (255, 255, 100)
        else:
            patience_color = (255, 100, 100)
        pygame.draw.rect(surface, patience_color, (status_box_x + 10, patience_bar_y, patience_fill, 14), border_radius=3)
    surface.blit(patience_label, (status_box_x + patience_bar_width // 2 + 10 - patience_label.get_width() // 2, patience_bar_y + 1))
    
    # Minimap (bottom right)
    minimap_size = 120
    minimap_x = width - minimap_size - 10
    minimap_y = height - minimap_size - 10
    
    pygame.draw.rect(surface, (20, 20, 30), (minimap_x, minimap_y, minimap_size, minimap_size), border_radius=5)
    pygame.draw.rect(surface, (100, 100, 120), (minimap_x, minimap_y, minimap_size, minimap_size), 2, border_radius=5)
    
    # Draw room indicators on minimap
    room_colors = {0: (80, 80, 100), 1: (60, 70, 80), 2: (70, 80, 100)}
    room_positions = {0: (minimap_x + 10, minimap_y + 10), 1: (minimap_x + 50, minimap_y + 10), 2: (minimap_x + 90, minimap_y + 10)}
    
    for room_id, pos in room_positions.items():
        color = room_colors[room_id]
        if room_id == current_room:
            pygame.draw.rect(surface, (100, 255, 100), (pos[0], pos[1], 20, 90), border_radius=3)
        else:
            pygame.draw.rect(surface, color, (pos[0], pos[1], 20, 90), border_radius=3)
        pygame.draw.rect(surface, WHITE, (pos[0], pos[1], 20, 90), 1, border_radius=3)
    
    # Player indicator
    player_pos = room_positions[current_room]
    player_minimap_x = player_pos[0] + 10
    player_minimap_y = player_pos[1] + int(90 * (player_y / height))
    pygame.draw.circle(surface, (100, 255, 100), (player_minimap_x, player_minimap_y), 3)
    
    # Jerome indicator
    if jerome_active:
        jerome_pos = room_positions.get(jerome_room)
        if jerome_pos:
            jerome_minimap_x = jerome_pos[0] + 10
            jerome_minimap_y = jerome_pos[1] + int(90 * (jerome_y / height))
            pygame.draw.circle(surface, (255, 50, 50), (jerome_minimap_x, jerome_minimap_y), 3)
            # Pulse effect
            if current_time % 1000 < 500:
                pygame.draw.circle(surface, (255, 50, 50, 100), (jerome_minimap_x, jerome_minimap_y), 5, 1)
    
    # Room labels on minimap
    minimap_font = pygame.font.Font(None, 12)
    labels = ["OFF", "HALL", "BRK"]
    for room_id, label in enumerate(labels):
        pos = room_positions[room_id]
        label_surf = minimap_font.render(label, True, WHITE)
        surface.blit(label_surf, (pos[0] + 10 - label_surf.get_width() // 2, pos[1] + 95))

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
            # Tutorial/Intro - press space to start
            if game_mode == "tutorial" and event.key == pygame.K_SPACE:
                game_mode = "camera"
                game_state = "playing"
                start_time = pygame.time.get_ticks()
                snack_check_timer = pygame.time.get_ticks()
                objective_text = "Stock the Break Room with 5 snacks to keep Jerome happy!"
                show_tutorial = False
                # Start Jerome patrolling in hallway
                jerome_x = width // 2
                jerome_y = height // 2
                jerome_room = 1
                jerome_state = "patrolling"
                jerome_patrol_timer = pygame.time.get_ticks()
            
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
    
    # Get current time
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) / 1000  # Convert to seconds
    
    # ChatGPT Joke Fetch Timer
    if chatgpt_available and current_time - joke_fetch_timer > joke_fetch_interval:
        joke_fetch_timer = current_time
        start_joke_fetch()
    
    # NEW GAME LOGIC - Snack Stocking System
    if game_mode != "tutorial" and game_state == "playing":
        # Periodic snack checks (every 15 seconds)
        if current_time - snack_check_timer > snack_check_interval:
            snack_check_timer = current_time
            
            # Check if snacks are low
            if snacks_stocked < snacks_needed:
                # Deplete Jerome's patience based on how low snacks are
                shortage = snacks_needed - snacks_stocked
                patience_loss = shortage * 8  # More shortage = faster patience loss
                jerome_patience = max(0, jerome_patience - patience_loss)
                
                if jerome_patience <= 50 and current_time - last_patience_warning > 10000:
                    warning_text = f"Jerome's patience is low! Stock more snacks! ({snacks_stocked}/{snacks_needed})"
                    warning_timer = current_time
                    last_patience_warning = current_time
                
                # Jerome gets angry when patience hits 0
                if jerome_patience <= 0 and jerome_state != "angry":
                    jerome_state = "angry"
                    objective_text = "JEROME IS ANGRY! STOCK SNACKS TO CALM HIM DOWN!"
                    danger_flash = 30
                    player_health = max(0, player_health - 15)
            else:
                # Snacks are good, restore patience
                jerome_patience = min(100, jerome_patience + 5)
                if jerome_state == "angry":
                    # Jerome calms down when snacks are fully stocked
                    jerome_state = "patrolling"
                    objective_text = "Jerome calmed down. Keep snacks stocked!"
                    player_health = min(player_max_health, player_health + 20)
                    warning_text = "Good job! (+20 HP)"
                    warning_timer = current_time
        
        # Continuous patience drain when understocked (faster feedback)
        if snacks_stocked < snacks_needed and current_time % 1000 < 50:
            jerome_patience = max(0, jerome_patience - 0.3)
        
        # Jerome AI based on state
        if jerome_state == "angry":
            # Chase the player aggressively with clipboard/flog
            current_speed = jerome_angry_speed
            
            # Track player across rooms
            if jerome_room != current_room:
                # Pathfind to player's room through transitions
                for transition_rect, dest_room, spawn_x, spawn_y in rooms[jerome_room]['transitions']:
                    if dest_room == current_room or (current_room not in [jerome_room, dest_room]):
                        jerome_rect_check = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
                        if jerome_rect_check.colliderect(transition_rect):
                            jerome_room = dest_room
                            # Ensure spawn position is valid
                            jerome_x = max(30, min(width - 50, spawn_x))
                            jerome_y = max(30, min(height - 50, spawn_y))
                            break
        
        elif jerome_state == "patrolling":
            # Jerome patrols waypoints in current room
            current_speed = jerome_patrol_speed
            
            # Change rooms periodically
            if current_time - jerome_patrol_timer > 20000:  # Change room every 20 seconds
                jerome_patrol_timer = current_time
                # Pick a random adjacent room
                possible_rooms = [dest for _, dest, _, _ in rooms[jerome_room]['transitions']]
                if possible_rooms:
                    next_room = random.choice(possible_rooms)
                    # Move to transition and spawn in new room
                    for transition_rect, dest_room, spawn_x, spawn_y in rooms[jerome_room]['transitions']:
                        if dest_room == next_room:
                            # Ensure spawn position is valid and not in walls
                            jerome_room = next_room
                            jerome_x = max(30, min(width - 50, spawn_x))
                            jerome_y = max(30, min(height - 50, spawn_y))
                            current_waypoint_index = 0
                            break
            
            # Patrol within current room
            if jerome_room in patrol_waypoints:
                waypoints = patrol_waypoints[jerome_room]
                target_x, target_y = waypoints[current_waypoint_index]
                
                # Move toward current waypoint
                dx = target_x - jerome_x
                dy = target_y - jerome_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < 10:  # Reached waypoint
                    current_waypoint_index = (current_waypoint_index + 1) % len(waypoints)
                else:
                    # Move toward target
                    jerome_x += (dx / distance) * current_speed if distance > 0 else 0
                    jerome_y += (dy / distance) * current_speed if distance > 0 else 0
    
    # Get key presses
    keys = pygame.key.get_pressed()
    
    # Initialize player_rect for collision detection (needed even in camera mode for Jerome AI)
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    
    # Track if player is moving for animation
    player_moving = False
    
    # Stamina regeneration
    if not is_sprinting and player_stamina < player_max_stamina:
        player_stamina = min(player_max_stamina, player_stamina + stamina_regen_rate)
    
    # Only process movement in walk mode
    if game_mode == "walk":
        # Store old position
        old_x = player_x
        old_y = player_y
        
        # Check for sprint (Shift key)
        is_sprinting = keys[pygame.K_LSHIFT] and player_stamina > 0
        current_speed = player_speed * 1.5 if is_sprinting else player_speed
        
        # Drain stamina when sprinting
        if is_sprinting:
            player_stamina = max(0, player_stamina - sprint_drain_rate)
        
        # Move player based on input (separate X and Y for smooth sliding)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= current_speed
            player_moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += current_speed
            player_moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_y -= current_speed
            player_moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_y += current_speed
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
        
        # SNACK SYSTEM - Pickup and Stock (ONE SNACK AT A TIME)
        if keys[pygame.K_e]:
            # PICKUP: Near supply station anywhere in the world
            if not carrying_snack:
                for supply in active_supplies:
                    supply_rect = pygame.Rect(supply['x'], supply['y'], 50, 50)
                    if supply['room'] == current_room and player_rect.colliderect(supply_rect.inflate(50, 50)):
                        carrying_snack = True
                        objective_text = f"Take snack to the Break Room table! ({snacks_stocked}/{snacks_needed})"
                        warning_text = "Picked up snack!"
                        warning_timer = current_time
                        # Remove this supply and spawn a new one
                        active_supplies.remove(supply)
                        spawn_new_supply()
                        break
            
            # STOCK: Place snack on break room table
            elif carrying_snack and current_room == 2:
                # Check if near the table
                table_rect = pygame.Rect(width // 2 - 150, height // 2 - 40, 300, 80)
                if player_rect.colliderect(table_rect.inflate(60, 60)):
                    # Successfully stocked!
                    carrying_snack = False
                    snacks_stocked += 1
                    
                    # Update objective
                    if snacks_stocked >= snacks_needed:
                        objective_text = f"Table fully stocked! ({snacks_stocked}/{snacks_needed}) Keep it that way!"
                    else:
                        objective_text = f"Stock more snacks! ({snacks_stocked}/{snacks_needed})"
                    
                    warning_text = f"Snack stocked! ({snacks_stocked}/{snacks_needed})"
                    warning_timer = current_time
                    
                    # Visual feedback
                    for _ in range(15):
                        particles.append(Particle(
                            table_rect.centerx + random.randint(-60, 60),
                            table_rect.centery + random.randint(-20, 20),
                            random.choice([RED, ORANGE, YELLOW, PURPLE, GREEN]),
                            lifetime=40,
                            vel_x=random.uniform(-1, 1),
                            vel_y=random.uniform(-2, -0.5),
                            size=4
                        ))
        
        # Snacks disappear over time (A NextGenner eats them) - DIFFICULTY RAMPS UP
        if current_time - snack_consumption_last > snack_consumption_interval and snacks_stocked > 0:
            snack_consumption_last = current_time
            snacks_stocked = max(0, snacks_stocked - 1)
            
            # Increase difficulty - consumption gets faster over time
            snack_consumption_interval = max(snack_consumption_min, snack_consumption_interval - difficulty_increase_rate)
            
            if snacks_stocked < snacks_needed:
                warning_text = f"A NextGenner ate a snack! Restock! ({snacks_stocked}/{snacks_needed})"
                warning_timer = current_time
    
    # Jerome AI - Movement (patrols or chases)
    if jerome_active:
        old_jerome_x = jerome_x
        old_jerome_y = jerome_y
        
        # Update Jerome's animation
        jerome_sprite.update_animation()
        
        # Determine speed based on state
        if jerome_state == "angry":
            current_speed = jerome_angry_speed
        else:
            current_speed = jerome_patrol_speed
        
        # Chase logic when angry - override patrol
        if jerome_state == "angry" and jerome_room == current_room:
            # Move towards player (simple chase AI)
            if jerome_x < player_x:
                jerome_x += current_speed
            elif jerome_x > player_x:
                jerome_x -= current_speed
            
            # Check X collision for Jerome
            jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
            for wall in rooms[jerome_room]['walls']:
                if jerome_rect.colliderect(wall):
                    jerome_x = old_jerome_x
                    break
            
            for furniture in rooms[jerome_room]['furniture']:
                if jerome_rect.colliderect(furniture['rect']):
                    jerome_x = old_jerome_x
                    break
            
            # Y-axis movement
            if jerome_y < player_y:
                jerome_y += current_speed
            elif jerome_y > player_y:
                jerome_y -= current_speed
            
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
        
        # Collision check with player (damage when touched)
        if jerome_room == current_room:
            jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
            
            # Update Jerome sprite position
            jerome_sprite.rect.topleft = (jerome_x, jerome_y)
            
            # Check if Jerome caught the player (only when angry with flog)
            if player_rect.colliderect(jerome_rect) and jerome_state == "angry":
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
                    # Ensure spawn position is valid
                    jerome_x = max(30, min(width - 50, spawn_x))
                    jerome_y = max(30, min(height - 50, spawn_y))
                    break
            
            # Move Jerome towards the transition that leads to player's room
            for transition_rect, destination_room, _, _ in rooms[jerome_room]['transitions']:
                if destination_room == current_room:
                    # Move towards this transition
                    transition_center_x = transition_rect.centerx
                    transition_center_y = transition_rect.centery
                    
                    if jerome_x < transition_center_x:
                        jerome_x += current_speed
                    elif jerome_x > transition_center_x:
                        jerome_x -= current_speed
                    
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
                        jerome_y += current_speed
                    elif jerome_y > transition_center_y:
                        jerome_y -= current_speed
                    
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
        
        # Draw the selected room view using external images
        camera_room = selected_camera
        room_surface = pygame.Surface((width - 100, height - 150))
        
        # Load and scale the camera image to fit the view
        camera_img = camera_images[selected_camera]
        scaled_img = pygame.transform.scale(camera_img, (width - 100, height - 150))
        room_surface.blit(scaled_img, (0, 0))
        
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
        camera_names = ["CAM 1: Entrance", "CAM 2: Hallway", "CAM 3: Breakroom"]
        ui_font = pygame.font.Font(None, 28)
        title_text = ui_font.render(camera_names[selected_camera], True, (150, 255, 150))
        screen.blit(title_text, (60, 30))
        
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
        
        # Draw decorations (non-collidable items like snacks)
        if 'decorations' in rooms[current_room]:
            for deco in rooms[current_room]['decorations']:
                pygame.draw.rect(screen, deco['color'], deco['rect'], border_radius=3)
                # Small label for snacks
                if deco.get('label'):
                    deco_font = pygame.font.Font(None, 14)
                    deco_text = deco_font.render(deco['label'], True, WHITE)
                    screen.blit(deco_text, (deco['rect'].centerx - deco_text.get_width() // 2, deco['rect'].y - 12))
        
        # Draw furniture sprites for current room
        for furn_sprite in furniture_sprites:
            if furn_sprite.room == current_room:
                # Skip shadow for table_with_snacks to reduce lag
                if furn_sprite.furniture_data.get('type') != 'table_with_snacks':
                    shadow_pos = (furn_sprite.rect.x + 4, furn_sprite.rect.bottom)
                    screen.blit(furn_sprite.shadow, shadow_pos)
                
                # Check if near player for highlighting
                if furn_sprite.furniture_data.get('type') == 'supply' and player_rect.colliderect(furn_sprite.rect.inflate(50, 50)):
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
        
        # Draw dynamic supply stations
        for supply in active_supplies:
            if supply['room'] == current_room:
                supply_rect = pygame.Rect(supply['x'], supply['y'], 50, 50)
                
                # Draw supply box
                pygame.draw.rect(screen, supply['color'], supply_rect)
                pygame.draw.rect(screen, (0, 0, 0), supply_rect, 2)
                
                # Draw glowing border when snacks are low
                if snacks_stocked < snacks_needed:
                    border_color = (255, 215, 0)  # Gold
                    pygame.draw.rect(screen, border_color, supply_rect, 4)
                    
                    # Strong glow
                    glow_surf, glow_pos = create_glow_effect(
                        supply_rect.centerx, supply_rect.centery,
                        30, border_color, 120
                    )
                    screen.blit(glow_surf, glow_pos)
                
                # Draw "SNACK" label
                label_font = pygame.font.Font(None, 18)
                label_text = label_font.render("SNACK", True, WHITE)
                label_rect = label_text.get_rect(center=supply_rect.center)
                bg_rect = label_rect.inflate(6, 4)
                pygame.draw.rect(screen, (0, 0, 0, 200), bg_rect, border_radius=3)
                screen.blit(label_text, label_rect)
                
                # Show pickup hint when player is nearby
                player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
                if not carrying_snack and player_rect.colliderect(supply_rect.inflate(50, 50)):
                    hint_font = pygame.font.Font(None, 22)
                    hint_text = hint_font.render("Press E to pick up", True, YELLOW)
                    hint_bg = pygame.Surface((hint_text.get_width() + 10, hint_text.get_height() + 6), pygame.SRCALPHA)
                    pygame.draw.rect(hint_bg, (0, 0, 0, 180), hint_bg.get_rect(), border_radius=5)
                    hint_bg.blit(hint_text, (5, 3))
                    screen.blit(hint_bg, (supply_rect.centerx - hint_bg.get_width() // 2, supply_rect.y - 35))
        
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
            
            # Draw clipboard/papers only when Jerome is angry
            if jerome_state == "angry":
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
            name_text = font_small.render("Jerome", True, (200, 150, 150))
            name_bg = pygame.Surface((name_text.get_width() + 8, name_text.get_height() + 4), pygame.SRCALPHA)
            pygame.draw.rect(name_bg, (80, 20, 20, 200), name_bg.get_rect(), border_radius=4)
            name_bg.blit(name_text, (4, 2))
            screen.blit(name_bg, (jerome_x - 5, jerome_y - 25))
        
        # Draw MMO-style UI
        draw_mmo_ui(screen, current_time)
        
        # Walk mode instructions
        walk_inst_font = pygame.font.Font(None, 18)
        walk_text = walk_inst_font.render("ESC/C - Cameras | SHIFT - Sprint | E - Pickup/Deliver", True, (180, 180, 180))
        screen.blit(walk_text, (10, height - 25))
    
    # Draw objective text (big and clear)
    if game_mode != "tutorial":
        objective_font = pygame.font.Font(None, 28)
        objective_surface = objective_font.render(objective_text, True, (255, 255, 200))
        objective_bg = pygame.Surface((objective_surface.get_width() + 30, 50), pygame.SRCALPHA)
        pygame.draw.rect(objective_bg, (20, 20, 30, 220), objective_bg.get_rect(), border_radius=8)
        pygame.draw.rect(objective_bg, (150, 150, 180), objective_bg.get_rect(), 2, border_radius=8)
        objective_bg.blit(objective_surface, (15, 13))
        
        objective_x = width // 2 - objective_bg.get_width() // 2
        objective_y = height - 80
        screen.blit(objective_bg, (objective_x, objective_y))
        
        # Draw ChatGPT Jokes on the right side
        joke_font = pygame.font.Font(None, 20)
        joke_title_font = pygame.font.Font(None, 24)
        
        # Title
        joke_title = joke_title_font.render("ChatGPT Joke:", True, (255, 215, 100))
        
        # Wrap joke text to fit in box
        joke_box_width = 280
        wrapped_lines = []
        words = joke_text.split(' ')
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if joke_font.size(test_line)[0] < joke_box_width - 20:
                current_line = test_line
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word + " "
        if current_line:
            wrapped_lines.append(current_line)
        
        # Calculate box height based on lines
        line_height = 22
        joke_box_height = 60 + len(wrapped_lines) * line_height
        
        # Draw joke box on right side
        joke_box_x = width - joke_box_width - 20
        joke_box_y = 80
        
        joke_bg = pygame.Surface((joke_box_width, joke_box_height), pygame.SRCALPHA)
        pygame.draw.rect(joke_bg, (40, 20, 60, 230), joke_bg.get_rect(), border_radius=8)
        pygame.draw.rect(joke_bg, (180, 150, 200), joke_bg.get_rect(), 2, border_radius=8)
        
        # Blit title
        joke_bg.blit(joke_title, (joke_box_width // 2 - joke_title.get_width() // 2, 10))
        
        # Blit wrapped joke lines
        for i, line in enumerate(wrapped_lines):
            line_surface = joke_font.render(line.strip(), True, (220, 220, 220))
            joke_bg.blit(line_surface, (10, 40 + i * line_height))
        
        screen.blit(joke_bg, (joke_box_x, joke_box_y))
    
    # Tutorial screen
    if game_mode == "tutorial":
        # Dark overlay
        tutorial_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(tutorial_overlay, (0, 0, 0, 200), tutorial_overlay.get_rect())
        screen.blit(tutorial_overlay, (0, 0))
        
        # Tutorial box
        tutorial_box_width = 600
        tutorial_box_height = 350
        tutorial_box_x = width // 2 - tutorial_box_width // 2
        tutorial_box_y = height // 2 - tutorial_box_height // 2
        
        pygame.draw.rect(screen, (30, 30, 40), (tutorial_box_x, tutorial_box_y, tutorial_box_width, tutorial_box_height), border_radius=10)
        pygame.draw.rect(screen, (100, 120, 140), (tutorial_box_x, tutorial_box_y, tutorial_box_width, tutorial_box_height), 3, border_radius=10)
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Office Nightmare", True, (255, 200, 100))
        screen.blit(title_text, (tutorial_box_x + tutorial_box_width // 2 - title_text.get_width() // 2, tutorial_box_y + 20))
        
        # Instructions
        inst_font = pygame.font.Font(None, 24)
        instructions = [
            "",
            "HOW TO PLAY:",
            "",
            "• Keep the Break Room table stocked with 5 snacks",
            "• Pick up snacks from supply stations (Press E)",
            "• Place them on the Break Room table (Press E)",
            "• Jerome eats snacks over time - keep restocking!",
            "• If snacks run low, Jerome loses patience",
            "• When patience hits 0%, Jerome gets ANGRY with his clipboard!",
            "",
            "CONTROLS:",
            "• WASD/Arrows - Move",
            "• SHIFT - Sprint (uses stamina)",
            "• C/ESC - Toggle Cameras",
            "• E - Pickup/Stock snacks",
            "",
            "Press SPACE to start your shift!"
        ]
        
        y_offset = tutorial_box_y + 80
        for line in instructions:
            if line:
                text = inst_font.render(line, True, (220, 220, 220))
                screen.blit(text, (tutorial_box_x + 30, y_offset))
            y_offset += 26
    
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
        screen.blit(warning_bg, (width // 2 - warning_surface.get_width() // 2 - 10, height - 130))
        screen.blit(warning_surface, (width // 2 - warning_surface.get_width() // 2, height - 125))
    
    # Show carrying indicator
    if carrying_snack:
        carry_font = pygame.font.Font(None, 24)
        carry_text = carry_font.render("Carrying: Snack", True, (255, 200, 100))
        carry_bg = pygame.Surface((carry_text.get_width() + 20, 35), pygame.SRCALPHA)
        pygame.draw.rect(carry_bg, (50, 50, 60, 220), carry_bg.get_rect(), border_radius=5)
        pygame.draw.rect(carry_bg, (255, 200, 100), carry_bg.get_rect(), 2, border_radius=5)
        carry_bg.blit(carry_text, (10, 7))
        screen.blit(carry_bg, (width // 2 - carry_bg.get_width() // 2, 20))
    
    # Update the display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
