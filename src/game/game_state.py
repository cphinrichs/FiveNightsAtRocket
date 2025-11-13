"""Game state management."""
from typing import Optional
from config import POWER_MAX, WIN_TIME


class GameState:
    """Manages the current state of the game."""
    
    def __init__(self):
        # Core state
        self.running = True
        self.game_over = False
        self.win = False
        self.death_message = ""
        
        # Time tracking
        self.night_time = 0.0
        
        # Player controls
        self.camera_active = False
        self.left_door_closed = False
        self.right_door_closed = False
        
        # Power system
        self.power = POWER_MAX
        
    def update(self, dt: float, power_drain: float):
        """Update game state each frame."""
        if self.game_over or self.win:
            return
            
        self.night_time += dt
        self.power = max(0, self.power - power_drain * dt)
        
        # Check win condition
        if self.night_time >= WIN_TIME:
            self.win = True
            
        # Check lose condition (can be extended)
        if self.power <= 0:
            self.game_over = True
            self.death_message = "Out of Power"
            
    def enemy_attack(self, enemy_name: str):
        """Handle an enemy attack (jumpscare/game over)."""
        self.game_over = True
        self.death_message = f"Caught by {enemy_name}!"
            
    def toggle_camera(self):
        """Toggle camera on/off."""
        self.camera_active = not self.camera_active
        
    def toggle_left_door(self):
        """Toggle left door open/closed."""
        self.left_door_closed = not self.left_door_closed
        
    def toggle_right_door(self):
        """Toggle right door open/closed."""
        self.right_door_closed = not self.right_door_closed
        
    def is_playing(self) -> bool:
        """Check if game is still in play."""
        return not self.game_over and not self.win
