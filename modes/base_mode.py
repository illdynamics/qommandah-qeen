from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from shared.wonqmode_data import WoNQModeConfig, WoNQModeType

class BaseMode(ABC):
    """
    Abstract base class for all WoNQ modes.
    
    Modes modify game behavior through hooks that can be enabled/disabled.
    Each mode has a unique type and configuration.
    """
    def __init__(self, mode_type: WoNQModeType, config: WoNQModeConfig):
        """
        Initialize the mode with its type and configuration.
        
        Args:
            mode_type: The type of this mode
            config: Configuration parameters for this mode
        """
        self._mode_type = mode_type
        self._config = config
        self._active = False
        self._hooks: Dict[str, List[Callable]] = {}
        self._initialize_hooks()

    def _initialize_hooks(self) -> None:
        """Initialize empty hook lists for this mode."""
        self._hooks = {
            "start": [],
            "stop": [],
            "update": [],
            "apply_to_player": [],
            "apply_to_world": [],
            "pre_render": [],
            "post_render": []
        }

    def start(self) -> None:
        """Activate this mode and register all hooks."""
        if self._active:
            return
        self._active = True
        self._on_start()
        self._register_hooks()

    def stop(self) -> None:
        """Deactivate this mode and unregister all hooks."""
        if not self._active:
            return
        self._active = False
        self._on_stop()
        self._unregister_hooks()

    def _on_start(self) -> None:
        """Called when mode starts. Can be overridden by subclasses."""
        pass

    def _on_stop(self) -> None:
        """Called when mode stops. Can be overridden by subclasses."""
        pass

    def _register_hooks(self) -> None:
        """Register all hooks defined by this mode."""
        pass

    def _unregister_hooks(self) -> None:
        """Unregister all hooks defined by this mode."""
        pass

    def update(self, delta_time: float) -> None:
        """
        Update the mode's internal state.
        
        Args:
            delta_time: Delta time in seconds
        """
        self._on_update(delta_time)

    def _on_update(self, delta_time: float) -> None:
        """Called each frame to update mode state. Can be overridden by subclasses."""
        pass

    def apply_to_player(self, player: Any) -> None:
        """
        Apply mode effects to a player entity.
        
        Args:
            player: The player entity to affect
        """
        self._on_apply_to_player(player)

    def _on_apply_to_player(self, player: Any) -> None:
        """Called to apply mode effects to player. Can be overridden by subclasses."""
        pass

    def apply_to_world(self, world: Any) -> None:
        """
        Apply mode effects to the game world.
        
        Args:
            world: The game world to affect
        """
        self._on_apply_to_world(world)

    def _on_apply_to_world(self, world: Any) -> None:
        """Called to apply mode effects to world. Can be overridden by subclasses."""
        pass

    def get_hook(self, hook_name: str) -> Optional[List[Callable]]:
        """
        Get hook functions by name.
        
        Args:
            hook_name: Name of the hook to retrieve
            
        Returns:
            List of hook functions if found, None otherwise
        """
        return self._hooks.get(hook_name)

    def set_hook(self, hook_name: str, hook_func: Callable) -> None:
        """
        Set a hook function.
        
        Args:
            hook_name: Name of the hook
            hook_func: The hook function to register
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(hook_func)

    def remove_hook(self, hook_name: str, hook_func: Callable) -> bool:
        """
        Remove a hook function.
        
        Args:
            hook_name: Name of the hook to remove
            hook_func: The hook function to remove
            
        Returns:
            True if the hook was removed, False if it didn't exist
        """
        if hook_name not in self._hooks:
            return False
        try:
            self._hooks[hook_name].remove(hook_func)
            return True
        except ValueError:
            return False

    def clear_hooks(self, hook_name: str) -> None:
        """
        Clear all hooks of a specific type.
        
        Args:
            hook_name: Name of the hook type to clear
        """
        if hook_name in self._hooks:
            self._hooks[hook_name].clear()

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            The configuration value or default
        """
        return self._config.parameters.get(key, default)

    def set_config_value(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config.parameters[key] = value

    def is_active(self) -> bool:
        """
        Check if mode is active.
        
        Returns:
            True if mode is active, False otherwise
        """
        return self._active

    def get_mode_type(self) -> WoNQModeType:
        """
        Get the mode type.
        
        Returns:
            The mode type
        """
        return self._mode_type

    def get_config(self) -> WoNQModeConfig:
        """
        Get the mode configuration.
        
        Returns:
            The mode configuration
        """
        return self._config

    def __str__(self) -> str:
        """String representation of the mode."""
        return f"{self._config.name} ({'Active' if self._active else 'Inactive'})"

    def __repr__(self) -> str:
        """Detailed representation of the mode."""
        return f"BaseMode(type={self._mode_type}, active={self._active}, config={self._config})"