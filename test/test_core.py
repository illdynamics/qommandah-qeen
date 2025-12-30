"""
Unit tests for core game modules.
"""
import unittest
import pygame
from unittest.mock import Mock, patch
from core.engine import Engine
from core.scene import Scene
from core.resources import ResourceManager
from core.time import Time
from core.input import InputManager
from core.camera import Camera
from core.particles import ParticleSystem

class TestEngine(unittest.TestCase):
    """Test the game engine."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.engine = Engine(title="Test", width=800, height=600, target_fps=60)
    
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertEqual(self.engine.title, "Test")
        self.assertEqual(self.engine.width, 800)
        self.assertEqual(self.engine.height, 600)
        self.assertEqual(self.engine.target_fps, 60)
    
    def test_set_scene(self):
        """Test scene setting."""
        mock_scene = Mock(spec=Scene)
        self.engine.set_scene(mock_scene)
        self.assertEqual(self.engine.next_scene, mock_scene)
    
    def test_get_screen_size(self):
        """Test screen size retrieval."""
        size = self.engine.get_screen_size()
        self.assertEqual(size, (800, 600))
    
    def test_get_screen_center(self):
        """Test screen center calculation."""
        center = self.engine.get_screen_center()
        self.assertEqual(center, (400, 300))

class TestTime(unittest.TestCase):
    """Test the time manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.time = Time()
    
    def test_singleton_pattern(self):
        """Test that Time is a singleton."""
        time2 = Time()
        self.assertIs(self.time, time2)
    
    def test_time_scale(self):
        """Test time scale manipulation."""
        self.time.set_time_scale(0.5)
        self.assertEqual(self.time.get_time_scale(), 0.5)
        
        self.time.set_time_scale(2.0)
        self.assertEqual(self.time.get_time_scale(), 2.0)
    
    def test_pause_functionality(self):
        """Test pause/unpause functionality."""
        self.time.set_paused(True)
        self.assertTrue(self.time.is_paused())
        
        self.time.set_paused(False)
        self.assertFalse(self.time.is_paused())
        
        self.time.toggle_pause()
        self.assertTrue(self.time.is_paused())

class TestResourceManager(unittest.TestCase):
    """Test the resource manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.resource_manager = ResourceManager()
    
    def test_singleton_pattern(self):
        """Test that ResourceManager is a singleton."""
        rm2 = ResourceManager()
        self.assertIs(self.resource_manager, rm2)
    
    @patch('pygame.image.load')
    def test_load_image(self, mock_load):
        """Test image loading."""
        mock_surface = Mock()
        mock_load.return_value = mock_surface
        
        result = self.resource_manager.load_image("test", "test.png")
        self.assertEqual(result, mock_surface)
        self.assertIn("test", self.resource_manager.images)
    
    def test_get_nonexistent_resource(self):
        """Test retrieving non-existent resource."""
        with self.assertRaises(KeyError):
            self.resource_manager.get_image("nonexistent")

class TestInputManager(unittest.TestCase):
    """Test the input manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.input_manager = InputManager()
        self.input_manager.initialize()
    
    def test_action_mapping(self):
        """Test action key mapping."""
        self.input_manager.map_action("jump", pygame.K_SPACE, pygame.K_UP)
        self.input_manager.map_action("move_left", pygame.K_LEFT, pygame.K_a)
        
        self.assertTrue(self.input_manager.is_action_down("jump") is not None)
    
    def test_key_state_tracking(self):
        """Test key state tracking."""
        # Simulate key press
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.input_manager._process_event(event)
        
        self.assertTrue(self.input_manager.is_key_down(pygame.K_SPACE))
        self.assertTrue(self.input_manager.is_key_pressed(pygame.K_SPACE))
        
        # Simulate key release
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE)
        self.input_manager._process_event(event)
        
        self.assertFalse(self.input_manager.is_key_down(pygame.K_SPACE))
        self.assertTrue(self.input_manager.is_key_released(pygame.K_SPACE))

class TestCamera(unittest.TestCase):
    """Test the camera system."""
    
    def setUp(self):
        """Set up test environment."""
        self.camera = Camera(viewport_size=(800, 600), world_bounds=(1600, 1200))
    
    def test_camera_initialization(self):
        """Test camera initialization."""
        self.assertEqual(self.camera.get_viewport_size(), (800, 600))
        self.assertEqual(self.camera.get_zoom(), 1.0)
    
    def test_world_to_screen_conversion(self):
        """Test world to screen coordinate conversion."""
        world_pos = (100, 100)
        screen_pos = self.camera.world_to_screen(world_pos)
        
        # With camera at (0, 0), positions should be the same
        self.assertEqual(screen_pos, world_pos)
    
    def test_screen_shake(self):
        """Test screen shake effect."""
        self.camera.shake(intensity=10.0, duration=1.0)
        self.assertTrue(self.camera.shake_intensity > 0)
    
    def test_zoom_functionality(self):
        """Test camera zoom functionality."""
        self.camera.set_zoom(2.0)
        self.assertEqual(self.camera.get_zoom(), 2.0)
        
        self.camera.set_zoom(0.5)
        self.assertEqual(self.camera.get_zoom(), 0.5)

class TestParticleSystem(unittest.TestCase):
    """Test the particle system."""
    
    def setUp(self):
        """Set up test environment."""
        self.particle_system = ParticleSystem()
    
    def test_emitter_creation(self):
        """Test particle emitter creation."""
        smoke_emitter = self.particle_system.create_smoke_emitter((100, 100))
        self.assertIsNotNone(smoke_emitter)
        
        explosion_emitter = self.particle_system.create_explosion((200, 200))
        self.assertIsNotNone(explosion_emitter)
    
    def test_particle_update(self):
        """Test particle system update."""
        # Create an emitter
        emitter = self.particle_system.create_smoke_emitter((100, 100))
        
        # Store initial particle count
        initial_count = len(emitter.particles)
        
        # Update the system
        self.particle_system.update()
        
        # Particle count should change (some may have expired)
        self.assertNotEqual(len(emitter.particles), initial_count)
    
    def test_clear_all_particles(self):
        """Test clearing all particles."""
        # Create multiple emitters
        self.particle_system.create_smoke_emitter((100, 100))
        self.particle_system.create_explosion((200, 200))
        
        # Clear all
        self.particle_system.clear_all()
        
        # Should have no emitters
        self.assertEqual(len(self.particle_system.emitters), 0)

if __name__ == '__main__':
    unittest.main()