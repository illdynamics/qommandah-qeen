import os
import sys
import json
import importlib
import pygame
from pathlib import Path

def count_total_briqs():
    """Count total briq files created across all cycles."""
    briq_count = 0
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".md") and "briq" in file.lower():
                briq_count += 1
    print(f"Total briq files: {briq_count}")
    return briq_count

def verify_imports():
    """Verify all import statements work correctly."""
    modules_to_test = [
        "core.engine",
        "core.scene",
        "core.resources",
        "core.time",
        "core.input",
        "core.camera",
        "core.particles",
        "world.tiles",
        "world.physics",
        "world.collision",
        "world.entities",
        "world.level_loader",
        "actors.player",
        "actors.player_states.base_state",
        "actors.player_states.normal_state",
        "actors.player_states.jumpupstiq_state",
        "actors.player_states.jettpaq_state",
        "actors.smoke_overlay",
        "actors.projectile",
        "actors.enemies.base_enemy",
        "actors.enemies.walqer_bot",
        "actors.enemies.jumper_drqne",
        "actors.enemies.qortana_halo",
        "actors.enemies.qlippy",
        "actors.enemies.briq_beaver",
        "objects.collectible",
        "objects.hazard",
        "objects.jumpupstiq_pickup",
        "objects.jettpaq_pickup",
        "objects.powerup_pickup",
        "objects.door",
        "objects.exit_zone",
        "modes.base_mode",
        "modes.registry",
        "modes.low_g_mode",
        "modes.glitch_mode",
        "modes.mirror_mode",
        "modes.bullet_time_mode",
        "modes.speedy_boots_mode",
        "modes.junglist_mode",
        "ui.hud",
        "ui.main_menu",
        "ui.pause_menu",
        "scenes.menu_scene",
        "scenes.game_scene",
        "shared.constants",
        "shared.types",
        "shared.exceptions",
        "shared.sprite_data",
        "shared.powerup",
        "shared.wonqmode_data"
    ]
    
    errors = []
    for module_path in modules_to_test:
        try:
            importlib.import_module(module_path)
            print(f"✓ {module_path}")
        except ImportError as e:
            errors.append(f"✗ {module_path}: {e}")
            print(f"✗ {module_path}: {e}")
    
    if errors:
        print(f"\nImport verification failed with {len(errors)} errors")
        return False
    else:
        print("\nAll imports verified successfully")
        return True

def verify_activation_deactivation():
    """Verify mode activation/deactivation systems."""
    try:
        from modes.registry import ModeRegistry
        from modes.base_mode import BaseMode
        from shared.wonqmode_data import WoNQModeType, WoNQModeConfig
        
        # Create test registry
        registry = ModeRegistry()
        
        # Test mode registration
        test_mode_type = WoNQModeType.LOW_G
        test_config = WoNQModeConfig(
            mode_type=test_mode_type,
            name="Test Mode",
            description="Test mode for verification",
            duration=10.0,
            cooldown=5.0,
            priority=1
        )
        
        # Create a mock mode
        class TestMode(BaseMode):
            def __init__(self):
                super().__init__(test_mode_type, test_config)
            
            def _on_start(self):
                pass
            
            def _on_stop(self):
                pass
        
        test_mode = TestMode()
        registry.register_mode(test_mode)
        
        # Test activation
        if not registry.activate_mode(test_mode_type):
            raise AssertionError("Failed to activate mode")
        
        if not registry.is_mode_active(test_mode_type):
            raise AssertionError("Mode not marked as active after activation")
        
        # Test deactivation
        if not registry.deactivate_mode(test_mode_type):
            raise AssertionError("Failed to deactivate mode")
        
        if registry.is_mode_active(test_mode_type):
            raise AssertionError("Mode still marked as active after deactivation")
        
        # Test toggle
        registry.toggle_mode(test_mode_type)
        if not registry.is_mode_active(test_mode_type):
            raise AssertionError("Toggle didn't activate mode")
        
        registry.toggle_mode(test_mode_type)
        if registry.is_mode_active(test_mode_type):
            raise AssertionError("Toggle didn't deactivate mode")
        
        # Test player state interaction
        from actors.player import Player
        from actors.player_states.normal_state import NormalState
        from actors.player_states.jumpupstiq_state import JumpUpStiqState
        from actors.player_states.jettpaq_state import JettpaqState
        
        # Create mock player
        player = Player(0, 0)
        
        # Test state transitions with mode activation
        player.change_state(NormalState)
        if not isinstance(player.current_state, NormalState):
            raise AssertionError("Player not in normal state")
        
        # Test powerup state activation
        player.change_state(JumpUpStiqState)
        if not isinstance(player.current_state, JumpUpStiqState):
            raise AssertionError("Player not in jumpupstiq state")
        
        # Test mode application to player
        registry.activate_mode(test_mode_type)
        registry.apply_modes_to_player(player)
        
        # Test powerup expiration
        player.change_state(NormalState)
        if not isinstance(player.current_state, NormalState):
            raise AssertionError("Player not returned to normal state")
        
        # Clean up
        registry.clear_all_modes()
        
        print("✓ Mode activation/deactivation verification passed")
        return True
        
    except Exception as e:
        print(f"✗ Mode activation/deactivation verification failed: {e}")
        return False

