"""Asset loading and management."""
import pygame
import os
from typing import Dict, Optional
from config import ROOM_IMAGES, ROOMS, BACKGROUND_MUSIC, MUSIC_VOLUME, SOUND_EFFECTS, SOUND_VOLUME


class AssetManager:
    """Manages loading and storage of game assets."""
    
    def __init__(self):
        self.room_images: Dict[str, Optional[pygame.Surface]] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.working_image: Optional[pygame.Surface] = None
        self.music_loaded: bool = False
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
    def load_all(self):
        """Load all game assets."""
        self._load_room_images()
        self._load_fonts()
        self._load_working_image()
        self._load_music()
        self._load_sound_effects()
        
    def _load_room_images(self):
        """Load images for each room."""
        for room, path in ROOM_IMAGES.items():
            try:
                self.room_images[room] = pygame.image.load(path).convert()
                print(f"[INFO] Loaded image for {room}: {path}")
            except Exception as e:
                print(f"[ERROR] Could not load image for {room} at {path}: {e}")
                self.room_images[room] = None
                
    def _load_fonts(self):
        """Load fonts for UI."""
        self.fonts['small'] = pygame.font.Font(None, 24)
        self.fonts['medium'] = pygame.font.Font(None, 32)
        self.fonts['large'] = pygame.font.Font(None, 64)
        
    def _load_working_image(self):
        """Load the working.jpg image."""
        import os
        from config import SCRIPT_DIR, IMAGES_DIR
        
        working_path = os.path.join(IMAGES_DIR, "working.jpg")
        try:
            self.working_image = pygame.image.load(working_path).convert()
            print(f"[INFO] Loaded working image: {working_path}")
        except Exception as e:
            print(f"[ERROR] Could not load working image at {working_path}: {e}")
            self.working_image = None
    
    def _load_music(self):
        """Load and start background music."""
        if not os.path.exists(BACKGROUND_MUSIC):
            print(f"[WARNING] Background music file not found: {BACKGROUND_MUSIC}")
            print(f"[INFO] Place your music file in the audio folder")
            self.music_loaded = False
            return
        
        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            self.music_loaded = True
            print(f"[INFO] Background music loaded and playing: {BACKGROUND_MUSIC}")
        except Exception as e:
            print(f"[ERROR] Could not load background music: {e}")
            self.music_loaded = False
    
    def _load_sound_effects(self):
        """Load sound effects."""
        for sound_name, sound_path in SOUND_EFFECTS.items():
            if os.path.exists(sound_path):
                try:
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(SOUND_VOLUME)
                    self.sounds[sound_name] = sound
                    print(f"[INFO] Loaded sound effect: {sound_name}")
                except Exception as e:
                    print(f"[ERROR] Could not load sound effect {sound_name}: {e}")
            else:
                print(f"[WARNING] Sound effect file not found: {sound_path}")
        
        if not self.sounds:
            print(f"[INFO] No sound effects loaded. Place .mp3 files in the audio folder.")
        
    def get_room_image(self, room: str) -> Optional[pygame.Surface]:
        """Get the image for a specific room."""
        return self.room_images.get(room)
        
    def get_working_image(self) -> Optional[pygame.Surface]:
        """Get the working screen image."""
        return self.working_image
        
    def get_font(self, size: str) -> pygame.font.Font:
        """Get a font by size name."""
        return self.fonts.get(size, self.fonts['medium'])
    
    def play_sound(self, sound_name: str):
        """Play a sound effect by name."""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def pause_music(self):
        """Pause the background music."""
        if self.music_loaded:
            pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause the background music."""
        if self.music_loaded:
            pygame.mixer.music.unpause()
    
    def stop_music(self):
        """Stop the background music."""
        if self.music_loaded:
            pygame.mixer.music.stop()
    
    def set_music_volume(self, volume: float):
        """Set the music volume (0.0 to 1.0)."""
        if self.music_loaded:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
    
    def set_sound_volume(self, volume: float):
        """Set the volume for all sound effects (0.0 to 1.0)."""
        clamped_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(clamped_volume)
