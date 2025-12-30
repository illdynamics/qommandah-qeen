import unittest
import pygame
from unittest.mock import Mock, patch
from objects.hazard import Hazard, SpikeHazard, AcidHazard, LaserHazard, HazardSystem
from world.entities import Entity
from shared.types import Rect
from core.time import Time

class TestHazard(unittest.TestCase):
    """Test base hazard functionality."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.hazard = Hazard(10.0, 20.0, 32.0, 32.0, "spike")
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_hazard_initialization(self):
        """Test hazard initialization."""
        self.assertEqual(self.hazard.x, 10.0)
        self.assertEqual(self.hazard.y, 20.0)
        self.assertEqual(self.hazard.width, 32.0)
        self.assertEqual(self.hazard.height, 32.0)
        self.assertEqual(self.hazard.hazard_type, "spike")
        self.assertTrue(self.hazard.active)
    
    def test_get_damage_value(self):
        """Test damage value retrieval."""
        damage = self.hazard._get_damage_value()
        self.assertIsInstance(damage, int)
        self.assertGreater(damage, 0)
    
    def test_check_collision(self):
        """Test collision detection."""
        other_rect = Rect(15, 25, 10, 10)
        result = self.hazard.check_collision(other_rect)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)
        
        far_rect = Rect(100, 100, 10, 10)
        result = self.hazard.check_collision(far_rect)
        self.assertFalse(result)
    
    def test_apply_damage(self):
        """Test damage application."""
        damage = self.hazard.apply_damage()
        self.assertIsInstance(damage, int)
        self.assertGreater(damage, 0)
    
    def test_toggle_active(self):
        """Test active state toggling."""
        self.assertTrue(self.hazard.active)
        self.hazard.toggle_active(False)
        self.assertFalse(self.hazard.active)
        self.hazard.toggle_active(True)
        self.assertTrue(self.hazard.active)
    
    def test_reset(self):
        """Test hazard reset."""
        self.hazard.toggle_active(False)
        self.hazard.reset()
        self.assertTrue(self.hazard.active)

class TestSpikeHazard(unittest.TestCase):
    """Test spike hazard subclass."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.spike = SpikeHazard(10.0, 20.0)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_spike_initialization(self):
        """Test spike hazard initialization."""
        self.assertEqual(self.spike.hazard_type, "spike")
        self.assertEqual(self.spike.width, 32.0)
        self.assertEqual(self.spike.height, 32.0)
    
    def test_spike_update(self):
        """Test spike update logic."""
        with patch.object(Time, 'get_delta_time', return_value=0.016):
            self.spike.update(0.016)
            # Should not crash or change state unexpectedly

class TestAcidHazard(unittest.TestCase):
    """Test acid hazard subclass."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.acid = AcidHazard(10.0, 20.0)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_acid_initialization(self):
        """Test acid hazard initialization."""
        self.assertEqual(self.acid.hazard_type, "acid")
        self.assertEqual(self.acid.width, 64.0)
        self.assertEqual(self.acid.height, 32.0)
    
    def test_acid_update(self):
        """Test acid update logic."""
        with patch.object(Time, 'get_delta_time', return_value=0.016):
            self.acid.update(0.016)
            # Should update bubble animation
    
    def test_acid_apply_damage(self):
        """Test acid damage application with timing."""
        damage = self.acid.apply_damage()
        self.assertIsInstance(damage, int)
        self.assertGreater(damage, 0)

class TestLaserHazard(unittest.TestCase):
    """Test laser hazard subclass."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.laser = LaserHazard(10.0, 20.0, horizontal=True)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_laser_initialization(self):
        """Test laser hazard initialization."""
        self.assertEqual(self.laser.hazard_type, "laser")
        self.assertEqual(self.laser.width, 128.0)
        self.assertEqual(self.laser.height, 8.0)
        self.assertTrue(self.laser.horizontal)
    
    def test_laser_update(self):
        """Test laser update with cycling."""
        with patch.object(Time, 'get_delta_time', return_value=0.016):
            initial_active = self.laser.active
            self.laser.update(0.016)
            # Laser should cycle on/off over time
    
    def test_laser_check_collision(self):
        """Test laser collision only when firing."""
        other_rect = Rect(15, 25, 10, 10)
        
        # Test when active
        self.laser.active = True
        result = self.laser.check_collision(other_rect)
        self.assertIsInstance(result, bool)
        
        # Test when inactive
        self.laser.active = False
        result = self.laser.check_collision(other_rect)
        self.assertFalse(result)

