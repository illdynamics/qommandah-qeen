import pygame
import math
from typing import Optional, Tuple
from .base_state import BasePlayerState
from shared.constants import (
    GRAVITY,
    PLAYER_JUMP_FORCE,
    PLAYER_MOVE_SPEED,
    PLAYER_TERMINAL_VELOCITY,
    JUMPUPSTIQ_BOUNCE_FORCE,
    JUMPUPSTIQ_BASS_BLAST_FORCE,
    JUMPUPSTIQ_BASS_BLAST_RADIUS,
    JUMPUPSTIQ_BOUNCE_DAMPING,
    JUMPUPSTIQ_HORIZONTAL_BOOST
)
from shared.types import Direction
from core.time import Time
from core.particles import ParticleSystem
from core.input import InputManager

class JumpUpStiqState(BasePlayerState):
    """Player state for Jumpupstiq powerup with pogo bounce mechanics."""
    def __init__(self, player: 'Player'):
        """
        Initialize jumpupstiq state.
        
        Args:
            player: The player instance this state belongs to
        """
        super().__init__(player)
        self.is_bouncing = False
        self.bounce_timer = 0.0
        self.bass_blast_cooldown = 0.0
        self.special_bounce_available = True
        self.particle_system = None

    def enter(self) -> None:
        """Initialize jumpupstiq state."""
        super().enter()
        self.is_bouncing = False
        self.bounce_timer = 0.0
        self.bass_blast_cooldown = 0.0
        self.special_bounce_available = True
        self._update_animation()

    def exit(self) -> None:
        """Clean up jumpupstiq state."""
        self._clear_particles()

    def update(self, dt: float) -> None:
        """Update jumpupstiq state logic.
        
        Args:
            dt: Delta time in seconds
        """
        super().update(dt)
        self._update_timers(dt)
        self._apply_gravity(dt)
        self._check_ground_collision()
        self._update_particles(dt)
        self._update_animation()

    def _apply_gravity(self, dt: float) -> None:
        """Apply gravity to player."""
        self.player.velocity.y += GRAVITY * dt
        # Clamp to terminal velocity
        if self.player.velocity.y > PLAYER_TERMINAL_VELOCITY:
            self.player.velocity.y = PLAYER_TERMINAL_VELOCITY

    def _check_ground_collision(self) -> None:
        """Check for ground collision."""
        from shared.constants import TILE_SIZE
        
        if self.player._collision and hasattr(self.player._collision, 'tilemap') and self.player._collision.tilemap:
            tilemap = self.player._collision.tilemap
            # Check ground below player feet
            feet_y = int((self.player.position.y + self.player.size.y) // TILE_SIZE)
            left_x = int(self.player.position.x // TILE_SIZE)
            right_x = int((self.player.position.x + self.player.size.x - 1) // TILE_SIZE)
            
            if self.player.velocity.y >= 0:
                for tx in range(left_x, right_x + 1):
                    if 0 <= tx < tilemap.width and 0 <= feet_y < tilemap.height:
                        if tilemap.is_solid(tx, feet_y):
                            self.player.position.y = feet_y * TILE_SIZE - self.player.size.y
                            self.player.velocity.y = 0
                            self.is_bouncing = False
                            self.player._on_ground = True
                            if not self.special_bounce_available:
                                self.special_bounce_available = True
                            return
            self.player._on_ground = False
        else:
            # Fallback ground check
            if self.player.position.y >= self.player.ground_level - self.player.size.y:
                self.player.position.y = self.player.ground_level - self.player.size.y
                self.player.velocity.y = 0
                self.is_bouncing = False
                self.player._on_ground = True
                if not self.special_bounce_available:
                    self.special_bounce_available = True

    def _update_timers(self, dt: float) -> None:
        """Update cooldown timers."""
        if self.bounce_timer > 0:
            self.bounce_timer -= dt
        if self.bass_blast_cooldown > 0:
            self.bass_blast_cooldown -= dt

    def handle_input(self) -> None:
        """Handle input for jumpupstiq state."""
        input_manager = InputManager.get_instance()
        
        # Use is_action_down for continuous movement
        if input_manager.is_action_down("move_left"):
            self._move_with_boost(Direction.LEFT)
        elif input_manager.is_action_down("move_right"):
            self._move_with_boost(Direction.RIGHT)
        else:
            # Apply friction when not moving
            self.player.velocity.x *= 0.85
        
        if input_manager.is_action_pressed("jump"):
            self._perform_bounce()
        
        if input_manager.is_action_pressed("special") and self.bass_blast_cooldown <= 0:
            self._perform_bass_blast()
        
        if input_manager.is_action_pressed("attack") and self.special_bounce_available:
            self._perform_special_bounce()

    def _move_with_boost(self, direction: Direction) -> None:
        """Move player with horizontal boost.
        
        Args:
            direction: Direction to move
        """
        boost_multiplier = JUMPUPSTIQ_HORIZONTAL_BOOST
        if direction == Direction.LEFT:
            self.player.velocity.x = -PLAYER_MOVE_SPEED * boost_multiplier
            self.player.facing_direction = Direction.LEFT
        elif direction == Direction.RIGHT:
            self.player.velocity.x = PLAYER_MOVE_SPEED * boost_multiplier
            self.player.facing_direction = Direction.RIGHT
        self._update_animation()

    def _perform_bounce(self) -> None:
        """Perform a bounce off the ground."""
        if not self.is_bouncing and self.bounce_timer <= 0:
            self.player.velocity.y = -JUMPUPSTIQ_BOUNCE_FORCE
            self.is_bouncing = True
            self.bounce_timer = 0.3
            self._create_bounce_particles(1.0)
            self._update_animation()

    def _perform_bass_blast(self) -> None:
        """Perform Bass Blast - powerful downward slam."""
        if self.player.velocity.y > 0:
            self.player.velocity.y = JUMPUPSTIQ_BASS_BLAST_FORCE
            self.bass_blast_cooldown = 2.0
            self._create_shockwave_particles()
            self._damage_enemies_in_radius()
            self._update_animation()

    def _perform_special_bounce(self) -> None:
        """Perform a special bounce with extra height."""
        if self.special_bounce_available:
            self.player.velocity.y = -JUMPUPSTIQ_BOUNCE_FORCE * 1.5
            self.is_bouncing = True
            self.special_bounce_available = False
            self._create_bounce_particles(2.0)
            self._update_animation()

    def _create_bounce_particles(self, intensity: float = 1.0) -> None:
        """Create particle system for bounce effects.
        
        Args:
            intensity: Particle effect intensity multiplier
        """
        if self.particle_system:
            # Create bounce particles at player position
            pass

    def _create_shockwave_particles(self) -> None:
        """Create shockwave particles for bass blast."""
        if self.particle_system:
            # Create shockwave particles
            pass

    def _damage_enemies_in_radius(self) -> None:
        """Damage enemies within bass blast radius."""
        # Implementation would check for enemies in radius
        pass

    def _perform_attack(self) -> None:
        """Perform attack action."""
        # JumpUpStiq specific attack
        pass

    def _update_particles(self, dt: float) -> None:
        """Update particle effects."""
        if self.particle_system:
            self.particle_system.update(dt)

    def _clear_particles(self) -> None:
        """Clear all particles."""
        if self.particle_system:
            self.particle_system.clear_all()

    def get_state_name(self) -> str:
        """Get state name.
        
        Returns:
            String identifier for this state
        """
        return "JumpUpStiqState"

    def render_particles(self, surface: pygame.Surface, camera_offset: tuple) -> None:
        """Render bounce particles.
        
        Args:
            surface: Surface to render to
            camera_offset: Camera offset for positioning
        """
        if self.particle_system:
            self.particle_system.render(surface, camera_offset)

    def _update_animation(self) -> None:
        """Update player animation based on state - use pogo sprites!"""
        if self.is_bouncing or self.player.velocity.y < -10:
            # Bouncing or moving up - use pogo_bounce
            animation_name = 'pogo_bounce'
        elif self.player.velocity.y > 50:
            # Falling - use pogo_bounce (falling frame)
            animation_name = 'pogo_bounce'
        elif abs(self.player.velocity.x) > 0.1:
            # Moving horizontally - use pogo_idle (it has movement)
            animation_name = 'pogo_idle'
        else:
            # Standing still on pogo - use pogo_idle
            animation_name = 'pogo_idle'
        
        if hasattr(self.player, 'current_animation') and self.player.current_animation != animation_name:
            self.player.current_animation = animation_name
            if hasattr(self.player, 'animation_timer'):
                self.player.animation_timer = 0.0

    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the jumpupstiq state player."""
        self.player.render_current_animation(surface, camera_offset)
        self.render_particles(surface, camera_offset)