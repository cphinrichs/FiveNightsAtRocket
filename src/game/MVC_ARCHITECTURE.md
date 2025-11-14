# Five Nights at Rocket - MVC Architecture Documentation

## Overview
This game follows the **Model-View-Controller (MVC)** design pattern, separating concerns into three distinct layers.

## Architecture

```
┌─────────────┐
│ CONTROLLER  │ ← Handles input, coordinates game loop
└──────┬──────┘
       │
   ┌───▼───┐
   │  MVC  │
   └───┬───┘
       │
    ┌──▼──────┐        ┌──────────┐
    │  MODEL  │◄───────│   VIEW   │
    └─────────┘        └──────────┘
       Data/Logic         Rendering

```

## File Structure

### **models.py** - MODEL Layer (742 lines)
**Purpose**: Contains all game data structures and business logic

**Key Classes**:
- `GameState`, `RoomType`, `Direction`, `InteractableType` - Enumerations for game constants
- `Particle` & `ParticleEmitter` - Visual effects system
- `Entity` - Base class for all game objects
- `Player` - Player character with inventory and movement
- `Enemy` - Base enemy class with AI navigation
  - `Jonathan` - Always chases, distracted by eggs
  - `Jeromathy` - Activated by snack depletion
  - `Angellica` - Triggered by YouTube usage
  - `NextGenIntern` - Harmless snack thief
- `Interactable` - Objects player can interact with
- `Room` - Room structure with walls and connections

**Responsibilities**:
- Store game state (positions, inventory, timers)
- Define entity behavior (movement, AI logic)
- Manage game rules and validation
- NO rendering or input handling

**Example**:
```python
# Model handles entity behavior
def update(self, dt: float, player: Player, rooms: Dict, current_room: str):
    """Update Jo-nathan's behavior each frame."""
    if self.state == "chasing":
        # Chase player logic
        self.move_towards(player.get_center())
```

---

### **views.py** - VIEW Layer (736 lines)
**Purpose**: Handles all visual rendering and presentation

**Key Components**:
- **Sprite Generation**: `create_player_sprite()`, `create_enemy_sprite()`, `create_interactable_sprite()`
- **Renderers**:
  - `PlayerRenderer` - Draws player with directional sprites
  - `EnemyRenderer` - Draws enemies with state-based sprites
  - `InteractableRenderer` - Draws objects
  - `RoomRenderer` - Draws floors, walls, labels
  - `ParticleRenderer` - Draws particle effects
  - `HUDRenderer` - Draws UI (inventory, time, battery)
  - `MenuRenderer` - Draws menus and overlays
  - `CameraRenderer` - Draws security camera view

**Responsibilities**:
- Generate and cache sprites
- Render game objects to screen
- Draw UI elements and effects
- Handle camera offsets
- NO game logic or state modification

**Example**:
```python
# View handles rendering
def draw(self, player: Player, surface: pygame.Surface, camera_offset: Tuple[int, int]):
    """Draw the player character with cached sprite."""
    sprite = self.get_cached_sprite(player.direction)
    surface.blit(sprite, (player.x - camera_offset[0], player.y - camera_offset[1]))
```

---

### **controller.py** - CONTROLLER Layer (719 lines)
**Purpose**: Coordinates game flow, handles input, manages game loop

**Key Class**:
- `GameController` - Main game coordinator

**Core Methods**:
- `__init__()` - Initialize pygame, renderers, game state
- `run()` - Async main game loop
- `handle_events()` - Process keyboard/mouse input
- `update()` - Update game logic each frame
- `render()` - Coordinate all rendering
- `check_wall_collision()` - Physics/collision detection
- `check_enemy_collisions()` - Combat resolution

**Responsibilities**:
- Game loop execution (60 FPS)
- Input handling and event routing
- Coordinate Model updates
- Trigger View rendering
- Collision detection and response
- Game state transitions

**Example**:
```python
# Controller coordinates everything
async def run(self):
    """Main game loop - coordinates input, update, render."""
    while self.running:
        dt = self.clock.tick(FPS) / 1000.0
        
        self.handle_events()  # Input → Controller
        self.update(dt)       # Controller → Model
        self.render()         # Controller → View
        
        await asyncio.sleep(0)  # Async for browser support
```

---

### **pathfinding.py** - UTILITY Module (139 lines)
**Purpose**: Helper functions for enemy navigation

**Key Function**:
- `simple_pathfind()` - Calculates navigation around obstacles

