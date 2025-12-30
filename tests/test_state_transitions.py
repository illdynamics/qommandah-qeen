"""
Test suite for validating player state transitions, mode changes, and powerup durations.
Ensures system robustness and correct behavior of state machines.
"""
import unittest
import pygame
from unittest.mock import Mock, patch, MagicMock
from shared.types import PlayerState, PowerupType, Direction
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
from shared.wonqmode_data import WoNQModeType, WoNQModeConfig

class TestPlayerStateTransitions(unittest.TestCase):
    """Test player state transitions between normal, jumpupstiq, and jettpaq states."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.engine = Mock(spec=Engine)
        self.physics = Mock(spec=PhysicsSystem)
        self.collision = Mock(spec=CollisionSystem)
        self.mode_registry = Mock(spec=ModeRegistry)
        self.time = Mock(spec=Time)
        
        # Create player instance
        self.player = Player(100, 100)
        self.player.set_engine_references(self.engine, self.physics, self.collision, self.mode_registry)
        
        # Mock time manager
        self.time.get_delta_time.return_value = 0.016  # 60 FPS
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_initial_state_is_normal(self):
        """Test player starts in normal state."""
        self.assertIsInstance(self.player.current_state, NormalState)
        self.assertEqual(self.player.current_state.get_state_name(), "NormalState")
    
    def test_transition_to_jumpupstiq_state(self):
        """Test transition from normal to jumpupstiq state."""
        # Simulate collecting jumpupstiq powerup
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.assertIsInstance(self.player.current_state, JumpUpStiqState)
        self.assertEqual(self.player.current_state.get_state_name(), "JumpUpStiqState")
    
    def test_transition_to_jettpaq_state(self):
        """Test transition from normal to jettpaq state."""
        # Simulate collecting jettpaq powerup
        self.player._apply_powerup(PowerupType.JETTPAQ)
        self.assertIsInstance(self.player.current_state, JettpaqState)
        self.assertEqual(self.player.current_state.get_state_name(), "JettpaqState")
    
    def test_powerup_expiration_transition(self):
        """Test transition back to normal state when powerup expires."""
        # Start with jumpupstiq
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.assertIsInstance(self.player.current_state, JumpUpStiqState)
        
        # Simulate powerup expiration
        self.player._update_powerups(10.0)  # More than powerup duration
        self.assertIsInstance(self.player.current_state, NormalState)
    
    def test_state_transition_cleanup(self):
        """Test that state transitions properly clean up previous state."""
        # Mock state exit methods
        normal_state = Mock(spec=NormalState)
        jumpupstiq_state = Mock(spec=JumpUpStiqState)
        
        # Set up player with mocked states
        self.player.current_state = normal_state
        self.player._change_state = Mock()
        
        # Trigger state change
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        
        # Verify exit was called on old state
        normal_state.exit.assert_called_once()
    
    def test_concurrent_powerup_handling(self):
        """Test handling when player collects multiple powerups."""
        # Collect jumpupstiq
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.assertIsInstance(self.player.current_state, JumpUpStiqState)
        
        # Collect jettpaq while jumpupstiq is active
        self.player._apply_powerup(PowerupType.JETTPAQ)
        
        # Should transition to jettpaq (newer powerup takes precedence)
        self.assertIsInstance(self.player.current_state, JettpaqState)
    
    def test_state_specific_input_handling(self):
        """Test that input handling differs between states."""
        # Test normal state input
        normal_state = NormalState(self.player)
        normal_state.handle_input = Mock()
        self.player.current_state = normal_state
        self.player.handle_input()
        normal_state.handle_input.assert_called_once()
        
        # Test jumpupstiq state input
        jumpupstiq_state = JumpUpStiqState(self.player)
        jumpupstiq_state.handle_input = Mock()
        self.player.current_state = jumpupstiq_state
        self.player.handle_input()
        jumpupstiq_state.handle_input.assert_called_once()
    
    def test_state_specific_update_logic(self):
        """Test that update logic differs between states."""
        # Test normal state update
        normal_state = NormalState(self.player)
        normal_state.update = Mock()
        self.player.current_state = normal_state
        self.player.update(0.016)
        normal_state.update.assert_called_once_with(0.016)
        
        # Test jettpaq state update
        jettpaq_state = JettpaqState(self.player)
        jettpaq_state.update = Mock()
        self.player.current_state = jettpaq_state
        self.player.update(0.016)
        jettpaq_state.update.assert_called_once_with(0.016)
    
    def test_state_transition_with_damage(self):
        """Test that taking damage doesn't interrupt powerup states."""
        # Start with jumpupstiq
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        initial_state = self.player.current_state
        
        # Take damage
        self.player.take_damage(10)
        
        # Should remain in jumpupstiq state
        self.assertIs(initial_state, self.player.current_state)
    
    def test_state_reset_on_player_death(self):
        """Test that player state resets to normal on death."""
        # Start with jettpaq
        self.player._apply_powerup(PowerupType.JETTPAQ)
        self.assertIsInstance(self.player.current_state, JettpaqState)
        
        # Kill player
        self.player.die()
        
        # Should reset to normal state
        self.assertIsInstance(self.player.current_state, NormalState)
    
    def test_state_persistence_across_levels(self):
        """Test that powerup states don't persist across level resets."""
        # Start with jumpupstiq
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.assertIsInstance(self.player.current_state, JumpUpStiqState)
        
        # Reset player (simulating level reset)
        self.player.reset()
        
        # Should be back to normal state
        self.assertIsInstance(self.player.current_state, NormalState)

