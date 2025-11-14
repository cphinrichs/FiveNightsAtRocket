# API Integration Guide for Game Hosting

## Overview
This guide explains how to serve the pygbag-built game through the Flask API backend.

## Architecture

```
Frontend (Browser)
    ↓
Flask API Server (/game endpoint)
    ↓
Pygbag Built Game Files
```

## Setup Steps

### 1. Build the Game

First, build the game using pygbag:

```bash
cd src/game
python -m pygbag --build main.py
```

This creates a `build/web/` directory with all the necessary files.

### 2. Update Flask API

Add game serving routes to `src/api/api.py`:

```python
from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)

# Path to the built game files
GAME_BUILD_DIR = os.path.join(os.path.dirname(__file__), '..', 'game', 'build', 'web')

@app.route('/game')
def serve_game():
    """Serve the main game page"""
    # Serve the index.html or use a custom template
    return send_from_directory(GAME_BUILD_DIR, 'index.html')

@app.route('/game/<path:filename>')
def serve_game_assets(filename):
    """Serve game assets (JS, WASM, images, etc.)"""
    return send_from_directory(GAME_BUILD_DIR, filename)

# CORS headers for web deployment
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    # Important for WASM
    response.headers.add('Cross-Origin-Embedder-Policy', 'require-corp')
    response.headers.add('Cross-Origin-Opener-Policy', 'same-origin')
    return response
```

### 3. Alternative: Use Custom HTML Template

If you want a custom landing page:

```python
from flask import render_template

@app.route('/game')
def serve_game():
    """Serve custom game page"""
    return render_template('game.html')
```

Create `src/api/templates/game.html`:
- Copy contents from `src/game/game_template.html`
- Adjust paths to point to `/game/<file>`

### 4. Directory Structure

```
src/
├── api/
│   ├── api.py              # Flask backend with /game routes
│   ├── templates/
│   │   └── game.html       # Optional custom template
│   └── static/
│       └── game/           # Optional: copy build files here
└── game/
    ├── main.py             # Game source
    ├── build/
    │   └── web/            # Pygbag output
    │       ├── index.html
    │       ├── main.py.js
    │       ├── main.py.wasm
    │       └── images/     # Game assets
    └── images/             # Source images
```

## Deployment Options

### Option 1: Direct Build Directory Serving (Development)

```python
# Point directly to build directory
GAME_BUILD_DIR = '../game/build/web'
```

Pros:
- Simple setup
- Fast iteration during development

Cons:
- Requires relative paths
- Build directory must exist

### Option 2: Copy to Static Directory (Production)

```bash
# After building
cp -r src/game/build/web/* src/api/static/game/
```

```python
# Serve from Flask static directory
GAME_BUILD_DIR = os.path.join(app.static_folder, 'game')
```

Pros:
- Self-contained deployment
- Works with standard Flask structure

Cons:
- Must copy files after each build
- Duplicates files

### Option 3: Separate Static Server (Scalable)

Serve game files from a CDN or separate static file server:

```python
# Redirect to external game host
@app.route('/game')
def serve_game():
    return redirect('https://cdn.example.com/game/')
```

Pros:
- Better performance
- Separate concerns
- CDN benefits

Cons:
- More complex setup
- Additional infrastructure

## Environment Configuration

Create `.env` file:

```env
# Game serving configuration
GAME_BUILD_DIR=/path/to/game/build/web
GAME_ENABLED=true
DEBUG=false
```

Load in Flask:

```python
from dotenv import load_dotenv
import os

load_dotenv()

GAME_BUILD_DIR = os.getenv('GAME_BUILD_DIR', '../game/build/web')
GAME_ENABLED = os.getenv('GAME_ENABLED', 'true').lower() == 'true'
```

## Testing

### 1. Local Testing

Start Flask server:
```bash
cd src/api
python api.py
```

Access game:
```
http://localhost:5000/game
```

### 2. Production Testing

Build and deploy:
```bash
# Build game
cd src/game
python -m pygbag --build main.py

# Copy to API static (if using Option 2)
cp -r build/web/* ../api/static/game/

# Start API
cd ../api
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

## Performance Optimization

### 1. Enable Gzip Compression

```python
from flask_compress import Compress

app = Flask(__name__)
Compress(app)
```

### 2. Cache Headers

```python
@app.route('/game/<path:filename>')
def serve_game_assets(filename):
    response = send_from_directory(GAME_BUILD_DIR, filename)
    # Cache static assets for 1 hour
    response.cache_control.max_age = 3600
    return response
```

### 3. Preload Critical Assets

In the HTML template:
```html
<link rel="preload" href="/game/main.py.wasm" as="fetch" crossorigin>
<link rel="preload" href="/game/images/hallway.jpg" as="image">
```

## Troubleshooting

### Game doesn't load
- Check browser console for errors
- Verify CORS headers are set
- Ensure WASM files are served with correct MIME type

### 404 on assets
- Check GAME_BUILD_DIR path
- Verify files exist in build directory
- Check route patterns match file paths

### Slow loading
- Enable compression (gzip)
- Add cache headers
- Consider CDN for assets
- Optimize image sizes

### WASM errors
- Ensure Cross-Origin headers are set
- Check browser WASM support
- Verify .wasm files aren't corrupted

## Security Considerations

### 1. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/game')
@limiter.limit("10 per minute")
def serve_game():
    return send_from_directory(GAME_BUILD_DIR, 'index.html')
```

### 2. Authentication (Optional)

```python
from flask_login import login_required

@app.route('/game')
@login_required
def serve_game():
    return send_from_directory(GAME_BUILD_DIR, 'index.html')
```

### 3. Content Security Policy

```python
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:;"
    return response
```

## Monitoring

### Track Game Sessions

```python
import logging

@app.route('/game')
def serve_game():
    logging.info(f'Game accessed from {request.remote_addr}')
    return send_from_directory(GAME_BUILD_DIR, 'index.html')
```

### Analytics Integration

Add to game template:
```html
<script>
    // Google Analytics, Plausible, etc.
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'GA-TRACKING-ID');
</script>
```

## Resources

- Flask Documentation: https://flask.palletsprojects.com/
- Pygbag Docs: https://github.com/pygame-web/pygbag
- WASM Security: https://webassembly.org/docs/security/