class TestHazardSystem(unittest.TestCase):
    """Test hazard system management."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.system = HazardSystem()
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_hazard_system_initialization(self):
        """Test hazard system initialization."""
        self.assertEqual(len(self.system.hazards), 0)
    
    def test_add_hazard(self):
        """Test adding hazards to system."""
        hazard = Hazard(0, 0, 32, 32, "spike")
        self.system.add_hazard(hazard)
        self.assertEqual(len(self.system.hazards), 1)
        self.assertIn(hazard, self.system.hazards)
    
    def test_create_spike(self):
        """Test spike hazard creation."""
        spike = self.system.create_spike(10, 20)
        self.assertIsInstance(spike, SpikeHazard)
        self.assertEqual(spike.x, 10)
        self.assertEqual(spike.y, 20)
        self.assertEqual(len(self.system.hazards), 1)
    
    def test_create_acid(self):
        """Test acid hazard creation."""
        acid = self.system.create_acid(30, 40)
        self.assertIsInstance(acid, AcidHazard)
        self.assertEqual(acid.x, 30)
        self.assertEqual(acid.y, 40)
        self.assertEqual(len(self.system.hazards), 2)
    
    def test_create_laser(self):
        """Test laser hazard creation."""
        laser = self.system.create_laser(50, 60, horizontal=False)
        self.assertIsInstance(laser, LaserHazard)
        self.assertEqual(laser.x, 50)
        self.assertEqual(laser.y, 60)
        self.assertFalse(laser.horizontal)
        self.assertEqual(len(self.system.hazards), 3)
    
    def test_update_hazards(self):
        """Test updating all hazards."""
        self.system.create_spike(0, 0)
        self.system.create_acid(10, 10)
        
        with patch.object(Time, 'get_delta_time', return_value=0.016):
            self.system.update(0.016)
            # Should update all hazards without error
    
    def test_check_hazard_collisions(self):
        """Test hazard collision checking."""
        self.system.create_spike(0, 0)
        entity_rect = Rect(5, 5, 10, 10)
        
        hazard = self.system.check_hazard_collisions(entity_rect)
        self.assertIsInstance(hazard, Hazard)
        
        far_rect = Rect(100, 100, 10, 10)
        hazard = self.system.check_hazard_collisions(far_rect)
        self.assertIsNone(hazard)
    
    def test_check_hazard_collisions_no_collision(self):
        """Test hazard collision checking with no collisions."""
        self.system.create_spike(0, 0)
        far_rect = Rect(100, 100, 10, 10)
        
        hazard = self.system.check_hazard_collisions(far_rect)
        self.assertIsNone(hazard)
    
    def test_clear_hazards(self):
        """Test clearing all hazards."""
        self.system.create_spike(0, 0)
        self.system.create_acid(10, 10)
        self.assertEqual(len(self.system.hazards), 2)
        
        self.system.clear_hazards()
        self.assertEqual(len(self.system.hazards), 0)
    
    def test_reset_hazards(self):
        """Test resetting all hazards."""
        spike = self.system.create_spike(0, 0)
        spike.toggle_active(False)
        
        self.system.reset_hazards()
        self.assertTrue(spike.active)
    
    def test_get_hazard_count(self):
        """Test getting hazard count."""
        self.assertEqual(self.system.get_hazard_count(), 0)
        self.system.create_spike(0, 0)
        self.assertEqual(self.system.get_hazard_count(), 1)
        self.system.create_acid(10, 10)
        self.assertEqual(self.system.get_hazard_count(), 2)
    
    def test_get_active_hazards(self):
        """Test getting active hazards."""
        spike = self.system.create_spike(0, 0)
        acid = self.system.create_acid(10, 10)
        acid.toggle_active(False)
        
        active_hazards = self.system.get_active_hazards()
        self.assertEqual(len(active_hazards), 1)
        self.assertIn(spike, active_hazards)
        self.assertNotIn(acid, active_hazards)

class TestHazardIntegration(unittest.TestCase):
    """Test hazard integration with game systems."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.system = HazardSystem()
        self.player_mock = Mock()
        self.player_mock.get_rect.return_value = Rect(50, 50, 32, 32)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_hazard_damage_application(self):
        """Test hazard damage application to player."""
        spike = self.system.create_spike(50, 50)
        
        with patch.object(self.player_mock, 'take_damage') as mock_take_damage:
            hazard = self.system.check_hazard_collisions(self.player_mock.get_rect())
            if hazard:
                damage = hazard.apply_damage()
                self.player_mock.take_damage(damage)
            
            mock_take_damage.assert_called_once()
    
    def test_multiple_hazard_types(self):
        """Test interaction with multiple hazard types."""
        self.system.create_spike(0, 0)
        self.system.create_acid(100, 100)
        self.system.create_laser(200, 200)
        
        self.assertEqual(len(self.system.hazards), 3)
        self.assertEqual(self.system.get_hazard_count(), 3)
        
        # Test each hazard type
        for hazard in self.system.hazards:
            self.assertIsInstance(hazard, Hazard)
            self.assertIn(hazard.hazard_type, ["spike", "acid", "laser"])
    
    def test_hazard_lifecycle(self):
        """Test complete hazard lifecycle."""
        # Create
        spike = self.system.create_spike(0, 0)
        self.assertEqual(len(self.system.hazards), 1)
        
        # Update
        with patch.object(Time, 'get_delta_time', return_value=0.016):
            self.system.update(0.016)
        
        # Check collision
        entity_rect = Rect(5, 5, 10, 10)
        hazard = self.system.check_hazard_collisions(entity_rect)
        self.assertEqual(hazard, spike)
        
        # Toggle active
        spike.toggle_active(False)
        self.assertFalse(spike.active)
        
        # Reset
        self.system.reset_hazards()
        self.assertTrue(spike.active)
        
        # Clear
        self.system.clear_hazards()
        self.assertEqual(len(self.system.hazards), 0)