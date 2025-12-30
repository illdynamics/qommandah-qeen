import os
import sys
import json
import importlib
import pygame
from pathlib import Path

def count_total_briqs():
    """Count total briq files created across all cycles."""
    briq_count = 0
    for root, dirs, files in os.walk("qodeyard"):
        for file in files:
            if file.endswith(".md"):
                briq_count += 1
    return briq_count

def verify_imports():
    """Verify all import statements work correctly."""
    import_errors = []
    
    # Test core imports
    try:
        from core.engine import Engine
    except ImportError as e:
        import_errors.append(f"core.engine: {e}")
    
    try:
        from core.scene import Scene
    except ImportError as e:
        import_errors.append(f"core.scene: {e}")
    
    try:
        from core.resources import ResourceManager
    except ImportError as e:
        import_errors.append(f"core.resources: {e}")
    
    try:
        from core.time import Time
    except ImportError as e:
        import_errors.append(f"core.time: {e}")
    
    try:
        from core.input import InputManager
    except ImportError as e:
        import_errors.append(f"core.input: {e}")
    
    try:
        from core.camera import Camera
    except ImportError as e:
        import_errors.append(f"core.camera: {e}")
    
    try:
        from core.particles import ParticleSystem
    except ImportError as e:
        import_errors.append(f"core.particles: {e}")
    
    # Test shared imports
    try:
        from shared.types import Vec2i, Rect, PlayerState, PowerupType
    except ImportError as e:
        import_errors.append(f"shared.types: {e}")
    
    try:
        from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT
    except ImportError as e:
        import_errors.append(f"shared.constants: {e}")
    
    # Test world imports
    try:
        from world.tiles import TileSet
    except ImportError as e:
        import_errors.append(f"world.tiles: {e}")
    
    try:
        from world.physics import PhysicsBody
    except ImportError as e:
        import_errors.append(f"world.physics: {e}")
    
    try:
        from world.collision import CollisionSystem
    except ImportError as e:
        import_errors.append(f"world.collision: {e}")
    
    try:
        from world.entities import Entity
    except ImportError as e:
        import_errors.append(f"world.entities: {e}")
    
    try:
        from world.level_loader import LevelLoader
    except ImportError as e:
        import_errors.append(f"world.level_loader: {e}")
    
    # Test actors imports
    try:
        from actors.player import Player
    except ImportError as e:
        import_errors.append(f"actors.player: {e}")
    
    try:
        from actors.player_states.base_state import BasePlayerState
    except ImportError as e:
        import_errors.append(f"actors.player_states.base_state: {e}")
    
    try:
        from actors.player_states.normal_state import NormalState
    except ImportError as e:
        import_errors.append(f"actors.player_states.normal_state: {e}")
    
    try:
        from actors.player_states.jumpupstiq_state import JumpUpStiqState
    except ImportError as e:
        import_errors.append(f"actors.player_states.jumpupstiq_state: {e}")
    
    try:
        from actors.player_states.jettpaq_state import JettpaqState
    except ImportError as e:
        import_errors.append(f"actors.player_states.jettpaq_state: {e}")
    
    try:
        from actors.smoke_overlay import SmokeOverlay
    except ImportError as e:
        import_errors.append(f"actors.smoke_overlay: {e}")
    
    try:
        from actors.projectile import Projectile
    except ImportError as e:
        import_errors.append(f"actors.projectile: {e}")
    
    try:
        from actors.enemies.base_enemy import BaseEnemy
    except ImportError as e:
        import_errors.append(f"actors.enemies.base_enemy: {e}")
    
    try:
        from actors.enemies.walqer_bot import WalqerBot
    except ImportError as e:
        import_errors.append(f"actors.enemies.walqer_bot: {e}")
    
    try:
        from actors.enemies.jumper_drqne import JumperDrqne
    except ImportError as e:
        import_errors.append(f"actors.enemies.jumper_drqne: {e}")
    
    try:
        from actors.enemies.qortana_halo import QortanaHalo
    except ImportError as e:
        import_errors.append(f"actors.enemies.qortana_halo: {e}")
    
    try:
        from actors.enemies.qlippy import Qlippy
    except ImportError as e:
        import_errors.append(f"actors.enemies.qlippy: {e}")
    
    try:
        from actors.enemies.briq_beaver import BriqBeaver
    except ImportError as e:
        import_errors.append(f"actors.enemies.briq_beaver: {e}")
    
    # Test objects imports
    try:
        from objects.collectible import Collectible
    except ImportError as e:
        import_errors.append(f"objects.collectible: {e}")
    
    try:
        from objects.hazard import Hazard
    except ImportError as e:
        import_errors.append(f"objects.hazard: {e}")
    
    try:
        from objects.jumpupstiq_pickup import JumpupstiqPickup
    except ImportError as e:
        import_errors.append(f"objects.jumpupstiq_pickup: {e}")
    
    try:
        from objects.jettpaq_pickup import JettpaqPickup
    except ImportError as e:
        import_errors.append(f"objects.jettpaq_pickup: {e}")
    
    try:
        from objects.powerup_pickup import PowerupPickup
    except ImportError as e:
        import_errors.append(f"objects.powerup_pickup: {e}")
    
    try:
        from objects.door import Door
    except ImportError as e:
        import_errors.append(f"objects.door: {e}")
    
    try:
        from objects.exit_zone import ExitZone
    except ImportError as e:
        import_errors.append(f"objects.exit_zone: {e}")
    
    # Test modes imports
    try:
        from modes.base_mode import BaseMode
    except ImportError as e:
        import_errors.append(f"modes.base_mode: {e}")
    
    try:
        from modes.registry import ModeRegistry
    except ImportError as e:
        import_errors.append(f"modes.registry: {e}")
    
    try:
        from modes.low_g_mode import LowGMode
    except ImportError as e:
        import_errors.append(f"modes.low_g_mode: {e}")
    
    try:
        from modes.glitch_mode import GlitchMode
    except ImportError as e:
        import_errors.append(f"modes.glitch_mode: {e}")
    
    try:
        from modes.mirror_mode import MirrorMode
    except ImportError as e:
        import_errors.append(f"modes.mirror_mode: {e}")
    
    try:
        from modes.bullet_time_mode import BulletTimeMode
    except ImportError as e:
        import_errors.append(f"modes.bullet_time_mode: {e}")
    
    try:
        from modes.speedy_boots_mode import SpeedyBootsMode
    except ImportError as e:
        import_errors.append(f"modes.speedy_boots_mode: {e}")
    
    try:
        from modes.junglist_mode import JunglistMode
    except ImportError as e:
        import_errors.append(f"modes.junglist_mode: {e}")
    
    # Test ui imports
    try:
        from ui.hud import HUD
    except ImportError as e:
        import_errors.append(f"ui.hud: {e}")
    
    try:
        from ui.main_menu import MainMenu
    except ImportError as e:
        import_errors.append(f"ui.main_menu: {e}")
    
    try:
        from ui.pause_menu import PauseMenu
    except ImportError as e:
        import_errors.append(f"ui.pause_menu: {e}")
    
    # Test scenes imports
    try:
        from scenes.menu_scene import MenuScene
    except ImportError as e:
        import_errors.append(f"scenes.menu_scene: {e}")
    
    try:
        from scenes.game_scene import GameScene
    except ImportError as e:
        import_errors.append(f"scenes.game_scene: {e}")
    
    return import_errors

