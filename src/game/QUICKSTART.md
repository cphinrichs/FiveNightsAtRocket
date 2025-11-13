# Quick Start Guide - Five Nights at Rocket

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install pygame pygbag
```

### Step 2: Run the Game
```bash
cd src/game
python main.py
```

### Step 3: Survive!
- Use WASD to move
- Press E to interact
- Survive from 9am to 5pm for 5 days

## 🎮 First Time Playing?

### Immediate Actions on Day 1:
1. **Get an egg** - Go to Break Room → Interact with cabinets (E)
2. **Stock up on snacks** - Interact with refrigerator (E)
3. **Check cameras** - Go to Meeting Room → Use camera system

### Essential Survival Tips:
- **Jo-nathan (orange)**: Always chasing you. Give him your egg to make him go away.
- **Jeromathy (blue)**: Keep snacks above 0 or he'll chase you.
- **Angellica (purple)**: Never watch YouTube when she's nearby!

### Controls Quick Reference:
```
WASD/Arrows - Move
E           - Interact
Y           - YouTube (at laptop)
C           - Coding (at laptop)
1-5         - Select camera view
ESC         - Pause/Close cameras
SPACE       - Menu selections
```

## 🌐 Deploy to Web Browser

### Option 1: Quick Build (Windows)
```bash
.\build.bat
```

### Option 2: Quick Build (Mac/Linux)
```bash
chmod +x build.sh
./build.sh
```

### Option 3: Manual Build
```bash
python -m pygbag --build main.py
# Then run:
python -m pygbag main.py
# Open browser to http://localhost:8000
```

## ⚡ Performance Tips

- The game runs at 60 FPS
- Resolution: 1280x720
- Use fullscreen for best experience
- Camera system intentionally drains battery - use wisely!

## 🆘 Troubleshooting

**Game won't start?**
- Make sure pygame is installed: `pip install pygame`
- Check Python version: Python 3.7+ required

**Can't build for web?**
- Install pygbag: `pip install pygbag`
- Make sure you're in the `src/game` directory

**Game too hard?**
- Use cameras to track enemies
- Plan your route before moving
- Keep resources stocked
- Remember: You only need to survive until 5pm!

**Game too easy?**
- Try speedrunning with YouTube
- Challenge: Beat all 5 days in minimum time
- See how fast you can collect all resources

## 📋 Checklist for Success

Daily routine:
- [ ] Get egg from cabinet (Break Room)
- [ ] Stock up on snacks (Break Room refrigerator)
- [ ] Check enemy positions (Meeting Room cameras)
- [ ] Work on coding project (Classroom laptop)
- [ ] Monitor battery level (shown in UI)
- [ ] Watch the clock (survive to 5:00 PM)

## 🎯 Win Condition

Complete all 5 days (Monday - Friday) from 9am to 5pm each day!

---

**Ready to survive? Launch the game and good luck!** 🚀
