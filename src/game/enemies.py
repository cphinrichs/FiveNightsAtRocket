"""Enemy system for tracking and moving enemies through rooms."""
import random
from typing import List, Optional


class Enemy:
    """Represents a single enemy that moves between rooms."""
    
    def __init__(self, name: str, starting_room: str, aggression: float = 1.0, behavior_type: str = "normal"):
        """
        Initialize an enemy.
        
        Args:
            name: Display name of the enemy
            starting_room: Initial room where enemy starts
            aggression: Multiplier for move speed (higher = moves more often)
            behavior_type: Type of check this enemy performs
                - "slacking_checker": Catches player if slacking
                - "egg_checker": Catches player without egg
                - "fridge_checker": Catches player if fridge is empty
        """
        self.name = name
        self.current_room = starting_room
        self.aggression = aggression
        self.behavior_type = behavior_type
        self.move_timer = 0.0
        self.at_door = None  # None, "left", or "right"
        self.attack_timer = 0.0
        
        # Free roam position (x, y coordinates in room)
        self.free_roam_x = 0.0
        self.free_roam_y = 0.0
        self._set_random_position_in_room()
        
    def update(self, dt: float, move_interval: float, attack_interval: float, room_path: List[str]):
        """
        Update enemy state.
        
        Args:
            dt: Delta time in seconds
            move_interval: Base time between moves
            attack_interval: Time at door before attacking
            room_path: List of rooms defining the path to office
        """
        self.move_timer += dt
        
        # Check if enemy should move
        adjusted_interval = move_interval / self.aggression
        if self.move_timer >= adjusted_interval:
            self.move_timer = 0.0
            self._attempt_move(room_path)
            
        # If at door, increment attack timer
        if self.at_door:
            self.attack_timer += dt
            if self.attack_timer >= attack_interval:
                return True  # Signal attack
                
        return False
        
    def _attempt_move(self, room_path: List[str]):
        """Attempt to move to the next room in the path."""
        if self.at_door:
            # Already at a door, don't move further
            return
            
        try:
            current_index = room_path.index(self.current_room)
            # Move toward the office (end of path)
            if current_index < len(room_path) - 1:
                # Move to next room
                self.current_room = room_path[current_index + 1]
                self._set_random_position_in_room()
            else:
                # Reached office, choose a door randomly
                self.at_door = random.choice(["left", "right"])
                self.attack_timer = 0.0
        except ValueError:
            # Enemy not in path, shouldn't happen but handle gracefully
            pass
    
    def _set_random_position_in_room(self):
        """Set a random position for enemy in current room (for free roam)."""
        # Position in center area of room, avoiding edges
        self.free_roam_x = random.uniform(200, 600)
        self.free_roam_y = random.uniform(150, 350)
            
    def reset_position(self, starting_room: str):
        """Reset enemy to starting position."""
        self.current_room = starting_room
        self.at_door = None
        self.attack_timer = 0.0
        self.move_timer = 0.0
        self._set_random_position_in_room()
        

class EnemyManager:
    """Manages all enemies in the game."""
    
    def __init__(self, room_path: List[str], move_interval: float = 10.0, attack_interval: float = 5.0):
        """
        Initialize enemy manager.
        
        Args:
            room_path: List of rooms from starting position to office
            move_interval: Base seconds between enemy moves
            attack_interval: Seconds at door before attack
        """
        self.enemies: List[Enemy] = []
        self.room_path = room_path
        self.move_interval = move_interval
        self.attack_interval = attack_interval
        
    def add_enemy(self, enemy: Enemy):
        """Add an enemy to the manager."""
        self.enemies.append(enemy)
        
    def update(self, dt: float, left_door_closed: bool, right_door_closed: bool, 
               is_slacking: bool, has_egg: bool, fridge_stock: int) -> Optional[str]:
        """
        Update all enemies.
        
        Args:
            dt: Delta time
            left_door_closed: Whether left door is closed
            right_door_closed: Whether right door is closed
            is_slacking: Whether player is slacking (not on computer)
            has_egg: Whether player has an egg
            fridge_stock: Number of items in fridge
            
        Returns:
            Name of attacking enemy if attack succeeds, None otherwise
        """
        for enemy in self.enemies:
            attacked = enemy.update(dt, self.move_interval, self.attack_interval, self.room_path)
            
            if attacked:
                # Check if door blocks the attack
                door_blocked = False
                if enemy.at_door == "left" and left_door_closed:
                    door_blocked = True
                elif enemy.at_door == "right" and right_door_closed:
                    door_blocked = True
                
                if door_blocked:
                    # Door blocked, send enemy back
                    enemy.reset_position(self.room_path[0])
                else:
                    # Enemy at door - check behavior-specific conditions
                    attack_succeeds = False
                    
                    if enemy.behavior_type == "slacking_checker":
                        # Angela/Angel: Catch if slacking
                        if is_slacking:
                            attack_succeeds = True
                    elif enemy.behavior_type == "egg_checker":
                        # Johnathan: Always interacts
                        if has_egg:
                            # Takes the egg and leaves (doesn't end game)
                            enemy.reset_position(self.room_path[0])
                            return f"egg_taken_{enemy.name}"  # Special return to indicate egg taken
                        else:
                            # No egg = game over
                            attack_succeeds = True
                    elif enemy.behavior_type == "fridge_checker":
                        # Jerome: Catch if fridge is empty
                        if fridge_stock <= 0:
                            attack_succeeds = True
                    
                    if attack_succeeds:
                        return enemy.name
                    else:
                        # Condition not met, enemy leaves disappointed
                        enemy.reset_position(self.room_path[0])
                    
        return None
        
    def get_enemies_in_room(self, room_name: str) -> List[Enemy]:
        """Get all enemies currently in a specific room."""
        return [e for e in self.enemies if e.current_room == room_name and not e.at_door]
        
    def get_enemies_at_doors(self) -> tuple[List[Enemy], List[Enemy]]:
        """Get enemies at left and right doors."""
        left = [e for e in self.enemies if e.at_door == "left"]
        right = [e for e in self.enemies if e.at_door == "right"]
        return left, right
    
    def get_enemies_in_free_roam_room(self, room_id: int) -> List[Enemy]:
        """
        Get enemies in a specific free roam room.
        
        Args:
            room_id: 0=Office, 1=Hallway, 2=Break Room
            
        Returns:
            List of enemies in that room
        """
        # Map free roam room IDs to enemy system room names
        room_map = {
            0: "Break Room",  # Office in free roam = Break Room in enemy path
            1: "Hallway",
            2: "Entrance"  # Break Room in free roam = Entrance in enemy path
        }
        
        room_name = room_map.get(room_id)
        if room_name:
            return self.get_enemies_in_room(room_name)
        return []