def test_game_build():
    """Test the game build process."""
    try:
        # Test that main.py can be imported
        import main
        
        # Test that requirements are met
        import pygame
        
        # Test that shared modules exist
        from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Test that core modules can be instantiated
        from core.engine import Engine
        from core.time import Time
        from core.resources import ResourceManager
        
        # Test singleton patterns
        time1 = Time()
        time2 = Time()
        if time1 is not time2:
            raise AssertionError("Time is not a singleton")
        
        res1 = ResourceManager()
        res2 = ResourceManager()
        if res1 is not res2:
            raise AssertionError("ResourceManager is not a singleton")
        
        print("✓ Game build test passed")
        return True
        
    except Exception as e:
        print(f"✗ Game build test failed: {e}")
        return False

def verify_file_structure():
    """Verify the complete file structure."""
    required_dirs = [
        "core",
        "world",
        "actors",
        "actors/player_states",
        "actors/enemies",
        "objects",
        "modes",
        "ui",
        "scenes",
        "shared",
        "levels"
    ]
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "core/__init__.py",
        "core/engine.py",
        "core/scene.py",
        "core/resources.py",
        "core/time.py",
        "core/input.py",
        "core/camera.py",
        "core/particles.py",
        "world/__init__.py",
        "world/tiles.py",
        "world/physics.py",
        "world/collision.py",
        "world/entities.py",
        "world/level_loader.py",
        "actors/__init__.py",
        "actors/player.py",
        "actors/smoke_overlay.py",
        "actors/projectile.py",
        "actors/player_states/__init__.py",
        "actors/player_states/base_state.py",
        "actors/player_states/normal_state.py",
        "actors/player_states/jumpupstiq_state.py",
        "actors/player_states/jettpaq_state.py",
        "actors/enemies/__init__.py",
        "actors/enemies/base_enemy.py",
        "actors/enemies/walqer_bot.py",
        "actors/enemies/jumper_drqne.py",
        "actors/enemies/qortana_halo.py",
        "actors/enemies/qlippy.py",
        "actors/enemies/briq_beaver.py",
        "objects/__init__.py",
        "objects/collectible.py",
        "objects/hazard.py",
        "objects/jumpupstiq_pickup.py",
        "objects/jettpaq_pickup.py",
        "objects/powerup_pickup.py",
        "objects/door.py",
        "objects/exit_zone.py",
        "modes/__init__.py",
        "modes/base_mode.py",
        "modes/registry.py",
        "modes/low_g_mode.py",
        "modes/glitch_mode.py",
        "modes/mirror_mode.py",
        "modes/bullet_time_mode.py",
        "modes/speedy_boots_mode.py",
        "modes/junglist_mode.py",
        "ui/__init__.py",
        "ui/hud.py",
        "ui/main_menu.py",
        "ui/pause_menu.py",
        "scenes/__init__.py",
        "scenes/menu_scene.py",
        "scenes/game_scene.py",
        "shared/__init__.py",
        "shared/constants.py",
        "shared/types.py",
        "shared/exceptions.py",
        "shared/sprite_data.py",
        "shared/powerup.py",
        "shared/wonqmode_data.py",
        "levels/level01.json",
        "levels/level03.json"
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if not os.path.isdir(directory):
            missing_dirs.append(directory)
    
    missing_files = []
    for file_path in required_files:
        if not os.path.isfile(file_path):
            missing_files.append(file_path)
    
    if missing_dirs:
        print("Missing directories:")
        for dir_path in missing_dirs:
            print(f"  ✗ {dir_path}")
    
    if missing_files:
        print("Missing files:")
        for file_path in missing_files:
            print(f"  ✗ {file_path}")
    
    if not missing_dirs and not missing_files:
        print("✓ File structure verification passed")
        return True
    else:
        print(f"\nFile structure verification failed: {len(missing_dirs)} missing directories, {len(missing_files)} missing files")
        return False

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Running Cyqle 1 Verification Tests")
    print("=" * 60)
    
    results = []
    
    print("\n1. Counting briq files...")
    briq_count = count_total_briqs()
    results.append(("Briq Count", briq_count > 0, f"Found {briq_count} briq files"))
    
    print("\n2. Verifying imports...")
    import_result = verify_imports()
    results.append(("Import Verification", import_result, ""))
    
    print("\n3. Verifying mode activation/deactivation...")
    mode_result = verify_activation_deactivation()
    results.append(("Mode System", mode_result, ""))
    
    print("\n4. Testing game build...")
    build_result = test_game_build()
    results.append(("Game Build", build_result, ""))
    
    print("\n5. Verifying file structure...")
    file_result = verify_file_structure()
    results.append(("File Structure", file_result, ""))
    
    print("\n" + "=" * 60)
    print("Verification Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed, message in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        if message:
            print(f"{status}: {test_name} - {message}")
        else:
            print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED! Game is ready for deployment.")
        return 0
    else:
        print("SOME TESTS FAILED. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())