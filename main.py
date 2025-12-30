#!/usr/bin/env python3
"""
QommandahQeen MAQZIMUM v0.2.0-alpha
A Commander Keen-inspired platformer with QonQrete aesthetics.
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
