# Five Nights at Rocket

A survival strategy game where you must navigate an office building, avoid dangerous coworkers, and survive until 5pm for 5 consecutive days!

## 🎮 Game Overview

You play as **Brenton**, an office worker trying to make it through a work week at Rocket Software. But this isn't a normal office - dangerous coworkers roam the halls with their own unique behaviors and rules. Manage your resources, track enemies via security cameras, and survive from 9am to 5pm each day!

## 🕹️ Controls

### Movement
- **WASD** or **Arrow Keys** - Move Brenton around the office
- Navigate between connected rooms through doorways

### Actions
- **E** - Interact with objects (refrigerator, cabinets, camera system, laptop, etc.)
- **Y** (at laptop) - Watch YouTube (makes time pass faster, but Angellica will chase you!)
- **C** (at laptop) - Work on coding project (safe option)
- **1-5** (in camera mode) - Select different rooms to view
- **ESC** - Pause game / Close camera view
- **SPACE** - Select menu options / Restart after game over

## 🗺️ The Office Layout

The office consists of five connected rooms:

1. **Office** - Contains Jeromathy's desk. Starting location.
2. **Hallway** - Central hub connecting all rooms
3. **Break Room** - Has refrigerator (restock snacks) and cabinets (get eggs)
4. **Meeting Room** - Security camera monitoring system
5. **Classroom** - Laptop for coding work or YouTube

## 👾 The Enemies

### Jo-nathan 🟠
- **Behavior**: Constantly chases you throughout the office
- **Weakness**: Give him an egg to send him back to the classroom
- **Strategy**: Keep an egg in your inventory from the break room cabinet

### Jeromathy 🔵
- **Behavior**: Patrols the office and checks on his desk
- **Trigger**: If he sees snacks are depleted (0/5), he becomes angry and chases you
- **Strategy**: Keep snacks stocked by visiting the refrigerator in the break room

### Angellica 💜
- **Behavior**: Roams the office peacefully
- **Trigger**: If she catches you watching YouTube, she will chase and kill you
- **Strategy**: Only use the laptop for coding work, or watch YouTube briefly when she's far away

## ⚡ Game Mechanics

### Time Management
- Each day runs from **9:00 AM to 5:00 PM**
- Time passes slowly during normal activities
- **Watching YouTube makes time pass 3x faster** - risky but can help you survive!
- Survive all 5 days (Monday-Friday) to win

### Battery System
- Opening security cameras drains your battery at 15% per second
- Battery starts at 100% each day
- **If battery reaches 0%, you die!**
- Use cameras strategically to track enemy locations

### Inventory
- **Snacks (0-5)**: Keep stocked to prevent Jeromathy from getting angry
- **Egg (Yes/No)**: Use to pacify Jo-nathan and send him away

### Resources
- **Refrigerator** (Break Room): Restock snacks (+1 snack per use)
- **Cabinets** (Break Room): Get an egg (one at a time)

## 🎯 Strategy Tips

1. **Start each day by getting an egg** - Visit the break room cabinet immediately
2. **Keep snacks stocked** - Don't let them hit 0 or Jeromathy will hunt you
3. **Use cameras wisely** - Check enemy positions but watch your battery!
4. **Safe laptop usage** - Stick to coding work unless you know Angellica is far away
5. **Plan your routes** - Know where doorways connect rooms
6. **YouTube speedrun** - If you're skilled, use YouTube to make time pass faster
7. **Track the clock** - You only need to survive until 5:00 PM each day

## 🏆 Win Condition

Survive from 9am to 5pm for 5 consecutive days (Monday through Friday) to complete the game!

## 💀 Lose Conditions

You will die if:
- Any enemy catches you (except Jo-nathan if you have an egg)
- Your battery reaches 0%
- You fail to manage resources properly

## 🚀 Running the Game

### Local Development (Python)
```bash
# Install pygame
pip install pygame

# Run the game
python main.py
```

### Browser Version (pygbag)
```bash
# Install pygbag
pip install pygbag

# Build and serve
python -m pygbag --build main.py

# Then open browser to the local server address
```

The game is designed to be fully compatible with pygbag for browser deployment!

## 🎨 Features

- **Smooth movement and collision detection**
- **Particle effects** for visual feedback
- **Screen shake** on death
- **Dynamic camera system** with battery drain
- **Progressive difficulty** across 5 days
- **Polished UI** with real-time stats
- **Tutorial system** for new players
- **Multiple game states** (menu, playing, camera, paused, game over, victory)
- **Strategic gameplay** balancing risk and reward

## 🛠️ Technical Details

- Built with **Pygame**
- Async game loop for **pygbag compatibility**
- 1280x720 resolution at 60 FPS
- Modular class-based architecture
- Entity-component structure for game objects
- State machine for game flow management

## 📝 Credits

Created for the Five Nights at Rocket project - a fun take on office survival!

---

**Good luck surviving the week at Rocket Software!** 🚀
