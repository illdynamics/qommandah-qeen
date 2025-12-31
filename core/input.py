import pygame
from typing import Dict, Set, Callable, Any, Optional
from shared.exceptions import InputException

class InputManager:
    """
    Manages keyboard, mouse, and gamepad input.
    Provides event-driven and state-based input handling.
    Singleton pattern - use InputManager.get_instance()
    """
    
    _instance: Optional['InputManager'] = None
    
    @classmethod
    def get_instance(cls) -> 'InputManager':
        """Get the singleton instance of InputManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the input manager."""
        self._key_states: Dict[int, bool] = {}
        self._key_pressed: Dict[int, bool] = {}
        self._key_released: Dict[int, bool] = {}
        
        self._mouse_pos = (0, 0)
        self._mouse_buttons = [False, False, False]
        self._mouse_pressed = [False, False, False]
        self._mouse_released = [False, False, False]
        
        self._event_handlers: Dict[int, Set[Callable]] = {}
        self._action_map: Dict[str, Set[int]] = {}
        self._action_states: Dict[str, bool] = {}
        
        self._joysticks: Dict[int, pygame.joystick.Joystick] = {}
        self._joystick_buttons: Dict[int, Dict[int, bool]] = {}
        self._joystick_axes: Dict[int, Dict[int, float]] = {}
        
        self._initialized = False
        
    def initialize(self) -> None:
        """Initialize input system and joysticks."""
        try:
            pygame.joystick.init()
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self._joysticks[i] = joystick
                self._joystick_buttons[i] = {}
                self._joystick_axes[i] = {}
            
            # Set up default action mappings
            self._setup_default_mappings()
                
            self._initialized = True
        except Exception as e:
            raise InputException(f"Failed to initialize input system: {e}")
    
    def _setup_default_mappings(self) -> None:
        """Set up default key-to-action mappings."""
        # Movement
        self.map_action("move_left", pygame.K_LEFT, pygame.K_a)
        self.map_action("move_right", pygame.K_RIGHT, pygame.K_d)
        self.map_action("move_up", pygame.K_UP, pygame.K_w)
        self.map_action("move_down", pygame.K_DOWN, pygame.K_s)
        
        # Actions
        self.map_action("jump", pygame.K_SPACE, pygame.K_UP, pygame.K_w, pygame.K_z)
        self.map_action("attack", pygame.K_x, pygame.K_LCTRL, pygame.K_RCTRL)
        self.map_action("interact", pygame.K_SPACE)  # SPACE for doors/interaction
        self.map_action("powerup_toggle", pygame.K_RETURN, pygame.K_e)  # ENTER/E for mount/unmount powerups
        
        # System
        self.map_action("pause", pygame.K_ESCAPE, pygame.K_p)
        self.map_action("confirm", pygame.K_RETURN, pygame.K_SPACE)
        self.map_action("cancel", pygame.K_ESCAPE, pygame.K_BACKSPACE)
    
    def update(self) -> None:
        """Update input states for the current frame."""
        # Reset pressed/released states
        self._key_pressed.clear()
        self._key_released.clear()
        self._mouse_pressed = [False, False, False]
        self._mouse_released = [False, False, False]
        
        # Reset joystick button states
        for joystick_id in self._joystick_buttons:
            for button_id in list(self._joystick_buttons[joystick_id].keys()):
                if self._joystick_buttons[joystick_id][button_id]:
                    self._joystick_buttons[joystick_id][button_id] = False
        
        # Process events
        for event in pygame.event.get():
            self._process_event(event)
        
        # Update action states
        self._update_action_states()
    
    def _process_event(self, event: pygame.event.Event) -> None:
        """Process a single pygame event."""
        # Keyboard events
        if event.type == pygame.KEYDOWN:
            self._key_states[event.key] = True
            self._key_pressed[event.key] = True
        elif event.type == pygame.KEYUP:
            self._key_states[event.key] = False
            self._key_released[event.key] = True
        
        # Mouse events
        elif event.type == pygame.MOUSEMOTION:
            self._mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if 0 <= event.button - 1 < 3:
                self._mouse_buttons[event.button - 1] = True
                self._mouse_pressed[event.button - 1] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if 0 <= event.button - 1 < 3:
                self._mouse_buttons[event.button - 1] = False
                self._mouse_released[event.button - 1] = True
        
        # Joystick events
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.joy in self._joystick_buttons:
                self._joystick_buttons[event.joy][event.button] = True
        elif event.type == pygame.JOYBUTTONUP:
            if event.joy in self._joystick_buttons:
                self._joystick_buttons[event.joy][event.button] = False
        elif event.type == pygame.JOYAXISMOTION:
            if event.joy in self._joystick_axes:
                self._joystick_axes[event.joy][event.axis] = event.value
        
        # Call event handlers
        if event.type in self._event_handlers:
            for handler in self._event_handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def _update_action_states(self) -> None:
        """Update action states based on current input."""
        for action, keys in self._action_map.items():
            action_active = False
            
            # Check keyboard keys
            for key in keys:
                if self.is_key_down(key):
                    action_active = True
                    break
            
            # Check mouse buttons (if keys are negative, they represent mouse buttons)
            for key in keys:
                if key < 0 and 0 <= -key - 1 < 3:
                    if self.is_mouse_button_down(-key - 1):
                        action_active = True
                        break
            
            # Check joystick buttons
            for joystick_id in self._joysticks:
                for button_id in self._joystick_buttons.get(joystick_id, {}):
                    if self.is_joystick_button_down(joystick_id, button_id):
                        action_active = True
                        break
            
            self._action_states[action] = action_active
    
    def register_event_handler(self, event_type: int, handler: Callable) -> None:
        """Register a handler for a specific event type."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = set()
        self._event_handlers[event_type].add(handler)
    
    def unregister_event_handler(self, event_type: int, handler: Callable) -> None:
        """Unregister a handler for a specific event type."""
        if event_type in self._event_handlers:
            self._event_handlers[event_type].discard(handler)
    
    def map_action(self, action: str, *keys: int) -> None:
        """Map keys to an action."""
        if action not in self._action_map:
            self._action_map[action] = set()
        self._action_map[action].update(keys)
    
    def unmap_action(self, action: str, *keys: int) -> None:
        """Remove key mappings from an action."""
        if action in self._action_map:
            if keys:
                self._action_map[action].difference_update(keys)
            else:
                del self._action_map[action]
                self._action_states.pop(action, None)
    
    def is_action_pressed(self, action: str) -> bool:
        """Check if an action was pressed this frame."""
        if action not in self._action_map:
            return False
        
        for key in self._action_map[action]:
            if key in self._key_pressed and self._key_pressed[key]:
                return True
            
            # Check mouse buttons
            if key < 0 and 0 <= -key - 1 < 3:
                if self._mouse_pressed[-key - 1]:
                    return True
        
        return False
    
    def is_action_released(self, action: str) -> bool:
        """Check if an action was released this frame."""
        if action not in self._action_map:
            return False
        
        for key in self._action_map[action]:
            if key in self._key_released and self._key_released[key]:
                return True
            
            # Check mouse buttons
            if key < 0 and 0 <= -key - 1 < 3:
                if self._mouse_released[-key - 1]:
                    return True
        
        return False
    
    def is_action_down(self, action: str) -> bool:
        """Check if an action is currently held down."""
        return self._action_states.get(action, False)
    
    def is_key_down(self, key: int) -> bool:
        """Check if a key is currently held down."""
        return self._key_states.get(key, False)
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key was pressed this frame."""
        return self._key_pressed.get(key, False)
    
    def is_key_released(self, key: int) -> bool:
        """Check if a key was released this frame."""
        return self._key_released.get(key, False)
    
    def get_mouse_position(self) -> tuple[int, int]:
        """Get current mouse position."""
        return self._mouse_pos
    
    def is_mouse_button_down(self, button: int) -> bool:
        """Check if a mouse button is currently held down."""
        if 0 <= button < 3:
            return self._mouse_buttons[button]
        return False
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button was pressed this frame."""
        if 0 <= button < 3:
            return self._mouse_pressed[button]
        return False
    
    def is_mouse_button_released(self, button: int) -> bool:
        """Check if a mouse button was released this frame."""
        if 0 <= button < 3:
            return self._mouse_released[button]
        return False
    
    def get_joystick_count(self) -> int:
        """Get number of connected joysticks."""
        return len(self._joysticks)
    
    def is_joystick_button_down(self, joystick_id: int, button: int) -> bool:
        """Check if a joystick button is currently held down."""
        if joystick_id in self._joystick_buttons:
            return self._joystick_buttons[joystick_id].get(button, False)
        return False
    
    def get_joystick_axis(self, joystick_id: int, axis: int) -> float:
        """Get joystick axis value."""
        if joystick_id in self._joystick_axes:
            return self._joystick_axes[joystick_id].get(axis, 0.0)
        return 0.0
    
    def get_joystick_name(self, joystick_id: int) -> str:
        """Get joystick name."""
        if joystick_id in self._joysticks:
            return self._joysticks[joystick_id].get_name()
        return ""
    
    def clear(self) -> None:
        """Clear all input states."""
        self._key_states.clear()
        self._key_pressed.clear()
        self._key_released.clear()
        
        self._mouse_pos = (0, 0)
        self._mouse_buttons = [False, False, False]
        self._mouse_pressed = [False, False, False]
        self._mouse_released = [False, False, False]
        
        for joystick_id in self._joystick_buttons:
            self._joystick_buttons[joystick_id].clear()
        
        for joystick_id in self._joystick_axes:
            self._joystick_axes[joystick_id].clear()
        
        self._action_states.clear()
    
    def is_initialized(self) -> bool:
        """Check if input manager is initialized."""
        return self._initialized
    
    def cleanup(self) -> None:
        """Clean up input resources."""
        for joystick in self._joysticks.values():
            joystick.quit()
        self._joysticks.clear()
        self._joystick_buttons.clear()
        self._joystick_axes.clear()
        self._initialized = False