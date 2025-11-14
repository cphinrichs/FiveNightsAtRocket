# Nine to Five at Rocket

A survival horror game where you must survive a full workday at Rocket Software from 9 AM to 5 PM while avoiding dangerous coworkers and managing your resources.

## 🎮 Game Overview

Navigate the office, manage your bandwidth, complete tasks, and survive until 5 PM! Balance between working, slacking, and avoiding enemies who patrol the office looking for you.

### Key Features
- **Three Game Modes**: Free Roam, Working, and Slacking
- **Resource Management**: Monitor bandwidth while using cameras or working
- **Enemy AI**: Each enemy has unique behaviors and attack patterns
- **Strategic Gameplay**: Choose when to work, slack, or explore
- **Time Management**: Time progresses differently based on your actions

## 🕹️ Controls

### Movement (Free Roam Mode)
- **WASD / Arrow Keys**: Move around the office
- **E**: Interact with objects
- **W**: Enter Working mode (in Meeting Room)
- **S**: Enter Slacking mode (in Meeting Room)

### Working Mode
- **C**: Open security cameras
- **S**: Switch to Slacking mode
- **ESC**: Return to Free Roam

### Slacking Mode
- **W**: Switch to Working mode
- **ESC**: Return to Free Roam

### Camera View
- **1-4**: Switch between camera feeds
  - 1: Break Room
  - 2: Office
  - 3: Hallway
  - 4: Classroom
- **ESC / E**: Close cameras

### General
- **ESC**: Pause game (in Free Roam) / Return to Free Roam (from modes)

## 🏢 Office Layout

```
Break Room ←→ Office ←→ Hallway ←→ Classroom
                           ↓
                      Meeting Room
```

### Rooms
- **Meeting Room**: Your safe space - access Working and Slacking modes here
- **Office**: Contains Jeromathy's desk and resources
- **Hallway**: Central hub connecting multiple rooms; Angellica's desk is here
- **Classroom**: Jo-nathan's workspace with laptops and resources
- **Break Room**: Snack storage area

## 👻 Enemies

### Jo-nathan
- **Behavior**: Relentlessly chases the player
- **Activation**: After 30 seconds
- **Counter**: Feed him an egg to delay him for 10 seconds
- **Danger**: Always hostile, will kill on contact without an egg

### Jeromathy
- **Behavior**: Patrols the office, gets angry when snacks run out
- **Activation**: After 8 seconds
- **Trigger**: Snack counter reaches 0
- **Counter**: Keep snacks stocked from the Break Room
- **Danger**: Chases and kills when angry

### Angellica
- **Behavior**: Checks on you every 30 seconds
- **Activation**: After 10 seconds
- **Trigger**: Not in Working mode, using cameras, or in Free Roam when checked
- **Counter**: Stay in Working mode in the Meeting Room
- **Danger**: Chases and kills if you're not working

### Runnit
- **Behavior**: Randomly sprints through rooms at high speed
- **Activation**: After 20 seconds
- **Pattern**: Sprints for 3 seconds, then cooldown for 10 seconds
- **Danger**: Only dangerous when sprinting (fast-moving)

### NextGen Intern
- **Behavior**: Periodically travels to Break Room to steal snacks
- **Activation**: After 15 seconds (staggered for multiple interns)
- **Effect**: Reduces snack count by 1
- **Danger**: Harmless to player, but depletes resources

## 📦 Resources

### Snacks
- **Location**: Break Room refrigerator
- **Purpose**: Keep Jeromathy calm
- **Management**: Restock regularly to prevent depletion
- **Warning**: NextGen Interns will steal snacks

### Eggs
- **Location**: Classroom cabinet
- **Purpose**: Distract Jo-nathan temporarily
- **Capacity**: Hold 1 egg at a time
- **Duration**: Delays Jo-nathan for 10 seconds while he eats

