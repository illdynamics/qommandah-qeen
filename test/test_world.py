"""
Unit tests for world systems.
"""
import unittest
import pygame
from unittest.mock import Mock, patch
from world.tiles import TileSet, TileType
from world.physics import PhysicsBody, apply_gravity, check_collision
from world.collision import CollisionSystem, CollisionResult, check_aabb_collision
from world.entities import Entity
from world.level_loader import LevelLoader

class TestTileSet(unittest.TestCase):
    """Test the tile set system."""
    
    def setUp(self):
        """Set up test environment."""
        self.tileset = TileSet(tile_size=32)
    
    def test_tile_property_management(self):
        """Test tile property storage and retrieval."""
        properties = {
            "collidable": True,
            "texture": "grass",
            "damage": 0,
            "friction": 0.8
        }
        
        self.tileset.add_tile(1, properties)
        retrieved = self.tileset.get_tile_properties(1)
        
        self.assertEqual(retrieved, properties)
        self.assertTrue(self.tileset.is_tile_collidable(1))
        self.assertEqual(self.tileset.get_tile_friction(1), 0.8)
    
    def test_nonexistent_tile(self):
        """Test retrieval of non-existent tile."""
        self.assertIsNone(self.tileset.get_tile_properties(999))
        self.assertFalse(self.tileset.is_tile_collidable(999))
        self.assertEqual(self.tileset.get_tile_friction(999), 0.8)  # Default
    
    def test_collision_region_management(self):
        """Test collision region management."""
        self.tileset.add_collision_region(0, 0, 100, 100)
        
        # Test collision inside region
        self.assertTrue(self.tileset.check_collision((50, 50), (10, 10)))
        
        # Test collision outside region
        self.assertFalse(self.tileset.check_collision((200, 200), (10, 10)))

class TestPhysicsBody(unittest.TestCase):
    """Test the physics body system."""
    
    def setUp(self):
        """Set up test environment."""
        self.body = PhysicsBody(position=(100, 100), size=(32, 32))
    
    def test_body_initialization(self):
        """Test physics body initialization."""
        self.assertEqual(self.body.position, (100, 100))
        self.assertEqual(self.body.size, (32, 32))
        self.assertEqual(self.body.velocity, (0, 0))
        self.assertEqual(self.body.acceleration, (0, 0))
    
    def test_velocity_application(self):
        """Test velocity application."""
        self.body.set_velocity((50, 0))
        self.assertEqual(self.body.velocity, (50, 0))
        
        self.body.add_velocity((0, -100))
        self.assertEqual(self.body.velocity, (50, -100))
    
    def test_force_application(self):
        """Test force application."""
        self.body.apply_force((100, 0))
        self.assertEqual(self.body.acceleration, (100, 0))
    
    def test_bounds_calculation(self):
        """Test bounds calculation."""
        bounds = self.body.get_bounds()
        self.assertEqual(bounds, (100, 100, 32, 32))
    
    def test_gravity_application(self):
        """Test gravity application."""
        apply_gravity(self.body, gravity_strength=980)
        self.assertEqual(self.body.acceleration, (0, 980))
    
    def test_collision_detection(self):
        """Test collision detection between bodies."""
        body1 = PhysicsBody(position=(0, 0), size=(32, 32))
        body2 = PhysicsBody(position=(16, 16), size=(32, 32))
        
        self.assertTrue(check_collision(body1, body2))
        
        body3 = PhysicsBody(position=(100, 100), size=(32, 32))
        self.assertFalse(check_collision(body1, body3))

