import pygame
import sys
import random
import math
import threading
import os
from openai import OpenAI
import heapq
from collections import deque

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

# Load office state images
working_image = pygame.image.load("working.jpg")
slacking_image = pygame.image.load("slacking.jpg")

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

# Cache fonts for performance (create once, reuse)
FONT_CACHE = {
    'small': pygame.font.Font(None, 14),
    'hint': pygame.font.Font(None, 20),
    'name': pygame.font.Font(None, 20),
    'fridge': pygame.font.Font(None, 22),
    'stats': pygame.font.Font(None, 24),
    'ui': pygame.font.Font(None, 26),
    'warning': pygame.font.Font(None, 28),
    'objective': pygame.font.Font(None, 28),
    'time': pygame.font.Font(None, 30),
    'congrats': pygame.font.Font(None, 36),
    'title': pygame.font.Font(None, 48),
    'big': pygame.font.Font(None, 72)
}

# Player settings
player_size = 40
player_x = 150  # Start away from furniture
player_y = 50   # Top area of office
player_speed = 4  # Smoother speed
player_color = (70, 130, 180)  # Steel blue for office worker

# Game mode
game_mode = "office"  # "tutorial", "office", "camera", "walk"
selected_camera = 0  # Which room camera is viewing (0=Entrance, 1=Hallway, 2=Breakroom)

# Game state
game_state = "playing"  # "playing", "game_over"

# WIFI resource system
wifi = 100.0  # WIFI percentage (0-100)
wifi_drain_rate = 0.015  # WIFI drains per frame when working or viewing cameras (slower drain)
at_desk = False  # True = working.jpg (at desk), False = slacking.jpg (away from desk)

# Fridge system (Jerome mechanic - like FNAF music box)
fridge_level = 100.0  # Fridge fullness (0-100)
fridge_drain_rate = 0.02  # Drains over time when in office mode
fridge_restock_amount = 50.0  # How much restocking adds

# Egg inventory (Jonathan defense)
has_egg = False  # Player starts without an egg

# Time system (like FNAF hours)
game_time = 0.0  # Time in seconds
game_time_speed = 1.0  # Time progresses at 1 second per real second when in office
target_time = 300.0  # Win after 5 minutes (300 seconds) - can adjust this

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
            # Simple bobbing effect - don't recreate sprite every frame for performance
            # Only update every few frames
            if self.animation_frame % 5 == 0:
                offset = int(math.sin(self.animation_frame / 10 * math.pi) * 2)
                # Skip sprite recreation for better performance

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
        # Only recreate sprite every 10 frames for performance
        if self.animation_frame % 10 == 0:
            self.create_sprite()
        
        # Create menacing particles (reduced frequency)
        if self.animation_frame % 30 == 0:
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

# Jerome (enemy) settings
jerome_active = True  # Jerome is always present, walking around
jerome_x = width // 2
jerome_y = height // 2
jerome_size = 45
jerome_patrol_speed = 1.5  # Slow patrol speed
jerome_angry_speed = 3.5  # Fast chase speed
jerome_color = (60, 40, 70)  # Dark purple/gray
jerome_room = 1  # Starts in hallway
jerome_state = "patrol"  # "patrol", "angry"
jerome_target_x = 0
jerome_target_y = 0
jerome_patrol_timer = 0
jerome_path = []  # Current pathfinding path
jerome_path_index = 0  # Current position in path
jerome_idle_timer = 0  # Time before choosing new destination

# Patrol waypoints for each room (fallback if pathfinding fails)
patrol_waypoints = {
    0: [(150, 150), (400, 200), (500, 400), (300, 350)],  # Your personal office
    1: [(200, 200), (500, 300), (800, 200), (500, 400)],  # Hallway
    2: [(300, 150), (600, 250), (400, 450)]  # Breakroom
}
jerome_waypoint_index = 0

# Jonathan (second enemy) settings
jonathan_active = True
jonathan_x = width // 3
jonathan_y = height // 3
jonathan_size = 45
jonathan_patrol_speed = 1.2  # Slightly slower than Jerome
jonathan_chase_speed = 2.5  # Speed when chasing player with egg
jonathan_color = (50, 70, 90)  # Blueish gray
jonathan_room = 2  # Starts in breakroom
jonathan_target_x = 0
jonathan_target_y = 0
jonathan_patrol_timer = 0
jonathan_waypoint_index = 0
jonathan_sprite = None
jonathan_path = []  # Current pathfinding path
jonathan_path_index = 0  # Current position in path
jonathan_idle_timer = 0  # Time before choosing new destination
jonathan_state = "patrol"  # "patrol" or "chasing_egg"
egg_held_time = 0  # Track how long player has held the egg
egg_chase_threshold = 30.0  # Seconds before Jonathan starts chasing

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
objective_text = "Survive 5 minutes! Keep FRIDGE stocked & get EGG for defense!"
show_tutorial = True
last_patience_warning = 0
warning_timer = 0

# ChatGPT Joke System - Jonathan displays jokes
jonathan_joke_text = "Loading joke..."
jonathan_joke_timer = 0
jonathan_joke_fetch_timer = 0
jonathan_joke_fetch_interval = 10000  # Fetch new joke every 10 seconds
jonathan_joke_display_duration = 10000  # Show joke for 10 seconds
is_fetching_joke = False
recent_jokes = []  # Track recent jokes to avoid repeats
max_recent_jokes = 5  # Remember last 5 jokes

# Initialize OpenAI client (set your API key as environment variable OPENAI_API_KEY)
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    chatgpt_available = True
except:
    client = None
    chatgpt_available = False
    jonathan_joke_text = "Set OPENAI_API_KEY environment variable to enable jokes!"

