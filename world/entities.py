"""
Base entity system for CyQle 1.

Provides the foundational Entity class that all game objects inherit from.
Entities have position, velocity, and basic lifecycle methods.
"""

from typing import Optional, Tuple
import pygame
from shared.types import Vector2


class Entity:
    """
    Base class for all game entities.
    
    An entity represents any object in the game world that has a position,
    can be updated, and can be drawn. This includes players, enemies,
    collectibles, projectiles, and environmental objects.
    """
    
    def __init__(self, position: Vector2, size: Tuple[int, int] = (32, 32)):
        """
        Initialize a new entity.
        
        Args:
            position: The initial position of the entity (x, y)
            size: The width and height of the entity's bounding box
        """
        self.position = position
        self.velocity = Vector2(0, 0)
        self.size = size
        self.active = True
        self.visible = True
        self.z_index = 0  # Drawing order (higher = drawn on top)
        
    def get_rect(self) -> pygame.Rect:
        """
        Get the entity's bounding rectangle.
        
        Returns:
            A pygame.Rect representing the entity's position and size
        """
        return pygame.Rect(self.position.x, self.position.y, self.size[0], self.size[1])
    
    def get_center(self) -> Vector2:
        """
        Get the center point of the entity.
        
        Returns:
            The center position of the entity
        """
        return Vector2(
            self.position.x + self.size[0] // 2,
            self.position.y + self.size[1] // 2
        )
    
    def update(self, dt: float) -> None:
        """
        Update the entity's state.
        
        This method should be overridden by subclasses to implement
        entity-specific behavior.
        
        Args:
            dt: Delta time in seconds since last update
        """
        # Apply velocity to position
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        
    def draw(self, surface: pygame.Surface, camera_offset: Vector2) -> None:
        """
        Draw the entity to the screen.
        
        This method should be overridden by subclasses to implement
        entity-specific rendering.
        
        Args:
            surface: The pygame surface to draw on
            camera_offset: The camera's offset for proper screen positioning
        """
        # Base implementation does nothing - subclasses must implement
        pass
    
    def is_colliding_with(self, other: 'Entity') -> bool:
        """
        Check if this entity is colliding with another entity.
        
        Args:
            other: Another entity to check collision with
            
        Returns:
            True if the entities' rectangles intersect, False otherwise
        """
        return self.get_rect().colliderect(other.get_rect())
    
    def destroy(self) -> None:
        """
        Mark the entity for destruction.
        
        The entity will be removed from the game world on the next update cycle.
        """
        self.active = False
        
    def is_active(self) -> bool:
        """
        Check if the entity is active and should be updated.
        
        Returns:
            True if the entity is active, False otherwise
        """
        return self.active
    
    def is_visible(self) -> bool:
        """
        Check if the entity is visible and should be drawn.
        
        Returns:
            True if the entity is visible, False otherwise
        """
        return self.visible
    
    def set_position(self, x: float, y: float) -> None:
        """
        Set the entity's position.
        
        Args:
            x: The new x-coordinate
            y: The new y-coordinate
        """
        self.position = Vector2(int(x), int(y))
        
    def set_velocity(self, x: float, y: float) -> None:
        """
        Set the entity's velocity.
        
        Args:
            x: The new x-velocity
            y: The new y-velocity
        """
        self.velocity = Vector2(int(x), int(y))
        
    def add_velocity(self, x: float, y: float) -> None:
        """
        Add to the entity's current velocity.
        
        Args:
            x: The x-velocity to add
            y: The y-velocity to add
        """
        self.velocity.x += x
        self.velocity.y += y
        
    def get_z_index(self) -> int:
        """
        Get the entity's drawing order.
        
        Returns:
            The z-index (higher = drawn on top)
        """
        return self.z_index
        
    def set_z_index(self, z_index: int) -> None:
        """
        Set the entity's drawing order.
        
        Args:
            z_index: The new z-index (higher = drawn on top)
        """
        self.z_index = z_index