**Algorithm**:
1. Try direct path to target
2. Sample points along path to detect walls
3. If blocked, evaluate 8 alternative directions
4. Choose direction that moves closest to target while avoiding walls

---

## Data Flow

### Input Flow
```
User Input → Controller.handle_events()
                ↓
         Route based on GameState
                ↓
         Modify Model state
```

### Update Flow
```
Controller.update(dt)
        ↓
    Update Models:
    - Player movement
    - Enemy AI logic
    - Collision detection
    - Time progression
        ↓
    Check win/loss conditions
```

### Render Flow
```
Controller.render()
        ↓
    Get camera offset from Model
        ↓
    Call appropriate View renderers:
    - RoomRenderer.draw()
    - EnemyRenderer.draw()
    - PlayerRenderer.draw()
    - HUDRenderer.draw()
```

## Key Design Principles

### 1. **Separation of Concerns**
- Models don't know about rendering
- Views don't modify game state
- Controller mediates between them

### 2. **Single Responsibility**
- Each class has one clear purpose
- Models handle data/logic
- Views handle visuals
- Controller handles coordination

### 3. **Sprite Caching**
- Views generate sprites once
- Cache sprites for reuse
- Reduces per-frame rendering cost

### 4. **State Machine Pattern**
- Game uses `GameState` enum
- Clear transitions between states
- Each state has dedicated update/render methods

### 5. **Component-Based Entities**
- Base `Entity` class provides common functionality
- Specific entities extend with unique behavior
- Composition over inheritance where possible

## Game Loop Breakdown

```python
# 60 FPS game loop
while running:
    # 1. Calculate delta time (frame-rate independent)
    dt = clock.tick(60) / 1000.0
    
    # 2. CONTROLLER: Process input
    for event in pygame.event.get():
        handle_input(event)
    
    # 3. CONTROLLER → MODEL: Update game state
    player.move(dx, dy, dt)
    for enemy in enemies:
        enemy.update(dt, player, rooms)
    check_collisions()
    
    # 4. CONTROLLER → VIEW: Render everything
    for room in rooms:
        room_renderer.draw(room, screen, camera_offset)
    player_renderer.draw(player, screen, camera_offset)
    for enemy in enemies:
        enemy_renderer.draw(enemy, screen, camera_offset)
    hud_renderer.draw(screen, game_data)
    
    # 5. Display to screen
    pygame.display.flip()
```

## Benefits of MVC Architecture

### **Maintainability**
- Easy to locate and fix bugs (each layer is isolated)
- Clear file organization (know where to look)
- Comments explain what, not just how

### **Testability**
- Can test Models without Views
- Can test Views without game logic
- Controller can be mocked for unit tests

### **Scalability**
- Add new entities by extending Model classes
- Add new renderers without touching game logic
- Swap rendering systems without changing Models

### **Collaboration**
- Artists work on Views
- Programmers work on Models
- Designers work on Controller balance
- Minimal merge conflicts

### **Reusability**
- Pathfinding module works independently
- Renderers can be used in other projects
- Model classes are pure Python (no pygame dependencies)

## Running the Game

**New MVC Version**:
```bash
python controller.py
```

**Old Monolithic Version**:
```bash
python main.py  # Still works, for comparison
```

## Lines of Code Comparison

| Version | Total Lines | Largest File |
|---------|-------------|--------------|
| **Original** | 1977 lines | main.py (1977) |
| **MVC** | 2336 lines | 4 files (avg 584) |

*MVC version has more comments and documentation, explaining every function and class.*

## Future Enhancements

With MVC architecture, these become easier:

1. **Add new enemy types** - Extend `Enemy` class in `models.py`
2. **Change art style** - Modify sprite generation in `views.py`
3. **Add multiplayer** - Network code in Controller, replicate Models
4. **Save/load system** - Serialize Models to JSON
5. **Different game modes** - New GameState values and handlers
6. **Mobile controls** - Add touch input handler in Controller
7. **Level editor** - Manipulate Room Models directly

## Comments Philosophy

Every file includes:
- **Module docstring** - Purpose and responsibilities
- **Class docstrings** - What the class represents
- **Method docstrings** - Parameters, returns, behavior
- **Inline comments** - Complex algorithms explained step-by-step

**Example**:
```python
def simple_pathfind(enemy_pos, target_pos, walls, room_bounds):
    """
    Simple pathfinding that tries to navigate around walls.
    
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
    # Implementation with step-by-step comments...
```

---

**Author**: MVC Refactoring
**Date**: November 13, 2025
**Pattern**: Model-View-Controller
**Language**: Python 3.13 with Pygame 2.6.1
