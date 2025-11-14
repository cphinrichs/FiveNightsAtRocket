# Sound Effects Implementation Guide

## Overview
Sound effects have been fully integrated into Nine to Five at Rocket. The game will work perfectly without audio files, but will play sounds when the appropriate .wav files are placed in the `audio/` folder.

## Sound Effects Added

### 1. **Jumpscare Sound** (`jumpscare.wav`)
- **When:** Enemy catches and kills the player
- **Volume:** 150% (intentionally loud for impact)
- **Location in code:** `trigger_jumpscare()` method

### 2. **Camera Sounds**
- **camera_open.wav** - When pressing E on camera or number key
- **camera_close.wav** - When closing camera with ESC or E
- **camera_switch.wav** - When switching between camera feeds (1-4 keys)
- **Volume:** 50% (default)
- **Location in code:** `switch_state()` and `update_camera()` methods

### 3. **Warning Sound** (`warning.wav`)
- **When:** Bandwidth drops below 20% while using cameras
- **Volume:** 50%
- **Behavior:** Only plays once when crossing the 20% threshold
- **Location in code:** `update_camera()` method

### 4. **Interaction Sounds**
- **pickup.wav** - Taking an egg from refrigerator
- **restock.wav** - Restocking snacks from cabinet
- **interact.wav** - Generic interaction (backup)
- **Volume:** 50%
- **Location in code:** `interactable.py` `interact()` method

### 5. **Movement Sounds**
- **footsteps.wav** - Plays every 0.4 seconds while moving
  - Volume: 20% (subtle, not annoying)
  - Location: `update_playing()` method
- **door_open.wav** - When walking through doorways
  - Volume: 30% (subtle)
  - Location: `check_door_transitions()` method

## Implementation Details

### Sound Loading
All sounds are loaded in `load_sound_effects()` method at game initialization:
- Tries relative path first (for pygbag deployment)
- Falls back to absolute path (for desktop)
- Gracefully handles missing files
- Reports which sounds loaded successfully

### Playing Sounds
Use the `play_sound()` method:
```python
self.play_sound('sound_name', volume=1.0)
```
- `sound_name`: Name of the sound effect
- `volume`: Optional multiplier (1.0 = default, 1.5 = 150%, 0.2 = 20%)

### Volume Control
Default volumes set in `load_sound_effects()`:
- All SFX: 50% base volume
- Can be temporarily adjusted per-play with volume parameter
- Background music: 70%

## File Requirements

### Background Music
- **File:** `dnd_background_music.mp3`
- **Format:** MP3, OGG, or WAV
- **Behavior:** Loops continuously during gameplay

### Sound Effects
All should be `.wav` format for best compatibility:
- jumpscare.wav
- camera_open.wav
- camera_close.wav
- camera_switch.wav
- warning.wav
- interact.wav
- pickup.wav
- restock.wav
- footsteps.wav
- door_open.wav

## Testing Checklist

Test each sound by:
- [ ] Jumpscare - Get caught by an enemy
- [ ] Camera open - Press E on camera or number key
- [ ] Camera close - Press ESC while in camera
- [ ] Camera switch - Press 1, 2, 3, or 4 in camera view
- [ ] Warning - Use camera until bandwidth drops below 20%
- [ ] Pickup - Take egg from refrigerator
- [ ] Restock - Get snacks from cabinet
- [ ] Interact - (Generic, rare to trigger)
- [ ] Footsteps - Walk around (should play every 0.4 seconds)
- [ ] Door - Walk through any doorway

## Adding New Sound Effects

To add a new sound effect:

1. Add the filename to `sound_files` dict in `load_sound_effects()`:
```python
'new_sound': 'new_sound.wav',
```

2. Place the .wav file in the `audio/` folder

3. Call it where needed:
```python
self.play_sound('new_sound', volume=0.5)
```

## Troubleshooting

**No sounds playing:**
- Check if .wav files are in `audio/` folder
- Check console output for "Loaded: X" messages
- Verify pygame.mixer initialized (should see mixer frequency in debug output)
- Check Windows volume mixer

**Sounds too loud/quiet:**
- Adjust volume parameter in `play_sound()` calls
- Adjust base volume in `load_sound_effects()` (sound.set_volume())
- For music, adjust in `load_background_music()` (pygame.mixer.music.set_volume())

**Sounds cutting off:**
- May need to increase pygame mixer channels
- Add `pygame.mixer.set_num_channels(16)` after mixer.init()

## Future Enhancements

Possible additions:
- Enemy-specific sounds (footsteps, breathing)
- Ambient office sounds
- UI click sounds for menu
- Victory/defeat music stings
- Laptop typing sounds
- Tension music when enemy is near
