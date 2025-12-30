import pygame
from typing import Optional
from shared.types import DoorState
from shared.constants import DOOR_CLOSED, DOOR_OPEN, DOOR_UNLOCKED, DOOR_LOCKED
from world.entities import Entity
from shared.exceptions import InvalidDoorStateError

class Door(Entity):
    """Door entity requiring specific keys to unlock."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 required_key_id: str, door_id: Optional[str] = None):
        """Initialize door with position, size, and key requirement.
        
        Args:
            x: X position
            y: Y position
            width: Door width
            height: Door height
            required_key_id: ID of key required to unlock
            door_id: Optional unique identifier for the door
        """
        super().__init__((x, y), (width, height))
        self.required_key_id = required_key_id
        self.door_id = door_id or f"door_{x}_{y}"
        self.state = DoorState.LOCKED
        self.visible = True
        self.open_progress = 0.0
        self.open_speed = 5.0  # units per second
        
        # Colors for different states
        self.colors = {
            DoorState.LOCKED: (200, 50, 50),    # Red
            DoorState.UNLOCKED: (50, 200, 50),  # Green
            DoorState.OPEN: (50, 50, 200)       # Blue
        }
    
    def update(self, dt: float) -> None:
        """Update door state and appearance."""
        if self.state == DoorState.OPEN:
            # Animate opening
            self.open_progress = min(1.0, self.open_progress + self.open_speed * dt)
        elif self.state == DoorState.LOCKED or self.state == DoorState.UNLOCKED:
            # Reset opening progress
            self.open_progress = max(0.0, self.open_progress - self.open_speed * dt)
    
    def render(self, surface: pygame.Surface, camera_offset: tuple) -> None:
        """Render door to surface with camera offset.
        
        Args:
            surface: Pygame surface to render to
            camera_offset: Camera offset (x, y)
        """
        if not self.visible:
            return
            
        x = int(self.position[0] - camera_offset[0])
        y = int(self.position[1] - camera_offset[1])
        width = int(self.size[0])
        height = int(self.size[1])
        
        # Calculate current door dimensions based on open progress
        current_width = int(width * (1.0 - self.open_progress))
        current_height = int(height * (1.0 - self.open_progress))
        
        # Center the shrinking door
        offset_x = (width - current_width) // 2
        offset_y = (height - current_height) // 2
        
        # Draw door rectangle
        color = self.colors.get(self.state, (128, 128, 128))
        pygame.draw.rect(surface, color, 
                        (x + offset_x, y + offset_y, current_width, current_height))
        
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255), 
                        (x + offset_x, y + offset_y, current_width, current_height), 2)
        
        # Draw state indicator
        font = pygame.font.Font(None, 16)
        state_text = self.state.name
        text = font.render(state_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(text, text_rect)
        
        # Draw key requirement if locked
        if self.state == DoorState.LOCKED:
            key_text = font.render(f"Key: {self.required_key_id}", True, (255, 255, 255))
            key_rect = key_text.get_rect(center=(x + width // 2, y + height // 2 + 20))
            surface.blit(key_text, key_rect)
    
    def unlock(self, key_id: str) -> bool:
        """Attempt to unlock door with key.
        
        Args:
            key_id: ID of key to try
            
        Returns:
            True if unlocked successfully, False otherwise
        """
        if key_id == self.required_key_id:
            self.state = DoorState.UNLOCKED
            return True
        return False
    
    def open_door(self) -> None:
        """Open the door (changes state to OPEN)."""
        if self.state == DoorState.UNLOCKED:
            self.state = DoorState.OPEN
    
    def close_door(self) -> None:
        """Close the door (changes state to LOCKED)."""
        self.state = DoorState.LOCKED
    
    def reset(self) -> None:
        """Reset door to initial locked state."""
        self.state = DoorState.LOCKED
        self.open_progress = 0.0
    
    def get_state(self) -> DoorState:
        """Get current door state.
        
        Returns:
            Current DoorState
        """
        return self.state
    
    def set_state(self, state: DoorState) -> None:
        """Set door state.
        
        Args:
            state: New DoorState
        """
        self.state = state
    
    def is_unlocked(self) -> bool:
        """Check if door is unlocked.
        
        Returns:
            True if door is unlocked, False otherwise
        """
        return self.state == DoorState.UNLOCKED or self.state == DoorState.OPEN
    
    def is_open(self) -> bool:
        """Check if door is open.
        
        Returns:
            True if door is open, False otherwise
        """
        return self.state == DoorState.OPEN
    
    def get_required_key(self) -> str:
        """Get required key ID.
        
        Returns:
            ID of key required to unlock
        """
        return self.required_key_id
    
    def get_door_id(self) -> str:
        """Get door identifier.
        
        Returns:
            Door ID string
        """
        return self.door_id
    
    def set_visible(self, visible: bool) -> None:
        """Set door visibility.
        
        Args:
            visible: True to make door visible
        """
        self.visible = visible
    
    def is_visible(self) -> bool:
        """Check if door is visible.
        
        Returns:
            True if door is visible
        """
        return self.visible
    
    def get_open_progress(self) -> float:
        """Get door opening progress (0.0 to 1.0).
        
        Returns:
            Opening progress
        """
        return self.open_progress