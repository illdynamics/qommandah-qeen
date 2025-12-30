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
        self.input = Mock(spec=InputManager)
        
        # Create player with mocked dependencies
        self.player = Player(100, 100)
        self.player.set_engine_references(self.engine, self.physics, self.collision, self.mode_registry)
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_initial_state_is_normal(self):
        """Test player starts in normal state."""
        self.assertEqual(self.player.current_state.get_state_name(), "NormalState")
    
    def test_transition_to_jumpupstiq_state(self):
        """Test transition from normal to jumpupstiq state."""
        # Mock powerup collection
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JUMPUPSTIQ
        self.player.collect(powerup_mock)
        
        # Check state transition
        self.assertEqual(self.player.current_state.get_state_name(), "JumpUpStiqState")
    
    def test_transition_to_jettpaq_state(self):
        """Test transition from normal to jettpaq state."""
        # Mock powerup collection
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JETTPAQ
        self.player.collect(powerup_mock)
        
        # Check state transition
        self.assertEqual(self.player.current_state.get_state_name(), "JettpaqState")
    
    def test_powerup_expiration_transition(self):
        """Test transition back to normal state when powerup expires."""
        # First transition to jumpupstiq
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JUMPUPSTIQ
        self.player.collect(powerup_mock)
        self.assertEqual(self.player.current_state.get_state_name(), "JumpUpStiqState")
        
        # Simulate powerup expiration
        self.player.update(10.0)  # Update with large dt to expire powerup
        
        # Should transition back to normal
        self.assertEqual(self.player.current_state.get_state_name(), "NormalState")
    
    def test_state_transition_cleanup(self):
        """Test that state transitions properly clean up previous state."""
        # Track enter/exit calls
        normal_state = self.player.current_state
        normal_state.exit = Mock()
        
        # Transition to jumpupstiq
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JUMPUPSTIQ
        self.player.collect(powerup_mock)
        
        # Verify exit was called on normal state
        normal_state.exit.assert_called_once()
    
    def test_concurrent_powerup_handling(self):
        """Test handling when player collects multiple powerups."""
        # Collect jumpupstiq
        powerup1 = Mock()
        powerup1.powerup_type = PowerupType.JUMPUPSTIQ
        self.player.collect(powerup1)
        self.assertEqual(self.player.current_state.get_state_name(), "JumpUpStiqState")
        
        # Collect jettpaq while jumpupstiq is active
        powerup2 = Mock()
        powerup2.powerup_type = PowerupType.JETTPAQ
        self.player.collect(powerup2)
        
        # Should transition to jettpaq (newer powerup takes precedence)
        self.assertEqual(self.player.current_state.get_state_name(), "JettpaqState")
    
    def test_state_specific_input_handling(self):
        """Test that input handling differs between states."""
        # Test normal state input
        normal_state = self.player.current_state
        normal_state.handle_input = Mock()
        self.player.handle_input()
        normal_state.handle_input.assert_called_once()
        
        # Transition to jumpupstiq and test its input
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JUMPUPSTIQ
        self.player.collect(powerup_mock)
        
        jumpupstiq_state = self.player.current_state
        jumpupstiq_state.handle_input = Mock()
        self.player.handle_input()
        jumpupstiq_state.handle_input.assert_called_once()
    
    def test_state_specific_update_logic(self):
        """Test that update logic differs between states."""
        # Test normal state update
        normal_state = self.player.current_state
        normal_state.update = Mock()
        self.player.update(0.016)
        normal_state.update.assert_called_once_with(0.016)
        
        # Transition to jettpaq and test its update
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JETTPAQ
        self.player.collect(powerup_mock)
        
        jettpaq_state = self.player.current_state
        jettpaq_state.update = Mock()
        self.player.update(0.016)
        jettpaq_state.update.assert_called_once_with(0.016)
    
    def test_state_transition_with_damage(self):
        """Test that taking damage doesn't interrupt powerup states."""
        # Transition to jumpupstiq
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JUMPUPSTIQ
        self.player.collect(powerup_mock)
        
        # Take damage while in jumpupstiq state
        initial_state = self.player.current_state
        self.player.take_damage(10)
        
        # Should remain in jumpupstiq state
        self.assertEqual(self.player.current_state, initial_state)
    
    def test_state_reset_on_player_death(self):
        """Test that player state resets to normal on death."""
        # Transition to jettpaq
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JETTPAQ
        self.player.collect(powerup_mock)
        self.assertEqual(self.player.current_state.get_state_name(), "JettpaqState")
        
        # Player dies
        self.player.die()
        
        # Should reset to normal state
        self.assertEqual(self.player.current_state.get_state_name(), "NormalState")
    
    def test_state_persistence_across_levels(self):
        """Test that powerup states don't persist across level resets."""
        # Transition to jumpupstiq
        powerup_mock = Mock()
        powerup_mock.powerup_type = PowerupType.JUMPUPSTIQ
        self.player.collect(powerup_mock)
        self.assertEqual(self.player.current_state.get_state_name(), "JumpUpStiqState")
        
        # Reset player (simulating level restart)
        self.player.reset()
        
        # Should be back to normal state
        self.assertEqual(self.player.current_state.get_state_name(), "NormalState")

