"""
BriqBeaver enemy class.
Enemy that throws arcing briQ projectiles at the player.
"""

import pygame
import math
import random
from typing import Optional, Tuple, List

from .base_enemy import BaseEnemy
from shared.types import Vec2i, EnemyState, Direction
from shared.constants import (
    ENEMY_BRIQ_BEAVER_HEALTH,
    ENEMY_BRIQ_BEAVER_DAMAGE,
    ENEMY_BRIQ_BEAVER_SPEED,
    ENEMY_BRIQ_BEAVER_DETECTION_RANGE,
    ENEMY_BRIQ_BEAVER_ATTACK_RANGE,
    ENEMY_BRIQ_BEAVER_THROW_COOLDOWN,
    ENEMY_BRIQ_BEAVER_THROW_WINDUP,
    ENEMY_BRIQ_BEAVER_PROJECTILE_SPEED,
    ENEMY_BRIQ_BEAVER_PROJECTILE_GRAVITY,
    ENEMY_BRIQ_BEAVER_PROJECTILE_DAMAGE,
    ENEMY_BRIQ_BEAVER_PROJECTILE_RANGE,
    TILE_SIZE
)
from core.resources import ResourceManager
from core.time import Time
from world.physics import PhysicsBody
from actors.projectile import Projectile
from core.particles import ParticleSystem, Particle


