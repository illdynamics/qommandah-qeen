import unittest
import pygame
from unittest.mock import Mock, patch, MagicMock
from shared.types import Vec2i, EnemyState, Direction
from actors.enemies.base_enemy import BaseEnemy
from actors.enemies.walqer_bot import WalqerBot
from actors.enemies.jumper_drqne import JumperDrqne
from actors.enemies.qortana_halo import QortanaHalo
from actors.enemies.qlippy import Qlippy
from actors.enemies.briq_beaver import BriqBeaver

class TestEnemyAI(unittest.TestCase):
    """Test enemy AI behaviors and interactions."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        
    def tearDown(self):
        """Clean up test environment."""
        pygame.quit()
        
    def test_base_enemy_state_transitions(self):
        """Test base enemy state machine transitions."""
        enemy = BaseEnemy(position=Vec2i(100, 100))
        
        # Initial state should be IDLE
        self.assertEqual(enemy.get_state(), EnemyState.IDLE)
        
        # Change to PATROL state
        enemy.change_state(EnemyState.PATROL)
        self.assertEqual(enemy.get_state(), EnemyState.PATROL)
        
        # Change to CHASE state
        enemy.change_state(EnemyState.CHASE)
        self.assertEqual(enemy.get_state(), EnemyState.CHASE)
        
        # Change to ATTACK state
        enemy.change_state(EnemyState.ATTACK)
        self.assertEqual(enemy.get_state(), EnemyState.ATTACK)
        
    def test_base_enemy_player_detection(self):
        """Test base enemy player detection logic."""
        enemy = BaseEnemy(
            position=Vec2i(100, 100),
            detection_range=200.0
        )
        
        # Player within detection range
        player_pos_within = Vec2i(150, 100)  # 50 pixels away
        self.assertTrue(enemy.can_detect_player(player_pos_within))
        
        # Player outside detection range
        player_pos_outside = Vec2i(350, 100)  # 250 pixels away
        self.assertFalse(enemy.can_detect_player(player_pos_outside))
        
    def test_walqer_bot_patrol_behavior(self):
        """Test WalqerBot patrol behavior."""
        walqer = WalqerBot(
            position=Vec2i(100, 100),
            patrol_range=50,
            direction=Direction.RIGHT
        )
        
        # Initial state should be PATROL
        self.assertEqual(walqer.get_state(), EnemyState.PATROL)
        
        # Test patrol movement
        initial_x = walqer.position.x
        walqer.think(0.5, None)  # No player position
        
        # Should move in patrol direction
        self.assertNotEqual(walqer.position.x, initial_x)
        
    def test_walqer_bot_shooting_behavior(self):
        """Test WalqerBot shooting when player is in range."""
        walqer = WalqerBot(
            position=Vec2i(100, 100),
            patrol_range=50
        )
        
        # Mock projectile creation
        with patch('actors.enemies.walqer_bot.Projectile') as mock_projectile_class:
            mock_projectile = Mock()
            mock_projectile_class.return_value = mock_projectile
            
            # Player within attack range
            player_pos = Vec2i(120, 100)  # 20 pixels away
            
            # Change to ATTACK state
            walqer.change_state(EnemyState.ATTACK)
            walqer.think(0.5, player_pos)
            
            # Should create projectile
            mock_projectile_class.assert_called_once()
            
    def test_jumper_drqne_jump_behavior(self):
        """Test JumperDrqne jumping at intervals."""
        jumper = JumperDrqne(
            position=Vec2i(100, 100),
            jump_interval=2.0  # Jump every 2 seconds
        )
        
        # Initial state should be IDLE
        self.assertEqual(jumper.get_state(), EnemyState.IDLE)
        
        # Update for jump interval
        jumper.update(2.1, None)  # Just past jump interval
        
        # Should have initiated jump
        self.assertEqual(jumper.get_state(), EnemyState.ATTACK)  # Jump state
        
    def test_jumper_drqne_explosion_on_death(self):
        """Test JumperDrqne creates explosion on death."""
        jumper = JumperDrqne(position=Vec2i(100, 100))
        
        # Mock particle system
        with patch('actors.enemies.jumper_drqne.ParticleSystem') as mock_particle_system_class:
            mock_particle_system = Mock()
            mock_particle_system_class.return_value = mock_particle_system
            
            # Kill the jumper
            jumper.take_damage(1000)  # Massive damage
            
            # Should create explosion
            mock_particle_system_class.assert_called_once()
            
    def test_qortana_halo_zigzag_movement(self):
        """Test QortanaHalo zigzag movement pattern."""
        sprite_data = Mock()
        qortana = QortanaHalo(
            position=Vec2i(100, 100),
            sprite_data=sprite_data
        )
        
        # Mock engine
        engine = Mock()
        engine.get_time.return_value = Mock()
        engine.get_time.return_value.get_delta_time.return_value = 0.1
        
        # Player position
        player_pos = Vec2i(200, 100)
        
        # Change to CHASE state
        qortana.change_state(EnemyState.CHASE)
        
        # Update with player position
        initial_position = qortana.position
        qortana.update(engine)
        
        # Should move toward player with zigzag pattern
        self.assertNotEqual(qortana.position, initial_position)
        
    def test_qortana_halo_electric_attack(self):
        """Test QortanaHalo electric zap attack."""
        sprite_data = Mock()
        qortana = QortanaHalo(
            position=Vec2i(100, 100),
            sprite_data=sprite_data
        )
        
        # Mock engine
        engine = Mock()
        
        # Player within attack range
        player_pos = Vec2i(120, 100)
        
        # Change to ATTACK state
        qortana.change_state(EnemyState.ATTACK)
        
        # Mock zap effect creation
        with patch.object(qortana, '_create_zap_effect'):
            qortana.update(engine)
            
            # Should create zap effect
            qortana._create_zap_effect.assert_called_once()
            
    def test_qlippy_movement_pattern(self):
        """Test Qlippy erratic movement pattern."""
        sprite_data = Mock()
        qlippy = Qlippy(
            position=Vec2i(100, 100),
            sprite_data=sprite_data
        )
        
        # Mock engine
        engine = Mock()
        engine.get_time.return_value = Mock()
        engine.get_time.return_value.get_delta_time.return_value = 0.1
        
        # Initial update
        initial_position = qlippy.position
        qlippy.update(engine)
        
        # Should move erratically
        self.assertNotEqual(qlippy.position, initial_position)
        
    def test_briq_beaver_projectile_throwing(self):
        """Test BriqBeaver throws arcing projectiles."""
        sprite_data = Mock()
        beaver = BriqBeaver(
            position=Vec2i(100, 100),
            sprite_data=sprite_data
        )
        
        # Mock time manager
        time_manager = Mock()
        time_manager.get_delta_time.return_value = 0.1
        
        # Player position
        player_pos = Vec2i(150, 100)
        
        # Update with player in range
        beaver.update(time_manager, player_pos)
        
        # Should start windup for throw
        self.assertEqual(beaver.get_state(), EnemyState.ATTACK)
        
    def test_enemy_damage_response(self):
        """Test enemy response to taking damage."""
        enemy = BaseEnemy(position=Vec2i(100, 100), health=100)
        
        initial_health = enemy.get_health()
        
        # Take damage
        enemy.take_damage(30, knockback=Vec2i(-10, 0))
        
        # Health should decrease
        self.assertEqual(enemy.get_health(), initial_health - 30)
        
        # Should enter HURT state
        self.assertEqual(enemy.get_state(), EnemyState.HURT)
        
    def test_enemy_death(self):
        """Test enemy death behavior."""
        enemy = BaseEnemy(position=Vec2i(100, 100), health=50)
        
        # Take lethal damage
        enemy.take_damage(100)
        
        # Should be dead
        self.assertFalse(enemy.is_alive())
        self.assertEqual(enemy.get_state(), EnemyState.DEAD)
        
    def test_enemy_animation_state_mapping(self):
        """Test enemy animation mapping for different states."""
        enemy = BaseEnemy(position=Vec2i(100, 100))
        
        # Test animation for IDLE state
        enemy.change_state(EnemyState.IDLE)
        animation_idle = enemy.get_animation_for_state()
        self.assertIsNotNone(animation_idle)
        
        # Test animation for PATROL state
        enemy.change_state(EnemyState.PATROL)
        animation_patrol = enemy.get_animation_for_state()
        self.assertIsNotNone(animation_patrol)
        
        # Test animation for ATTACK state
        enemy.change_state(EnemyState.ATTACK)
        animation_attack = enemy.get_animation_for_state()
        self.assertIsNotNone(animation_attack)