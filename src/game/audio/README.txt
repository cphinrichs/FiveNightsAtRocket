AUDIO FILES FOR NINE TO FIVE AT ROCKET
=======================================

This folder contains all audio files for the game. Place your audio files here.

BACKGROUND MUSIC:
-----------------
• dnd_background_music.mp3 - Main background music (loops continuously)
  - Format: MP3, OGG, or WAV
  - Volume: Set to 70% by default
  - Plays when game starts, stops on game over

SOUND EFFECTS (all should be .mp3 format):
-------------------------------------------

JUMPSCARE & DANGER:
• jumpscare1.mp3, jumpscare2.mp3, jumpscare3.mp3, etc. - Multiple jumpscare sounds
  - The game will randomly select one when an enemy catches you
  - Supports up to 5 different jumpscare sounds (jumpscare1.mp3 through jumpscare5.mp3)
  - Volume: 150% (intentionally loud)
  - You can add as many as you want (1-5), the game will use what's available
• egg_taken1.mp3, egg_taken2.mp3, egg_taken3.mp3, etc. - Multiple egg taken sounds
  - The game will randomly select one when Jonathan takes your egg
  - Supports up to 5 different sounds (egg_taken1.mp3 through egg_taken5.mp3)
  - Volume: 120% (noticeable but not overwhelming)
  - You can add as many as you want (1-5), the game will use what's available
• snack_taken1.mp3, snack_taken2.mp3, snack_taken3.mp3, etc. - Multiple snack taken sounds
  - The game will randomly select one when a NextGen Intern takes a snack
  - Supports up to 5 different sounds (snack_taken1.mp3 through snack_taken5.mp3)
  - Volume: 100% (default)
  - You can add as many as you want (1-5), the game will use what's available
• warning.mp3 - Plays when bandwidth drops below 20%

CAMERA SYSTEM:
• camera_open.mp3 - Plays when opening camera view
• camera_close.mp3 - Plays when closing camera view
• camera_switch.mp3 - Plays when switching between camera feeds

INTERACTIONS:
• interact.mp3 - Generic interaction sound (backup for non-specific interactions)
• pickup.mp3 - Plays when picking up an egg from refrigerator
• restock.mp3 - Plays when restocking snacks from cabinet

MOVEMENT:
• footsteps.mp3 - Plays every 0.4 seconds while player is moving (quiet, 20% volume)
• door_open.mp3 - Plays when player walks through a door (quiet, 30% volume)

AUDIO SPECIFICATIONS:
---------------------
• Background Music: MP3, OGG, or WAV format
• Sound Effects: MP3 format (consistent with background music)
• Sample Rate: 44.1kHz recommended
• Bit Depth: 16-bit or higher

The game will work fine without audio files - it will simply skip sounds that are missing.

VOLUME LEVELS:
--------------
• Background Music: 70% (adjustable in main.py)
• Default SFX: 50%
• Jumpscare: 150% (intentionally loud)
• Egg Taken: 120% (noticeable)
• Snack Taken: 100% (normal)
• Footsteps: 20% (subtle)
• Door: 30% (subtle)

TO ADD YOUR OWN AUDIO:
----------------------
1. Place audio files in this folder with the exact names listed above
2. For background music, name it "dnd_background_music.mp3"
3. For sound effects, use .mp3 files with the names listed
4. Test in-game to ensure volume levels are appropriate
5. Adjust volumes in main.py if needed (look for play_sound() calls)

RECOMMENDED SOURCES:
--------------------
• freesound.org - Free sound effects
• incompetech.com - Royalty-free music
• opengameart.org - Game audio resources

Make sure you have rights to use any audio you add!
