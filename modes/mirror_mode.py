from typing import Any, Dict
import pygame
from modes.base_mode import BaseMode
from shared.wonqmode_data import WoNQModeType, WoNQModeConfig

class MirrorMode(BaseMode):
    """
    Mode that flips all input and rendering horizontally.
    """
    def __init__(self):
        """Initialize mirror mode."""
        config = WoNQModeConfig(
            mode_type=WoNQModeType.MIRROR,
            name="Mirror Mode",
            description="Flips all input and rendering horizontally",
            duration=45.0,
            cooldown=30.0
        )
        super().__init__(WoNQModeType.MIRROR, config)
        self._active = False
        self._remaining_duration = 0.0
        self._cooldown_timer = 0.0

    def start(self) -> None:
        """
        Activate the mirror mode.
        """
        if self._cooldown_timer <= 0.0:
            super().start()
            self._active = True
            self._remaining_duration = self.get_config_value("duration", 45.0)
            self._on_start()

    def stop(self) -> None:
        """
        Deactivate the mirror mode.
        """
        super().stop()
        self._active = False
        self._cooldown_timer = self.get_config_value("cooldown", 30.0)
        self._on_stop()

    def _on_start(self) -> None:
        """Called when mode starts."""
        self._register_hooks()

    def _on_stop(self) -> None:
        """Called when mode stops."""
        self._unregister_hooks()

    def _register_hooks(self) -> None:
        """Register all hooks defined by this mode."""
        self.set_hook("process_input", self._process_input_hook)
        self.set_hook("transform_position", self._transform_position_hook)
        self.set_hook("transform_surface", self._transform_surface_hook)

    def _unregister_hooks(self) -> None:
        """Unregister all hooks defined by this mode."""
        self.clear_hooks("process_input")
        self.clear_hooks("transform_position")
        self.clear_hooks("transform_surface")

    def _process_input_hook(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data by flipping horizontal controls.
        
        Args:
            input_data: Raw input data
            
        Returns:
            dict: Modified input data with flipped horizontal controls
        """
        if "horizontal" in input_data:
            input_data["horizontal"] = -input_data["horizontal"]
        return input_data

    def _transform_position_hook(self, x: float, y: float, screen_width: int) -> tuple[float, float]:
        """
        Transform a position for mirror rendering.
        
        Args:
            x: Original x position
            y: Original y position
            screen_width: Width of the screen
            
        Returns:
            tuple: Transformed (x, y) position
        """
        return (screen_width - x, y)

    def _transform_surface_hook(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Transform a surface for mirror rendering.
        
        Args:
            surface: Original surface
            
        Returns:
            pygame.Surface: Transformed surface
        """
        return pygame.transform.flip(surface, True, False)

    def update(self, dt: float) -> None:
        """
        Update the mode logic.
        
        Args:
            dt: Delta time in seconds
        """
        if self._active:
            self._remaining_duration -= dt
            if self._remaining_duration <= 0.0:
                self.stop()
        elif self._cooldown_timer > 0.0:
            self._cooldown_timer -= dt

    def render(self, surface: pygame.Surface) -> None:
        """
        Render mode-specific visuals.
        
        Args:
            surface: Surface to render to
        """
        pass

    def apply_to_player(self, player) -> None:
        """
        Apply mode effects to a player entity.
        
        Args:
            player: The player entity to affect
        """
        pass

    def apply_to_world(self, world) -> None:
        """
        Apply mode effects to the game world.
        
        Args:
            world: The game world to affect
        """
        pass

    def is_active(self) -> bool:
        """
        Check if the mode is currently active.
        
        Returns:
            bool: True if active
        """
        return self._active