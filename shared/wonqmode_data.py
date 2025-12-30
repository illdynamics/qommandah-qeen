from enum import Enum, auto
from typing import Dict, Any, Callable, Optional, List, Tuple
from dataclasses import dataclass, field
import pygame
from shared.types import Vec2i, Rect
from shared.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    TILE_SIZE,
    GRAVITY,
    PLAYER_JUMP_FORCE,
    PLAYER_MOVE_SPEED,
    PLAYER_TERMINAL_VELOCITY
)

class WoNQModeType(Enum):
    """Enumeration of all available WoNQ mode types."""
    LOW_G = auto()
    GLITCH = auto()
    MIRROR = auto()
    BULLET_TIME = auto()
    SPEEDY_BOOTS = auto()
    JUNGLIST = auto()

@dataclass
class WoNQModeConfig:
    """Configuration data for a WoNQ mode."""
    mode_type: WoNQModeType
    name: str
    description: str
    duration: float = 0.0  # 0.0 means infinite
    cooldown: float = 0.0
    priority: int = 0
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WoNQModeHook:
    """Hook definition for WoNQ mode event handling."""
    hook_type: str
    callback: Callable
    priority: int = 0

class WoNQModeRegistry:
    """Registry for managing WoNQ mode definitions and instances."""
    def __init__(self):
        self._modes: Dict[WoNQModeType, WoNQModeConfig] = {}
        self._active_modes: Dict[WoNQModeType, WoNQModeConfig] = {}
        self._hooks: Dict[str, List[WoNQModeHook]] = {}

    def register_mode(self, mode_config: WoNQModeConfig) -> None:
        """Register a new WoNQ mode configuration."""
        self._modes[mode_config.mode_type] = mode_config

    def get_mode(self, mode_type: WoNQModeType) -> Optional[WoNQModeConfig]:
        """Retrieve a WoNQ mode configuration by type."""
        return self._modes.get(mode_type)

    def get_all_modes(self) -> List[WoNQModeConfig]:
        """Retrieve all registered WoNQ mode configurations."""
        return list(self._modes.values())

    def register_hook(self, hook_type: str, callback: Callable, priority: int = 0) -> None:
        """Register a hook for a specific event type."""
        if hook_type not in self._hooks:
            self._hooks[hook_type] = []
        self._hooks[hook_type].append(WoNQModeHook(hook_type, callback, priority))
        self._hooks[hook_type].sort(key=lambda h: h.priority, reverse=True)

    def trigger_hooks(self, hook_type: str, *args, **kwargs) -> None:
        """Trigger all hooks of a specific type."""
        for hook in self._hooks.get(hook_type, []):
            hook.callback(*args, **kwargs)

    def activate_mode(self, mode_type: WoNQModeType) -> bool:
        """Activate a WoNQ mode."""
        if mode_type not in self._modes:
            return False
        if mode_type in self._active_modes:
            return False
        self._active_modes[mode_type] = self._modes[mode_type]
        return True

    def deactivate_mode(self, mode_type: WoNQModeType) -> bool:
        """Deactivate a WoNQ mode."""
        if mode_type not in self._active_modes:
            return False
        del self._active_modes[mode_type]
        return True

    def get_active_modes(self) -> List[WoNQModeConfig]:
        """Retrieve all currently active WoNQ modes."""
        return list(self._active_modes.values())

    def is_mode_active(self, mode_type: WoNQModeType) -> bool:
        """Check if a specific WoNQ mode is active."""
        return mode_type in self._active_modes

    def update_modes(self, delta_time: float) -> None:
        """Update all active modes (handle duration, cooldown, etc.)."""
        # Implementation for duration/cooldown management would go here
        pass

    def clear_all_modes(self) -> None:
        """Deactivate all active WoNQ modes."""
        self._active_modes.clear()

def create_default_registry() -> WoNQModeRegistry:
    """Create and populate a WoNQModeRegistry with default modes."""
    registry = WoNQModeRegistry()
    
    registry.register_mode(WoNQModeConfig(
        mode_type=WoNQModeType.LOW_G,
        name="Low Gravity",
        description="Reduces gravity for floaty jumps",
        parameters={"gravity_multiplier": 0.5}
    ))
    
    registry.register_mode(WoNQModeConfig(
        mode_type=WoNQModeType.GLITCH,
        name="Glitch Mode",
        description="Adds visual glitches and corruption effects",
        parameters={"intensity": 0.7}
    ))
    
    registry.register_mode(WoNQModeConfig(
        mode_type=WoNQModeType.MIRROR,
        name="Mirror Mode",
        description="Flips the screen horizontally",
        parameters={"flip_horizontal": True}
    ))
    
    registry.register_mode(WoNQModeConfig(
        mode_type=WoNQModeType.BULLET_TIME,
        name="Bullet Time",
        description="Slows down time for precision platforming",
        duration=5.0,
        cooldown=10.0,
        parameters={"time_scale": 0.3}
    ))
    
    registry.register_mode(WoNQModeConfig(
        mode_type=WoNQModeType.SPEEDY_BOOTS,
        name="Speedy Boots",
        description="Doubles player movement speed",
        parameters={"speed_multiplier": 2.0}
    ))
    
    registry.register_mode(WoNQModeConfig(
        mode_type=WoNQModeType.JUNGLIST,
        name="Junglist",
        description="174 BPM pulses and beat detection",
        parameters={"bpm": 174, "pulse_strength": 0.8}
    ))
    
    return registry