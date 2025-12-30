"""
Base scene class for game scenes.
"""

import pygame
from typing import Any, Optional
from abc import ABC, abstractmethod


class Scene(ABC):
    """
    Abstract base class for all game scenes.
    
    Scenes represent different states of the game (menu, level, pause, etc.)
    and implement the game logic and rendering for that state.
    """
    
    def __init__(self, engine: Any):
        """
        Initialize the scene.
        
        Args:
            engine: Reference to the game engine
        """
        self.engine = engine
        self.next_scene: Optional[str] = None
        self._is_initialized = False
        
    @abstractmethod
    def setup(self) -> None:
        """
        Set up the scene. Called when the scene becomes active.
        
        This should initialize all resources, create entities, load assets, etc.
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up scene resources. Called when the scene is being exited.
        
        This should free resources, save state, etc.
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle a single pygame event.
        
        Args:
            event: Pygame event to handle
        """
        pass
    
    @abstractmethod
    def fixed_update(self, delta_time: float) -> None:
        """
        Update scene with fixed timestep (for physics, etc.).
        
        Args:
            delta_time: Fixed timestep duration
        """
        pass
    
    @abstractmethod
    def update(self, delta_time: float, alpha: float) -> None:
        """
        Update scene with variable timestep (for interpolation, etc.).
        
        Args:
            delta_time: Variable timestep duration
            alpha: Interpolation factor for rendering (0.0 to 1.0)
        """
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the scene to the given surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        pass
    
    def request_scene_change(self, scene_name: str) -> None:
        """
        Request a scene change.
        
        Args:
            scene_name: Name of the scene to transition to
        """
        self.next_scene = scene_name
    
    def is_initialized(self) -> bool:
        """
        Check if the scene has been initialized.
        
        Returns:
            True if scene has been set up, False otherwise
        """
        return self._is_initialized
    
    def get_engine(self) -> Any:
        """
        Get reference to the game engine.
        
        Returns:
            Engine instance
        """
        return self.engine
    
    def get_screen_size(self) -> tuple[int, int]:
        """
        Get screen dimensions from engine.
        
        Returns:
            Tuple of (width, height)
        """
        return self.engine.get_screen_size()
    
    def get_screen_center(self) -> tuple[int, int]:
        """
        Get screen center coordinates from engine.
        
        Returns:
            Tuple of (center_x, center_y)
        """
        return self.engine.get_screen_center()
    
    def create_surface(self, size: tuple[int, int], alpha: bool = False) -> pygame.Surface:
        """
        Create a new pygame surface.
        
        Args:
            size: Surface dimensions (width, height)
            alpha: Whether to include alpha channel
            
        Returns:
            New pygame surface
        """
        if alpha:
            return pygame.Surface(size, pygame.SRCALPHA)
        return pygame.Surface(size)
    
    def draw_text(self, surface: pygame.Surface, text: str, position: tuple[int, int], 
                  color: tuple[int, int, int] = (255, 255, 255), 
                  font_size: int = 24, font_name: Optional[str] = None) -> None:
        """
        Draw text on a surface.
        
        Args:
            surface: Surface to draw on
            text: Text to draw
            position: (x, y) position
            color: RGB color tuple
            font_size: Font size in pixels
            font_name: Font name (None for default)
        """
        try:
            if font_name:
                font = pygame.font.SysFont(font_name, font_size)
            else:
                font = pygame.font.Font(None, font_size)
            
            text_surface = font.render(text, True, color)
            surface.blit(text_surface, position)
        except Exception:
            # Fallback if font loading fails
            pass