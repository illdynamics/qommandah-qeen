"""
Mode that reduces gravity by 60% for floaty jumps.
"""
import pygame
from typing import Any, Optional
from modes.base_mode import BaseMode
from shared.wonqmode_data import WoNQModeType, WoNQModeConfig
from shared.constants import GRAVITY


class LowGMode(BaseMode):
    def __init__(self):
        """Initialize low gravity mode."""
        config = WoNQModeConfig(
            mode_type=WoNQModeType.LOW_G,
            name="Low Gravity",
            description="Reduces gravity by 60% for floaty jumps",
            duration=0,  # Permanent while active
            cooldown=0,
            gravity_multiplier=0.4  # 40% of normal gravity
        )
        super().__init__(WoNQModeType.LOW_G, config)
        self._original_gravity = GRAVITY
        self._gravity_multiplier = 0.4

    def start(self) -> None:
        """Activate low gravity mode."""
        super().start()

    def stop(self) -> None:
        """Deactivate low gravity mode."""
        super().stop()

    def _on_start(self) -> None:
        """Called when mode starts."""
        self._register_hooks()

    def _on_stop(self) -> None:
        """Called when mode stops."""
        self._unregister_hooks()
        self._restore_gravity()

    def _register_hooks(self) -> None:
        """Register gravity modification hooks."""
        self.set_hook("get_gravity", self._modify_gravity)
        self.set_hook("get_jump_force", self._modify_jump_physics)

    def _unregister_hooks(self) -> None:
        """Unregister all hooks."""
        self.clear_hooks("get_gravity")
        self.clear_hooks("get_jump_force")

    def _modify_gravity(self, current_gravity: float) -> float:
        """
        Modify gravity value.
        
        Args:
            current_gravity: Current gravity value
            
        Returns:
            Modified gravity value
        """
        return current_gravity * self._gravity_multiplier

    def _modify_jump_physics(self, jump_force: float) -> float:
        """
        Modify jump physics for better control in low gravity.
        
        Args:
            jump_force: Current jump force
            
        Returns:
            Modified jump force
        """
        # Slightly reduce jump force for better control
        return jump_force * 0.9

    def _restore_gravity(self) -> None:
        """Restore original gravity value."""
        # Gravity is restored automatically when hooks are removed

    def update(self, delta_time: float) -> None:
        """
        Update mode logic.
        
        Args:
            dt: Delta time in seconds
        """
        super().update(delta_time)

    def apply_to_player(self, player) -> None:
        """
        Apply low gravity effects to player.
        
        Args:
            player: Player entity
        """
        # Player physics are handled by hooks

    def apply_to_world(self, world) -> None:
        """
        Apply low gravity effects to game world.
        
        Args:
            world: Game world
        """
        # World physics are handled by hooks

    def get_gravity_multiplier(self) -> float:
        """
        Get current gravity multiplier.
        
        Returns:
            Gravity multiplier (0.0 to 1.0)
        """
        return self._gravity_multiplier

    def set_gravity_multiplier(self, multiplier: float) -> None:
        """
        Set gravity multiplier.
        
        Args:
            multiplier: New gravity multiplier (0.0 to 1.0)
        """
        self._gravity_multiplier = max(0.0, min(1.0, multiplier))
        self.set_config_value("gravity_multiplier", self._gravity_multiplier)

    def is_active(self) -> bool:
        """
        Check if mode is active.
        
        Returns:
            True if active
        """
        return super().is_active()