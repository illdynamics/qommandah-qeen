import unittest
import pygame
from unittest.mock import Mock, patch, MagicMock
from shared.types import Vec2i
from actors.projectile import Projectile
from actors.enemies.base_enemy import BaseEnemy
from world.collision import CollisionSystem, CollisionResult
from core.particles import ParticleSystem

class TestProjectile(unittest.TestCase):
    """Test projectile launch, update, collision, and destruction."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.position = Vec2i(100, 100)
        self.direction = Vec2i(1, 0)  # Right
        self.owner = Mock()
        self.projectile = Projectile(
            position=self.position,
            direction=self.direction,
            owner=self.owner,
            damage=10,
            speed=200.0,
            lifetime=5.0,
            size=8,
            color=(255, 0, 0)
        )
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
        
    def test_projectile_initialization(self):
        """Test projectile initialization with correct properties."""
        self.assertEqual(self.projectile.position, self.position)
        self.assertEqual(self.projectile.direction, self.direction)
        self.assertEqual(self.projectile.owner, self.owner)
        self.assertEqual(self.projectile.damage, 10)
        self.assertEqual(self.projectile.speed, 200.0)
        self.assertEqual(self.projectile.lifetime, 5.0)
        self.assertEqual(self.projectile.size, 8)
        self.assertEqual(self.projectile.color, (255, 0, 0))
        self.assertTrue(self.projectile.is_active())
        
    def test_projectile_update_movement(self):
        """Test projectile movement update."""
        initial_position = self.projectile.position
        dt = 0.5  # 500ms
        
        self.projectile.update(dt)
        
        # Position should change based on direction and speed
        expected_x = initial_position.x + self.direction.x * self.projectile.speed * dt
        expected_y = initial_position.y + self.direction.y * self.projectile.speed * dt
        
        self.assertAlmostEqual(self.projectile.position.x, expected_x)
        self.assertAlmostEqual(self.projectile.position.y, expected_y)
        
    def test_projectile_lifetime_decrease(self):
        """Test projectile lifetime decreases with update."""
        initial_lifetime = self.projectile.get_remaining_lifetime()
        dt = 1.0
        
        self.projectile.update(dt)
        
        self.assertAlmostEqual(
            self.projectile.get_remaining_lifetime(),
            initial_lifetime - dt,
            places=5
        )
        
    def test_projectile_expiration(self):
        """Test projectile expires when lifetime reaches zero."""
        dt = 6.0  # More than 5.0 lifetime
        
        self.projectile.update(dt)
        
        self.assertFalse(self.projectile.is_active())
        
    def test_projectile_collision_detection(self):
        """Test projectile collision detection with collision system."""
        collision_system = Mock(spec=CollisionSystem)
        collision_system.check_tile_collision.return_value = []
        
        collisions = self.projectile.check_collision(collision_system)
        
        collision_system.check_tile_collision.assert_called_once()
        self.assertEqual(collisions, [])
        
    def test_projectile_entity_collision(self):
        """Test projectile collision with entities."""
        enemy = Mock(spec=BaseEnemy)
        enemy.get_rect.return_value = pygame.Rect(110, 100, 32, 32)
        enemy.is_alive.return_value = True
        
        entities = [enemy]
        
        collided_entity = self.projectile.check_entity_collision(entities)
        
        self.assertEqual(collided_entity, enemy)
        
    def test_projectile_entity_collision_filter_owner(self):
        """Test projectile doesn't collide with its owner."""
        owner_entity = Mock()
        owner_entity.get_rect.return_value = pygame.Rect(110, 100, 32, 32)
        self.projectile.owner = owner_entity
        
        entities = [owner_entity]
        
        collided_entity = self.projectile.check_entity_collision(entities)
        
        self.assertIsNone(collided_entity)
        
    def test_projectile_handle_collision(self):
        """Test projectile handles collision with world geometry."""
        collision_result = Mock(spec=CollisionResult)
        collision_result.collided = True
        collision_result.normal = Vec2i(-1, 0)  # Hit from right
        
        collisions = [collision_result]
        
        self.projectile.handle_collision(collisions)
        
        # Projectile should be destroyed on collision
        self.assertFalse(self.projectile.is_active())
        
    def test_projectile_handle_entity_hit(self):
        """Test projectile handles hitting an entity."""
        enemy = Mock(spec=BaseEnemy)
        enemy.take_damage = Mock()
        
        should_continue = self.projectile.handle_entity_hit(enemy)
        
        enemy.take_damage.assert_called_once_with(self.projectile.damage)
        self.assertFalse(should_continue)  # Non-penetrating projectile
        
    def test_penetrating_projectile(self):
        """Test penetrating projectile continues after hitting entities."""
        self.projectile.set_penetrating(True)
        
        enemy1 = Mock(spec=BaseEnemy)
        enemy1.take_damage = Mock()
        
        enemy2 = Mock(spec=BaseEnemy)
        enemy2.take_damage = Mock()
        
        # First hit
        should_continue = self.projectile.handle_entity_hit(enemy1)
        self.assertTrue(should_continue)
        enemy1.take_damage.assert_called_once_with(self.projectile.damage)
        
        # Second hit
        should_continue = self.projectile.handle_entity_hit(enemy2)
        self.assertTrue(should_continue)
        enemy2.take_damage.assert_called_once_with(self.projectile.damage)
        
    def test_projectile_destroy(self):
        """Test projectile destruction."""
        particle_system = Mock(spec=ParticleSystem)
        self.projectile.set_particle_system(particle_system)
        
        self.projectile.destroy()
        
        self.assertFalse(self.projectile.is_active())
        
    def test_projectile_velocity_getter(self):
        """Test projectile velocity calculation."""
        velocity = self.projectile.get_velocity()
        
        expected_x = self.direction.x * self.projectile.speed
        expected_y = self.direction.y * self.projectile.speed
        
        self.assertAlmostEqual(velocity.x, expected_x)
        self.assertAlmostEqual(velocity.y, expected_y)
        
    def test_projectile_reset_hit_list(self):
        """Test resetting hit list for penetrating projectiles."""
        self.projectile.set_penetrating(True)
        
        enemy = Mock(spec=BaseEnemy)
        self.projectile.handle_entity_hit(enemy)
        
        # Reset hit list
        self.projectile.reset_hit_list()
        
        # Should be able to hit same enemy again
        should_continue = self.projectile.handle_entity_hit(enemy)
        self.assertTrue(should_continue)
        
    def test_projectile_render(self):
        """Test projectile rendering (visual verification)."""
        surface = pygame.Surface((200, 200))
        camera_offset = Vec2i(0, 0)
        
        # This should not raise exceptions
        self.projectile.render(surface, camera_offset)
        
    def test_projectile_with_particle_system(self):
        """Test projectile with particle system for trail effects."""
        particle_system = Mock(spec=ParticleSystem)
        self.projectile.set_particle_system(particle_system)
        
        dt = 0.1
        self.projectile.update(dt)
        
        # Particle system should be used for trail effects
        self.assertIsNotNone(self.projectile.particle_system)