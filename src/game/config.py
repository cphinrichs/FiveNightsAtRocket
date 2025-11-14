"""Game configuration and constants."""
import os

# Display settings
WIDTH = 800
HEIGHT = 480
FPS = 60

# Camera settings
CAMERA_ZOOM = 1.5  # Zoom factor for camera view

# Gameplay settings
POWER_MAX = 100.0
POWER_DRAIN_BASE = 0.05  # Reduced base drain (slacking on phone)
POWER_DRAIN_CAMERA = 0.2
POWER_DRAIN_DOOR = 0.3
POWER_DRAIN_COMPUTER = 0.15  # Power drain when using computer/laptop
WIN_TIME = 360  # 6 minutes (360 seconds) to survive

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")
AUDIO_DIR = os.path.join(SCRIPT_DIR, "audio")

# Audio settings
MUSIC_VOLUME = 0.7  # Background music volume (0.0 to 1.0)
SOUND_VOLUME = 0.5  # Sound effects volume (0.0 to 1.0)
BACKGROUND_MUSIC = os.path.join(AUDIO_DIR, "dnd_background_music.mp3")  # or .ogg, .wav

# Sound effect files (place these in the audio folder)
SOUND_EFFECTS = {
    "door_open": os.path.join(AUDIO_DIR, "door_open.mp3"),
    "door_close": os.path.join(AUDIO_DIR, "door_close.mp3"),
    "camera_on": os.path.join(AUDIO_DIR, "camera_change.mp3"),
    "camera_off": os.path.join(AUDIO_DIR, "camera_change.mp3"),
    "computer_on": os.path.join(AUDIO_DIR, "computer_on.mp3"),
    "jumpscare": os.path.join(AUDIO_DIR, "jumpscare.mp3"),
    "pickup_egg": os.path.join(AUDIO_DIR, "pickup_egg.mp3"),
    "restock": os.path.join(AUDIO_DIR, "restock.mp3"),
    "egg_taken": os.path.join(AUDIO_DIR, "egg_taken.mp3"),
}

# Room definitions
ROOMS = ["Break Room", "Hallway", "Entrance"]
ROOM_IMAGES = {
    "Break Room": os.path.join(IMAGES_DIR, "break_room.jpg"),
    "Hallway": os.path.join(IMAGES_DIR, "hallway.jpg"),
    "Entrance": os.path.join(IMAGES_DIR, "entrance.jpg")
}

# Enemy settings
ENEMY_MOVE_INTERVAL = 10.0  # Base seconds between enemy moves
ENEMY_ATTACK_INTERVAL = 5.0  # Seconds at door before attack
ENEMY_PATH = ["Entrance", "Hallway", "Break Room"]  # Path enemies follow to office

# Enemy definitions (name, starting_room, aggression_level, behavior_type)
ENEMIES = [
    ("Angela", "Entrance", 1.2, "slacking_checker"),  # Catches you slacking
    ("Angel", "Entrance", 1.0, "slacking_checker"),   # Also catches you slacking
    ("Johnathan", "Entrance", 1.5, "egg_checker"),    # Needs egg protection
    ("Jerome", "Entrance", 0.8, "fridge_checker"),    # Checks fridge stock
]

# Colors
COLOR_BG = (20, 20, 32)
COLOR_OFFICE_BG = (30, 30, 50)
COLOR_CAMERA_FALLBACK = (60, 60, 120)
COLOR_DOOR_CLOSED = (120, 20, 20)
COLOR_DOOR_OPEN = (40, 120, 40)
COLOR_TEXT = (230, 230, 230)
COLOR_TITLE = (255, 255, 255)
COLOR_GAME_OVER = (255, 60, 60)
COLOR_WIN = (60, 255, 120)
COLOR_ENEMY = (255, 200, 50)
