import pygame
from core.scene import Scene


class BaseObject:
    """Base class for all game objects like collectibles, powerups, hazards."""
    
    def __init__(self, scene: Scene, pos: tuple, size: tuple = (32, 32)):
        self.scene = scene
        self.position = pos
        self.size = size
        self._active = True
        self._marked_for_removal = False
        self.z_index = 0
    
    def update(self, dt: float) -> None:
        """Update the object. Override in subclasses."""
        pass
    
    def render(self, surface: pygame.Surface, camera_offset) -> None:
        """Render the object. Override in subclasses."""
        pass
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def is_active(self) -> bool:
        """Check if object is still active."""
        return self._active and not self._marked_for_removal
    
    def mark_for_removal(self) -> None:
        """Mark this object to be removed on next update cycle."""
        self._marked_for_removal = True
        self._active = False
    
    def destroy(self) -> None:
        """Destroy this object."""
        self._active = False
        self._marked_for_removal = True
