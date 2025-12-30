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
        self.direction = Vec2i(1, 0)
        self.owner = Mock()
        self.projectile = Projectile(
            position=self.position,
            direction=self.direction,
            owner=self.owner,
            damage=10,
            speed=200,
            lifetime=2.0,
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
        self.assertEqual(self.projectile.speed, 200)
        self.assertEqual(self.projectile.lifetime, 2.0)
        self.assertEqual(self.projectile.remaining_lifetime, 2.0)
        self.assertEqual(self.projectile.size, 8)
        self.assertEqual(self.projectile.color, (255, 0, 0))
        self.assertTrue(self.projectile.active)
        self.assertFalse(self.projectile.penetrating)
        self.assertEqual(len(self.projectile.hit_entities), 0)

    def test_projectile_update_movement(self):
        """Test projectile movement update."""
        initial_position = self.projectile.position
        self.projectile.update(0.5)  # 0.5 seconds
        expected_x = initial_position.x + 200 * 0.5  # speed * time
        self.assertEqual(self.projectile.position.x, expected_x)
        self.assertEqual(self.projectile.position.y, initial_position.y)

    def test_projectile_lifetime_decrease(self):
        """Test projectile lifetime decreases with update."""
        initial_lifetime = self.projectile.remaining_lifetime
        self.projectile.update(0.5)
        self.assertEqual(self.projectile.remaining_lifetime, initial_lifetime - 0.5)

    def test_projectile_expiration(self):
        """Test projectile expires when lifetime reaches zero."""
        self.projectile.update(2.0)  # Exactly lifetime
        self.assertFalse(self.projectile.is_active())

    def test_projectile_collision_detection(self):
        """Test projectile collision detection with collision system."""
        collision_system = Mock(spec=CollisionSystem)
        collision_results = [Mock(spec=CollisionResult)]
        collision_system.check_tile_collision.return_value = collision_results
        
        results = self.projectile.check_collision(collision_system)
        self.assertEqual(results, collision_results)
        collision_system.check_tile_collision.assert_called_once_with(
            self.projectile.get_rect()
        )

    def test_projectile_entity_collision(self):
        """Test projectile collision with entities."""
        entity = Mock(spec=Entity)
        entity.get_rect.return_value = pygame.Rect(110, 100, 32, 32)  # In path of projectile
        
        entities = [entity]
        collided_entity = self.projectile.check_entity_collision(entities)
        self.assertEqual(collided_entity, entity)

    def test_projectile_entity_collision_filter_owner(self):
        """Test projectile doesn't collide with its owner."""
        owner_entity = self.owner
        owner_entity.get_rect.return_value = pygame.Rect(110, 100, 32, 32)
        
        entities = [owner_entity]
        collided_entity = self.projectile.check_entity_collision(entities)
        self.assertIsNone(collided_entity)

    def test_projectile_handle_collision(self):
        """Test projectile handles collision with world geometry."""
        collision_result = Mock(spec=CollisionResult)
        collision_results = [collision_result]
        
        with patch.object(self.projectile, '_create_impact_effect') as mock_effect:
            with patch.object(self.projectile, 'destroy') as mock_destroy:
                self.projectile.handle_collision(collision_results)
                mock_effect.assert_called_once()
                mock_destroy.assert_called_once()

    def test_projectile_handle_entity_hit(self):
        """Test projectile handles hitting an entity."""
        entity = Mock(spec=BaseEnemy)
        entity.take_damage = Mock()
        
        with patch.object(self.projectile, '_create_impact_effect') as mock_effect:
            with patch.object(self.projectile, 'destroy') as mock_destroy:
                # Test non-penetrating projectile
                should_continue = self.projectile.handle_entity_hit(entity)
                entity.take_damage.assert_called_once_with(10)
                mock_effect.assert_called_once()
                mock_destroy.assert_called_once()
                self.assertFalse(should_continue)
                self.assertIn(entity, self.projectile.hit_entities)

    def test_penetrating_projectile(self):
        """Test penetrating projectile continues after hitting entities."""
        self.projectile.set_penetrating(True)
        entity = Mock(spec=BaseEnemy)
        entity.take_damage = Mock()
        
        with patch.object(self.projectile, '_create_impact_effect') as mock_effect:
            with patch.object(self.projectile, 'destroy') as mock_destroy:
                should_continue = self.projectile.handle_entity_hit(entity)
                entity.take_damage.assert_called_once_with(10)
                mock_effect.assert_called_once()
                mock_destroy.assert_not_called()
                self.assertTrue(should_continue)
                self.assertIn(entity, self.projectile.hit_entities)

    def test_projectile_destroy(self):
        """Test projectile destruction."""
        self.projectile.destroy()
        self.assertFalse(self.projectile.active)

    def test_projectile_velocity_getter(self):
        """Test projectile velocity calculation."""
        velocity = self.projectile.get_velocity()
        self.assertEqual(velocity.x, 200)  # direction.x * speed
        self.assertEqual(velocity.y, 0)    # direction.y * speed

    def test_projectile_reset_hit_list(self):
        """Test resetting hit list for penetrating projectiles."""
        entity = Mock(spec=Entity)
        self.projectile.hit_entities.append(entity)
        self.projectile.reset_hit_list()
        self.assertEqual(len(self.projectile.hit_entities), 0)

    def test_projectile_render(self):
        """Test projectile rendering (visual verification)."""
        surface = Mock(spec=pygame.Surface)
        camera_offset = Vec2i(0, 0)
        
        with patch('pygame.draw.circle') as mock_draw:
            self.projectile.render(surface, camera_offset)
            mock_draw.assert_called_once()

    def test_projectile_with_particle_system(self):
        """Test projectile with particle system for trail effects."""
        particle_system = Mock(spec=ParticleSystem)
        smoke_emitter = Mock()
        particle_system.create_smoke_emitter.return_value = smoke_emitter
        
        self.projectile.set_particle_system(particle_system)
        self.assertEqual(self.projectile.particle_system, particle_system)
        particle_system.create_smoke_emitter.assert_called_once_with(
            (self.position.x, self.position.y)
        )
        self.assertEqual(self.projectile.trail_emitter, smoke_emitter)