def verify_activation_deactivation():
    """Verify mode activation/deactivation systems."""
    from modes.registry import ModeRegistry
    from modes.low_g_mode import LowGMode
    from modes.mirror_mode import MirrorMode
    
    registry = ModeRegistry()
    
    # Test mode registration
    low_g_mode = LowGMode()
    mirror_mode = MirrorMode()
    
    registry.register_mode(low_g_mode)
    registry.register_mode(mirror_mode)
    
    # Test activation
    assert registry.activate_mode(low_g_mode.get_mode_type()) == True
    assert low_g_mode.is_active() == True
    
    # Test deactivation
    assert registry.deactivate_mode(low_g_mode.get_mode_type()) == True
    assert low_g_mode.is_active() == False
    
    # Test toggle
    assert registry.toggle_mode(mirror_mode.get_mode_type()) == True
    assert mirror_mode.is_active() == True
    assert registry.toggle_mode(mirror_mode.get_mode_type()) == False
    assert mirror_mode.is_active() == False
    
    return True

def test_game_build():
    """Test the game build process."""
    # Check if main.py exists
    if not os.path.exists("qodeyard/main.py"):
        return False, "main.py not found"
    
    # Check if requirements.txt exists
    if not os.path.exists("qodeyard/requirements.txt"):
        return False, "requirements.txt not found"
    
    # Check if README.md exists
    if not os.path.exists("qodeyard/README.md"):
        return False, "README.md not found"
    
    # Check if all required directories exist
    required_dirs = [
        "qodeyard/core",
        "qodeyard/shared",
        "qodeyard/world",
        "qodeyard/actors",
        "qodeyard/actors/player_states",
        "qodeyard/actors/enemies",
        "qodeyard/objects",
        "qodeyard/modes",
        "qodeyard/ui",
        "qodeyard/scenes",
        "qodeyard/levels"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            return False, f"Directory not found: {dir_path}"
    
    return True, "Game build structure is valid"

def verify_file_structure():
    """Verify the complete file structure."""
    required_files = [
        # Core files
        "qodeyard/core/__init__.py",
        "qodeyard/core/engine.py",
        "qodeyard/core/scene.py",
        "qodeyard/core/resources.py",
        "qodeyard/core/time.py",
        "qodeyard/core/input.py",
        "qodeyard/core/camera.py",
        "qodeyard/core/particles.py",
        
        # Shared files
        "qodeyard/shared/__init__.py",
        "qodeyard/shared/constants.py",
        "qodeyard/shared/types.py",
        "qodeyard/shared/exceptions.py",
        "qodeyard/shared/sprite_data.py",
        "qodeyard/shared/powerup.py",
        "qodeyard/shared/wonqmode_data.py",
        "qodeyard/shared/smoke_overlay.py",
        
        # World files
        "qodeyard/world/__init__.py",
        "qodeyard/world/tiles.py",
        "qodeyard/world/physics.py",
        "qodeyard/world/collision.py",
        "qodeyard/world/entities.py",
        "qodeyard/world/level_loader.py",
        
        # Actors files
        "qodeyard/actors/__init__.py",
        "qodeyard/actors/player.py",
        "qodeyard/actors/smoke_overlay.py",
        "qodeyard/actors/projectile.py",
        
        # Player states
        "qodeyard/actors/player_states/__init__.py",
        "qodeyard/actors/player_states/base_state.py",
        "qodeyard/actors/player_states/normal_state.py",
        "qodeyard/actors/player_states/jumpupstiq_state.py",
        "qodeyard/actors/player_states/jettpaq_state.py",
        
        # Enemies
        "qodeyard/actors/enemies/__init__.py",
        "qodeyard/actors/enemies/base_enemy.py",
        "qodeyard/actors/enemies/walqer_bot.py",
        "qodeyard/actors/enemies/jumper_drqne.py",
        "qodeyard/actors/enemies/qortana_halo.py",
        "qodeyard/actors/enemies/qlippy.py",
        "qodeyard/actors/enemies/briq_beaver.py",
        
        # Objects
        "qodeyard/objects/__init__.py",
        "qodeyard/objects/collectible.py",
        "qodeyard/objects/hazard.py",
        "qodeyard/objects/jumpupstiq_pickup.py",
        "qodeyard/objects/jettpaq_pickup.py",
        "qodeyard/objects/powerup_pickup.py",
        "qodeyard/objects/door.py",
        "qodeyard/objects/exit_zone.py",
        
        # Modes
        "qodeyard/modes/__init__.py",
        "qodeyard/modes/base_mode.py",
        "qodeyard/modes/registry.py",
        "qodeyard/modes/low_g_mode.py",
        "qodeyard/modes/glitch_mode.py",
        "qodeyard/modes/mirror_mode.py",
        "qodeyard/modes/bullet_time_mode.py",
        "qodeyard/modes/speedy_boots_mode.py",
        "qodeyard/modes/junglist_mode.py",
        
        # UI
        "qodeyard/ui/__init__.py",
        "qodeyard/ui/hud.py",
        "qodeyard/ui/main_menu.py",
        "qodeyard/ui/pause_menu.py",
        
        # Scenes
        "qodeyard/scenes/__init__.py",
        "qodeyard/scenes/menu_scene.py",
        "qodeyard/scenes/game_scene.py",
        
        # Levels
        "qodeyard/levels/level01.json",
        "qodeyard/levels/level03.json",
        
        # Main files
        "qodeyard/main.py",
        "qodeyard/requirements.txt",
        "qodeyard/README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_files

def main():
    """Run all verification tests."""
    print("=== Running Verification Tests ===")
    
    # Test 1: Count briqs
    print("\n1. Counting briq files...")
    briq_count = count_total_briqs()
    print(f"   Total briq files: {briq_count}")
    
    # Test 2: Verify imports
    print("\n2. Verifying imports...")
    import_errors = verify_imports()
    if import_errors:
        print(f"   Found {len(import_errors)} import errors:")
        for error in import_errors:
            print(f"   - {error}")
    else:
        print("   All imports successful!")
    
    # Test 3: Verify mode activation/deactivation
    print("\n3. Testing mode activation/deactivation...")
    try:
        mode_test_result = verify_activation_deactivation()
        print("   Mode system working correctly!")
    except Exception as e:
        print(f"   Mode system test failed: {e}")
        mode_test_result = False
    
    # Test 4: Test game build
    print("\n4. Testing game build...")
    build_success, build_message = test_game_build()
    if build_success:
        print(f"   {build_message}")
    else:
        print(f"   Build test failed: {build_message}")
    
    # Test 5: Verify file structure
    print("\n5. Verifying file structure...")
    missing_files = verify_file_structure()
    if missing_files:
        print(f"   Found {len(missing_files)} missing files:")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print("   All required files present!")
    
    # Summary
    print("\n=== Verification Summary ===")
    print(f"Briq files: {briq_count}")
    print(f"Import errors: {len(import_errors)}")
    print(f"Mode system: {'PASS' if mode_test_result else 'FAIL'}")
    print(f"Build structure: {'PASS' if build_success else 'FAIL'}")
    print(f"Missing files: {len(missing_files)}")
    
    if not import_errors and mode_test_result and build_success and not missing_files:
        print("\n✅ All verification tests passed!")
        return True
    else:
        print("\n❌ Some verification tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)