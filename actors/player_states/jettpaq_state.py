import pygame
import math
import random
from typing import Optional, Tuple
from .base_state import BasePlayerState
from shared.constants import (
    JETTPAQ_DASH_SPEED,
    JETTPAQ_DASH_DURATION,
    JETTPAQ_COOLDOWN,
    JETTPAQ_FUEL_MAX,
    JETTPAQ_FUEL_CONSUMPTION_RATE,
    JETTPAQ_FUEL_RECHARGE_RATE,
    JETTPAQ_FUEL_RECHARGE_DELAY,
    PLAYER_MOVE_SPEED,
    GRAVITY,
    PLAYER_JUMP_FORCE,
    PLAYER_TERMINAL_VELOCITY
)
from shared.types import Direction
from core.time import Time
from core.input import InputManager
from core.particles import ParticleSystem, Particle

class JettpaqState(BasePlayerState):
    """Player state for JettPaQ powerup with dash mechanics."""
    
    def __init__(self, player: 'Player'):
        """
        Initialize JettPaQ state.
        
        Args:
            player: The player instance this state belongs to
        """
        super().__init__(player)
        self._dash_active = False
        self._dash_direction = Direction.RIGHT
        self._dash_timer = 0.0
        self._cooldown_timer = 0.0
        self._fuel = JETTPAQ_FUEL_MAX
        self._fuel_recharge_delay_timer = 0.0
        self._particle_system = None
        self._trail_particles = []
        self._dash_particles = []
        self._initialize_particle_system()
        self._update_player_appearance()
    
    def _initialize_particle_system(self) -> None:
        """Initialize particle system for visual effects."""
        self._particle_system = ParticleSystem()
    
    def _update_player_appearance(self) -> None:
        """Update player appearance for JettPaQ state."""
        # In a full implementation, this would change the player's sprite
        # to show the jetpack visually
        pass
    
    def enter(self) -> None:
        """Initialize JettPaQ state."""
        self._dash_active = False
        self._dash_timer = 0.0
        self._cooldown_timer = 0.0
        self._fuel = JETTPAQ_FUEL_MAX
        self._fuel_recharge_delay_timer = 0.0
        self._clear_particles()
    
    def exit(self) -> None:
        """Clean up JettPaQ state."""
        self._dash_active = False
        self._clear_particles()
    
    def update(self, dt: float) -> None:
        """
        Update JettPaQ state logic.
        
        Args:
            dt: Delta time in seconds
        """
        self._update_timers(dt)
        self._update_fuel(dt)
        self._update_dash(dt)
        
        if not self._dash_active:
            self._apply_normal_physics(dt)
        
        self._update_particles(dt)
        self._check_state_transitions()
    
    def _update_timers(self, dt: float) -> None:
        """Update all active timers."""
        if self._dash_active:
            self._dash_timer -= dt
            if self._dash_timer <= 0:
                self._end_dash()
        
        if self._cooldown_timer > 0:
            self._cooldown_timer -= dt
        
        if self._fuel_recharge_delay_timer > 0:
            self._fuel_recharge_delay_timer -= dt
    
    def _update_fuel(self, dt: float) -> None:
        """Update fuel management."""
        if self._dash_active:
            # Consume fuel during dash
            fuel_consumed = JETTPAQ_FUEL_CONSUMPTION_RATE * dt
            self._fuel = max(0, self._fuel - fuel_consumed)
            self._fuel_recharge_delay_timer = JETTPAQ_FUEL_RECHARGE_DELAY
        elif self._fuel_recharge_delay_timer <= 0 and self._fuel < JETTPAQ_FUEL_MAX:
            # Recharge fuel when not dashing and delay has passed
            fuel_recharged = JETTPAQ_FUEL_RECHARGE_RATE * dt
            self._fuel = min(JETTPAQ_FUEL_MAX, self._fuel + fuel_recharged)
    
    def _update_dash(self, dt: float) -> None:
        """Update dash movement and effects."""
        if self._dash_active:
            # Apply dash movement
            dash_speed = JETTPAQ_DASH_SPEED
            if self._dash_direction == Direction.LEFT:
                self.player.velocity.x = -dash_speed
            elif self._dash_direction == Direction.RIGHT:
                self.player.velocity.x = dash_speed
            
            # Create dash particles
            self._create_dash_particles()
    
    def _apply_normal_physics(self, dt: float) -> None:
        """Apply normal physics when not dashing."""
        # Apply gravity
        self.player.velocity.y += GRAVITY * dt
        
        # Clamp terminal velocity
        if self.player.velocity.y > PLAYER_TERMINAL_VELOCITY:
            self.player.velocity.y = PLAYER_TERMINAL_VELOCITY
        
        # Create trail particles when moving
        if abs(self.player.velocity.x) > 0.1:
            self._create_trail_particles()
    
    def _update_particles(self, dt: float) -> None:
        """Update particle effects."""
        if self._particle_system:
            self._particle_system.update()
    
    def _check_state_transitions(self) -> None:
        """Check for transitions to other states."""
        # Check if fuel is depleted and dash is not active
        if self._fuel <= 0 and not self._dash_active:
            self._change_state(type(self.player.normal_state))
    
    def handle_input(self) -> None:
        """Handle input in JettPaQ state."""
        input_manager = InputManager.get_instance()
        
        # Check for dash activation
        if input_manager.is_action_pressed("dash") and self._can_dash():
            self._activate_dash()
        
        # Handle movement when not dashing
        if not self._dash_active:
            if input_manager.is_action_down("move_left"):
                self._move(Direction.LEFT)
            elif input_manager.is_action_down("move_right"):
                self._move(Direction.RIGHT)
            
            if input_manager.is_action_pressed("jump"):
                self._jump()
    
    def _can_dash(self) -> bool:
        """Check if dash can be activated."""
        return (not self._dash_active and 
                self._cooldown_timer <= 0 and 
                self._fuel > JETTPAQ_FUEL_MAX * 0.1)  # Need at least 10% fuel
    
    def _activate_dash(self) -> None:
        """Activate dash ability."""
        self._dash_active = True
        self._dash_timer = JETTPAQ_DASH_DURATION
        self._cooldown_timer = JETTPAQ_COOLDOWN
        
        # Determine dash direction based on input or facing
        input_manager = InputManager.get_instance()
        if input_manager.is_action_down("move_left"):
            self._dash_direction = Direction.LEFT
        elif input_manager.is_action_down("move_right"):
            self._dash_direction = Direction.RIGHT
        else:
            # Use player's facing direction
            self._dash_direction = self.player.facing_direction
        
        self._create_dash_effect()
    
    def _end_dash(self) -> None:
        """End dash ability."""
        self._dash_active = False
        self._dash_timer = 0.0
    
    def _move(self, direction: Direction) -> None:
        """
        Move player in specified direction.
        
        Args:
            direction: Direction to move
        """
        move_speed = PLAYER_MOVE_SPEED
        if direction == Direction.LEFT:
            self.player.velocity.x = -move_speed
            self.player.facing_direction = Direction.LEFT
        elif direction == Direction.RIGHT:
            self.player.velocity.x = move_speed
            self.player.facing_direction = Direction.RIGHT
    
    def _jump(self) -> bool:
        """
        Make player jump.
        
        Returns:
            True if jump was successful
        """
        if self.player.is_on_ground:
            self.player.velocity.y = PLAYER_JUMP_FORCE  # Already negative
            return True
        return False
    
    def _create_dash_effect(self) -> None:
        """Create visual effect for dash activation."""
        # Create a burst of particles
        for _ in range(20):
            angle = math.radians(random.uniform(0, 360))
            speed = random.uniform(50, 200)
            velocity = (
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            particle = Particle(
                position=(self.player.position[0], self.player.position[1]),
                velocity=velocity,
                color=(100, 200, 255),  # Blueish color for jetpack
                size=random.randint(2, 6),
                lifetime=random.uniform(0.3, 0.8),
                fade_out=True,
                gravity=0.0
            )
            self._dash_particles.append(particle)
    
    def _create_dash_particles(self) -> None:
        """Create particles during dash."""
        if random.random() < 0.3:  # 30% chance per frame
            offset_x = 0
            if self._dash_direction == Direction.LEFT:
                offset_x = 10
            elif self._dash_direction == Direction.RIGHT:
                offset_x = -10
            
            particle = Particle(
                position=(
                    self.player.position[0] + offset_x,
                    self.player.position[1] + random.uniform(-5, 5)
                ),
                velocity=(
                    random.uniform(-20, 20),
                    random.uniform(-10, 10)
                ),
                color=(150, 220, 255),  # Light blue
                size=random.randint(3, 8),
                lifetime=random.uniform(0.2, 0.5),
                fade_out=True,
                gravity=0.1
            )
            self._dash_particles.append(particle)
    
    def _create_trail_particles(self) -> None:
        """Create trail particles when moving."""
        if random.random() < 0.2:  # 20% chance per frame
            offset_x = 0
            if self.player.facing_direction == Direction.LEFT:
                offset_x = 5
            elif self.player.facing_direction == Direction.RIGHT:
                offset_x = -5
            
            particle = Particle(
                position=(
                    self.player.position[0] + offset_x,
                    self.player.position[1] + random.uniform(-10, 10)
                ),
                velocity=(
                    random.uniform(-10, 10),
                    random.uniform(-5, 5)
                ),
                color=(200, 230, 255),  # Very light blue
                size=random.randint(2, 5),
                lifetime=random.uniform(0.3, 0.7),
                fade_out=True,
                gravity=0.05
            )
            self._trail_particles.append(particle)
    
    def _clear_particles(self) -> None:
        """Clear all particles."""
        self._dash_particles.clear()
        self._trail_particles.clear()
    
    def get_state_name(self) -> str:
        """
        Get state name.
        
        Returns:
            String identifier for this state
        """
        return "JETTPAQ"
    
    def render_particles(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """
        Render particle effects.
        
        Args:
            surface: Surface to render to
            camera_offset: Camera offset for positioning
        """
        # Render dash particles
        for particle in self._dash_particles:
            if particle.is_active():
                particle.render(surface, camera_offset)
        
        # Render trail particles
        for particle in self._trail_particles:
            if particle.is_active():
                particle.render(surface, camera_offset)
        
        # Clean up inactive particles
        self._dash_particles = [p for p in self._dash_particles if p.is_active()]
        self._trail_particles = [p for p in self._trail_particles if p.is_active()]
    
    def get_fuel_percentage(self) -> float:
        """
        Get current fuel percentage.
        
        Returns:
            Fuel percentage (0.0 to 1.0)
        """
        return self._fuel / JETTPAQ_FUEL_MAX
    
    def is_dash_available(self) -> bool:
        """
        Check if dash is available.
        
        Returns:
            True if dash can be activated
        """
        return self._can_dash()
    
    def get_cooldown_percentage(self) -> float:
        """
        Get cooldown progress percentage.
        
        Returns:
            Cooldown percentage (0.0 to 1.0)
        """
        if self._cooldown_timer <= 0:
            return 0.0
        return 1.0 - (self._cooldown_timer / JETTPAQ_COOLDOWN)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the jettpaq state player."""
        self.player.render_current_animation(surface, camera_offset)
        self.render_particles(surface, camera_offset)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the jettpaq state player."""
        self.player.render_current_animation(surface, camera_offset)
        self.render_particles(surface, camera_offset)