# MVC Quick Reference Card

## 🎮 What Changed?

**Before**: 1 file (1977 lines) - Everything mixed together  
**After**: 4 files (2427 lines) - Clean separation + 30% documentation

## 📁 File Guide

```
┌─────────────────────────────────────────────────────────┐
│ controller.py - "THE CONDUCTOR"                         │
│ • Run this file to start the game!                      │
│ • Handles: Input, game loop, collision, state          │
│ • Coordinates: Models ↔ Views                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ models.py - "THE BRAIN"                                 │
│ • Game logic and data                                   │
│ • Classes: Player, Enemies, Rooms, Interactables       │
│ • No rendering code!                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ views.py - "THE ARTIST"                                 │
│ • All rendering and visuals                             │
│ • Renderers: Player, Enemy, Room, HUD, Menu            │
│ • No game logic!                                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ pathfinding.py - "THE NAVIGATOR"                        │
│ • Enemy pathfinding utilities                           │
│ • Wall avoidance algorithm                              │
│ • Pure functions, no state                              │
└─────────────────────────────────────────────────────────┘
```

## 🔍 Where to Find Things

| Want to... | Look in... | For... |
|------------|------------|--------|
| **Add new enemy** | `models.py` | Extend `Enemy` class |
| **Change enemy AI** | `models.py` | Enemy `update()` methods |
| **Modify visuals** | `views.py` | Renderer classes |
| **Change colors** | `views.py` | Color constants at top |
| **Add new room** | `controller.py` | `_init_rooms()` method |
| **Fix collision** | `controller.py` | `check_wall_collision()` |
| **Add new key** | `controller.py` | `handle_playing_input()` |
| **Change UI** | `views.py` | `HUDRenderer` class |
| **Fix pathfinding** | `pathfinding.py` | `simple_pathfind()` |

## 🎯 Common Tasks

### Add New Enemy Type

**1. Define in models.py:**
```python
class NewEnemy(Enemy):
    """New enemy description"""
    def __init__(self, x, y):
        super().__init__(x, y, 38, 38, (255, 0, 0), "New Enemy")
    
    def update(self, dt, player, rooms, current_room):
        """Behavior logic here"""
        pass
```

**2. Create in controller.py:**
```python
def _init_enemies(self):
    # Add to enemy list
    self.enemies.append(NewEnemy(x, y))
```

**3. That's it!** View automatically renders it.

### Change Player Speed

**models.py, Player.__init__():**
```python
self.speed = 200  # Change this number
```

### Add New Interactable

**models.py, Room._setup_room():**
```python
self.interactables.append(Interactable(
    x, y, width, height,
    InteractableType.NEW_TYPE,
    (r, g, b)
))
```

**models.py, InteractableType enum:**
```python
class InteractableType(Enum):
    NEW_TYPE = "new_type"
```

**models.py, Interactable.interact():**
```python
elif self.type == InteractableType.NEW_TYPE:
    # Do something
    return "Message to player"
```

## 🏗️ Architecture in 30 Seconds

```
Input → Controller → Updates Models
                        ↓
                   Models hold data
                        ↓
        Controller → Renders with Views
                        ↓
                   Display to screen
```

## 📊 Class Hierarchy

```
Entity (base)
├── Player
└── Enemy
    ├── Jonathan
    ├── Jeromathy
    ├── Angellica
    └── NextGenIntern

Interactable
Room
Particle
ParticleEmitter
```

## 🎨 Rendering Flow

```
GameController.render()
    ↓
RoomRenderer.draw(room)
InteractableRenderer.draw(item)
EnemyRenderer.draw(enemy)
PlayerRenderer.draw(player)
ParticleRenderer.draw(particles)
HUDRenderer.draw(game_data)
    ↓
pygame.display.flip()
```

## 🔄 Update Flow

```
GameController.update(dt)
    ↓
1. Update time/day
2. Handle player movement
3. Update all enemies
4. Update interactables
5. Check collisions
6. Update particles
    ↓
Game state modified
```

## 🎮 Input Handling

```
pygame.event.get()
    ↓
GameController.handle_events()
    ↓
Route by GameState:
├── MENU → handle_menu_input()
├── PLAYING → handle_playing_input()
├── CAMERA → handle_camera_input()
├── PAUSED → handle_paused_input()
└── GAME_OVER → handle_end_screen_input()
```

## 💡 Key Concepts

### Model Responsibilities
✅ Store data (position, inventory, timers)  
✅ Define behavior (movement, AI logic)  
✅ Validate game rules  
❌ NO rendering  
❌ NO input handling  

### View Responsibilities
✅ Generate sprites  
✅ Render to screen  
✅ Visual effects  
❌ NO game logic  
❌ NO state modification  

### Controller Responsibilities
✅ Handle input  
✅ Update models  
✅ Trigger rendering  
✅ Collision detection  
✅ State transitions  

## 🚀 Quick Commands

**Run game:**
```bash
python controller.py
```

**Check line counts:**
```bash
# PowerShell
Get-ChildItem *.py | ForEach-Object { 
    [PSCustomObject]@{
        File = $_.Name
        Lines = (Get-Content $_ | Measure-Object -Line).Lines
    }
}
```

**Find a class:**
```bash
# PowerShell
Select-String "class YourClass" *.py
```

**Find a function:**
```bash
# PowerShell
Select-String "def your_function" *.py
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `MVC_ARCHITECTURE.md` | Full architecture guide |
| `REFACTORING_SUMMARY.md` | What changed and why |
| `QUICKSTART.md` | How to play |
| `README.md` | Game description |
| `BALANCE_CHANGES.md` | Gameplay tuning |

## 🎓 Learning Resources

**Concepts demonstrated:**
- Model-View-Controller pattern
- Separation of concerns
- Type hints and documentation
- Sprite caching optimization
- State machine pattern
- Component-based entities
- Async game loops

**Perfect for:**
- Portfolio projects
- Code reviews
- Job interviews
- Teaching examples
- Best practices reference

## 🐛 Debugging Tips

**Game logic bug?** → Check `models.py`  
**Visual bug?** → Check `views.py`  
**Input not working?** → Check `controller.py` event handlers  
**Enemies stuck?** → Check `pathfinding.py`  
**Performance issue?** → Profile each module separately  

## ✨ Best Practices

1. **Add to models first** - Define what it IS
2. **Update views if needed** - Define how it LOOKS
3. **Wire in controller** - Define how it BEHAVES
4. **Test incrementally** - One change at a time
5. **Comment everything** - Explain WHY, not just WHAT

## 🎊 Success!

You now have:
- ✅ Clean MVC architecture
- ✅ Every function documented
- ✅ Type hints throughout
- ✅ Separated concerns
- ✅ Maintainable codebase
- ✅ Professional structure

**Time to code**: Much faster to find things!  
**Time to understand**: Much easier to read!  
**Time to extend**: Much simpler to add features!  

---

**Quick Start**: `python controller.py`  
**Full Docs**: Read `MVC_ARCHITECTURE.md`  
**Summary**: Read `REFACTORING_SUMMARY.md`  

**Happy Coding! 🚀**
