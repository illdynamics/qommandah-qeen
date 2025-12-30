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
        mock_scene.engine = self.engine
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
        resource_manager2 = ResourceManager()
        self.assertIs(self.resource_manager, resource_manager2)
    
    @patch('pygame.image.load')
    def test_load_image(self, mock_load):
        """Test image loading."""
        mock_surface = Mock()
        mock_load.return_value = mock_surface
        
        image = self.resource_manager.load_image("test", "test.png")
        self.assertEqual(image, mock_surface)
        mock_load.assert_called_once_with("test.png")
    
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
        self.assertTrue(self.input_manager.is_action_down("jump"))
    
    def test_key_state_tracking(self):
        """Test key state tracking."""
        # Simulate key press
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.input_manager._process_event(event)
        self.assertTrue(self.input_manager.is_key_down(pygame.K_SPACE))
        
        # Simulate key release
        event = pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE)
        self.input_manager._process_event(event)
        self.assertFalse(self.input_manager.is_key_down(pygame.K_SPACE))

class TestCamera(unittest.TestCase):
    """Test the camera system."""
    
    def setUp(self):
        """Set up test environment."""
        self.camera = Camera(viewport_size=(800, 600), world_bounds=(1600, 1200))
    
    def test_camera_initialization(self):
        """Test camera initialization."""
        self.assertEqual(self.camera.get_viewport_size(), (800, 600))
    
    def test_world_to_screen_conversion(self):
        """Test world to screen coordinate conversion."""
        from shared.types import Vector2
        world_pos = Vector2(100, 100)
        screen_pos = self.camera.world_to_screen(world_pos)
        self.assertEqual(screen_pos.x, 100)
        self.assertEqual(screen_pos.y, 100)
    
    def test_screen_shake(self):
        """Test screen shake effect."""
        self.camera.shake(intensity=10.0, duration=1.0)
        self.assertGreater(self.camera.shake_intensity, 0)
    
    def test_zoom_functionality(self):
        """Test camera zoom functionality."""
        self.camera.set_zoom(2.0)
        self.assertEqual(self.camera.get_zoom(), 2.0)

class TestParticleSystem(unittest.TestCase):
    """Test the particle system."""
    
    def setUp(self):
        """Set up test environment."""
        self.particle_system = ParticleSystem()
    
    def test_emitter_creation(self):
        """Test particle emitter creation."""
        emitter = self.particle_system.create_smoke_emitter((100, 100))
        self.assertIsNotNone(emitter)
        self.assertEqual(len(self.particle_system.emitters), 1)
    
    def test_particle_update(self):
        """Test particle system update."""
        emitter = self.particle_system.create_smoke_emitter((100, 100))
        self.particle_system.update()
        # Should create particles
        self.assertGreater(len(emitter.particles), 0)
    
    def test_clear_all_particles(self):
        """Test clearing all particles."""
        self.particle_system.create_smoke_emitter((100, 100))
        self.particle_system.create_explosion((200, 200))
        self.particle_system.clear_all()
        self.assertEqual(len(self.particle_system.emitters), 0)

if __name__ == '__main__':
    unittest.main()