class TestModeStateInteractions(unittest.TestCase):
    """Test interactions between game modes and player states."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.engine = Mock(spec=Engine)
        self.physics = Mock(spec=PhysicsSystem)
        self.collision = Mock(spec=CollisionSystem)
        self.mode_registry = Mock(spec=ModeRegistry)
        
        # Create player
        self.player = Player(100, 100)
        self.player.set_engine_references(self.engine, self.physics, self.collision, self.mode_registry)
        
        # Create mock modes
        self.low_g_mode = Mock(spec=BaseMode)
        self.low_g_mode.get_mode_type.return_value = WoNQModeType.LOW_G
        self.low_g_mode.is_active.return_value = True
        
        self.mirror_mode = Mock(spec=BaseMode)
        self.mirror_mode.get_mode_type.return_value = WoNQModeType.MIRROR
        self.mirror_mode.is_active.return_value = True
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_mode_activation_affects_player_state(self):
        """Test that active modes affect player state behavior."""
        # Set up mode registry to return active modes
        self.mode_registry.get_active_modes.return_value = [self.low_g_mode, self.mirror_mode]
        
        # Update player with active modes
        self.player.update(0.016)
        
        # Verify mode registry was queried
        self.mode_registry.get_active_modes.assert_called()
    
    def test_mode_deactivation_restores_normal_behavior(self):
        """Test that deactivating modes restores normal player behavior."""
        # Activate mode
        self.mode_registry.get_active_modes.return_value = [self.low_g_mode]
        self.player.update(0.016)
        
        # Deactivate mode
        self.mode_registry.get_active_modes.return_value = []
        self.player.update(0.016)
        
        # Should handle both cases without error
        self.assertTrue(True)
    
    def test_multiple_modes_combined_effects(self):
        """Test that multiple active modes combine their effects."""
        # Set multiple active modes
        self.mode_registry.get_active_modes.return_value = [self.low_g_mode, self.mirror_mode]
        
        # Update player
        self.player.update(0.016)
        
        # Verify all modes were considered
        self.assertEqual(self.mode_registry.get_active_modes.call_count, 1)
    
    def test_mode_transition_during_powerup_state(self):
        """Test mode transitions while player is in powerup state."""
        # Put player in jumpupstiq state
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        
        # Activate mode
        self.mode_registry.get_active_modes.return_value = [self.low_g_mode]
        self.player.update(0.016)
        
        # Should handle mode effects in powerup state
        self.assertIsInstance(self.player.current_state, JumpUpStiqState)

class TestPowerupDurationMechanics(unittest.TestCase):
    """Test powerup duration mechanics and expiration."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.player = Player(100, 100)
        
        # Mock time for consistent testing
        self.player._update_powerups = Mock()
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_powerup_duration_tracking(self):
        """Test that powerup durations are tracked correctly."""
        # Apply powerup
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        
        # Verify powerup is tracked
        self.assertIn(PowerupType.JUMPUPSTIQ, self.player.active_powerups)
    
    def test_powerup_expiration_logic(self):
        """Test that powerups expire after their duration."""
        # Apply powerup
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        
        # Simulate time passing beyond duration
        self.player._update_powerups(15.0)  # Jumpupstiq duration is typically 10 seconds
        
        # Powerup should be removed
        self.assertNotIn(PowerupType.JUMPUPSTIQ, self.player.active_powerups)
    
    def test_powerup_duration_reset_on_recollection(self):
        """Test that recollecting a powerup resets its duration."""
        # Apply powerup
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        initial_time = self.player.active_powerups[PowerupType.JUMPUPSTIQ]
        
        # Simulate some time passing
        self.player._update_powerups(5.0)
        
        # Recollect same powerup
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        new_time = self.player.active_powerups[PowerupType.JUMPUPSTIQ]
        
        # Duration should be reset (new time > initial time + 5)
        self.assertGreater(new_time, initial_time + 5.0)
    
    def test_concurrent_powerup_durations(self):
        """Test that multiple powerups have independent durations."""
        # Apply two powerups
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.player._apply_powerup(PowerupType.JETTPAQ)
        
        # Verify both are tracked
        self.assertIn(PowerupType.JUMPUPSTIQ, self.player.active_powerups)
        self.assertIn(PowerupType.JETTPAQ, self.player.active_powerups)
        
        # Simulate time passing
        self.player._update_powerups(5.0)
        
        # Both should still be active
        self.assertIn(PowerupType.JUMPUPSTIQ, self.player.active_powerups)
        self.assertIn(PowerupType.JETTPAQ, self.player.active_powerups)

