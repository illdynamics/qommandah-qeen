#!/usr/bin/env python3
"""
QommandahQeen MAQZIMUM v0.5.4-alpha
A Commander Keen-inspired platformer with QonQrete aesthetics.

CONTROLS:
- Arrow Keys / WASD: Move
- Z / Up / W: Jump  
- X / Ctrl: Shoot
- SPACE: Interact (open doors with key)
- ENTER / E: Mount/Unmount powerups (JumpUpstiq, JettPaq)
- ESC / P: Pause
- F11: Fullscreen

HOW TO USE POWERUPS:
- JumpUpstiq (red pogo): Stand on it and press ENTER to mount
  - Press ENTER again to unmount (drops it where you stand)
  - Double jump height when mounted!
- JettPaq (blue jetpack): Walk into it to auto-equip (timed powerup)

DOORS & KEYS:
- Pick up the key by walking into it
- Stand at the door and press SPACE to unlock and enter
- Door plays opening animation then transitions to next room

v0.5.4-alpha Changelog:
- NEW CONTROL SCHEME: SPACE=Interact, ENTER=Mount/Unmount powerups
- JumpUpstiq requires ENTER to mount (no auto-pickup)
- Doors use key system with unlock animation
- Level 1: key next to door, wall barrier on right
"""

import sys
import os

# Add current directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from core.engine import Engine
from ui.main_menu import MainMenu


def initialize_game() -> Engine:
    """Initialize and launch the game."""
    # Create engine - starts windowed, can toggle fullscreen in options
    engine = Engine(
        title="QommandahQeen MAQZIMUM", 
        width=1280, 
        height=720, 
        target_fps=60, 
        fullscreen=False
    )
    
    # Create and set initial scene (Main Menu)
    menu_scene = MainMenu(engine)
    engine.set_scene(menu_scene)
    
    return engine


def run_game() -> None:
    """Main game loop."""
    try:
        engine = initialize_game()
        engine.run()
    except Exception as e:
        print(f"Game crashed with error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    run_game()
