# Pygbag Deployment Guide

## Overview
This guide explains how to build and deploy the game using pygbag for web browser play.

## Prerequisites
- Python 3.9 or higher
- pygame 2.5.0+
- pygbag 0.8.7+

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Building for Web

### Option 1: Using Build Script (Recommended)

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

**Windows:**
```cmd
build.bat
```

### Option 2: Manual Build

```bash
cd src/game
python -m pygbag --build main.py
```

## Testing Locally

### Browser Test (Recommended)
```bash
cd src/game
python -m pygbag main.py
```
Then open the URL shown in your browser (usually http://localhost:8000)

### Desktop Test
```bash
cd src/game
python main.py
```

## Deployment

### Option 1: Deploy with Backend API

The game can be served through the Flask API backend:

1. Build the game:
```bash
cd src/game
python -m pygbag --build main.py
```

2. The built files will be in `build/web/` directory

3. Copy the built files to your API's static directory

4. Serve through your API endpoint

### Option 2: Deploy to Static Hosting

The game can be deployed to any static hosting service:

1. Build the game as above

2. Upload the contents of `build/web/` to:
   - GitHub Pages
   - Netlify
   - Vercel
   - Any static file host

3. Configure CORS headers if needed

## File Structure for Pygbag

```
src/game/
├── main.py              # Main entry point (must have async def main())
├── requirements.txt     # Python dependencies
├── .pygbag             # Pygbag configuration
├── images/             # Game assets (must be relative paths)
│   ├── hallway.jpg
│   ├── break_room.jpg
│   ├── office.jpg
│   └── classroom.jpg
└── *.py                # Other game modules
```

## Important Notes

### Async/Await
- The game already uses `asyncio` for pygbag compatibility
- Main loop includes `await asyncio.sleep(0)` for browser cooperation

### File Paths
- All image paths use relative paths first (pygbag compatible)
- Fallback to absolute paths for desktop compatibility
- Images must be in the `images/` subdirectory

### Browser Compatibility
- Works on Chrome, Firefox, Safari, Edge
- Requires WebAssembly support
- Mobile browsers supported (touch controls recommended)

### Performance
- Target 60 FPS maintained
- Optimized asset loading
- Efficient collision detection

## Troubleshooting

### Build fails
- Ensure Python 3.9+ is installed
- Check pygbag version: `pip show pygbag`
- Verify all imports are available

### Images don't load
- Check images are in `images/` folder
- Verify file names match (case-sensitive)
- Check browser console for errors

### Slow performance
- Check browser WebAssembly support
- Close other browser tabs
- Try desktop version for comparison

### Controls don't work
- Ensure browser window has focus
- Check for keyboard layout issues
- Try refreshing the page

## Integration with API

To integrate with the Flask backend:

1. Build the game
2. Configure API endpoint in `src/api/api.py` to serve static files
3. Point to the build directory
4. Set proper CORS headers

Example Flask route:
```python
from flask import send_from_directory

@app.route('/game')
def game():
    return send_from_directory('path/to/build/web', 'index.html')

@app.route('/game/<path:path>')
def game_static(path):
    return send_from_directory('path/to/build/web', path)
```

## Resources

- Pygbag Documentation: https://github.com/pygame-web/pygbag
- Pygame Documentation: https://www.pygame.org/docs/
- WebAssembly Info: https://webassembly.org/
