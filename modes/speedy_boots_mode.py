import pygame
from typing import Any, Dict, Optional, List, Tuple
from modes.base_mode import BaseMode
from shared.wonqmode_data import WoNQModeType, WoNQModeConfig
from shared.constants import PLAYER_MOVE_SPEED, PLAYER_ACCELERATION
from core.particles import ParticleSystem, Particle

class SpeedyBootsMode(BaseMode):
    """Mode that doubles player movement speed and acceleration."""
    def __init__(self):
        """Initialize Speedy Boots mode."""
        config = WoNQModeConfig(
            mode_type=WoNQModeType.SPEEDY_BOOTS,
            name="Speedy Boots",
            description="Doubles player movement speed and acceleration",
            duration=30.0,
            cooldown=60.0,
            visual_effects=True,
            speed_multiplier=2.0
        )
        super().__init__(WoNQModeType.SPEEDY_BOOTS, config)
        self._speed_multiplier = 2.0
        self._original_speed = PLAYER_SPEED
        self._original_acceleration = PLAYER_ACCELERATION
        self._trail_particles: List[Particle] = []
        self._particle_system: Optional[ParticleSystem] = None
        self._visual_effects_enabled = True

    def start(self) -> None:
        """Activate Speedy Boots mode."""
        super().start()
        self._apply_speed_boost()
        self._start_visual_effects()

    def stop(self) -> None:
        """Deactivate Speedy Boots mode."""
        self._restore_original_speed()
        self._clear_visual_effects()
        super().stop()

    def _register_hooks(self) -> None:
        """Register mode-specific hooks."""
        self.set_hook("player_move", self._hook_player_move)
        self.set_hook("player_physics_update", self._hook_player_physics_update)
        self.set_hook("post_render", self._hook_post_render)

    def _unregister_hooks(self) -> None:
        """Unregister mode-specific hooks."""
        self.clear_hooks("player_move")
        self.clear_hooks("player_physics_update")
        self.clear_hooks("post_render")

    def _apply_speed_boost(self) -> None:
        """Apply speed boost to player."""
        self._original_speed = self.get_config_value("player_speed", PLAYER_SPEED)
        self._original_acceleration = self.get_config_value("player_acceleration", PLAYER_ACCELERATION)
        
        new_speed = self._original_speed * self._speed_multiplier
        new_acceleration = self._original_acceleration * self._speed_multiplier
        
        self.set_config_value("player_speed", new_speed)
        self.set_config_value("player_acceleration", new_acceleration)

    def _restore_original_speed(self) -> None:
        """Restore original player speed."""
        self.set_config_value("player_speed", self._original_speed)
        self.set_config_value("player_acceleration", self._original_acceleration)

    def _start_visual_effects(self) -> None:
        """Start visual effects for speedy boots."""
        if self._visual_effects_enabled:
            self._particle_system = ParticleSystem()

    def _clear_visual_effects(self) -> None:
        """Clear visual effects."""
        self._trail_particles.clear()
        self._particle_system = None

    def update(self, dt: float) -> None:
        """
        Update mode state.
        
        Args:
            dt: Delta time in seconds
        """
        super().update(dt)
        self._update_trail_particles(dt)

    def _update_trail_particles(self, dt: float) -> None:
        """Update trail particle effects."""
        if not self._particle_system:
            return
        
        self._particle_system.update()
        
        # Remove old particles
        self._trail_particles = [p for p in self._trail_particles if p.is_active()]
        
        # Update particle system
        self._particle_system.update()

    def _hook_player_move(self, player: Any, movement: Dict[str, float]) -> Dict[str, float]:
        """
        Hook for player movement - apply speed multiplier.
        
        Args:
            player: Player entity
            movement: Movement dictionary with x, y components
            
        Returns:
            Modified movement dictionary
        """
        if self.is_active():
            movement["x"] *= self._speed_multiplier
            movement["y"] *= self._speed_multiplier
        return movement

    def _hook_player_physics_update(self, player: Any, dt: float) -> None:
        """
        Hook for player physics updates - create trail particles.
        
        Args:
            player: Player entity
            dt: Delta time in seconds
        """
        if self.is_active() and self._visual_effects_enabled and self._particle_system:
            self._create_trail_particle(player)

    def _create_trail_particle(self, player: Any) -> None:
        """Create a trail particle at player position."""
        if not self._particle_system:
            return
        
        # Get player position and velocity
        pos = getattr(player, "position", (0, 0))
        velocity = getattr(player, "velocity", (0, 0))
        
        # Create particle with speed-based color
        speed = (velocity[0]**2 + velocity[1]**2)**0.5
        color_intensity = min(255, int(speed * 10))
        color = (color_intensity, 100, 255 - color_intensity // 2)
        
        particle = Particle(
            position=pos,
            velocity=(-velocity[0] * 0.1, -velocity[1] * 0.1),
            color=color,
            size=3,
            lifetime=0.5,
            fade_out=True,
            gravity=0.0
        )
        
        self._trail_particles.append(particle)
        if self._particle_system:
            self._particle_system.add_particle(particle)

    def _hook_post_render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """
        Hook for post-rendering - draw trail particles.
        
        Args:
            surface: Pygame surface to render to
            camera_offset: Camera offset for positioning
        """
        if self.is_active() and self._visual_effects_enabled and self._particle_system:
            self._particle_system.render(surface, camera_offset)

    def apply_to_player(self, player: Any) -> None:
        """
        Apply mode effects to player.
        
        Args:
            player: Player entity to affect
        """
        if self.is_active():
            # Apply speed multiplier to player attributes
            if hasattr(player, "move_speed"):
                player.move_speed = self._original_speed * self._speed_multiplier
            if hasattr(player, "acceleration"):
                player.acceleration = self._original_acceleration * self._speed_multiplier

    def get_speed_multiplier(self) -> float:
        """
        Get current speed multiplier.
        
        Returns:
            Speed multiplier value
        """
        return self._speed_multiplier

    def set_speed_multiplier(self, multiplier: float) -> None:
        """
        Set speed multiplier.
        
        Args:
            multiplier: New speed multiplier (1.0 = normal, 2.0 = double speed)
        """
        self._speed_multiplier = max(1.0, multiplier)
        self.set_config_value("speed_multiplier", self._speed_multiplier)

    def get_visual_effects_enabled(self) -> bool:
        """
        Check if visual effects are enabled.
        
        Returns:
            True if visual effects are enabled
        """
        return self._visual_effects_enabled

    def set_visual_effects_enabled(self, enabled: bool) -> None:
        """
        Enable or disable visual effects.
        
        Args:
            enabled: True to enable visual effects
        """
        self._visual_effects_enabled = enabled
        if not enabled:
            self._clear_visual_effects()
        elif self.is_active():
            self._start_visual_effects()