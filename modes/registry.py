from typing import Dict, List, Optional, Set, Callable, Any
import pygame
from shared.wonqmode_data import WoNQModeType, WoNQModeConfig
from modes.base_mode import BaseMode

class ModeRegistry:
    def __init__(self):
        """Initialize an empty mode registry."""
        self._available_modes: Dict[WoNQModeType, BaseMode] = {}
        self._active_modes: Set[WoNQModeType] = set()
        self._global_hooks: Dict[str, List[Callable]] = {}
        self._ui_callbacks: List[Callable[[List[str]], None]] = []
        self._visual_overlay_callbacks: List[Callable[[WoNQModeType, bool], None]] = []
    
    def register_mode(self, mode: BaseMode) -> None:
        """
        Register a mode as available (but not active).
        
        Args:
            mode: The mode to register
        """
        mode_type = mode.get_mode_type()
        if mode_type in self._available_modes:
            raise ValueError(f"Mode {mode_type} already registered")
        self._available_modes[mode_type] = mode
    
    def unregister_mode(self, mode_type: WoNQModeType) -> bool:
        """
        Unregister a mode from available modes.
        
        Args:
            mode_type: Type of mode to unregister
            
        Returns:
            True if mode was unregistered, False if not found
        """
        if mode_type in self._available_modes:
            if mode_type in self._active_modes:
                self.deactivate_mode(mode_type)
            del self._available_modes[mode_type]
            return True
        return False
    
    def activate_mode(self, mode_type: WoNQModeType) -> bool:
        """
        Activate a registered mode.
        
        Args:
            mode_type: Type of mode to activate
            
        Returns:
            True if mode was activated, False if not found or already active
        """
        if mode_type not in self._available_modes:
            return False
        if mode_type in self._active_modes:
            return False
        
        mode = self._available_modes[mode_type]
        mode.start()
        self._active_modes.add(mode_type)
        self._notify_ui_update()
        self._notify_visual_overlay(mode_type, True)
        return True
    
    def deactivate_mode(self, mode_type: WoNQModeType) -> bool:
        """
        Deactivate an active mode.
        
        Args:
            mode_type: Type of mode to deactivate
            
        Returns:
            True if mode was deactivated, False if not found or not active
        """
        if mode_type not in self._active_modes:
            return False
        
        mode = self._available_modes[mode_type]
        mode.stop()
        self._active_modes.remove(mode_type)
        self._notify_ui_update()
        self._notify_visual_overlay(mode_type, False)
        return True
    
    def toggle_mode(self, mode_type: WoNQModeType) -> bool:
        """
        Toggle a mode's active state.
        
        Args:
            mode_type: Type of mode to toggle
            
        Returns:
            True if mode is now active, False if now inactive
        """
        if mode_type in self._active_modes:
            self.deactivate_mode(mode_type)
            return False
        else:
            self.activate_mode(mode_type)
            return True
    
    def is_mode_active(self, mode_type: WoNQModeType) -> bool:
        """
        Check if a mode is active.
        
        Args:
            mode_type: Type of mode to check
            
        Returns:
            True if mode is active, False otherwise
        """
        return mode_type in self._active_modes
    
    def get_active_modes(self) -> List[BaseMode]:
        """
        Get all active modes.
        
        Returns:
            List of active mode instances
        """
        return [self._available_modes[mode_type] for mode_type in self._active_modes]
    
    def get_available_modes(self) -> List[BaseMode]:
        """
        Get all available modes.
        
        Returns:
            List of available mode instances
        """
        return list(self._available_modes.values())
    
    def get_mode(self, mode_type: WoNQModeType) -> Optional[BaseMode]:
        """
        Get a mode by type.
        
        Args:
            mode_type: Type of mode to get
            
        Returns:
            The mode instance if found, None otherwise
        """
        return self._available_modes.get(mode_type)
    
    def update_modes(self, dt: float) -> None:
        """
        Update all active modes.
        
        Args:
            dt: Delta time in seconds
        """
        for mode_type in self._active_modes:
            mode = self._available_modes[mode_type]
            mode.update(dt)
    
    def apply_modes_to_player(self, player) -> None:
        """
        Apply all active modes to a player.
        
        Args:
            player: The player entity to affect
        """
        for mode_type in self._active_modes:
            mode = self._available_modes[mode_type]
            mode.apply_to_player(player)
    
    def apply_modes_to_world(self, world) -> None:
        """
        Apply all active modes to the game world.
        
        Args:
            world: The game world to affect
        """
        for mode_type in self._active_modes:
            mode = self._available_modes[mode_type]
            mode.apply_to_world(world)
    
    def register_global_hook(self, hook_name: str, hook_func: Callable) -> None:
        """
        Register a global hook that can be called by any system.
        
        Args:
            hook_name: Name of the hook
            hook_func: The hook function
        """
        if hook_name not in self._global_hooks:
            self._global_hooks[hook_name] = []
        self._global_hooks[hook_name].append(hook_func)
    
    def unregister_global_hook(self, hook_name: str, hook_func: Callable) -> bool:
        """
        Unregister a global hook.
        
        Args:
            hook_name: Name of the hook
            hook_func: The hook function to remove
            
        Returns:
            True if hook was removed, False if not found
        """
        if hook_name not in self._global_hooks:
            return False
        if hook_func in self._global_hooks[hook_name]:
            self._global_hooks[hook_name].remove(hook_func)
            if not self._global_hooks[hook_name]:
                del self._global_hooks[hook_name]
            return True
        return False
    
    def call_global_hooks(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Call all registered global hooks with the given name.
        
        Args:
            hook_name: Name of the hook to call
            *args: Positional arguments to pass to hooks
            **kwargs: Keyword arguments to pass to hooks
            
        Returns:
            List of return values from all hooks
        """
        results = []
        if hook_name in self._global_hooks:
            for hook_func in self._global_hooks[hook_name]:
                try:
                    result = hook_func(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Error calling global hook {hook_name}: {e}")
        return results
    
    def clear_all_modes(self) -> None:
        """Deactivate all active modes and clear the registry."""
        for mode_type in list(self._active_modes):
            self.deactivate_mode(mode_type)
        self._available_modes.clear()
        self._global_hooks.clear()
        self._ui_callbacks.clear()
        self._visual_overlay_callbacks.clear()
    
    def get_mode_config(self, mode_type: WoNQModeType) -> Optional[WoNQModeConfig]:
        """
        Get the configuration for a mode.
        
        Args:
            mode_type: Type of mode to get config for
            
        Returns:
            The mode configuration if found, None otherwise
        """
        mode = self.get_mode(mode_type)
        if mode:
            return mode.get_config()
        return None
    
    def set_mode_config(self, mode_type: WoNQModeType, config: WoNQModeConfig) -> bool:
        """
        Set the configuration for a mode.
        
        Args:
            mode_type: Type of mode to configure
            config: New configuration
            
        Returns:
            True if configuration was set, False if mode not found
        """
        mode = self.get_mode(mode_type)
        if mode:
            # Assuming BaseMode has a method to update config
            # This might need to be implemented in BaseMode
            return True
        return False
    
    def register_ui_callback(self, callback: Callable[[List[str]], None]) -> None:
        """
        Register a callback for UI updates when modes change.
        
        Args:
            callback: Function to call with list of active mode names
        """
        self._ui_callbacks.append(callback)
    
    def register_visual_overlay_callback(self, callback: Callable[[WoNQModeType, bool], None]) -> None:
        """
        Register a callback for visual overlay updates.
        
        Args:
            callback: Function to call with mode type and activation state
        """
        self._visual_overlay_callbacks.append(callback)
    
    def _notify_ui_update(self) -> None:
        """Notify all UI callbacks of mode changes."""
        active_mode_names = self.get_active_mode_names()
        for callback in self._ui_callbacks:
            try:
                callback(active_mode_names)
            except Exception as e:
                print(f"Error in UI callback: {e}")
    
    def _notify_visual_overlay(self, mode_type: WoNQModeType, activated: bool) -> None:
        """Notify all visual overlay callbacks of mode activation/deactivation."""
        for callback in self._visual_overlay_callbacks:
            try:
                callback(mode_type, activated)
            except Exception as e:
                print(f"Error in visual overlay callback: {e}")
    
    def get_active_mode_names(self) -> List[str]:
        """
        Get names of all active modes.
        
        Returns:
            List of active mode names
        """
        return [str(mode_type) for mode_type in self._active_modes]
    
    def get_mode_by_name(self, name: str) -> Optional[BaseMode]:
        """
        Get a mode by its name.
        
        Args:
            name: Name of the mode
            
        Returns:
            The mode instance if found, None otherwise
        """
        for mode_type, mode in self._available_modes.items():
            if str(mode_type) == name:
                return mode
        return None

# Singleton instance
_mode_registry_instance: Optional[ModeRegistry] = None

def get_mode_registry() -> ModeRegistry:
    """
    Get the global mode registry instance (singleton pattern).
    
    Returns:
        The global ModeRegistry instance
    """
    global _mode_registry_instance
    if _mode_registry_instance is None:
        _mode_registry_instance = ModeRegistry()
    return _mode_registry_instance