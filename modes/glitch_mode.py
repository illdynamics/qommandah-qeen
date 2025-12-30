import random
import pygame
from typing import Any, Dict, List
from modes.base_mode import BaseMode
from shared.wonqmode_data import WoNQModeType, WoNQModeConfig

class GlitchMode(BaseMode):
    """Mode that adds visual glitches and corruption effects"""
    def __init__(self):
        config = WoNQModeConfig(
            mode_type=WoNQModeType.GLITCH,
            name="Glitch Mode",
            description="Adds visual glitches and screen corruption",
            duration=20.0,
            cooldown=45.0,
            glitch_intensity=0.5,
            glitch_frequency=2.0
        )
        super().__init__(WoNQModeType.GLITCH, config)
        self.active_glitches: List[str] = []
        self.glitch_timer = 0.0
        self.next_glitch_time = 0.0
        self.is_active_flag = False

    def start(self) -> None:
        """Activate glitch mode"""
        if not self.is_active_flag:
            super().start()
            self.is_active_flag = True
            self._on_start()

    def stop(self) -> None:
        """Deactivate glitch mode"""
        if self.is_active_flag:
            super().stop()
            self.is_active_flag = False
            self._on_stop()

    def _on_start(self) -> None:
        """Called when mode starts."""
        self._register_hooks()
        self.start_glitch_cycle()

    def _on_stop(self) -> None:
        """Called when mode stops."""
        self._unregister_hooks()
        self.clear_glitches()

    def _register_hooks(self) -> None:
        """Register glitch hooks."""
        self.set_hook("pre_render", self._apply_glitch_effects)
        self.set_hook("post_render", self._apply_post_glitches)

    def _unregister_hooks(self) -> None:
        """Unregister glitch hooks."""
        self.clear_hooks("pre_render")
        self.clear_hooks("post_render")

    def start_glitch_cycle(self):
        """Start periodic glitch effects"""
        self.glitch_timer = 0.0
        self.schedule_next_glitch()

    def schedule_next_glitch(self):
        """Schedule the next glitch event"""
        frequency = self.get_config_value("glitch_frequency", 2.0)
        self.next_glitch_time = random.uniform(0.5 / frequency, 2.0 / frequency)

    def update(self, dt):
        """Update glitch timing and effects"""
        super().update(dt)
        if self.is_active_flag:
            self.glitch_timer += dt
            if self.glitch_timer >= self.next_glitch_time:
                self.trigger_glitch()
                self.glitch_timer = 0.0
                self.schedule_next_glitch()

    def trigger_glitch(self):
        """Trigger a random glitch effect"""
        glitch_types = [
            "horizontal_shift",
            "vertical_shift",
            "color_invert",
            "scan_lines",
            "pixelate",
            "noise"
        ]
        glitch_type = random.choice(glitch_types)
        
        if glitch_type == "horizontal_shift":
            self.apply_horizontal_shift()
        elif glitch_type == "vertical_shift":
            self.apply_vertical_shift()
        elif glitch_type == "color_invert":
            self.apply_color_invert()
        elif glitch_type == "scan_lines":
            self.apply_scan_lines()
        elif glitch_type == "pixelate":
            self.apply_pixelate()
        elif glitch_type == "noise":
            self.apply_noise()
        
        self.active_glitches.append(glitch_type)

    def apply_horizontal_shift(self):
        """Apply horizontal screen shift glitch"""
        pass

    def apply_vertical_shift(self):
        """Apply vertical screen shift glitch"""
        pass

    def apply_color_invert(self):
        """Apply color inversion glitch"""
        pass

    def apply_scan_lines(self):
        """Apply scan lines glitch"""
        pass

    def apply_pixelate(self):
        """Apply pixelation glitch"""
        pass

    def apply_noise(self):
        """Apply random noise glitch"""
        pass

    def _apply_glitch_effects(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply glitch effects to surface."""
        return surface

    def _apply_post_glitches(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply post-processing glitches."""
        return surface

    def clear_glitches(self):
        """Clear all active glitch effects"""
        self.active_glitches.clear()

    def get_glitch_intensity(self):
        """Get current glitch intensity"""
        return self.get_config_value("glitch_intensity", 0.5)

    def set_glitch_intensity(self, intensity):
        """Set glitch intensity (0.0 to 1.0)"""
        self.set_config_value("glitch_intensity", intensity)

    def get_active_glitch(self):
        """Get currently active glitch type"""
        return self.active_glitches[-1] if self.active_glitches else None

    def force_glitch(self, glitch_type):
        """Force a specific glitch type"""
        if glitch_type in ["horizontal_shift", "vertical_shift", "color_invert", 
                          "scan_lines", "pixelate", "noise"]:
            self.trigger_glitch()

    def is_active(self) -> bool:
        """Check if mode is active."""
        return self.is_active_flag