# Game Update Notes - Major Changes

## Summary of Latest Updates

### 🔧 Bug Fixes

1. **Fixed Pause/Unpause Issue**
   - ESC key now properly toggles pause state
   - Moved pause handling from continuous key check to KEYDOWN event
   - ESC in camera view now closes cameras
   - No more conflicts between different ESC key handlers

### 🚪 Room & Door System Overhaul

2. **Doorways Replace Doors**
   - Removed visible door objects
   - Doorways are now breaks/gaps in the walls
   - More natural flow between rooms
   - Cleaner visual appearance

3. **Updated Room Layout**
   - **Office** ← → **Hallway** ← → **Meeting Room**
   - **Office** ← → **Break Room**
   - **Hallway** ← → **Classroom**
   - All rooms are now properly adjacent to their connections

### 🏷️ UI Improvements

4. **Desk Labels**
   - Jeromathy's desk now displays "Jeromathy"
   - Angellica's desk now displays "Angellica"
   - Labels visible on interactable objects

### 🍕 Gameplay Balance

5. **Starting Snacks**
   - Players now start with **5 snacks** (was 0)
   - No immediate danger from Jeromathy at game start
   - Gives players breathing room to learn mechanics

### 👤 New Character: NextGen Intern

6. **NextGen Intern Added**
   - Appears as a green character
   - Mostly stays in the Classroom
   - **Special Behavior:** Randomly goes to Break Room every ~45 seconds
   - **Takes a snack** when visiting Break Room
   - Returns to Classroom after getting snack
   - Adds dynamic resource management challenge
   - Does NOT attack the player (harmless NPC)

## Character Roster

Now there are **4 characters** in the game:

1. **Jo-nathan** (Orange) - Chases player, pacified by eggs
2. **Jeromathy** (Blue) - Gets angry if snacks depleted
3. **Angellica** (Purple) - Attacks if you watch YouTube
4. **NextGen Intern** (Green) - Takes snacks periodically (NEW!)

## Room Layout

```
[Office]———[Hallway]———[Meeting Room]
   |            |
[Break Rm]  [Classroom]
```

### Room Connections:
- **Office** connects to: Hallway (right), Break Room (bottom)
- **Hallway** connects to: Office (left), Meeting Room (right), Classroom (bottom)
- **Meeting Room** connects to: Hallway (left)
- **Break Room** connects to: Office (top)
- **Classroom** connects to: Hallway (top)

## Strategic Implications

### Snack Management Now Critical!
- Start with 5 snacks
- NextGen Intern takes 1 snack per visit (~every 45 seconds)
- Jeromathy gets angry if snacks hit 0
- Must balance between:
  - Keeping stock for Jeromathy
  - Accounting for Intern's consumption
  - Timing visits to Break Room refrigerator

### New Strategy Tips:
1. **Monitor snack count carefully** - Intern adds pressure
2. **Restock proactively** - Don't wait until 0
3. **Keep 2-3 snacks minimum** - Buffer for Intern visits
4. **Use cameras** to track Intern's movements
5. **Time your Break Room visits** when Intern is in Classroom

## Technical Changes

### Code Architecture:
- Enhanced Room class with `add_walls_with_doorway()` method
- Proper wall segments with gaps for doorways
- Interactable objects support custom labels
- Event-based key handling for pause/unpause
- NextGenIntern class with pathfinding AI

### Visual Improvements:
- Desk labels show character names
- Cleaner room aesthetics
- Better visual flow between spaces

## Known Behaviors

- **NextGen Intern is NOT an enemy** - You won't die if you touch them
- Intern's snack visits are semi-random (45s average)
- Intern can move through rooms to reach Break Room
- If snacks are already 0, Intern's visit has no effect

---

**All features tested and working!** Enjoy the updated game! 🎮
