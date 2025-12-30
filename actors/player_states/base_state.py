"""
Abstract base class for all player states.
Adheres to style guides with type annotations and best practices.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple
import pygame

if TYPE_CHECKING:
    from player import Player


class BasePlayerState(ABC):
    """Abstract base class for all player states."""
    
    def __init__(self, player: 'Player') -> None:
        """Initialize the state with a reference to the player.
        
        Args:
            player: The player instance this state belongs to
        """
        self.player = player
    
    @abstractmethod
    def enter(self) -> None:
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the state logic.
        
        Args:
            dt: Delta time in seconds
        """
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """Called when exiting this state."""
        pass
    
    @abstractmethod
    def handle_input(self) -> None:
        """Handle input for this state."""
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the state-specific player appearance."""
        pass
    
    @abstractmethod
    def get_state_name(self) -> str:
        """Get the name of this state.
        
        Returns:
            String identifier for this state
        """
        pass
    
    def _change_state(self, new_state_type: type) -> None:
        """Helper method to change to a new state.
        
        Args:
            new_state_type: The class of the new state to transition to
        """
        # This would be implemented in the player class
        pass