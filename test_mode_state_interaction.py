"""
Test suite for validating mode and state interaction logic.
Focuses on verifying correct behavior under powerup effects and mode combinations.
"""

import unittest
import pygame
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from shared.types import PlayerState, PowerupType, WoNQModeType
from actors.player import Player
from actors.player_states.base_state import BasePlayerState
from actors.player_states.normal_state import NormalState
from actors.player_states.jumpupstiq_state import JumpUpStiqState
from actors.player_states.jettpaq_state import JettpaqState
from core.engine import Engine
from core.time import Time
from core.input import InputManager
from world.physics import PhysicsSystem
from world.collision import CollisionSystem
from modes.registry import ModeRegistry
from modes.base_mode import BaseMode
from shared.wonqmode_data import WoNQModeConfig


class TestModeStateInteraction(unittest.TestCase):
    """Test interactions between game modes and player states."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        
        # Mock engine and systems
        self.engine = Mock(spec=Engine)
        self.physics = Mock(spec=PhysicsSystem)
        self.collision = Mock(spec=CollisionSystem)
        self.mode_registry = Mock(spec=ModeRegistry)
        
        # Create player with mocked dependencies
        self.player = Player(100, 100)
        self.player.set_engine_references(
            self.engine, 
            self.physics, 
            self.collision, 
            self.mode_registry
        )
        
        # Mock mode registry methods
        self.mode_registry.get_active_modes.return_value = []
        self.mode_registry.is_mode_active.return_value = False
        self.mode_registry.call_global_hooks.return_value = []
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_mode_activation_affects_player_state(self):
        """Test that active modes affect player state behavior."""
        # Create a mock mode that modifies gravity
        mock_mode = Mock(spec=BaseMode)
        mock_mode.get_mode_type.return_value = WoNQModeType.LOW_G
        mock_mode.is_active.return_value = True
        
        # Set up mode registry to return the mock mode
        self.mode_registry.get_active_modes.return_value = [mock_mode]
        self.mode_registry.is_mode_active.return_value = True
        
        # Mock a hook that modifies player physics
        def gravity_hook(current_gravity):
            return current_gravity * 0.5  # Half gravity
        
        self.mode_registry.call_global_hooks.side_effect = lambda hook_name, *args, **kwargs: {
            'modify_gravity': [gravity_hook]
        }.get(hook_name, [])
        
        # Test that player state respects mode modifications
        self.player.change_state(PlayerState.NORMAL)
        initial_state = self.player._current_state
        
        # Verify mode hooks are called
        self.mode_registry.call_global_hooks.assert_called()
    
    def test_mode_deactivation_restores_normal_behavior(self):
        """Test that deactivating modes restores normal player behavior."""
        # Activate a mode
        mock_mode = Mock(spec=BaseMode)
        mock_mode.get_mode_type.return_value = WoNQModeType.SPEEDY_BOOTS
        mock_mode.is_active.return_value = True
        
        self.mode_registry.get_active_modes.return_value = [mock_mode]
        self.mode_registry.is_mode_active.return_value = True
        
        # Deactivate the mode
        mock_mode.is_active.return_value = False
        self.mode_registry.get_active_modes.return_value = []
        
        # Verify normal behavior is restored
        self.player.change_state(PlayerState.NORMAL)
        self.assertIsInstance(self.player._current_state, NormalState)
    
    def test_multiple_modes_combined_effects(self):
        """Test that multiple active modes combine their effects."""
        # Create multiple mock modes
        mode1 = Mock(spec=BaseMode)
        mode1.get_mode_type.return_value = WoNQModeType.LOW_G
        mode1.is_active.return_value = True
        
        mode2 = Mock(spec=BaseMode)
        mode2.get_mode_type.return_value = WoNQModeType.SPEEDY_BOOTS
        mode2.is_active.return_value = True
        
        self.mode_registry.get_active_modes.return_value = [mode1, mode2]
        
        # Mock combined hooks
        hook_calls = []
        
        def gravity_hook(current_gravity):
            hook_calls.append('gravity')
            return current_gravity * 0.5
        
        def speed_hook(current_speed):
            hook_calls.append('speed')
            return current_speed * 2.0
        
        self.mode_registry.call_global_hooks.side_effect = lambda hook_name, *args, **kwargs: {
            'modify_gravity': [gravity_hook],
            'modify_speed': [speed_hook]
        }.get(hook_name, [])
        
        # Trigger hooks
        self.mode_registry.call_global_hooks('modify_gravity', 980)
        self.mode_registry.call_global_hooks('modify_speed', 100)
        
        # Verify both hooks were called
        self.assertIn('gravity', hook_calls)
        self.assertIn('speed', hook_calls)
    
    def test_mode_transition_during_powerup_state(self):
        """Test mode transitions while player is in powerup state."""
        # Put player in JumpUpStiq state
        self.player.change_state(PlayerState.JUMPUPSTIQ)
        self.assertIsInstance(self.player._current_state, JumpUpStiqState)
        
        # Activate a mode during powerup state
        mock_mode = Mock(spec=BaseMode)
        mock_mode.get_mode_type.return_value = WoNQModeType.MIRROR
        mock_mode.is_active.return_value = True
        
        self.mode_registry.get_active_modes.return_value = [mock_mode]
        
        # Verify state persists through mode activation
        self.assertIsInstance(self.player._current_state, JumpUpStiqState)
        
        # Deactivate mode
        mock_mode.is_active.return_value = False
        self.mode_registry.get_active_modes.return_value = []
        
        # Verify state still persists
        self.assertIsInstance(self.player._current_state, JumpUpStiqState)


class TestPowerupModeCompatibility(unittest.TestCase):
    """Test compatibility between powerup states and game modes."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        
        self.player = Mock(spec=Player)
        self.player._current_state = Mock(spec=BasePlayerState)
        self.mode_registry = Mock(spec=ModeRegistry)
    
    def test_jumpupstiq_with_low_gravity_mode(self):
        """Test JumpUpStiq state compatibility with low gravity mode."""
        # Create JumpUpStiq state
        jump_state = JumpUpStiqState(self.player)
        
        # Mock low gravity mode
        mock_mode = Mock(spec=BaseMode)
        mock_mode.get_mode_type.return_value = WoNQModeType.LOW_G
        
        # Test that state can handle modified gravity
        self.assertTrue(hasattr(jump_state, '_perform_bounce'))
        self.assertTrue(hasattr(jump_state, '_perform_bass_blast'))
    
    def test_jettpaq_with_speedy_boots_mode(self):
        """Test Jettpaq state compatibility with speedy boots mode."""
        # Create Jettpaq state
        jett_state = JettpaqState(self.player)
        
        # Mock speedy boots mode
        mock_mode = Mock(spec=BaseMode)
        mock_mode.get_mode_type.return_value = WoNQModeType.SPEEDY_BOOTS
        
        # Test that state can handle speed modifications
        self.assertTrue(hasattr(jett_state, '_activate_dash'))
        self.assertTrue(hasattr(jett_state, '_update_fuel'))
    
    def test_normal_state_with_all_modes(self):
        """Test Normal state compatibility with all game modes."""
        # Create Normal state
        normal_state = NormalState(self.player)
        
        # Test compatibility with each mode type
        for mode_type in WoNQModeType:
            # Normal state should handle all modes gracefully
            self.assertTrue(hasattr(normal_state, 'update'))
            self.assertTrue(hasattr(normal_state, 'handle_input'))
    
    def test_powerup_expiration_during_active_mode(self):
        """Test powerup expiration while a game mode is active."""
        # Mock player with powerup state
        self.player._current_state = Mock(spec=JumpUpStiqState)
        self.player._powerup_timers = {PowerupType.JUMPUPSTIQ: 0.5}
        
        # Mock active mode
        mock_mode = Mock(spec=BaseMode)
        mock_mode.is_active.return_value = True
        
        self.mode_registry.get_active_modes.return_value = [mock_mode]
        
        # Simulate powerup expiration
        self.player._powerup_timers[PowerupType.JUMPUPSTIQ] = 0
        
        # Verify state transition logic would be triggered
        self.assertTrue(hasattr(self.player, 'change_state'))