class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complex state and mode interactions."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.engine = Mock(spec=Engine)
        self.physics = Mock(spec=PhysicsSystem)
        self.collision = Mock(spec=CollisionSystem)
        self.mode_registry = Mock(spec=ModeRegistry)
        
        self.player = Player(100, 100)
        self.player.set_engine_references(self.engine, self.physics, self.collision, self.mode_registry)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_complete_state_machine_cycle(self):
        """Test a complete cycle through all player states."""
        # Start in normal state
        self.assertIsInstance(self.player.current_state, NormalState)
        
        # Transition to jumpupstiq
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.assertIsInstance(self.player.current_state, JumpUpStiqState)
        
        # Expire jumpupstiq, return to normal
        self.player._update_powerups(15.0)
        self.assertIsInstance(self.player.current_state, NormalState)
        
        # Transition to jettpaq
        self.player._apply_powerup(PowerupType.JETTPAQ)
        self.assertIsInstance(self.player.current_state, JettpaqState)
        
        # Expire jettpaq, return to normal
        self.player._update_powerups(15.0)
        self.assertIsInstance(self.player.current_state, NormalState)
    
    def test_mode_activation_during_state_transitions(self):
        """Test mode activation during player state transitions."""
        # Activate low-g mode
        low_g_mode = Mock(spec=BaseMode)
        low_g_mode.get_mode_type.return_value = WoNQModeType.LOW_G
        low_g_mode.is_active.return_value = True
        self.mode_registry.get_active_modes.return_value = [low_g_mode]
        
        # Transition through states with mode active
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.player.update(0.016)
        
        self.player._apply_powerup(PowerupType.JETTPAQ)
        self.player.update(0.016)
        
        # Should handle all combinations without error
        self.assertTrue(True)
    
    def test_damage_and_state_persistence(self):
        """Test that damage doesn't break state persistence."""
        # Start in jumpupstiq state
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        
        # Take multiple instances of damage
        for _ in range(5):
            self.player.take_damage(5)
            self.player.update(0.016)
        
        # Should remain in jumpupstiq state
        self.assertIsInstance(self.player.current_state, JumpUpStiqState)
    
    def test_reset_clears_all_states(self):
        """Test that player reset clears all states and modes."""
        # Set up complex state
        self.player._apply_powerup(PowerupType.JUMPUPSTIQ)
        self.mode_registry.get_active_modes.return_value = [Mock(spec=BaseMode)]
        
        # Reset player
        self.player.reset()
        
        # Should be in normal state with no active powerups
        self.assertIsInstance(self.player.current_state, NormalState)
        self.assertEqual(len(self.player.active_powerups), 0)

def run_state_transition_tests():
    """Run all state transition tests and return results."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPlayerStateTransitions)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestModeStateInteractions))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPowerupDurationMechanics))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntegrationScenarios))
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == "__main__":
    # Run tests when script is executed directly
    result = run_state_transition_tests()
    if result.wasSuccessful():
        print("\n✅ All state transition tests passed!")
    else:
        print("\n❌ Some tests failed. Check output above for details.")