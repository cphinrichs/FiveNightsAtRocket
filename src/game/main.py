"""Minimal Five Nights at Freddy's style prototype for Pygbag/browser.
Refactored into modular architecture.
Controls: C = camera, A/D = doors, LEFT/RIGHT = switch rooms, ESC = quit (native only)
"""
import pygame
import asyncio

from config import (
    WIDTH, HEIGHT, FPS,
    POWER_DRAIN_BASE, POWER_DRAIN_CAMERA, POWER_DRAIN_DOOR,
    ENEMY_PATH, ENEMY_MOVE_INTERVAL, ENEMY_ATTACK_INTERVAL, ENEMIES
)
from assets import AssetManager
from game_state import GameState
from camera import Camera
from renderer import Renderer
from enemies import EnemyManager, Enemy


async def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Five Nights at Rocket")
    clock = pygame.time.Clock()
    
    # Initialize game systems
    assets = AssetManager()
    assets.load_all()
    
    game_state = GameState()
    camera = Camera()
    renderer = Renderer(screen, assets)
    
    # Initialize enemies
    enemy_manager = EnemyManager(ENEMY_PATH, ENEMY_MOVE_INTERVAL, ENEMY_ATTACK_INTERVAL)
    for enemy_name, starting_room, aggression in ENEMIES:
        enemy_manager.add_enemy(Enemy(enemy_name, starting_room, aggression))
    
    # Link enemy manager to renderer
    renderer.set_enemy_manager(enemy_manager)
    
    # Main game loop
    while game_state.running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
            elif event.type == pygame.KEYDOWN and game_state.is_playing():
                if event.key == pygame.K_ESCAPE:
                    game_state.running = False
                elif event.key == pygame.K_c:
                    game_state.toggle_camera()
                elif event.key == pygame.K_a:
                    game_state.toggle_left_door()
                elif event.key == pygame.K_d:
                    game_state.toggle_right_door()
                elif game_state.camera_active:
                    if event.key == pygame.K_LEFT:
                        camera.switch_room(-1)
                    elif event.key == pygame.K_RIGHT:
                        camera.switch_room(1)
        
        # Update game logic
        dt = clock.tick(FPS) / 1000.0
        
        if game_state.is_playing():
            # Calculate power drain
            drain = POWER_DRAIN_BASE
            if game_state.camera_active:
                drain += POWER_DRAIN_CAMERA
            if game_state.left_door_closed:
                drain += POWER_DRAIN_DOOR
            if game_state.right_door_closed:
                drain += POWER_DRAIN_DOOR
                
            game_state.update(dt, drain)
            
            # Update enemies
            attacking_enemy = enemy_manager.update(
                dt, 
                game_state.left_door_closed, 
                game_state.right_door_closed
            )
            if attacking_enemy:
                game_state.enemy_attack(attacking_enemy)
            
            # Update camera if active
            if game_state.camera_active:
                room_image = assets.get_room_image(camera.get_current_room_name())
                camera.update(dt, room_image)
        
        # Render
        renderer.render_frame(game_state, camera)
        
        # Yield to browser (required for Pygbag)
        await asyncio.sleep(0.016)
    
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