class TestNormalStateFunctionality(unittest.TestCase):
    """Test specific functionality of NormalState."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.player = Mock(spec=Player)
        self.state = NormalState(self.player)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_normal_state_name(self):
        """Test NormalState returns correct name."""
        self.assertEqual(self.state.get_state_name(), "NormalState")
    
    def test_normal_state_enter_exit(self):
        """Test NormalState enter and exit methods."""
        self.state.enter()
        self.state.exit()
        # No assertion needed, just checking no exceptions
    
    def test_normal_state_input_handling(self):
        """Test NormalState input handling."""
        self.state.handle_input()
        # Should call player movement methods based on input
    
    def test_normal_state_update(self):
        """Test NormalState update logic."""
        self.state.update(0.016)
        # Should update player physics and animations

class TestJumpUpStiqStateFunctionality(unittest.TestCase):
    """Test specific functionality of JumpUpStiqState."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.player = Mock(spec=Player)
        self.state = JumpUpStiqState(self.player)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_jumpupstiq_state_name(self):
        """Test JumpUpStiqState returns correct name."""
        self.assertEqual(self.state.get_state_name(), "JumpUpStiqState")
    
    def test_jumpupstiq_bounce_mechanics(self):
        """Test JumpUpStiqState bounce mechanics."""
        # Mock player on ground
        self.player.is_on_ground = True
        self.player.velocity_y = 0
        
        # Test bounce
        self.state._perform_bounce()
        # Should apply upward force
    
    def test_jumpupstiq_bass_blast(self):
        """Test JumpUpStiqState bass blast ability."""
        self.state._perform_bass_blast()
        # Should create shockwave and damage enemies

class TestJettpaqStateFunctionality(unittest.TestCase):
    """Test specific functionality of JettpaqState."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.player = Mock(spec=Player)
        self.state = JettpaqState(self.player)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_jettpaq_state_name(self):
        """Test JettpaqState returns correct name."""
        self.assertEqual(self.state.get_state_name(), "JettpaqState")
    
    def test_jettpaq_dash_mechanics(self):
        """Test JettpaqState dash mechanics."""
        # Test dash activation
        self.state._activate_dash()
        # Should set dashing flag and apply dash velocity
    
    def test_jettpaq_fuel_management(self):
        """Test JettpaqState fuel management."""
        # Test fuel consumption
        initial_fuel = self.state.fuel
        self.state._update_fuel(0.016)
        # Fuel should decrease when dashing
    
    def test_jettpaq_cooldown(self):
        """Test JettpaqState dash cooldown."""
        # Activate dash
        self.state._activate_dash()
        
        # End dash
        self.state._end_dash()
        
        # Should start cooldown timer
        self.assertGreater(self.state.dash_cooldown_timer, 0)

if __name__ == '__main__':
    unittest.main()