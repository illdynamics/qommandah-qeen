import pygame
import random
import math
from typing import Optional, Tuple, List
from .base_enemy import BaseEnemy
from shared.types import Vec2i, Direction, EnemyState
from shared.constants import (
    ENEMY_WALQER_HEALTH,
    ENEMY_WALQER_DAMAGE,
    ENEMY_WALQER_SPEED,
    ENEMY_WALQER_DETECTION_RANGE,
    ENEMY_WALQER_ATTACK_RANGE,
    ENEMY_WALQER_ATTACK_COOLDOWN,
    ENEMY_WALQER_PROJECTILE_SPEED,
    TILE_SIZE
)
from core.resources import ResourceManager
from core.time import Time
from world.physics import PhysicsBody
from actors.projectile import Projectile

class WalqerBot(BaseEnemy):
    """Patrolling enemy that shoots at player when in range."""
    
    def __init__(
        self,
        position: Vec2i,
        patrol_range: int = 100,
        direction: Direction = Direction.RIGHT
    ) -> None:
        """
        Initialize WalqerBot enemy.
        
        Args:
            position: Starting position (top-left corner)
            patrol_range: How far the enemy patrols from starting position
            direction: Initial facing direction
        """
        super().__init__(
            position=position,
            health=ENEMY_WALQER_HEALTH,
            damage=ENEMY_WALQER_DAMAGE,
            speed=ENEMY_WALQER_SPEED,
            attack_range=ENEMY_WALQER_ATTACK_RANGE,
            detection_range=ENEMY_WALQER_DETECTION_RANGE,
            sprite_key="walqer_bot"
        )
        
        self.patrol_range = patrol_range
        self.start_position = position
        self.patrol_target = position
        self.patrol_direction = direction
        self.attack_cooldown = 0.0
        self.projectiles: List[Projectile] = []
        self.vision_cone_angle = math.pi / 6  # 30 degree vision cone
        
        # Float position for smooth movement
        self._float_x = float(position.x)
        self._float_y = float(position.y)
        
        # Initialize patrol behavior
        self._update_patrol_target()
        
    def _update_patrol_target(self) -> None:
        """Update patrol target based on current direction and range."""
        if self.patrol_direction == Direction.RIGHT:
            self.patrol_target = Vec2i(
                self.start_position.x + self.patrol_range,
                self.start_position.y
            )
        else:
            self.patrol_target = Vec2i(
                self.start_position.x - self.patrol_range,
                self.start_position.y
            )
    
    def think(self, delta_time: float, player_position: Optional[Vec2i] = None) -> None:
        """
        Main AI thinking method.
        
        Args:
            delta_time: Time since last frame in seconds
            player_position: Current position of the player (if known)
        """
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(delta_time)
            if not projectile.is_active():
                self.projectiles.remove(projectile)
        
        # Update timers
        if self._hurt_timer > 0:
            self._hurt_timer -= delta_time
            if self._hurt_timer <= 0:
                # After hurt, turn around and check for player
                self._direction = Direction.LEFT if self._direction == Direction.RIGHT else Direction.RIGHT
                self._update_patrol_target()
                self.change_state(EnemyState.PATROL)
        
        if self._death_timer > 0:
            self._death_timer -= delta_time
            if self._death_timer <= 0:
                self.destroy()
                return
        
        # State-specific behavior
        if self._state == EnemyState.IDLE:
            self._handle_idle_state(delta_time, player_position)
        elif self._state == EnemyState.PATROL:
            self._handle_patrol_state(delta_time, player_position)
        elif self._state == EnemyState.CHASE:
            self._handle_chase_state(delta_time, player_position)
        elif self._state == EnemyState.ATTACK:
            self._handle_attack_state(delta_time, player_position)
        elif self._state == EnemyState.HURT:
            self._handle_hurt_state(delta_time)
        elif self._state == EnemyState.DEAD:
            self._handle_dead_state(delta_time)
    
    def _handle_idle_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle idle state behavior."""
        if player_position and self.can_detect_player(player_position):
            # Check if player is in vision cone
            if self._is_player_in_vision_cone(player_position):
                self.change_state(EnemyState.CHASE)
            else:
                self.change_state(EnemyState.PATROL)
    
    def _handle_patrol_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle patrol state behavior - walk back and forth on small path."""
        # Check for player detection
        if player_position and self.can_detect_player(player_position):
            if self._is_player_in_vision_cone(player_position):
                self.change_state(EnemyState.CHASE)
                return
        
        # Patrol movement using float position for smooth movement
        dx = self.patrol_target.x - self._float_x
        
        if abs(dx) < 8:  # Smaller threshold for snappier patrol
            # Reached patrol target - reverse direction
            self.patrol_direction = Direction.LEFT if self.patrol_direction == Direction.RIGHT else Direction.RIGHT
            self._direction = self.patrol_direction
            self._update_patrol_target()
        else:
            # Walk toward patrol target - 60 pixels per second (smooth visible patrol)
            patrol_speed = 60.0  # pixels per second
            move_amount = patrol_speed * delta_time
            direction_x = 1 if dx > 0 else -1
            
            # Update float position smoothly
            self._float_x += direction_x * move_amount
            
            # Update integer position for collision/rendering
            self.position = Vec2i(int(self._float_x), self.position.y)
            self._direction = Direction.RIGHT if direction_x > 0 else Direction.LEFT
    
    def _handle_chase_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle chase state behavior."""
        if not player_position:
            self.change_state(EnemyState.PATROL)
            return
        
        distance_to_player = math.sqrt(
            (self._float_x - player_position.x) ** 2 +
            (self._float_y - player_position.y) ** 2
        )
        
        # Check if player is in attack range
        if distance_to_player <= self._attack_range:
            self.change_state(EnemyState.ATTACK)
            return
        
        # Check if player is still detectable
        if not self.can_detect_player(player_position):
            self.change_state(EnemyState.PATROL)
            return
        
        # Chase player - walk toward them smoothly
        dx = player_position.x - self._float_x
        if abs(dx) > 5:  # Only move if not already close
            # Chase speed: 70 pixels per second
            chase_speed = 70.0  # pixels per second
            move_amount = chase_speed * delta_time
            direction_x = 1 if dx > 0 else -1
            
            # Update float position smoothly
            self._float_x += direction_x * move_amount
            self.position = Vec2i(int(self._float_x), self.position.y)
        
        # Update facing direction
        self._direction = Direction.RIGHT if dx > 0 else Direction.LEFT
    
    def _handle_attack_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle attack state behavior."""
        if not player_position:
            self.change_state(EnemyState.PATROL)
            return
        
        # Check if player is still in attack range
        distance_to_player = math.sqrt(
            (self.position.x - player_position.x) ** 2 +
            (self.position.y - player_position.y) ** 2
        )
        
        if distance_to_player > self._attack_range:
            self.change_state(EnemyState.CHASE)
            return
        
        # Face the player
        self.direction = Direction.RIGHT if player_position.x > self.position.x else Direction.LEFT
        
        # Attack if cooldown is ready
        if self.attack_cooldown <= 0:
            self._perform_attack(player_position)
            self.attack_cooldown = ENEMY_WALQER_ATTACK_COOLDOWN
    
    def _handle_hurt_state(self, delta_time: float) -> None:
        """Handle hurt state behavior - enemy is stunned."""
        # Timer is handled in think() - enemy turns around after hurt
        pass
    
    def _handle_dead_state(self, delta_time: float) -> None:
        """Handle dead state behavior."""
        # Wait for death animation to complete
        if self.death_timer <= 0:
            self.destroy()
    
    def _perform_attack(self, player_position: Vec2i) -> None:
        """Perform shooting attack toward player."""
        # Calculate direction to player
        dx = player_position.x - self.position.x
        dy = player_position.y - self.position.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        # Normalize direction
        direction = Vec2i(
            int((dx / distance) * ENEMY_WALQER_PROJECTILE_SPEED),
            int((dy / distance) * ENEMY_WALQER_PROJECTILE_SPEED)
        )
        
        # Create projectile
        projectile = Projectile(
            position=self.position,
            direction=direction,
            owner=self,
            damage=self.damage,
            speed=ENEMY_WALQER_PROJECTILE_SPEED
        )
        
        self.projectiles.append(projectile)
    
    def _is_player_in_vision_cone(self, player_position: Vec2i) -> bool:
        """Check if player is within vision cone."""
        # Calculate angle to player
        dx = player_position.x - self.position.x
        dy = player_position.y - self.position.y
        angle_to_player = math.atan2(dy, dx)
        
        # Calculate enemy's facing angle
        facing_angle = 0 if self.direction == Direction.RIGHT else math.pi
        
        # Calculate angle difference
        angle_diff = abs(angle_to_player - facing_angle)
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        
        return angle_diff <= self.vision_cone_angle
    
    def update(self, delta_time: float) -> None:
        """Update enemy state and animations."""
        super().update(delta_time)
        
        # Update projectiles
        for projectile in self.projectiles:
            projectile.update(delta_time)
    
    def render(self, surface: pygame.Surface, camera_offset) -> None:
        """Render the enemy to the screen."""
        super().render(surface, camera_offset)
        
        # Render projectiles
        for projectile in self.projectiles:
            projectile.render(surface, camera_offset)
    
    def take_damage(self, amount: int, knockback: Optional[Vec2i] = None) -> None:
        """Apply damage to the enemy."""
        super().take_damage(amount, knockback)
        
        # If not dead, change to hurt state
        if self._state != EnemyState.DEAD:
            self.change_state(EnemyState.HURT)