class BriqBeaver(BaseEnemy):
    """Enemy that throws arcing briQ projectiles at the player."""
    
    def __init__(
        self,
        position: Vec2i,
        patrol_range: int = 100,
        direction: Direction = Direction.RIGHT
    ) -> None:
        """
        Initialize BriqBeaver enemy.
        
        Args:
            position: Starting position (top-left corner)
            patrol_range: How far the enemy patrols from starting position
            direction: Initial facing direction
        """
        super().__init__(
            position=position,
            health=ENEMY_BRIQ_BEAVER_HEALTH,
            damage=ENEMY_BRIQ_BEAVER_DAMAGE,
            speed=ENEMY_BRIQ_BEAVER_SPEED,
            attack_range=ENEMY_BRIQ_BEAVER_ATTACK_RANGE,
            detection_range=ENEMY_BRIQ_BEAVER_DETECTION_RANGE,
            sprite_key="briq_beaver"
        )
        
        self.patrol_range = patrol_range
        self.initial_direction = direction
        self.patrol_target = self._calculate_patrol_target(direction)
        self.patrol_points = [
            Vec2i(position.x - patrol_range, position.y),
            Vec2i(position.x + patrol_range, position.y)
        ]
        self.current_patrol_index = 0 if direction == Direction.LEFT else 1
        
        # Throwing mechanics
        self.throw_cooldown_timer = 0.0
        self.windup_timer = 0.0
        self.is_winding_up = False
        self.windup_target = None
        
        # Projectile management
        self.active_projectiles: List[Projectile] = []
        self.particle_system: Optional[ParticleSystem] = None
        self.windup_particles: List[Particle] = []
        
        # Animation states
        self.windup_progress = 0.0
        
    def _calculate_patrol_target(self, direction: Direction) -> Vec2i:
        """Calculate patrol target based on direction and range."""
        if direction == Direction.LEFT:
            return Vec2i(self.position.x - self.patrol_range, self.position.y)
        else:
            return Vec2i(self.position.x + self.patrol_range, self.position.y)
    
    def think(self, delta_time: float, player_position: Optional[Vec2i] = None) -> None:
        """
        Main AI thinking method.
        
        Args:
            delta_time: Time since last frame in seconds
            player_position: Current position of the player (if known)
        """
        self._update_timers(delta_time)
        
        if self.state == EnemyState.DEAD:
            self._handle_dead_state(delta_time)
            return
            
        if self.state == EnemyState.HURT:
            self._handle_hurt_state(delta_time)
            return
            
        if self.is_winding_up:
            self._update_windup(delta_time, player_position)
            return
            
        if player_position and self.can_detect_player(player_position):
            distance_to_player = math.sqrt(
                (player_position.x - self.position.x) ** 2 +
                (player_position.y - self.position.y) ** 2
            )
            
            if distance_to_player <= self.attack_range and self.throw_cooldown_timer <= 0:
                self._start_windup(player_position)
            elif distance_to_player <= self.detection_range:
                self.change_state(EnemyState.CHASE)
                self._handle_chase_state(delta_time, player_position)
            else:
                self.change_state(EnemyState.PATROL)
                self._handle_patrol_state(delta_time, player_position)
        else:
            self.change_state(EnemyState.PATROL)
            self._handle_patrol_state(delta_time, player_position)
    
    def _handle_idle_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle idle state behavior."""
        # BriqBeaver doesn't have an idle state, defaults to patrol
        self.change_state(EnemyState.PATROL)
    
    def _handle_patrol_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle patrol state behavior."""
        target = self.patrol_points[self.current_patrol_index]
        distance_to_target = math.sqrt(
            (target.x - self.position.x) ** 2 +
            (target.y - self.position.y) ** 2
        )
        
        if distance_to_target < 5:  # Reached patrol point
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            target = self.patrol_points[self.current_patrol_index]
            
            # Update direction based on movement
            if target.x > self.position.x:
                self.direction = Direction.RIGHT
            else:
                self.direction = Direction.LEFT
        
        # Move toward patrol point
        direction_x = 1 if target.x > self.position.x else -1
        self.move(Vec2i(direction_x * int(self.speed * delta_time * 60), 0))
    
    def _handle_chase_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle chase state behavior."""
        if not player_position:
            return
            
        # Move toward player
        direction_x = 1 if player_position.x > self.position.x else -1
        self.move(Vec2i(direction_x * int(self.speed * delta_time * 60), 0))
        
        # Update direction
        self.direction = Direction.RIGHT if direction_x > 0 else Direction.LEFT
    
    def _handle_attack_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle attack state behavior."""
        # Attack state is handled in think() when winding up
        pass
    
    def _handle_hurt_state(self, delta_time: float) -> None:
        """Handle hurt state behavior."""
        self.hurt_timer -= delta_time
        if self.hurt_timer <= 0:
            self.change_state(EnemyState.PATROL)
    
    def _handle_dead_state(self, delta_time: float) -> None:
        """Handle dead state behavior."""
        # Clean up projectiles
        for projectile in self.active_projectiles:
            projectile.destroy()
        self.active_projectiles.clear()
        
        # Clean up particles
        self.windup_particles.clear()
    
    def _start_windup(self, player_position: Vec2i) -> None:
        """Start windup animation before throwing."""
        self.is_winding_up = True
        self.windup_timer = ENEMY_BRIQ_BEAVER_THROW_WINDUP
        self.windup_target = player_position
        self.windup_progress = 0.0
        self.change_state(EnemyState.ATTACK)
        self._create_windup_particles()
    
    def _update_windup(self, delta_time: float, player_position: Vec2i) -> None:
        """Update windup animation."""
        self.windup_timer -= delta_time
        self.windup_progress = 1.0 - (self.windup_timer / ENEMY_BRIQ_BEAVER_THROW_WINDUP)
        
        # Update windup particles
        self._update_windup_particles(delta_time)
        
        if self.windup_timer <= 0:
            self.is_winding_up = False
            self._execute_throw(player_position)
            self.throw_cooldown_timer = ENEMY_BRIQ_BEAVER_THROW_COOLDOWN
            self.change_state(EnemyState.PATROL)
    
    def _execute_throw(self, target_position: Vec2i) -> None:
        """Throw a briQ projectile at the target position."""
        # Calculate throw direction and velocity
        dx = target_position.x - self.position.x
        dy = target_position.y - self.position.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
            
        # Normalize direction
        dir_x = dx / distance
        dir_y = dy / distance
        
        # Create projectile with arcing trajectory
        projectile = Projectile(
            position=Vec2i(self.position.x + (self.direction.value * 20), self.position.y),
            direction=Vec2i(int(dir_x * 100), int(dir_y * 100)),  # Initial direction
            owner=self,
            damage=ENEMY_BRIQ_BEAVER_PROJECTILE_DAMAGE,
            speed=ENEMY_BRIQ_BEAVER_PROJECTILE_SPEED,
            lifetime=ENEMY_BRIQ_BEAVER_PROJECTILE_RANGE / ENEMY_BRIQ_BEAVER_PROJECTILE_SPEED,
            size=16,
            color=(255, 200, 50)  # Briq yellow color
        )
        
        # Apply gravity to projectile
        projectile.set_penetrating(False)
        self.active_projectiles.append(projectile)
        
        # Create throw visual effect
        self._create_throw_effect()
    
    def _create_windup_particles(self) -> None:
        """Create particles for windup animation."""
        self.windup_particles.clear()
        
        # Create particles around the beaver
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(10, 30)
            x = self.position.x + radius * math.cos(angle)
            y = self.position.y + radius * math.sin(angle)
            
            particle = Particle(
                position=(x, y),
                velocity=(0, 0),
                color=(255, 200, 50, 200),  # Semi-transparent yellow
                size=random.randint(2, 5),
                lifetime=ENEMY_BRIQ_BEAVER_THROW_WINDUP,
                fade_out=True,
                gravity=0.0
            )
            self.windup_particles.append(particle)
    
    def _update_windup_particles(self, delta_time: float) -> None:
        """Update windup particles."""
        # Move particles toward center during windup
        for particle in self.windup_particles:
            # Calculate direction to center
            dx = self.position.x - particle.position[0]
            dy = self.position.y - particle.position[1]
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 0:
                # Move particle toward center
                speed = 50.0 * self.windup_progress  # Faster as windup progresses
                particle.velocity = (
                    (dx / dist) * speed,
                    (dy / dist) * speed
                )
            
            # Update particle
            particle.update()
        
        # Remove dead particles
        self.windup_particles = [p for p in self.windup_particles if p.lifetime > 0]
    
    def _create_throw_effect(self) -> None:
        """Create visual effect when throwing."""
        if self.particle_system:
            # Create explosion emitter at throw position
            emitter = self.particle_system.create_explosion(
                (self.position.x + (self.direction.value * 20), self.position.y)
            )
            emitter.create_explosion()
    
    def _update_timers(self, delta_time: float) -> None:
        """Update all active timers."""
        super()._update_timers(delta_time)
        
        if self.throw_cooldown_timer > 0:
            self.throw_cooldown_timer -= delta_time
    
    def update(self, delta_time: float) -> None:
        """Update enemy state and animations."""
        super().update(delta_time)
        
        # Update projectiles
        for projectile in self.active_projectiles[:]:
            projectile.update(delta_time)
            if not projectile.is_active():
                self.active_projectiles.remove(projectile)
        
        # Update animation based on state
        if self.is_winding_up:
            self._update_windup_animation(delta_time)
        else:
            self._update_normal_animation(delta_time)
    
    def _update_windup_animation(self, delta_time: float) -> None:
        """Update windup animation."""
        # Windup animation would go here
        # For now, just update the animation timer
        pass
    
    def _update_normal_animation(self, delta_time: float) -> None:
        """Update normal movement animation."""
        # Normal movement animation would go here
        pass
    
    def get_animation_for_state(self) -> Optional[str]:
        """Get animation name for current state."""
        if self.is_winding_up:
            return "windup"
        elif self.state == EnemyState.HURT:
            return "hurt"
        elif self.state == EnemyState.DEAD:
            return "dead"
        elif self.state == EnemyState.CHASE or self.state == EnemyState.PATROL:
            return "walk"
        else:
            return "idle"
    
    def render(self, surface: pygame.Surface, camera_offset) -> None:
        """Render the enemy to the screen."""
        super().render(surface, camera_offset)
        
        # Handle tuple or Vector2
        if hasattr(camera_offset, 'x'):
            cam_tuple = (camera_offset.x, camera_offset.y)
        else:
            cam_tuple = (camera_offset[0], camera_offset[1])
        
        # Render windup particles
        for particle in self.windup_particles:
            particle.render(surface, cam_tuple)
        
        # Render projectiles
        for projectile in self.active_projectiles:
            projectile.render(surface, camera_offset)
    
    def take_damage(self, amount: int, knockback: Optional[Vec2i] = None) -> None:
        """Apply damage to the enemy."""
        super().take_damage(amount, knockback)
        
        # Interrupt windup if taking damage
        if self.is_winding_up:
            self.is_winding_up = False
            self.windup_particles.clear()
    
    def set_particle_system(self, particle_system: ParticleSystem) -> None:
        """Set particle system for visual effects."""
        self.particle_system = particle_system
    
    def get_projectiles(self) -> List[Projectile]:
        """Get all active projectiles."""
        return self.active_projectiles.copy()
    
    def handle_collision_with_projectile(self, projectile_index: int) -> None:
        """Handle collision between projectile and environment."""
        if 0 <= projectile_index < len(self.active_projectiles):
            self.active_projectiles[projectile_index].destroy()
            self.active_projectiles.pop(projectile_index)
    
    def reset(self) -> None:
        """Reset briq beaver to initial state."""
        super().reset()
        
        self.is_winding_up = False
        self.windup_timer = 0.0
        self.throw_cooldown_timer = 0.0
        self.windup_progress = 0.0
        self.windup_target = None
        
        # Clear projectiles and particles
        for projectile in self.active_projectiles:
            projectile.destroy()
        self.active_projectiles.clear()
        self.windup_particles.clear()
        
        # Reset patrol
        self.current_patrol_index = 0 if self.initial_direction == Direction.LEFT else 1
        self.patrol_target = self._calculate_patrol_target(self.initial_direction)