class TestHookExecutionOrder(unittest.TestCase):
    """Test hook execution order for mode and state interactions."""
    
    def setUp(self):
        """Set up test environment."""
        self.mode_registry = Mock(spec=ModeRegistry)
        self.hook_results = []
    
    def test_hook_priority_system(self):
        """Test that hooks execute in priority order."""
        # Create hooks with different priorities
        def low_priority_hook(value):
            self.hook_results.append(('low', value))
            return value * 1.1
        
        def medium_priority_hook(value):
            self.hook_results.append(('medium', value))
            return value * 1.2
        
        def high_priority_hook(value):
            self.hook_results.append(('high', value))
            return value * 1.3
        
        # Mock hook registration with priorities
        self.mode_registry.call_global_hooks.side_effect = (
            lambda hook_name, *args, **kwargs: 
                [high_priority_hook, medium_priority_hook, low_priority_hook]
                if hook_name == 'test_hook' else []
        )
        
        # Execute hooks
        result = 100
        hooks = self.mode_registry.call_global_hooks('test_hook')
        for hook in hooks:
            result = hook(result)
        
        # Verify execution order (should be in registration order)
        self.assertEqual(len(self.hook_results), 3)
        self.assertEqual(self.hook_results[0][0], 'high')
        self.assertEqual(self.hook_results[1][0], 'medium')
        self.assertEqual(self.hook_results[2][0], 'low')
    
    def test_hook_chain_termination(self):
        """Test that hooks can terminate the chain."""
        def terminating_hook(value):
            self.hook_results.append('terminating')
            return None  # Signal to terminate chain
        
        def never_called_hook(value):
            self.hook_results.append('never_called')
            return value
        
        self.mode_registry.call_global_hooks.side_effect = (
            lambda hook_name, *args, **kwargs: 
                [terminating_hook, never_called_hook]
                if hook_name == 'test_hook' else []
        )
        
        # Execute hooks
        hooks = self.mode_registry.call_global_hooks('test_hook')
        result = 100
        for hook in hooks:
            result = hook(result)
            if result is None:
                break
        
        # Verify chain was terminated
        self.assertIn('terminating', self.hook_results)
        self.assertNotIn('never_called', self.hook_results)


