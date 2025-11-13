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
        
        # Game mode
        self.free_roam_mode = False  # True when player leaves office
        
        # Player controls
        self.camera_active = False
        self.left_door_closed = False
        self.right_door_closed = False
        
        # New mechanics
        self.computer_active = False  # True when "working" on computer
        self.has_egg = False  # True if player has an egg
        self.fridge_stock = 3  # Number of items in fridge (starts full)
        
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
        
    def toggle_computer(self):
        """Toggle computer on/off (pretending to work)."""
        self.computer_active = not self.computer_active
        
    def pickup_egg(self):
        """Pick up an egg."""
        self.has_egg = True
        
    def lose_egg(self):
        """Lose/give away egg."""
        self.has_egg = False
        
    def restock_fridge(self):
        """Add an item to the fridge."""
        if self.fridge_stock < 3:
            self.fridge_stock += 1
            return True
        return False
        
    def deplete_fridge(self):
        """Remove an item from fridge (natural depletion over time)."""
        if self.fridge_stock > 0:
            self.fridge_stock -= 1
    
    def is_slacking(self) -> bool:
        """Check if player is currently slacking (not on computer and not in free roam)."""
        return not self.computer_active and not self.free_roam_mode and not self.camera_active
        
    def enter_free_roam(self):
        """Enter free roam mode (leave office)."""
        self.free_roam_mode = True
        self.camera_active = False
        self.computer_active = False  # Can't use computer while walking
        
    def exit_free_roam(self):
        """Return to office from free roam."""
        self.free_roam_mode = False
        
    def is_playing(self) -> bool:
        """Check if game is still in play."""
        return not self.game_over and not self.win
    
    def reset(self):
        """Reset the game to initial state."""
        from config import POWER_MAX
        
        self.game_over = False
        self.win = False
        self.death_message = ""
        self.night_time = 0.0
        self.free_roam_mode = False
        self.camera_active = False
        self.left_door_closed = False
        self.right_door_closed = False
        self.computer_active = False
        self.has_egg = False
        self.fridge_stock = 3
        self.power = POWER_MAX
