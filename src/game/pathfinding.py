"""
PATHFINDING UTILITIES
=====================
Helper functions for enemy navigation around obstacles.
Simple pathfinding system that tries direct paths first,
then tests alternative directions to avoid walls.
"""

import pygame
import math
from typing import List, Tuple


def simple_pathfind(enemy_pos: Tuple[float, float], target_pos: Tuple[float, float], 
                   walls: List[pygame.Rect], room_bounds: pygame.Rect) -> Tuple[float, float]:
    """
    Simple pathfinding that tries to navigate around walls.
    Uses sampling to test if paths are clear.
    
    Algorithm:
    1. Try direct path to target
    2. If blocked, test alternative directions
    3. Choose best alternative that moves toward target
    
    Args:
        enemy_pos: Current position (x, y) of enemy
        target_pos: Target position (x, y) to reach
        walls: List of wall rectangles to avoid
        room_bounds: Boundary of the room
        
    Returns:
        Normalized direction vector (dx, dy) to move in
    """
    ex, ey = enemy_pos
    tx, ty = target_pos
    
    # Calculate direct vector to target
    dx = tx - ex
    dy = ty - ey
    dist = math.sqrt(dx * dx + dy * dy)
    
    # Already at target
    if dist < 5:
        return 0, 0
    
    # Normalize direction
    dx /= dist
    dy /= dist
    
    # Check if direct path is clear
    # Sample points along the path to detect wall collisions
    steps = int(dist / 20)  # Check every 20 pixels
    direct_clear = True
    
    if steps > 0:
        for i in range(1, steps + 1):
            # Position along the path
            check_x = ex + (dx * dist * i / steps)
            check_y = ey + (dy * dist * i / steps)
            check_rect = pygame.Rect(check_x - 15, check_y - 15, 30, 30)
            
            # Check collision with walls
            for wall in walls:
                if check_rect.colliderect(wall):
                    direct_clear = False
                    break
            
            if not direct_clear:
                break
    
    # If direct path is clear, go straight to target
    if direct_clear:
        return dx, dy
    
    # Otherwise, try alternative directions
    # Test 8 cardinal and diagonal directions
    alternatives = [
        (1, 0),       # Right
        (-1, 0),      # Left
        (0, 1),       # Down
        (0, -1),      # Up
        (0.7, 0.7),   # Diagonal down-right
        (-0.7, 0.7),  # Diagonal down-left
        (0.7, -0.7),  # Diagonal up-right
        (-0.7, -0.7), # Diagonal up-left
    ]
    
    best_dir = (0, 0)
    best_score = -999999  # Start with very low score
    
    # Evaluate each alternative direction
    for alt_dx, alt_dy in alternatives:
        # Normalize alternative direction
        alt_len = math.sqrt(alt_dx * alt_dx + alt_dy * alt_dy)
        if alt_len > 0:
            norm_dx = alt_dx / alt_len
            norm_dy = alt_dy / alt_len
        else:
            continue
        
        # Test if this direction is clear (sample 50 pixels ahead)
        test_x = ex + norm_dx * 50
        test_y = ey + norm_dy * 50
        test_rect = pygame.Rect(test_x - 15, test_y - 15, 30, 30)
        
        # Check if in bounds
        if not room_bounds.collidepoint(test_x, test_y):
            continue
        
        # Check if clear of walls
        clear = True
        for wall in walls:
            if test_rect.colliderect(wall):
                clear = False
                break
        
        if not clear:
            continue
        
        # Score this direction based on:
        # 1. How close it gets to target
        # 2. Dot product with ideal direction (prefer directions toward target)
        dot_product = norm_dx * dx + norm_dy * dy  # Higher = more aligned with target
        
        # Calculate distance to target if we moved this way
        new_x = ex + norm_dx * 50
        new_y = ey + norm_dy * 50
        new_dist = math.sqrt((tx - new_x) ** 2 + (ty - new_y) ** 2)
        
        # Prefer directions that reduce distance to target
        distance_score = -new_dist  # Negative because we want to minimize
        
        # Combined score
        score = dot_product * 100 + distance_score
        
        # Keep best scoring direction
        if score > best_score:
            best_score = score
            best_dir = (norm_dx, norm_dy)
    
    # Return best direction found (or stay still if all blocked)
    return best_dir