class TestCollisionSystem(unittest.TestCase):
    """Test the collision system."""
    
    def setUp(self):
        """Set up test environment."""
        self.tilemap = Mock()
        self.collision_system = CollisionSystem(self.tilemap)
    
    def test_aabb_collision_detection(self):
        """Test AABB collision detection."""
        rect1 = pygame.Rect(0, 0, 32, 32)
        rect2 = pygame.Rect(16, 16, 32, 32)
        rect3 = pygame.Rect(100, 100, 32, 32)
        
        self.assertTrue(check_aabb_collision(rect1, rect2))
        self.assertFalse(check_aabb_collision(rect1, rect3))
    
    def test_collider_management(self):
        """Test collider addition and management."""
        rect = pygame.Rect(0, 0, 32, 32)
        
        self.collision_system.add_static_collider(rect, TileType.SOLID)
        self.collision_system.add_dynamic_collider(rect)
        
        collisions = self.collision_system.check_static_collision(rect)
        self.assertGreater(len(collisions), 0)
        
        self.collision_system.clear_dynamic_colliders()
        collisions = self.collision_system.check_dynamic_collision(rect)
        self.assertEqual(len(collisions), 0)
    
    def test_raycasting(self):
        """Test raycasting functionality."""
        # Add a collider
        rect = pygame.Rect(50, 50, 32, 32)
        self.collision_system.add_static_collider(rect, TileType.SOLID)
        
        # Cast ray that should hit
        result = self.collision_system.raycast(
            origin=(0, 60),
            direction=(1, 0),
            distance=100
        )
        
        self.assertIsNotNone(result)
        
        # Cast ray that should miss
        result = self.collision_system.raycast(
            origin=(0, 0),
            direction=(0, 1),
            distance=30
        )
        
        self.assertIsNone(result)

class TestEntity(unittest.TestCase):
    """Test the base entity system."""
    
    def setUp(self):
        """Set up test environment."""
        self.entity = Entity(position=(100, 100), size=(32, 32))
    
    def test_entity_initialization(self):
        """Test entity initialization."""
        self.assertEqual(self.entity.position, (100, 100))
        self.assertEqual(self.entity.size, (32, 32))
        self.assertTrue(self.entity.active)
        self.assertTrue(self.entity.visible)
    
    def test_rect_calculation(self):
        """Test rectangle calculation."""
        rect = self.entity.get_rect()
        self.assertEqual(rect.x, 100)
        self.assertEqual(rect.y, 100)
        self.assertEqual(rect.width, 32)
        self.assertEqual(rect.height, 32)
    
    def test_center_calculation(self):
        """Test center calculation."""
        center = self.entity.get_center()
        self.assertEqual(center, (116, 116))  # 100 + 32/2
    
    def test_collision_detection(self):
        """Test collision detection between entities."""
        entity2 = Entity(position=(116, 116), size=(32, 32))
        
        self.assertTrue(self.entity.is_colliding_with(entity2))
        
        entity3 = Entity(position=(200, 200), size=(32, 32))
        self.assertFalse(self.entity.is_colliding_with(entity3))
    
    def test_destruction_marking(self):
        """Test entity destruction marking."""
        self.entity.destroy()
        self.assertFalse(self.entity.active)
    
    def test_position_velocity_manipulation(self):
        """Test position and velocity manipulation."""
        self.entity.set_position(200, 200)
        self.assertEqual(self.entity.position, (200, 200))
        
        self.entity.set_velocity(50, -50)
        self.assertEqual(self.entity.velocity, (50, -50))
        
        self.entity.add_velocity(0, 100)
        self.assertEqual(self.entity.velocity, (50, 50))
    
    def test_z_index_management(self):
        """Test z-index management."""
        self.assertEqual(self.entity.get_z_index(), 0)
        
        self.entity.set_z_index(10)
        self.assertEqual(self.entity.get_z_index(), 10)

class TestLevelLoader(unittest.TestCase):
    """Test the level loader."""
    
    def setUp(self):
        """Set up test environment."""
        self.level_loader = LevelLoader()
    
    @patch('json.load')
    @patch('builtins.open')
    def test_level_loading(self, mock_open, mock_json_load):
        """Test level loading from JSON."""
        # Mock level data
        mock_data = {
            "name": "Test Level",
            "width": 40,
            "height": 20,
            "tiles": [[1] * 40 for _ in range(20)],
            "entities": [],
            "modes": [],
            "background": "default",
            "music": "test"
        }
        mock_json_load.return_value = mock_data
        
        level_data = self.level_loader.load_level("test_level.json")
        
        self.assertEqual(level_data.name, "Test Level")
        self.assertEqual(level_data.width, 40)
        self.assertEqual(level_data.height, 20)
        self.assertEqual(len(level_data.tiles), 20)
        self.assertEqual(len(level_data.tiles[0]), 40)
    
    def test_invalid_level_data(self):
        """Test handling of invalid level data."""
        with self.assertRaises(Exception):
            self.level_loader.load_level("nonexistent.json")

if __name__ == '__main__':
    unittest.main()