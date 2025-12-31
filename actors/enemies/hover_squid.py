"""
HoverSquid enemy - A floating tentacled menace!
Uses qq-hover-squid.png (512x256 = 4x2 grid of 128x128)
"""

import pygame
import math
import random
from typing import Optional
from .base_enemy import BaseEnemy
from shared.types import Vec2i, Direction, EnemyState
from shared.constants import TILE_SIZE


# HoverSquid specific constants
HOVER_SQUID_HEALTH = 40
HOVER_SQUID_DAMAGE = 15
HOVER_SQUID_SPEED = 50
HOVER_SQUID_DETECTION_RANGE = 250
HOVER_SQUID_ATTACK_RANGE = 80
HOVER_SQUID_HOVER_HEIGHT = 32
HOVER_SQUID_BOB_SPEED = 2.0
HOVER_SQUID_BOB_AMPLITUDE = 8


class HoverSquid(BaseEnemy):
    """
    A floating squid enemy that hovers and bobs up and down.
    Attacks by swooping toward the player.
    """
    
    def __init__(self, position: Vec2i) -> None:
        """Initialize HoverSquid enemy."""
        super().__init__(
            position=position,
            health=HOVER_SQUID_HEALTH,
            damage=HOVER_SQUID_DAMAGE,
            speed=HOVER_SQUID_SPEED,
            attack_range=HOVER_SQUID_ATTACK_RANGE,
            detection_range=HOVER_SQUID_DETECTION_RANGE,
            sprite_key="hover_squid"
        )
        
        # Hover behavior
        self.base_y = position.y
        self.hover_timer = random.uniform(0, math.pi * 2)  # Random phase offset
        self.bob_speed = HOVER_SQUID_BOB_SPEED
        self.bob_amplitude = HOVER_SQUID_BOB_AMPLITUDE
        
        # Attack behavior
        self.attack_cooldown = 0.0
        self.attack_cooldown_duration = 2.0
        self.swoop_target: Optional[Vec2i] = None
        self.swoop_start: Optional[Vec2i] = None
        self.swoop_progress = 0.0
        self.swoop_duration = 0.5
        self.is_swooping = False
        
        # Patrol
        self.patrol_direction = Direction.RIGHT
        self.patrol_distance = 100
        self.start_x = position.x
        self.start_y = position.y  # For vertical patrol
        
        # Float positions for smooth movement
        self._float_x = float(position.x)
        self._float_y = float(position.y)
        
    def think(self, delta_time: float, player_position: Optional[Vec2i] = None) -> None:
        """Main AI thinking method."""
        # Update hover bob
        self._update_hover(delta_time)
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= delta_time
        
        # Update timers
        if self._hurt_timer > 0:
            self._hurt_timer -= delta_time
            if self._hurt_timer <= 0:
                # After hurt, turn around and look for player
                self._direction = Direction.LEFT if self._direction == Direction.RIGHT else Direction.RIGHT
                self.patrol_direction = self._direction
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
    
    def _update_hover(self, delta_time: float) -> None:
        """Update the hovering bob motion using float position."""
        if not self.is_swooping:
            self.hover_timer += delta_time * self.bob_speed
            bob_offset = math.sin(self.hover_timer) * self.bob_amplitude
            self._float_y = self.base_y + bob_offset
            self.position = Vec2i(int(self._float_x), int(self._float_y))
    
    def _handle_idle_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle idle state behavior."""
        if player_position and self.can_detect_player(player_position):
            self.change_state(EnemyState.CHASE)
        else:
            # Start patrolling
            self.change_state(EnemyState.PATROL)
    
    def _handle_patrol_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle patrol state behavior - fly in figure-8 pattern smoothly."""
        # Check for player
        if player_position and self.can_detect_player(player_position):
            self.change_state(EnemyState.CHASE)
            return
        
        # Smooth figure-8 / oval patrol pattern
        patrol_speed = 50.0  # pixels per second
        
        # Horizontal patrol using float position
        if self.patrol_direction == Direction.RIGHT:
            self._float_x += patrol_speed * delta_time
            if self._float_x >= self.start_x + self.patrol_distance:
                self.patrol_direction = Direction.LEFT
                self._direction = Direction.LEFT
            else:
                self._direction = Direction.RIGHT
        else:
            self._float_x -= patrol_speed * delta_time
            if self._float_x <= self.start_x - self.patrol_distance:
                self.patrol_direction = Direction.RIGHT
                self._direction = Direction.RIGHT
            else:
                self._direction = Direction.LEFT
        
        # Vertical patrol - sine wave based on horizontal position
        progress = (self._float_x - (self.start_x - self.patrol_distance)) / (2 * self.patrol_distance)
        vertical_offset = math.sin(progress * math.pi * 2) * 50  # 50 pixel vertical range
        self.base_y = self.start_y + vertical_offset
        
        # Update integer position for rendering
        self.position = Vec2i(int(self._float_x), int(self._float_y))
    
    def _handle_chase_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle chase state behavior with smooth movement."""
        if not player_position:
            self.change_state(EnemyState.PATROL)
            return
        
        # Check if in attack range
        distance = self._distance_to(player_position)
        if distance <= self._attack_range and self.attack_cooldown <= 0:
            self.change_state(EnemyState.ATTACK)
            self._start_swoop(player_position)
            return
        
        # Check if player escaped
        if not self.can_detect_player(player_position):
            self.change_state(EnemyState.PATROL)
            return
        
        # Float toward player smoothly
        chase_speed = 60.0  # pixels per second
        dx = player_position.x - self._float_x
        direction_x = 1 if dx > 0 else -1
        self._float_x += direction_x * chase_speed * delta_time
        
        # Update base_y to slowly approach player's height
        target_y = player_position.y - HOVER_SQUID_HOVER_HEIGHT
        if abs(self.base_y - target_y) > 4:
            y_direction = 1 if target_y > self.base_y else -1
            self.base_y += y_direction * chase_speed * 0.5 * delta_time
        
        # Update integer position
        self.position = Vec2i(int(self._float_x), int(self._float_y))
        
        # Update direction
        self._direction = Direction.RIGHT if dx > 0 else Direction.LEFT
    
    def _start_swoop(self, target: Vec2i) -> None:
        """Start a swoop attack toward target."""
        self.is_swooping = True
        self.swoop_start = Vec2i(self.position.x, self.position.y)
        self.swoop_target = target
        self.swoop_progress = 0.0
    
    def _handle_attack_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle attack state behavior - perform swoop attack."""
        if not self.is_swooping:
            self.change_state(EnemyState.CHASE)
            self.attack_cooldown = self.attack_cooldown_duration
            return
        
        # Update swoop progress
        self.swoop_progress += delta_time / self.swoop_duration
        
        if self.swoop_progress >= 1.0:
            # Swoop complete
            self.is_swooping = False
            self.attack_cooldown = self.attack_cooldown_duration
            # Return to base height
            if self.swoop_target:
                self.base_y = self.swoop_target.y - HOVER_SQUID_HOVER_HEIGHT * 2
            self.change_state(EnemyState.CHASE)
            return
        
        # Interpolate position with ease-in-out
        if self.swoop_start and self.swoop_target:
            t = self.swoop_progress
            # Ease-in-out cubic
            t = t * t * (3 - 2 * t)
            
            new_x = int(self.swoop_start.x + (self.swoop_target.x - self.swoop_start.x) * t)
            new_y = int(self.swoop_start.y + (self.swoop_target.y - self.swoop_start.y) * t)
            self.position = Vec2i(new_x, new_y)
    
    def _handle_hurt_state(self, delta_time: float) -> None:
        """Handle hurt state behavior."""
        # Timer is handled in think() - enemy turns around after hurt
        pass
    
    def _handle_dead_state(self, delta_time: float) -> None:
        """Handle dead state behavior."""
        if self._death_timer <= 0:
            self.destroy()
    
    def _distance_to(self, target: Vec2i) -> float:
        """Calculate distance to target."""
        dx = target.x - self.position.x
        dy = target.y - self.position.y
        return math.sqrt(dx * dx + dy * dy)
    
    def take_damage(self, amount: int, knockback: Optional[Vec2i] = None) -> None:
        """Apply damage to the enemy."""
        # Cancel swoop on damage
        self.is_swooping = False
        super().take_damage(amount, knockback)
    
    def get_animation_for_state(self) -> Optional[str]:
        """Get the animation name for the current state."""
        if self._state == EnemyState.ATTACK or self.is_swooping:
            return "attack"
        return "idle"
