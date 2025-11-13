"""Minimal Five Nights at Freddy's style prototype for Pygbag/browser.
Refactored into modular architecture.
Controls: C = camera, A/D = doors, LEFT/RIGHT = switch rooms, ESC = quit (native only)
"""
import pygame
import asyncio

from config import (
    WIDTH, HEIGHT, FPS,
    POWER_DRAIN_BASE, POWER_DRAIN_CAMERA, POWER_DRAIN_DOOR, POWER_DRAIN_COMPUTER,
    ENEMY_PATH, ENEMY_MOVE_INTERVAL, ENEMY_ATTACK_INTERVAL, ENEMIES
)
from assets import AssetManager
from game_state import GameState
from camera import Camera
from renderer import Renderer
from enemies import EnemyManager, Enemy
from free_roam_manager import FreeRoamManager


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
    free_roam = FreeRoamManager()
    
    # Initialize enemies
    enemy_manager = EnemyManager(ENEMY_PATH, ENEMY_MOVE_INTERVAL, ENEMY_ATTACK_INTERVAL)
    for enemy_name, starting_room, aggression, behavior_type in ENEMIES:
        enemy_manager.add_enemy(Enemy(enemy_name, starting_room, aggression, behavior_type))
    
    # Link enemy manager to renderer
    renderer.set_enemy_manager(enemy_manager)
    renderer.set_free_roam_manager(free_roam)
    
    # Main game loop
    while game_state.running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state.running = False
            elif event.type == pygame.KEYDOWN and game_state.is_playing():
                if event.key == pygame.K_ESCAPE:
                    if game_state.free_roam_mode:
                        # Exit free roam back to office
                        game_state.exit_free_roam()
                        free_roam.reset_to_office()
                    else:
                        game_state.running = False
                elif event.key == pygame.K_w and not game_state.free_roam_mode and not game_state.camera_active:
                    # Enter free roam mode from office
                    game_state.enter_free_roam()
                elif not game_state.free_roam_mode:
                    # Office controls
                    if event.key == pygame.K_c:
                        game_state.toggle_camera()
                    elif event.key == pygame.K_SPACE:
                        # Toggle computer (pretending to work)
                        game_state.toggle_computer()
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
            if game_state.computer_active:
                drain += POWER_DRAIN_COMPUTER
            if game_state.left_door_closed:
                drain += POWER_DRAIN_DOOR
            if game_state.right_door_closed:
                drain += POWER_DRAIN_DOOR
                
            game_state.update(dt, drain)
            
            # Deplete fridge over time (every 30 seconds)
            if int(game_state.night_time) % 30 == 0 and int(game_state.night_time) > 0:
                if int((game_state.night_time - dt)) % 30 != 0:  # Only once per interval
                    game_state.deplete_fridge()
            
            # Update enemies
            attacking_enemy = enemy_manager.update(
                dt, 
                game_state.left_door_closed, 
                game_state.right_door_closed,
                game_state.is_slacking(),
                game_state.has_egg,
                game_state.fridge_stock
            )
            if attacking_enemy:
                if attacking_enemy.startswith("egg_taken_"):
                    # Johnathan took the egg
                    game_state.lose_egg()
                else:
                    # Player caught by enemy
                    game_state.enemy_attack(attacking_enemy)
            
            # Update based on mode
            if game_state.free_roam_mode:
                # Update free roam
                keys = pygame.key.get_pressed()
                player_moved, interaction = free_roam.update(dt, keys)
                
                # Handle interactions
                if interaction == 'supply':
                    # Restock fridge
                    if game_state.restock_fridge():
                        pass  # Successfully restocked
                
                # Check for egg pickup (E key near supply boxes)
                if (keys[pygame.K_e] or keys[pygame.K_SPACE]) and free_roam.current_room_id == 2:
                    # In break room, check if near supply boxes
                    room = free_roam.get_current_room()
                    player_rect = free_roam.get_player_rect()
                    for furn in room.furniture:
                        if furn.get('type') == 'supply':
                            inflated = furn['rect'].inflate(50, 50)
                            if player_rect.colliderect(inflated) and not game_state.has_egg:
                                game_state.pickup_egg()
                                break
                
                # Check if enemies catch player in free roam
                player_rect = free_roam.get_player_rect()
                room_id = free_roam.current_room_id
                enemies_here = enemy_manager.get_enemies_in_free_roam_room(room_id)
                
                for enemy in enemies_here:
                    # Create enemy collision rect
                    enemy_rect = pygame.Rect(int(enemy.free_roam_x), int(enemy.free_roam_y), 45, 45)
                    
                    # Check collision with player
                    if player_rect.colliderect(enemy_rect):
                        game_state.enemy_attack(enemy.name)
                        break
                        
            elif game_state.camera_active:
                # Update camera if active
                room_image = assets.get_room_image(camera.get_current_room_name())
                camera.update(dt, room_image)
        
        # Render
        renderer.render_frame(game_state, camera)
        
        # Yield to browser (required for Pygbag)
        await asyncio.sleep(0.016)
    
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