### Bandwidth
- **Maximum**: 100%
- **Drain Rate**: 2%/second (cameras or working mode)
- **Refill Rate**: 0.5%/second (when idle in Free Roam)
- **Warning**: Game over if bandwidth reaches 0 while working

## 🎯 Game Modes Explained

### Free Roam Mode (PLAYING)
- Explore the office freely
- **Time**: Frozen (doesn't progress)
- **Bandwidth**: Slowly refills
- **Safety**: Vulnerable to enemy attacks
- **Use**: Gather resources, check enemy positions, navigate

### Working Mode
- Simulate working at your computer
- **Time**: Progresses at normal speed
- **Bandwidth**: Drains at 2%/second
- **Safety**: Safe from all enemies
- **Benefit**: Satisfies Angellica's checks
- **Access**: Camera view available

### Slacking Mode
- Take a break from work
- **Time**: Progresses at normal speed
- **Bandwidth**: Slowly refills
- **Safety**: Safe from all enemies
- **Risk**: Angellica will attack if she checks on you
- **Use**: Recover bandwidth without working

## 🎲 Strategy Tips

1. **Time Management**: Time only moves in Working/Slacking modes - use Free Roam to plan
2. **Bandwidth Conservation**: Don't stay in Working mode too long; alternate with Slacking
3. **Resource Routes**: Plan efficient paths to restock eggs and snacks
4. **Enemy Patterns**: Learn activation times and patrol routes
5. **Safe Timing**: Use Slacking mode strategically between Angellica's 30-second checks
6. **Visual Warnings**: Enemy indicators appear in Working/Slacking modes when they enter your room
7. **Sound Cues**: Listen for footsteps and audio warnings

## 🏆 Victory Condition

Survive from **9:00 AM to 5:00 PM** (8 in-game hours) without being caught by enemies or running out of bandwidth while working.

## 💀 Game Over Conditions

- Caught by Jo-nathan without an egg
- Caught by Jeromathy when angry (snacks depleted)
- Caught by Angellica while not working
- Caught by Runnit while he's sprinting
- Bandwidth reaches 0% while in Working mode

## 🛠️ Installation

### Requirements
- Python 3.8+
- Pygame

### Setup
```bash
# Clone the repository
git clone https://github.com/cphinrichs/FiveNightsAtRocket.git
cd FiveNightsAtRocket

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install pygame

# Run the game
python src/game/main.py
```

## 📁 Project Structure

```
FiveNightsAtRocket/
├── src/
│   ├── game/
│   │   ├── main.py           # Main game file
│   │   ├── enemies.py        # Enemy AI and behaviors
│   │   ├── entities.py       # Player and base entity classes
│   │   ├── room.py           # Room definitions
│   │   ├── interactable.py   # Interactive objects
│   │   ├── constants.py      # Game constants
│   │   ├── enums.py          # Enumerations
│   │   ├── sprites.py        # Sprite generation
│   │   ├── particles.py      # Particle effects
│   │   ├── ai_messages.py    # AI-generated messages
│   │   ├── images/           # Game images
│   │   ├── audio/            # Sound effects and music
│   │   └── sounds/           # Additional sounds
│   ├── api/                  # API integration
│   └── web/                  # Web interface
├── documentation/            # Game documentation
└── README.md
```

## 🎨 Credits

Developed by the Rocket Software team as a fun office-themed survival game.

### Technologies Used
- **Python**: Core game logic
- **Pygame**: Game engine and graphics
- **AI Generation**: Dynamic death messages

## 📝 License

See LICENSE file for details.

## 🐛 Known Issues

- Enemy pathfinding may occasionally get stuck on complex wall layouts
- Audio might not load in some environments (gracefully falls back to silent mode)

## 🔮 Future Improvements

- Additional enemy types
- More rooms and layout variations
- Difficulty levels
- Achievement system
- Save/load functionality
- Multiplayer mode

---

**Good luck surviving your workday at Rocket!** 🚀
