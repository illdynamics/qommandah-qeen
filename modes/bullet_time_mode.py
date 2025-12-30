"""
Mode that slows down time to 30% normal speed.
"""
import pygame
from typing import Any, Dict
from modes.base_mode import BaseMode
from shared.wonqmode_data import WoNQModeType, WoNQModeConfig


class BulletTimeMode(BaseMode):
    def __init__(self):
        """
        Initialize bullet time mode.
        """
        config = WoNQModeConfig(
            mode_type=WoNQModeType.BULLET_TIME,
            name="Bullet Time",
            description="Slows down time to 30% normal speed",
            duration=5.0,  # 5 seconds duration
            cooldown=10.0,  # 10 seconds cooldown
            time_scale=0.3  # 30% normal speed
        )
        super().__init__(WoNQModeType.BULLET_TIME, config)
        self._remaining_duration = 0.0
        self._cooldown_remaining = 0.0
        self._time_scale = 0.3

    def start(self) -> None:
        """
        Activate bullet time if not on cooldown.
        """
        if self._cooldown_remaining > 0:
            return
        super().start()

    def stop(self) -> None:
        """
        Deactivate bullet time.
        """
        super().stop()

    def _on_start(self) -> None:
        """Called when mode starts."""
        self._remaining_duration = self.get_config_value("duration", 5.0)
        self._register_hooks()

    def _on_stop(self) -> None:
        """Called when mode stops."""
        self._unregister_hooks()
        self._cooldown_remaining = self.get_config_value("cooldown", 10.0)

    def _register_hooks(self) -> None:
        """Register all hooks defined by this mode."""
        self.set_hook("get_time_scale", self._get_time_scale_hook)

    def _unregister_hooks(self) -> None:
        """Unregister all hooks defined by this mode."""
        self.clear_hooks("get_time_scale")

    def _get_time_scale_hook(self) -> float:
        """
        Get the current time scale factor.
        
        Returns:
            float: Time scale (1.0 = normal, 0.3 = bullet time)
        """
        return self._time_scale

    def update(self, dt: float) -> None:
        """
        Update the mode logic.
        
        Args:
            dt: Delta time in seconds
        """
        super().update(dt)
        
        if self._remaining_duration > 0:
            self._remaining_duration -= dt
            if self._remaining_duration <= 0:
                self.stop()
        
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= dt

    def render(self, surface: pygame.Surface) -> None:
        """
        Render bullet time visual effect.
        
        Args:
            surface: Surface to render to
        """
        if self.is_active():
            # Create a blue tint overlay for bullet time
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((100, 100, 255, 30))  # Semi-transparent blue
            surface.blit(overlay, (0, 0))

    def get_remaining_duration(self) -> float:
        """
        Get remaining active duration.
        
        Returns:
            float: Remaining duration in seconds
        """
        return self._remaining_duration

    def get_cooldown_remaining(self) -> float:
        """
        Get remaining cooldown time.
        
        Returns:
            float: Remaining cooldown in seconds
        """
        return self._cooldown_remaining

    def can_activate(self) -> bool:
        """
        Check if bullet time can be activated.
        
        Returns:
            bool: True if can be activated
        """
        return self._cooldown_remaining <= 0

    def is_active(self) -> bool:
        """
        Check if the mode is currently active.
        
        Returns:
            bool: True if active
        """
        return super().is_active()

    def get_time_scale(self) -> float:
        """
        Get the current time scale factor.
        
        Returns:
            float: Time scale (1.0 = normal, 0.3 = bullet time)
        """
        return self._time_scale

    def get_ui_info(self) -> Dict[str, Any]:
        """
        Get UI information for displaying mode status.
        
        Returns:
            dict: UI information
        """
        return {
            "name": self.get_config_value("name", "Bullet Time"),
            "active": self.is_active(),
            "duration": self.get_remaining_duration(),
            "cooldown": self.get_cooldown_remaining(),
            "can_activate": self.can_activate()
        }

    def apply_to_player(self, player) -> None:
        """
        Apply mode effects to a player entity.
        
        Args:
            player: The player entity to affect
        """
        # Player movement is affected by time scale through hooks

    def apply_to_world(self, world) -> None:
        """
        Apply mode effects to the game world.
        
        Args:
            world: The game world to affect
        """
        # World physics are affected by time scale through hooks