def fetch_joke_from_chatgpt():
    """Fetch a joke from ChatGPT in a separate thread for Jonathan"""
    global jonathan_joke_text, is_fetching_joke, recent_jokes
    
    if not chatgpt_available:
        return
    
    is_fetching_joke = True
    
    try:
        # Vary the prompts to get more diverse jokes
        joke_prompts = [
            "Tell me a hilarious one-liner joke.",
            "Give me a short, unexpected punchline joke.",
            "Tell me a clever wordplay joke in 1-2 sentences.",
            "Share a quick, funny observational joke.",
            "Tell me an absurd, surreal joke (keep it brief).",
            "Give me a witty joke about everyday life.",
            "Tell me a dad joke that's actually funny.",
            "Share a short joke with a twist ending.",
            "Tell me a silly knock-knock joke variant.",
            "Give me a humorous tech or science joke."
        ]
        
        # Build a prompt that avoids recent jokes
        prompt = random.choice(joke_prompts)
        if recent_jokes:
            prompt += f"\n\nDon't repeat these recent jokes: {'; '.join(recent_jokes[-3:])}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative comedian. Tell very short, unique jokes (1-2 sentences max). Be original and avoid clichés."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.8,  # Balanced creativity and coherence
            presence_penalty=0.3,  # Mild encouragement for novel content
            frequency_penalty=0.3  # Mild discouragement of repetition
        )
        
        new_joke = response.choices[0].message.content.strip()
        
        # Track recent jokes to avoid repeats
        if new_joke not in recent_jokes:
            jonathan_joke_text = new_joke
            recent_jokes.append(new_joke)
            if len(recent_jokes) > max_recent_jokes:
                recent_jokes.pop(0)
        else:
            # If we got a repeat, just use it but don't add to history
            jonathan_joke_text = new_joke
        
    except Exception as e:
        jonathan_joke_text = f"Joke error: {str(e)[:50]}..."
    
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
    0: {  # Your Personal Office - Small workspace (only room where you can access desk/cameras)
        'walls': [
            pygame.Rect(0, 0, width, 20),                    # Top wall
            pygame.Rect(0, 0, 20, height),                   # Left wall
            pygame.Rect(0, height - 20, width, 20),          # Bottom wall
            pygame.Rect(width - 20, 0, 20, height // 2 - 60),           # Right wall top part
            pygame.Rect(width - 20, height // 2 + 60, 20, height // 2 - 60), # Right wall bottom part
        ],
        'floor_color': CARPET_BLUE,
        'furniture': [
            # Your main desk (center-left)
            {'rect': pygame.Rect(80, 250, 180, 80), 'color': DESK_BROWN, 'label': "Your Desk"},
            
            # Filing cabinet (left side)
            {'rect': pygame.Rect(50, 80, 60, 100), 'color': OFFICE_GRAY, 'label': "Files"},
            
            # Bookshelf (top)
            {'rect': pygame.Rect(300, 40, 250, 50), 'color': RUSTY_BROWN, 'label': None},
            
            # Small side table (bottom)
            {'rect': pygame.Rect(350, 450, 100, 60), 'color': DESK_BROWN, 'label': None},
            
            # Plant or decoration
            {'rect': pygame.Rect(600, 80, 40, 40), 'color': (80, 120, 80), 'label': "Plant"},
            
            # Trash can
            {'rect': pygame.Rect(280, 320, 30, 40), 'color': OFFICE_GRAY, 'label': None},
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
            
            # Fridge next to the table (right side)
            {'rect': pygame.Rect(width // 2 + 170, height // 2 - 50, 60, 100), 'color': WALL_DARK, 'label': "Broken"},
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


# ==================== PATHFINDING SYSTEM ====================

# Grid-based pathfinding settings
GRID_SIZE = 20  # Size of each grid cell (smaller = more precise, slower)
grid_width = width // GRID_SIZE
grid_height = height // GRID_SIZE

class NavigationGrid:
    """Grid-based navigation system for pathfinding"""
    def __init__(self):
        self.grids = {}  # One grid per room
        self.build_navigation_grids()
    
    def build_navigation_grids(self):
        """Build walkable grids for all rooms"""
        for room_id, room_data in rooms.items():
            grid = [[True for _ in range(grid_width)] for _ in range(grid_height)]
            
            # Mark walls as unwalkable
            for wall in room_data['walls']:
                for y in range(max(0, wall.top // GRID_SIZE), min(grid_height, (wall.bottom + GRID_SIZE - 1) // GRID_SIZE)):
                    for x in range(max(0, wall.left // GRID_SIZE), min(grid_width, (wall.right + GRID_SIZE - 1) // GRID_SIZE)):
                        grid[y][x] = False
            
            # Mark furniture as unwalkable
            for furn in room_data['furniture']:
                rect = furn['rect']
                for y in range(max(0, rect.top // GRID_SIZE), min(grid_height, (rect.bottom + GRID_SIZE - 1) // GRID_SIZE)):
                    for x in range(max(0, rect.left // GRID_SIZE), min(grid_width, (rect.right + GRID_SIZE - 1) // GRID_SIZE)):
                        grid[y][x] = False
            
            self.grids[room_id] = grid
    
    def is_walkable(self, room_id, x, y):
        """Check if a grid position is walkable"""
        grid_x = int(x // GRID_SIZE)
        grid_y = int(y // GRID_SIZE)
        
        if grid_x < 0 or grid_x >= grid_width or grid_y < 0 or grid_y >= grid_height:
            return False
        
        if room_id not in self.grids:
            return False
        
        return self.grids[room_id][grid_y][grid_x]
    
    def get_neighbors(self, room_id, grid_x, grid_y):
        """Get walkable neighboring cells (8-directional)"""
        neighbors = []
        
        # 8 directions: N, S, E, W, NE, NW, SE, SW
        directions = [
            (0, -1, 1.0),   # North
            (0, 1, 1.0),    # South
            (1, 0, 1.0),    # East
            (-1, 0, 1.0),   # West
            (1, -1, 1.4),   # Northeast (diagonal)
            (-1, -1, 1.4),  # Northwest (diagonal)
            (1, 1, 1.4),    # Southeast (diagonal)
            (-1, 1, 1.4)    # Southwest (diagonal)
        ]
        
        for dx, dy, cost in directions:
            new_x, new_y = grid_x + dx, grid_y + dy
            
            if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
                if self.grids[room_id][new_y][new_x]:
                    # For diagonal moves, check if the path is clear
                    if dx != 0 and dy != 0:
                        # Check both adjacent cells for diagonal movement
                        if self.grids[room_id][grid_y][new_x] and self.grids[room_id][new_y][grid_x]:
                            neighbors.append((new_x, new_y, cost))
                    else:
                        neighbors.append((new_x, new_y, cost))
        
        return neighbors

def heuristic(ax, ay, bx, by):
    """Manhattan distance heuristic for A*"""
    return abs(ax - bx) + abs(ay - by)

def astar_pathfind(nav_grid, room_id, start_x, start_y, goal_x, goal_y):
    """
    A* pathfinding algorithm
    Returns list of (x, y) world coordinates forming a path, or None if no path found
    """
    # Convert world coordinates to grid coordinates
    start_gx = int(start_x // GRID_SIZE)
    start_gy = int(start_y // GRID_SIZE)
    goal_gx = int(goal_x // GRID_SIZE)
    goal_gy = int(goal_y // GRID_SIZE)
    
    # Bounds checking
    if not (0 <= start_gx < grid_width and 0 <= start_gy < grid_height):
        return None
    if not (0 <= goal_gx < grid_width and 0 <= goal_gy < grid_height):
        return None
    
    # Check if start and goal are walkable
    if not nav_grid.is_walkable(room_id, start_x, start_y):
        return None
    if not nav_grid.is_walkable(room_id, goal_x, goal_y):
        return None
    
    # A* algorithm
    frontier = []  # Priority queue: (priority, counter, (x, y))
    heapq.heappush(frontier, (0, 0, (start_gx, start_gy)))
    
    came_from = {}
    cost_so_far = {}
    came_from[(start_gx, start_gy)] = None
    cost_so_far[(start_gx, start_gy)] = 0
    
    counter = 1  # To break ties in priority queue
    
    while frontier:
        _, _, current = heapq.heappop(frontier)
        current_x, current_y = current
        
        # Early exit when goal reached
        if current_x == goal_gx and current_y == goal_gy:
            break
        
        # Explore neighbors
        for next_x, next_y, move_cost in nav_grid.get_neighbors(room_id, current_x, current_y):
            new_cost = cost_so_far[current] + move_cost
            
            if (next_x, next_y) not in cost_so_far or new_cost < cost_so_far[(next_x, next_y)]:
                cost_so_far[(next_x, next_y)] = new_cost
                priority = new_cost + heuristic(next_x, next_y, goal_gx, goal_gy)
                heapq.heappush(frontier, (priority, counter, (next_x, next_y)))
                counter += 1
                came_from[(next_x, next_y)] = current
    
    # Reconstruct path
    if (goal_gx, goal_gy) not in came_from:
        return None  # No path found
    
    path = []
    current = (goal_gx, goal_gy)
    
    while current is not None:
        # Convert grid coordinates back to world coordinates (center of cell)
        world_x = current[0] * GRID_SIZE + GRID_SIZE // 2
        world_y = current[1] * GRID_SIZE + GRID_SIZE // 2
        path.append((world_x, world_y))
        current = came_from[current]
    
    path.reverse()
    return path

# Create global navigation grid
nav_grid = NavigationGrid()

# ==================== END PATHFINDING SYSTEM ====================


# Initialize sprites
def init_sprites():
    global player_sprite, jerome_sprite, jonathan_sprite, furniture_sprites, all_sprites
    
    # Clear existing sprites
    all_sprites.empty()
    furniture_sprites.empty()
    
    # Create player sprite
    player_sprite = Player(player_x, player_y)
    all_sprites.add(player_sprite)
    
    # Create Jerome sprite
    jerome_sprite = Jerome(jerome_x, jerome_y)
    all_sprites.add(jerome_sprite)
    
    # Create Jonathan sprite
    jonathan_sprite = Jerome(jonathan_x, jonathan_y)  # Reuse Jerome class for now
    all_sprites.add(jonathan_sprite)
    
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
            
            if game_mode == "office":
                if event.key == pygame.K_s:
                    # Toggle between working (at desk) and slacking (away from desk)
                    at_desk = not at_desk
                elif event.key == pygame.K_SPACE or event.key == pygame.K_c:
                    # Open cameras
                    game_mode = "camera"
                elif event.key == pygame.K_w:
                    # Switch to walk mode
                    game_mode = "walk"
                    current_room = 0  # Start in office room
                    player_x = 150  # Safe spawn position
                    player_y = 50
                    walls = rooms[current_room]['walls']
                    transitions = rooms[current_room]['transitions']
            
            elif game_mode == "camera":
                if event.key == pygame.K_1:
                    selected_camera = 0
                elif event.key == pygame.K_2:
                    selected_camera = 1
                elif event.key == pygame.K_3:
                    selected_camera = 2
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    # Close cameras, return to office
                    game_mode = "office"
            
            elif game_mode == "walk":
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_c:
                    # Can only return to office mode if in room 0 (office space)
                    if current_room == 0:
                        game_mode = "office"
                    else:
                        warning_text = "Return to your office to access desk!"
                        warning_timer = current_time
    
    # Get current time
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) / 1000  # Convert to seconds
    
    # Time Progression System - only progresses when in office mode
    if game_mode == "office" and game_state == "playing":
        game_time += game_time_speed * (1/60)  # Assuming 60 FPS
        
        # Fridge Depletion - drains over time when in office
        if fridge_level > 0:
            fridge_level -= fridge_drain_rate
            fridge_level = max(0, fridge_level)
    
    # Track egg held time (always counting in all modes)
    if has_egg and game_state == "playing":
        egg_held_time += (1/60)  # Increment in real-time
        
        # Check if Jonathan should start chasing
        if egg_held_time >= egg_chase_threshold:
            # Trigger warning when Jonathan first starts chasing
            if jonathan_state != "chasing_egg":
                warning_text = "Jonathan wants his egg back!"
                warning_timer = current_time
            jonathan_state = "chasing_egg"
        else:
            jonathan_state = "patrol"
    else:
        # Reset if no egg
        if not has_egg:
            egg_held_time = 0
            if jonathan_state == "chasing_egg":
                jonathan_state = "patrol"
    
    # WIFI Drain System - drains when viewing cameras OR when at desk working
    if wifi > 0:
        if game_mode == "camera":
            # Drain when viewing cameras
            wifi -= wifi_drain_rate
            wifi = max(0, wifi)  # Don't go below 0
        elif game_mode == "office" and at_desk:
            # Drain when working at desk
            wifi -= wifi_drain_rate
            wifi = max(0, wifi)  # Don't go below 0
    
    # Check for WIFI depletion game over
    if wifi <= 0 and game_state == "playing":
        game_state = "game_over"
    
    # Check for fridge empty - Jerome spawns and kills player
    if fridge_level <= 0 and game_state == "playing":
        game_state = "game_over"
        # Could add a specific "Jerome got you" message later
    
    # Check for win condition
    if game_time >= target_time and game_state == "playing":
        game_state = "win"
    
    # Jonathan Joke Fetch Timer (every 10 seconds)
    if chatgpt_available and current_time - jonathan_joke_fetch_timer > jonathan_joke_fetch_interval:
        jonathan_joke_fetch_timer = current_time
        jonathan_joke_timer = current_time  # Reset display timer
        start_joke_fetch()
    

        
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
        
        # NEW GAME MECHANICS - Fridge Restocking and Egg Pickup
        if keys[pygame.K_e]:
            # Check if in breakroom (room 2)
            if current_room == 2:
                table_rect = pygame.Rect(width // 2 - 150, height // 2 - 40, 300, 80)
                fridge_rect = pygame.Rect(width // 2 + 170, height // 2 - 50, 60, 100)  # The fridge next to the table
                
                # RESTOCK FRIDGE: At the broken fridge (top left of break room)
                if player_rect.colliderect(fridge_rect.inflate(60, 60)) and fridge_level < 100:
                    fridge_level = min(100, fridge_level + fridge_restock_amount)
                    warning_text = f"Fridge restocked! ({int(fridge_level)}%)"
                    warning_timer = current_time
                    # Visual feedback
                    for _ in range(10):
                        particles.append(Particle(
                            fridge_rect.centerx + random.randint(-30, 30),
                            fridge_rect.centery + random.randint(-40, 40),
                            (100, 200, 255),
                            lifetime=30,
                            vel_x=random.uniform(-1, 1),
                            vel_y=random.uniform(-2, -0.5),
                            size=3
                        ))
                
                # PICK UP EGG: At the break room table (if don't have one)
                if player_rect.colliderect(table_rect.inflate(60, 60)) and not has_egg:
                    has_egg = True
                    egg_held_time = 0  # Reset timer when picking up egg
                    warning_text = "Egg acquired! (Jonathan defense)"
                    warning_timer = current_time
                    # Visual feedback
                    for _ in range(10):
                        particles.append(Particle(
                            table_rect.centerx + random.randint(-60, 60),
                            table_rect.centery + random.randint(-20, 20),
                            (255, 255, 100),
                            lifetime=30,
                            vel_x=random.uniform(-1, 1),
                            vel_y=random.uniform(-2, -0.5),
                            size=3
                        ))
        

    
    # ============ JEROME AI - Pathfinding-based Movement ============
    if jerome_active:
        # Update Jerome's animation
        jerome_sprite.update_animation()
        
        # Determine speed based on state
        if jerome_state == "angry":
            current_speed = jerome_angry_speed
            target_x, target_y = player_x, player_y  # Chase player
        else:
            current_speed = jerome_patrol_speed
            # Choose random waypoint in current room for patrol
            if not jerome_path or jerome_idle_timer <= 0:
                waypoints = patrol_waypoints.get(jerome_room, [(width//2, height//2)])
                target_waypoint = random.choice(waypoints)
                target_x, target_y = target_waypoint
                jerome_idle_timer = random.randint(120, 300)  # Wait before next destination
            else:
                jerome_idle_timer -= 1
                target_x = jerome_target_x if jerome_target_x else jerome_x
                target_y = jerome_target_y if jerome_target_y else jerome_y
        
        # Generate new path if needed
        if not jerome_path or jerome_path_index >= len(jerome_path):
            # Try to pathfind to target
            new_path = astar_pathfind(nav_grid, jerome_room, jerome_x, jerome_y, target_x, target_y)
            if new_path and len(new_path) > 1:
                jerome_path = new_path
                jerome_path_index = 1  # Start from second point (first is current position)
                jerome_target_x = target_x
                jerome_target_y = target_y
            else:
                jerome_path = []
                jerome_path_index = 0
        
        # Follow the path
        if jerome_path and jerome_path_index < len(jerome_path):
            target_point = jerome_path[jerome_path_index]
            dx = target_point[0] - jerome_x
            dy = target_point[1] - jerome_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < current_speed * 2:
                # Reached this waypoint, move to next
                jerome_path_index += 1
            else:
                # Move towards waypoint
                jerome_x += (dx / distance) * current_speed
                jerome_y += (dy / distance) * current_speed
        
        # Update Jerome sprite position
        jerome_sprite.rect.topleft = (jerome_x, jerome_y)
        
        # Collision check with player (damage when touched)
        if jerome_room == current_room:
            jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
            
            # Check if Jerome caught the player (only when angry)
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
        
        # Check for room transitions when Jerome reaches a doorway
        jerome_rect = pygame.Rect(jerome_x, jerome_y, jerome_size, jerome_size)
        for transition_rect, destination_room, spawn_x, spawn_y in rooms[jerome_room]['transitions']:
            if jerome_rect.colliderect(transition_rect):
                # Jerome transitions through the door
                jerome_room = destination_room
                jerome_x = spawn_x
                jerome_y = spawn_y
                jerome_path = []  # Clear path when changing rooms
                jerome_path_index = 0
                break
    
    # Update particles (limit total count to 100 for performance)
    particles[:] = [p for p in particles if p.update()]
    if len(particles) > 100:
        particles = particles[-100:]
    
    # ============ JONATHAN AI - Pathfinding-based Patrol ============
    if jonathan_active:
        # Update Jonathan's animation
        jonathan_sprite.update_animation()
        
        # Determine behavior based on state
        if jonathan_state == "chasing_egg" and has_egg:
            # Chase the player to steal the egg!
            current_speed = jonathan_chase_speed
            target_x, target_y = player_x, player_y
            
            # Clear path more frequently when chasing to stay updated
            if jonathan_room == current_room:
                # Same room - recalculate path frequently to follow player
                if not jonathan_path or jonathan_path_index >= len(jonathan_path) or random.randint(0, 15) == 0:
                    new_path = astar_pathfind(nav_grid, jonathan_room, jonathan_x, jonathan_y, target_x, target_y)
                    if new_path and len(new_path) > 1:
                        jonathan_path = new_path
                        jonathan_path_index = 1
                        jonathan_target_x = target_x
                        jonathan_target_y = target_y
            else:
                # Different room - navigate to the doorway that leads to player's room
                if not jonathan_path or jonathan_path_index >= len(jonathan_path):
                    # Find the correct doorway that connects to player's room
                    doorway_found = False
                    for transition_rect, dest_room, spawn_x, spawn_y in rooms[jonathan_room]['transitions']:
                        if dest_room == current_room:
                            # This doorway leads directly to player's room
                            target_x, target_y = transition_rect.centerx, transition_rect.centery
                            new_path = astar_pathfind(nav_grid, jonathan_room, jonathan_x, jonathan_y, target_x, target_y)
                            if new_path and len(new_path) > 1:
                                jonathan_path = new_path
                                jonathan_path_index = 1
                                doorway_found = True
                            break
                    
                    # If no direct doorway, just pick the first available (multi-room pathfinding)
                    if not doorway_found and rooms[jonathan_room]['transitions']:
                        transition_rect, dest_room, spawn_x, spawn_y = rooms[jonathan_room]['transitions'][0]
                        target_x, target_y = transition_rect.centerx, transition_rect.centery
                        new_path = astar_pathfind(nav_grid, jonathan_room, jonathan_x, jonathan_y, target_x, target_y)
                        if new_path and len(new_path) > 1:
                            jonathan_path = new_path
                            jonathan_path_index = 1
        else:
            # Normal patrol behavior
            current_speed = jonathan_patrol_speed
            
            # Choose random destinations to patrol around
            if not jonathan_path or jonathan_idle_timer <= 0:
                # Pick a random walkable location in the current room or nearby room
                if random.randint(0, 100) < 20 and rooms[jonathan_room]['transitions']:  # 20% chance to go to different room
                    # Go to a random doorway to transition to another room
                    transition_rect, dest_room, spawn_x, spawn_y = random.choice(rooms[jonathan_room]['transitions'])
                    target_x, target_y = transition_rect.centerx, transition_rect.centery
                else:
                    # Stay in current room - pick random waypoint
                    waypoints = patrol_waypoints.get(jonathan_room, [(width//2, height//2)])
                    target_waypoint = random.choice(waypoints)
                    target_x, target_y = target_waypoint
                
                jonathan_idle_timer = random.randint(180, 400)  # Wait before next destination
            else:
                jonathan_idle_timer -= 1
                target_x = jonathan_target_x if jonathan_target_x else jonathan_x
                target_y = jonathan_target_y if jonathan_target_y else jonathan_y
            
            # Generate new path if needed
            if not jonathan_path or jonathan_path_index >= len(jonathan_path):
                # Try to pathfind to target
                new_path = astar_pathfind(nav_grid, jonathan_room, jonathan_x, jonathan_y, target_x, target_y)
                if new_path and len(new_path) > 1:
                    jonathan_path = new_path
                    jonathan_path_index = 1  # Start from second point
                    jonathan_target_x = target_x
                    jonathan_target_y = target_y
                else:
                    jonathan_path = []
                    jonathan_path_index = 0
        
        # Follow the path
        if jonathan_path and jonathan_path_index < len(jonathan_path):
            target_point = jonathan_path[jonathan_path_index]
            dx = target_point[0] - jonathan_x
            dy = target_point[1] - jonathan_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < current_speed * 2:
                # Reached this waypoint, move to next
                jonathan_path_index += 1
            else:
                # Move towards waypoint
                jonathan_x += (dx / distance) * current_speed
                jonathan_y += (dy / distance) * current_speed
        
        # Update Jonathan sprite position
        jonathan_sprite.rect.topleft = (jonathan_x, jonathan_y)
        
        # Check if Jonathan catches player with egg
        if jonathan_state == "chasing_egg" and has_egg and jonathan_room == current_room:
            jonathan_rect = pygame.Rect(jonathan_x, jonathan_y, jonathan_size, jonathan_size)
            if player_rect.colliderect(jonathan_rect):
                # Jonathan steals the egg!
                has_egg = False
                egg_held_time = 0
                jonathan_state = "patrol"
                warning_text = "Jonathan stole your egg!"
                warning_timer = current_time
                
                # Visual feedback - egg particles
                for _ in range(20):
                    particles.append(Particle(
                        player_x + player_size // 2,
                        player_y + player_size // 2,
                        (255, 255, 100),
                        lifetime=40,
                        vel_x=random.uniform(-3, 3),
                        vel_y=random.uniform(-3, 3),
                        size=random.randint(2, 5)
                    ))
        
        # Check for room transitions when Jonathan reaches a doorway
        jonathan_rect = pygame.Rect(jonathan_x, jonathan_y, jonathan_size, jonathan_size)
        for transition_rect, destination_room, spawn_x, spawn_y in rooms[jonathan_room]['transitions']:
            if jonathan_rect.colliderect(transition_rect):
                # Jonathan transitions through the door
                jonathan_room = destination_room
                jonathan_x = spawn_x
                jonathan_y = spawn_y
                jonathan_path = []  # Clear path when changing rooms
                jonathan_path_index = 0
                jonathan_idle_timer = 0  # Pick new destination immediately
                break
    
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
    if game_mode == "office":
        # Office mode - show working or slacking image (no camera effects)
        screen.fill(BLACK)
        
        # Display the appropriate office image
        office_img = working_image if at_desk else slacking_image
        scaled_office_img = pygame.transform.scale(office_img, (width, height))
        screen.blit(scaled_office_img, (0, 0))
        
        # Office UI
        ui_font = pygame.font.Font(None, 24)
        
        # Instructions
        instructions = [
            "S - Toggle Work/Slack",
            "SPACE/C - Open Cameras",
            "W - Walk Mode"
        ]
        for i, inst in enumerate(instructions):
            text = ui_font.render(inst, True, (200, 200, 200))
            # Add semi-transparent background for readability
            text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 6), pygame.SRCALPHA)
            pygame.draw.rect(text_bg, (0, 0, 0, 180), text_bg.get_rect(), border_radius=5)
            text_bg.blit(text, (5, 3))
            screen.blit(text_bg, (10, 10 + i * 30))
        
        # WIFI Display
        wifi_font = pygame.font.Font(None, 32)
        wifi_color = GREEN if wifi > 50 else YELLOW if wifi > 20 else RED
        wifi_text = wifi_font.render(f"WIFI: {int(wifi)}%", True, wifi_color)
        wifi_bg = pygame.Surface((wifi_text.get_width() + 10, wifi_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(wifi_bg, (0, 0, 0, 180), wifi_bg.get_rect(), border_radius=5)
        wifi_bg.blit(wifi_text, (5, 3))
        screen.blit(wifi_bg, (width - wifi_bg.get_width() - 10, height - 50))
        
        # Desk status indicator
        status_text = "AT DESK" if at_desk else "SLACKING"
        status_color = (255, 100, 100) if at_desk else (100, 255, 100)
        status_render = FONT_CACHE['warning'].render(status_text, True, status_color)
        status_bg = pygame.Surface((status_render.get_width() + 10, status_render.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(status_bg, (0, 0, 0, 180), status_bg.get_rect(), border_radius=5)
        status_bg.blit(status_render, (5, 3))
        screen.blit(status_bg, (width - status_bg.get_width() - 10, height - 90))
        
        # Draining indicator when at desk
        if at_desk:
            drain_text = FONT_CACHE['hint'].render("DRAINING...", True, (255, 100, 100))
            drain_bg = pygame.Surface((drain_text.get_width() + 10, drain_text.get_height() + 6), pygame.SRCALPHA)
            pygame.draw.rect(drain_bg, (0, 0, 0, 180), drain_bg.get_rect(), border_radius=5)
            drain_bg.blit(drain_text, (5, 3))
            screen.blit(drain_bg, (width - drain_bg.get_width() - 10, height - 120))
        
        # Fridge Display (Jerome mechanic)
        fridge_color = GREEN if fridge_level > 50 else YELLOW if fridge_level > 20 else RED
        fridge_text = FONT_CACHE['time'].render(f"FRIDGE: {int(fridge_level)}%", True, fridge_color)
        fridge_bg = pygame.Surface((fridge_text.get_width() + 10, fridge_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(fridge_bg, (0, 0, 0, 180), fridge_bg.get_rect(), border_radius=5)
        fridge_bg.blit(fridge_text, (5, 3))
        screen.blit(fridge_bg, (10, height - 50))
        
        # Game Time Display (FNAF-style clock)
        time_font = pygame.font.Font(None, 36)
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = time_font.render(f"{minutes}:{seconds:02d}", True, WHITE)
        time_bg = pygame.Surface((time_text.get_width() + 10, time_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(time_bg, (0, 0, 0, 180), time_bg.get_rect(), border_radius=5)
        time_bg.blit(time_text, (5, 3))
        screen.blit(time_bg, (width // 2 - time_bg.get_width() // 2, 10))
        
        # Egg Inventory Display
        egg_font = pygame.font.Font(None, 28)
        egg_status = "EGG: YES" if has_egg else "EGG: NO"
        
        # Change color based on chase status
        if has_egg and jonathan_state == "chasing_egg":
            egg_color = RED  # Red when Jonathan is chasing
        elif has_egg:
            egg_color = YELLOW if egg_held_time > egg_chase_threshold * 0.7 else GREEN  # Yellow as warning
        else:
            egg_color = RED
            
        egg_text = egg_font.render(egg_status, True, egg_color)
        egg_bg = pygame.Surface((egg_text.get_width() + 10, egg_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(egg_bg, (0, 0, 0, 180), egg_bg.get_rect(), border_radius=5)
        egg_bg.blit(egg_text, (5, 3))
        screen.blit(egg_bg, (10, height - 90))
        
        # Show timer when holding egg
        if has_egg:
            time_remaining = max(0, egg_chase_threshold - egg_held_time)
            timer_font = pygame.font.Font(None, 20)
            if jonathan_state == "chasing_egg":
                timer_text = timer_font.render("JONATHAN CHASING!", True, RED)
            else:
                timer_text = timer_font.render(f"Time: {int(time_remaining)}s", True, egg_color)
            timer_bg = pygame.Surface((timer_text.get_width() + 10, timer_text.get_height() + 6), pygame.SRCALPHA)
            pygame.draw.rect(timer_bg, (0, 0, 0, 180), timer_bg.get_rect(), border_radius=5)
            timer_bg.blit(timer_text, (5, 3))
            screen.blit(timer_bg, (10, height - 120))
    
    elif game_mode == "camera":
        # Camera mode - show selected room with FNAF-style camera effect
        screen.fill(BLACK)
        
        # Draw the selected room view using external images
        camera_room = selected_camera
        room_surface = pygame.Surface((width - 100, height - 150))
        
        # Show the camera images
        base_img = camera_images[selected_camera]
        
        # Load and scale the image to fit the view
        scaled_img = pygame.transform.scale(base_img, (width - 100, height - 150))
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
            "SPACE/ESC - Close Cameras"
        ]
        for i, inst in enumerate(instructions):
            text = inst_font.render(inst, True, (180, 180, 180))
            screen.blit(text, (60, height - 70 + i * 25))
        
        # WIFI Display (FNAF-style power meter) - draining warning
        wifi_font = pygame.font.Font(None, 32)
        wifi_color = GREEN if wifi > 50 else YELLOW if wifi > 20 else RED
        wifi_text = wifi_font.render(f"WIFI: {int(wifi)}%", True, wifi_color)
        screen.blit(wifi_text, (width - 200, height - 50))
        
        # Draining indicator
        status_font = pygame.font.Font(None, 20)
        drain_text = status_font.render("DRAINING...", True, (255, 100, 100))
        screen.blit(drain_text, (width - 200, height - 75))
        
        # Fridge Display in camera mode
        fridge_font = pygame.font.Font(None, 24)
        fridge_color = GREEN if fridge_level > 50 else YELLOW if fridge_level > 20 else RED
        fridge_text = fridge_font.render(f"FRIDGE: {int(fridge_level)}%", True, fridge_color)
        screen.blit(fridge_text, (60, height - 40))
        
        # Egg Inventory in camera mode
        egg_font = pygame.font.Font(None, 24)
        egg_status = "EGG: YES" if has_egg else "EGG: NO"
        egg_color = GREEN if has_egg else RED
        egg_text = egg_font.render(egg_status, True, egg_color)
        screen.blit(egg_text, (60, height - 20))
        
        # Game Time Display
        time_font = pygame.font.Font(None, 28)
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = time_font.render(f"TIME: {minutes}:{seconds:02d}", True, WHITE)
        screen.blit(time_text, (width // 2 - time_text.get_width() // 2, 30))
        
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
        
        # Show hints for breakroom interactions
        if current_room == 2:  # Breakroom
            table_rect = pygame.Rect(width // 2 - 150, height // 2 - 40, 300, 80)
            fridge_rect = pygame.Rect(width // 2 + 170, height // 2 - 50, 60, 100)
            player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
            hint_font = pygame.font.Font(None, 20)
            
            # Show fridge restock hint at the broken fridge
            if player_rect.colliderect(fridge_rect.inflate(60, 60)) and fridge_level < 100:
                hint_text = hint_font.render("E - Restock Fridge", True, (100, 200, 255))
                hint_bg = pygame.Surface((hint_text.get_width() + 10, hint_text.get_height() + 6), pygame.SRCALPHA)
                pygame.draw.rect(hint_bg, (0, 0, 0, 180), hint_bg.get_rect(), border_radius=5)
                hint_bg.blit(hint_text, (5, 3))
                screen.blit(hint_bg, (fridge_rect.centerx - hint_bg.get_width() // 2, fridge_rect.y - 50))
            
            # Show egg pickup hint at the table
            if player_rect.colliderect(table_rect.inflate(60, 60)) and not has_egg:
                hint_text = hint_font.render("E - Pick up Egg", True, (255, 255, 100))
                hint_bg = pygame.Surface((hint_text.get_width() + 10, hint_text.get_height() + 6), pygame.SRCALPHA)
                pygame.draw.rect(hint_bg, (0, 0, 0, 180), hint_bg.get_rect(), border_radius=5)
                hint_bg.blit(hint_text, (5, 3))
                screen.blit(hint_bg, (table_rect.centerx - hint_bg.get_width() // 2, table_rect.y - 50))
        
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
                
                # Special rendering for the Fridge in breakroom
                if furn_sprite.label == "Broken" and current_room == 2:
                    # Draw glowing fridge effect
                    fridge_glow_color = (150, 200, 255) if fridge_level > 50 else (255, 200, 100) if fridge_level > 20 else (255, 100, 100)
                    glow_surf, glow_pos = create_glow_effect(
                        furn_sprite.rect.centerx, furn_sprite.rect.centery,
                        40, fridge_glow_color, 80
                    )
                    screen.blit(glow_surf, glow_pos)
                    
                    # Draw fridge interior glow (simulating open door with light)
                    interior_glow = pygame.Surface((furn_sprite.rect.width - 10, furn_sprite.rect.height - 10), pygame.SRCALPHA)
                    pygame.draw.rect(interior_glow, (*fridge_glow_color, 120), interior_glow.get_rect(), border_radius=5)
                    screen.blit(interior_glow, (furn_sprite.rect.x + 5, furn_sprite.rect.y + 5))
                    
                    # Draw shelves/items inside
                    item_colors = [(255, 100, 100), (100, 255, 100), (100, 200, 255), (255, 255, 100)]
                    shelf_y_positions = [20, 40, 60, 80]
                    for i, shelf_y in enumerate(shelf_y_positions):
                        if i < len(item_colors):
                            # Draw small food items on shelves
                            item_x = furn_sprite.rect.x + 15 + (i % 2) * 20
                            pygame.draw.rect(screen, item_colors[i], 
                                           (item_x, furn_sprite.rect.y + shelf_y, 12, 8), border_radius=2)
                    
                    # Draw "FRIDGE" label on top
                    fridge_font = pygame.font.Font(None, 22)
                    fridge_text = fridge_font.render("FRIDGE", True, WHITE)
                    fridge_text_bg = pygame.Surface((fridge_text.get_width() + 8, fridge_text.get_height() + 4), pygame.SRCALPHA)
                    pygame.draw.rect(fridge_text_bg, (0, 0, 0, 200), fridge_text_bg.get_rect(), border_radius=4)
                    fridge_text_bg.blit(fridge_text, (4, 2))
                    screen.blit(fridge_text_bg, (furn_sprite.rect.centerx - fridge_text_bg.get_width() // 2, 
                                                 furn_sprite.rect.y - 25))
                    
                    # Show fill level bar above fridge
                    bar_width = 50
                    bar_height = 8
                    bar_x = furn_sprite.rect.centerx - bar_width // 2
                    bar_y = furn_sprite.rect.y - 45
                    
                    # Background
                    pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
                    # Fill
                    fill_width = int(bar_width * (fridge_level / 100))
                    fill_color = GREEN if fridge_level > 50 else YELLOW if fridge_level > 20 else RED
                    if fill_width > 0:
                        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=3)
                    # Border
                    pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=3)
                
                # Draw label if exists (for non-fridge items)
                elif furn_sprite.label and furn_sprite.label != "Broken":
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
        

        
        # Draw particles (limit to 50 for performance)
        for particle in particles[:50]:
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
        
        # Draw Jonathan if active (only if in the same room as player)
        if jonathan_active and jonathan_room == current_room:
            # Draw Jonathan's shadow
            shadow_pos = (jonathan_x + 4, jonathan_y + jonathan_size)
            screen.blit(jonathan_sprite.shadow, shadow_pos)
            
            # Draw friendly blue glow around Jonathan
            glow_surf, glow_pos = create_glow_effect(
                jonathan_x + jonathan_size // 2, jonathan_y + jonathan_size // 2,
                40, (20, 100, 120), 100
            )
            screen.blit(glow_surf, glow_pos)
            
            # Draw Jonathan sprite
            screen.blit(jonathan_sprite.image, jonathan_sprite.rect)
            
            # Draw Jonathan's title
            font_small = pygame.font.Font(None, 20)
            name_text = font_small.render("Jonathan", True, (150, 200, 210))
            name_bg = pygame.Surface((name_text.get_width() + 8, name_text.get_height() + 4), pygame.SRCALPHA)
            pygame.draw.rect(name_bg, (20, 60, 80, 200), name_bg.get_rect(), border_radius=4)
            name_bg.blit(name_text, (4, 2))
            screen.blit(name_bg, (jonathan_x - 10, jonathan_y - 25))
            
            # Draw joke speech bubble above Jonathan if joke is available
            if jonathan_joke_text:
                joke_font = pygame.font.Font(None, 18)
                max_width = 300
                
                # Word wrap the joke
                words = jonathan_joke_text.split(' ')
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    if joke_font.size(test_line)[0] < max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word + " "
                if current_line:
                    lines.append(current_line)
                
                # Limit to 4 lines
                lines = lines[:4]
                
                # Calculate bubble size
                line_height = 20
                bubble_height = len(lines) * line_height + 20
                bubble_width = max_width + 20
                
                # Draw speech bubble
                bubble_x = jonathan_x + jonathan_size // 2 - bubble_width // 2
                bubble_y = jonathan_y - bubble_height - 35
                
                # Make sure bubble stays on screen
                bubble_x = max(10, min(bubble_x, width - bubble_width - 10))
                bubble_y = max(10, bubble_y)
                
                # Draw bubble background
                bubble_surf = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
                pygame.draw.rect(bubble_surf, (240, 240, 255, 230), bubble_surf.get_rect(), border_radius=10)
                pygame.draw.rect(bubble_surf, (100, 150, 200), bubble_surf.get_rect(), 2, border_radius=10)
                
                # Draw text lines
                for i, line in enumerate(lines):
                    text_surf = joke_font.render(line.strip(), True, (20, 20, 50))
                    bubble_surf.blit(text_surf, (10, 10 + i * line_height))
                
                screen.blit(bubble_surf, (bubble_x, bubble_y))
                
                # Draw bubble pointer (triangle pointing to Jonathan)
                pointer_points = [
                    (jonathan_x + jonathan_size // 2, jonathan_y - 30),
                    (jonathan_x + jonathan_size // 2 - 10, bubble_y + bubble_height),
                    (jonathan_x + jonathan_size // 2 + 10, bubble_y + bubble_height)
                ]
                pygame.draw.polygon(screen, (240, 240, 255), pointer_points)
                pygame.draw.polygon(screen, (100, 150, 200), pointer_points, 2)
        
        # Draw MMO-style UI
        draw_mmo_ui(screen, current_time)
        
        # Walk mode instructions
        walk_inst_font = pygame.font.Font(None, 18)
        if current_room == 0:
            walk_text = walk_inst_font.render("ESC/C - Return to Desk | SHIFT - Sprint | E - Interact", True, (180, 180, 180))
        else:
            walk_text = walk_inst_font.render("Return to your office to access desk | SHIFT - Sprint | E - Interact", True, (180, 180, 180))
        screen.blit(walk_text, (10, height - 25))
        
        # Room indicator
        room_names = {0: "Your Office", 1: "Hallway", 2: "Break Room"}
        room_name_font = pygame.font.Font(None, 24)
        room_name_text = room_name_font.render(f"Location: {room_names[current_room]}", True, (200, 200, 220))
        room_name_bg = pygame.Surface((room_name_text.get_width() + 10, room_name_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(room_name_bg, (0, 0, 0, 180), room_name_bg.get_rect(), border_radius=5)
        room_name_bg.blit(room_name_text, (5, 3))
        screen.blit(room_name_bg, (10, 45))
        
        # WIFI Display in walk mode
        wifi_font = pygame.font.Font(None, 28)
        wifi_color = GREEN if wifi > 50 else YELLOW if wifi > 20 else RED
        wifi_text = wifi_font.render(f"WIFI: {int(wifi)}%", True, wifi_color)
        wifi_bg = pygame.Surface((wifi_text.get_width() + 10, wifi_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(wifi_bg, (0, 0, 0, 180), wifi_bg.get_rect(), border_radius=5)
        wifi_bg.blit(wifi_text, (5, 3))
        screen.blit(wifi_bg, (width - wifi_bg.get_width() - 10, 10))
        
        # Fridge Display in walk mode
        fridge_font = pygame.font.Font(None, 26)
        fridge_color = GREEN if fridge_level > 50 else YELLOW if fridge_level > 20 else RED
        fridge_text = fridge_font.render(f"FRIDGE: {int(fridge_level)}%", True, fridge_color)
        fridge_bg = pygame.Surface((fridge_text.get_width() + 10, fridge_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(fridge_bg, (0, 0, 0, 180), fridge_bg.get_rect(), border_radius=5)
        fridge_bg.blit(fridge_text, (5, 3))
        screen.blit(fridge_bg, (width - fridge_bg.get_width() - 10, 45))
        
        # Egg Inventory in walk mode
        egg_font = pygame.font.Font(None, 26)
        egg_status = "EGG: YES" if has_egg else "EGG: NO"
        egg_color = GREEN if has_egg else RED
        egg_text = egg_font.render(egg_status, True, egg_color)
        egg_bg = pygame.Surface((egg_text.get_width() + 10, egg_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(egg_bg, (0, 0, 0, 180), egg_bg.get_rect(), border_radius=5)
        egg_bg.blit(egg_text, (5, 3))
        screen.blit(egg_bg, (width - egg_bg.get_width() - 10, 80))
        
        # Game Time Display in walk mode
        time_font = pygame.font.Font(None, 30)
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = time_font.render(f"{minutes}:{seconds:02d}", True, WHITE)
        time_bg = pygame.Surface((time_text.get_width() + 10, time_text.get_height() + 6), pygame.SRCALPHA)
        pygame.draw.rect(time_bg, (0, 0, 0, 180), time_bg.get_rect(), border_radius=5)
        time_bg.blit(time_text, (5, 3))
        screen.blit(time_bg, (10, 10))
    
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
            "• Survive 5 minutes to win!",
            "• Keep the FRIDGE stocked (go to Breakroom, press E)",
            "• Get an EGG for defense (Breakroom table, press E)",
            "• WIFI drains when working or viewing cameras",
            "• Time only moves when in office (working/slacking)",
            "",
            "CONTROLS:",
            "• S - Toggle Work/Slack in office",
            "• SPACE/C - Open/Close Cameras",
            "• W - Walk Mode (to restock/get egg)",
            "• WASD/Arrows - Move (walk mode)",
            "• E - Restock/Pickup (walk mode)",
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
    
    # Game Over Screen
    if game_state == "game_over":
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
        screen.blit(overlay, (0, 0))
        
        game_over_text = FONT_CACHE['big'].render("GAME OVER", True, RED)
        screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 100))
        
        reason_font = FONT_CACHE['congrats']
        if wifi <= 0:
            reason = "WIFI ran out!"
        elif fridge_level <= 0:
            reason = "Jerome got you! (Fridge empty)"
        else:
            reason = "You died!"
        reason_text = reason_font.render(reason, True, WHITE)
        screen.blit(reason_text, (width // 2 - reason_text.get_width() // 2, height // 2))
        
        # Stats
        stats_font = pygame.font.Font(None, 28)
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        survived_text = stats_font.render(f"Survived: {minutes}:{seconds:02d}", True, WHITE)
        screen.blit(survived_text, (width // 2 - survived_text.get_width() // 2, height // 2 + 60))
        
        restart_font = pygame.font.Font(None, 24)
        restart_text = restart_font.render("Close and restart to try again", True, (180, 180, 180))
        screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height // 2 + 120))
    
    # Win Screen
    elif game_state == "win":
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 50, 0, 200), overlay.get_rect())
        screen.blit(overlay, (0, 0))
        
        win_text = FONT_CACHE['big'].render("YOU WIN!", True, (100, 255, 100))
        screen.blit(win_text, (width // 2 - win_text.get_width() // 2, height // 2 - 100))
        
        congrats_text = FONT_CACHE['congrats'].render("You survived the shift!", True, WHITE)
        screen.blit(congrats_text, (width // 2 - congrats_text.get_width() // 2, height // 2))
        
        stats_font = FONT_CACHE['warning']
        stats_lines = [
            f"WIFI Remaining: {int(wifi)}%",
            f"Fridge Level: {int(fridge_level)}%",
            f"Had Egg: {'Yes' if has_egg else 'No'}"
        ]
        for i, line in enumerate(stats_lines):
            stat_text = stats_font.render(line, True, WHITE)
            screen.blit(stat_text, (width // 2 - stat_text.get_width() // 2, height // 2 + 60 + i * 35))
    
    # Warning text
    elif warning_text and (current_time - warning_timer) < 3000:
        warning_surface = FONT_CACHE['warning'].render(warning_text, True, (255, 200, 100))
        warning_bg = pygame.Surface((warning_surface.get_width() + 20, 40))
        warning_bg.fill(SHADOW_BLACK)
        warning_bg.set_alpha(200)
        screen.blit(warning_bg, (width // 2 - warning_surface.get_width() // 2 - 10, height - 130))
        screen.blit(warning_surface, (width // 2 - warning_surface.get_width() // 2, height - 125))
    

    
    # Update the display
    pygame.display.flip()
    
    # Control frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
