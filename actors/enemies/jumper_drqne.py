import pygame
import random
import math
from typing import Optional, Tuple, List
from .base_enemy import BaseEnemy
from shared.types import Vec2i, Direction, EnemyState
from shared.constants import (
    ENEMY_JUMPER_HEALTH,
    ENEMY_JUMPER_DAMAGE,
    ENEMY_JUMPER_SPEED,
    ENEMY_JUMPER_JUMP_FORCE,
    ENEMY_JUMPER_JUMP_INTERVAL,
    ENEMY_JUMPER_DETECTION_RANGE,
    ENEMY_JUMPER_ATTACK_RANGE,
    TILE_SIZE
)
from core.resources import ResourceManager
from core.time import Time
from world.physics import PhysicsBody
from core.particles import ParticleSystem, ExplosionEmitter

class JumperDrqne(BaseEnemy):
    """Enemy that jumps at regular intervals and explodes on death."""
    
    def __init__(
        self,
        position: Vec2i,
        jump_interval: float = ENEMY_JUMPER_JUMP_INTERVAL,
        jump_force: float = ENEMY_JUMPER_JUMP_FORCE
    ) -> None:
        """
        Initialize JumperDrqne enemy.
        
        Args:
            position: Starting position (top-left corner)
            jump_interval: Time between jumps in seconds
            jump_force: Vertical force applied when jumping
        """
        super().__init__(
            position=position,
            health=ENEMY_JUMPER_HEALTH,
            damage=ENEMY_JUMPER_DAMAGE,
            speed=ENEMY_JUMPER_SPEED,
            attack_range=ENEMY_JUMPER_ATTACK_RANGE,
            detection_range=ENEMY_JUMPER_DETECTION_RANGE,
            sprite_key="jumper_drqne"
        )
        
        self.jump_interval = jump_interval
        self.jump_force = jump_force
        self.jump_timer = 0.0
        self.is_jumping = False
        self.jump_cooldown = 0.0
        self.jump_cooldown_duration = 0.5  # Cooldown after landing
        
        # Physics body for jumping
        self.physics_body = PhysicsBody(
            position=Vec2i(position.x, position.y),
            size=Vec2i(TILE_SIZE, TILE_SIZE)
        )
        
        # Jump target (for AI)
        self.jump_target: Optional[Vec2i] = None
        self.jump_prep_time = 0.0
        self.jump_prep_duration = 0.3  # Time to prepare before jumping
        
        # Particle system for jump effects
        self.particle_system: Optional[ParticleSystem] = None
        self.explosion_emitter: Optional[ExplosionEmitter] = None
        
        # Initialize state
        self.change_state(EnemyState.IDLE)
        
    def think(self, delta_time: float, player_position: Optional[Vec2i] = None) -> None:
        """
        Main AI thinking method.
        
        Args:
            delta_time: Time since last frame in seconds
            player_position: Current position of the player (if known)
        """
        super().think(delta_time, player_position)
        
        # Update timers
        self._update_timers(delta_time)
        
        # Handle current state
        if self.state == EnemyState.IDLE:
            self._handle_idle_state(delta_time, player_position)
        elif self.state == EnemyState.PATROL:
            self._handle_patrol_state(delta_time, player_position)
        elif self.state == EnemyState.CHASE:
            self._handle_chase_state(delta_time, player_position)
        elif self.state == EnemyState.ATTACK:
            self._handle_attack_state(delta_time, player_position)
        elif self.state == EnemyState.HURT:
            self._handle_hurt_state(delta_time)
        elif self.state == EnemyState.DEAD:
            self._handle_dead_state(delta_time)
            
    def _handle_idle_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle idle state behavior."""
        if player_position and self.can_detect_player(player_position):
            self.change_state(EnemyState.CHASE)
            return
            
        # Update jump timer
        self.jump_timer += delta_time
        if self.jump_timer >= self.jump_interval and self.jump_cooldown <= 0:
            self._prepare_jump()
            
    def _handle_patrol_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle patrol state behavior."""
        if player_position and self.can_detect_player(player_position):
            self.change_state(EnemyState.CHASE)
            return
            
        # Update jump timer
        self.jump_timer += delta_time
        if self.jump_timer >= self.jump_interval and self.jump_cooldown <= 0:
            self._prepare_jump()
            
    def _handle_chase_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle chase state behavior."""
        if not player_position:
            self.change_state(EnemyState.IDLE)
            return
            
        # Check if player is in attack range
        distance_to_player = math.sqrt(
            (player_position.x - self.position.x) ** 2 + 
            (player_position.y - self.position.y) ** 2
        )
        
        if distance_to_player <= self.attack_range:
            self.change_state(EnemyState.ATTACK)
            return
            
        # Update jump timer
        self.jump_timer += delta_time
        if self.jump_timer >= self.jump_interval and self.jump_cooldown <= 0:
            self._prepare_jump(player_position)
            
    def _handle_attack_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        """Handle attack state behavior."""
        if not player_position:
            self.change_state(EnemyState.IDLE)
            return
            
        # Check if player is still in attack range
        distance_to_player = math.sqrt(
            (player_position.x - self.position.x) ** 2 + 
            (player_position.y - self.position.y) ** 2
        )
        
        if distance_to_player > self.attack_range:
            self.change_state(EnemyState.CHASE)
            return
            
        # Update jump timer
        self.jump_timer += delta_time
        if self.jump_timer >= self.jump_interval and self.jump_cooldown <= 0:
            self._prepare_jump(player_position)
            
    def _handle_hurt_state(self, delta_time: float) -> None:
        """Handle hurt state behavior."""
        # After hurt animation, return to previous state
        if self.hurt_timer <= 0:
            self.change_state(EnemyState.CHASE)
            
    def _handle_dead_state(self, delta_time: float) -> None:
        """Handle dead state behavior."""
        # Create explosion on death
        if not self.explosion_emitter and self.particle_system:
            self.explosion_emitter = self.particle_system.create_explosion(
                (self.position.x + TILE_SIZE // 2, self.position.y + TILE_SIZE // 2)
            )
            
    def _prepare_jump(self, target: Optional[Vec2i] = None) -> None:
        """Prepare for a jump."""
        self.jump_target = target
        self.jump_prep_time = self.jump_prep_duration
        self.is_jumping = False
        
    def _perform_jump(self) -> None:
        """Perform the jump."""
        if self.jump_cooldown > 0:
            return
            
        # Apply jump force
        self.physics_body.velocity = Vec2i(
            self.physics_body.velocity.x,
            -self.jump_force
        )
        
        self.is_jumping = True
        self.jump_timer = 0.0
        
        # Create jump particles
        if self.particle_system:
            self._create_jump_particles()
            
    def _create_jump_particles(self) -> None:
        """Create particle effects for jumping."""
        if not self.particle_system:
            return
            
        # Create dust particles at feet
        for _ in range(5):
            x = self.position.x + random.randint(0, TILE_SIZE)
            y = self.position.y + TILE_SIZE
            self.particle_system.create_smoke_emitter((x, y))
            
    def _update_timers(self, delta_time: float) -> None:
        """Update all active timers."""
        super()._update_timers(delta_time)
        
        # Update jump preparation timer
        if self.jump_prep_time > 0:
            self.jump_prep_time -= delta_time
            if self.jump_prep_time <= 0 and not self.is_jumping:
                self._perform_jump()
                
        # Update jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= delta_time
            
        # Update physics
        self.physics_body.update(delta_time)
        
        # Check if landed
        if self.is_jumping and self.physics_body.velocity.y >= 0:
            # Simple ground check (would need collision system in real implementation)
            if self.physics_body.position.y >= self.position.y:
                self.is_jumping = False
                self.jump_cooldown = self.jump_cooldown_duration
                
                # Create landing particles
                if self.particle_system:
                    self._create_landing_particles()
                    
    def _create_landing_particles(self) -> None:
        """Create particle effects for landing."""
        if not self.particle_system:
            return
            
        # Create impact particles
        for _ in range(8):
            x = self.position.x + random.randint(0, TILE_SIZE)
            y = self.position.y + TILE_SIZE
            self.particle_system.create_smoke_emitter((x, y))
            
    def update(self, delta_time: float) -> None:
        """Update enemy state and animations."""
        super().update(delta_time)
        
        # Update position from physics
        if self.is_jumping:
            self.position = self.physics_body.position
            
        # Update animation based on state
        animation_name = self.get_animation_for_state()
        if animation_name:
            self.current_animation = animation_name
            
    def get_animation_for_state(self) -> Optional[str]:
        """Get animation name for current state."""
        if self.state == EnemyState.DEAD:
            return "dead"
        elif self.state == EnemyState.HURT:
            return "hurt"
        elif self.is_jumping:
            return "jump"
        elif self.jump_prep_time > 0:
            return "prepare"
        else:
            return "idle"
            
    def render(self, surface: pygame.Surface, camera_offset) -> None:
        """Render the enemy to the screen."""
        super().render(surface, camera_offset)
        
        # Render health bar
        self.render_health_bar(surface, camera_offset)
        
    def take_damage(self, amount: int, knockback: Optional[Vec2i] = None) -> None:
        """Apply damage to the enemy."""
        super().take_damage(amount, knockback)
        
        # Apply knockback to physics
        if knockback and self.physics_body:
            self.physics_body.velocity = Vec2i(
                self.physics_body.velocity.x + knockback.x,
                self.physics_body.velocity.y + knockback.y
            )
            
    def set_particle_system(self, particle_system: ParticleSystem) -> None:
        """Set particle system for visual effects."""
        self.particle_system = particle_system
        
    def get_jump_progress(self) -> float:
        """Get jump preparation progress (0 to 1)."""
        if self.jump_prep_time <= 0:
            return 0.0
        return 1.0 - (self.jump_prep_time / self.jump_prep_duration)
        
    def is_preparing_jump(self) -> bool:
        """Check if enemy is preparing to jump."""
        return self.jump_prep_time > 0
        
    def can_jump(self) -> bool:
        """Check if enemy can jump."""
        return self.jump_cooldown <= 0 and not self.is_jumping