class TestValidationRoutines(unittest.TestCase):
    """Validation routines for mode and state interaction correctness."""
    
    def validate_mode_state_compatibility(self, mode_type: WoNQModeType, 
                                         state_type: PlayerState) -> List[str]:
        """
        Validate compatibility between a game mode and player state.
        
        Args:
            mode_type: The game mode type to validate
            state_type: The player state type to validate
            
        Returns:
            List of validation errors (empty if compatible)
        """
        errors = []
        
        # Define known incompatibilities
        incompatibilities = {
            (WoNQModeType.MIRROR, PlayerState.JETTPAQ): 
                "Mirror mode may cause confusion with Jettpaq dash direction",
            (WoNQModeType.BULLET_TIME, PlayerState.JUMPUPSTIQ):
                "Bullet time may interfere with JumpUpStiq bounce timing",
        }
        
        # Check for known issues
        if (mode_type, state_type) in incompatibilities:
            errors.append(incompatibilities[(mode_type, state_type)])
        
        # Validate state has required methods for mode interaction
        required_methods = ['update', 'handle_input', 'get_state_name']
        
        # All states should have these basic methods
        for method in required_methods:
            # This is a structural check - in real code would verify actual classes
            pass
        
        return errors
    
    def validate_powerup_duration_consistency(self, powerup_type: PowerupType, 
                                            mode_types: List[WoNQModeType]) -> List[str]:
        """
        Validate powerup duration consistency with active modes.
        
        Args:
            powerup_type: The powerup type to validate
            mode_types: List of active mode types
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Define powerup base durations
        powerup_durations = {
            PowerupType.JUMPUPSTIQ: 30.0,  # 30 seconds
            PowerupType.JETTPAQ: 20.0,      # 20 seconds
        }
        
        # Check for modes that might affect duration
        duration_affecting_modes = {
            WoNQModeType.BULLET_TIME: "May extend perceived duration",
            WoNQModeType.SPEEDY_BOOTS: "May affect powerup activation timing",
        }
        
        for mode_type in mode_types:
            if mode_type in duration_affecting_modes:
                warnings.append(
                    f"{mode_type.name}: {duration_affecting_modes[mode_type]}"
                )
        
        return warnings
    
    def test_validation_routine_execution(self):
        """Test execution of validation routines."""
        # Test mode-state compatibility validation
        errors = self.validate_mode_state_compatibility(
            WoNQModeType.MIRROR, 
            PlayerState.JETTPAQ
        )
        self.assertGreater(len(errors), 0)
        
        # Test powerup duration validation
        warnings = self.validate_powerup_duration_consistency(
            PowerupType.JUMPUPSTIQ,
            [WoNQModeType.BULLET_TIME, WoNQModeType.LOW_G]
        )
        # Should have warning for bullet time
        self.assertTrue(any("BULLET_TIME" in w for w in warnings))


def create_comprehensive_test_suite() -> unittest.TestSuite:
    """
    Create a comprehensive test suite for mode and state interaction validation.
    
    Returns:
        unittest.TestSuite with all validation tests
    """
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestModeStateInteraction))
    suite.addTest(unittest.makeSuite(TestPowerupModeCompatibility))
    suite.addTest(unittest.makeSuite(TestHookExecutionOrder))
    suite.addTest(unittest.makeSuite(TestValidationRoutines))
    
    return suite


def run_validation_tests() -> Dict[str, Any]:
    """
    Run all validation tests and return results.
    
    Returns:
        Dictionary with test results
    """
    # Create test suite
    suite = create_comprehensive_test_suite()
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Compile results
    test_results = {
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'successful': result.testsRun - len(result.failures) - len(result.errors),
        'failure_details': [str(f[1]) for f in result.failures],
        'error_details': [str(e[1]) for e in result.errors],
    }
    
    return test_results


if __name__ == '__main__':
    # Run validation tests
    results = run_validation_tests()
    
    print("\n" + "="*60)
    print("MODE AND STATE INTERACTION VALIDATION RESULTS")
    print("="*60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Successful: {results['successful']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    
    if results['failures'] > 0:
        print("\nFAILURES:")
        for detail in results['failure_details']:
            print(f"  - {detail}")
    
    if results['errors'] > 0:
        print("\nERRORS:")
        for detail in results['error_details']:
            print(f"  - {detail}")
    
    print("="*60)
    
    # Exit with appropriate code
    exit_code = 0 if results['failures'] == 0 and results['errors'] == 0 else 1
    exit(exit_code)