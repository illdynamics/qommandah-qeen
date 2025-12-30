"""
Camera system for Cyqle 1.
Implements smooth following, parallax backgrounds, and viewport management.
"""

import pygame
import math
from typing import Tuple, List, Optional
from shared.types import Vector2


class Camera:
    """
    Game camera that follows the player with smooth interpolation.
    
    Features:
    - Smooth following with lerp
    - Parallax background layers
    - Viewport bounds and limits
    - Screen shake effects
    - Zoom functionality
    """
    
    def __init__(self, 
                 viewport_size: Tuple[int, int],
                 world_bounds: Optional[Tuple[int, int]] = None) -> None:
        """
        Initialize the camera.
        
        Args:
            viewport_size: (width, height) of the camera viewport
            world_bounds: Optional (width, height) of the world for bounds checking
        """
        self._viewport_size = Vector2(*viewport_size)
        self._position = Vector2(0, 0)
        self._target_position = Vector2(0, 0)
        self._smooth_speed: float = 0.1
        self._zoom: float = 1.0
        self._target_zoom: float = 1.0
        self._zoom_speed: float = 0.05
        
        self._world_bounds = Vector2(*world_bounds) if world_bounds else None
        self._shake_intensity: float = 0.0
        self._shake_duration: float = 0.0
        self._shake_timer: float = 0.0
        
        self._parallax_layers: List[Tuple[float, pygame.Surface]] = []
        self._deadzone_radius: float = 50.0
        self._is_locked: bool = False
    
    def update(self, delta_time: float) -> None:
        """
        Update camera position and effects.
        
        Args:
            delta_time: Time since last update in seconds
        """
        if not self._is_locked:
            # Smoothly interpolate to target position
            diff = self._target_position - self._position
            self._position += diff * self._smooth_speed
            
            # Apply bounds if world bounds are set
            if self._world_bounds:
                # Calculate the valid camera range
                # Camera position is CENTER of view
                half_viewport_x = self._viewport_size.x * 0.5 / self._zoom
                half_viewport_y = self._viewport_size.y * 0.5 / self._zoom
                
                # If viewport is smaller than world, clamp to keep view inside world
                # If viewport is larger than world, center the world in view
                if self._viewport_size.x / self._zoom < self._world_bounds.x:
                    min_x = half_viewport_x
                    max_x = self._world_bounds.x - half_viewport_x
                else:
                    # Viewport wider than world - center horizontally
                    min_x = max_x = self._world_bounds.x / 2
                
                if self._viewport_size.y / self._zoom < self._world_bounds.y:
                    min_y = half_viewport_y
                    max_y = self._world_bounds.y - half_viewport_y
                else:
                    # Viewport taller than world - center vertically
                    min_y = max_y = self._world_bounds.y / 2
                
                self._position = Vector2(
                    max(min_x, min(max_x, self._position.x)),
                    max(min_y, min(max_y, self._position.y))
                )
        
        # Update zoom
        zoom_diff = self._target_zoom - self._zoom
        self._zoom += zoom_diff * self._zoom_speed
        
        # Update screen shake
        if self._shake_timer > 0:
            self._shake_timer -= delta_time
            if self._shake_timer <= 0:
                self._shake_intensity = 0.0
                self._shake_duration = 0.0
    
    def set_target(self, target: Vector2) -> None:
        """
        Set the camera's target position.
        
        Args:
            target: Target position in world coordinates
        """
        self._target_position = Vector2(target.x, target.y)
        
        # Apply deadzone
        if not self._is_locked:
            diff = self._target_position - self._position
            distance = math.sqrt(diff.x ** 2 + diff.y ** 2)
            
            if distance < self._deadzone_radius:
                # Inside deadzone, don't move camera
                self._target_position = Vector2(self._position.x, self._position.y)
    
    def get_position(self) -> Vector2:
        """
        Get current camera position (CENTER of view).
        
        Returns:
            Vector2: Camera center position in world coordinates
        """
        pos = Vector2(self._position.x, self._position.y)
        
        # Apply screen shake
        if self._shake_timer > 0:
            import random
            angle = random.uniform(0, 6.28318530718)  # 2 * pi
            intensity = self._shake_intensity * (self._shake_timer / self._shake_duration)
            pos = Vector2(
                pos.x + random.uniform(-intensity, intensity),
                pos.y + random.uniform(-intensity, intensity)
            )
        
        return pos
    
    def get_offset(self) -> Vector2:
        """
        Get camera offset for rendering (TOP-LEFT of view).
        
        This is what you subtract from world positions to get screen positions.
        
        Returns:
            Vector2: Top-left offset for rendering
        """
        center = self.get_position()
        half_viewport_x = self._viewport_size.x * 0.5 / self._zoom
        half_viewport_y = self._viewport_size.y * 0.5 / self._zoom
        
        return Vector2(
            center.x - half_viewport_x,
            center.y - half_viewport_y
        )
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in world coordinates
            
        Returns:
            Vector2: Position in screen coordinates
        """
        camera_pos = self.get_position()
        screen_center = self._viewport_size * 0.5
        
        # Apply camera transform
        screen_pos = (world_pos - camera_pos) * self._zoom + screen_center
        return screen_pos
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Position in screen coordinates
            
        Returns:
            Vector2: Position in world coordinates
        """
        camera_pos = self.get_position()
        screen_center = self._viewport_size * 0.5
        
        # Reverse camera transform
        world_pos = (screen_pos - screen_center) / self._zoom + camera_pos
        return world_pos
    
    def get_viewport_rect(self) -> pygame.Rect:
        """
        Get the camera's viewport in world coordinates.
        
        Returns:
            pygame.Rect: Viewport rectangle in world space
        """
        pos = self.get_position()
        half_size = self._viewport_size * 0.5 / self._zoom
        
        return pygame.Rect(
            pos.x - half_size.x,
            pos.y - half_size.y,
            self._viewport_size.x / self._zoom,
            self._viewport_size.y / self._zoom
        )
    
    def set_zoom(self, zoom: float) -> None:
        """
        Set camera zoom level.
        
        Args:
            zoom: Zoom multiplier (1.0 = normal, 2.0 = 2x zoom in, 0.5 = 2x zoom out)
        """
        self._target_zoom = max(0.1, zoom)
    
    def get_zoom(self) -> float:
        """
        Get current zoom level.
        
        Returns:
            float: Current zoom multiplier
        """
        return self._zoom
    
    def shake(self, intensity: float, duration: float) -> None:
        """
        Apply screen shake effect.
        
        Args:
            intensity: Maximum shake offset in pixels
            duration: Shake duration in seconds
        """
        self._shake_intensity = intensity
        self._shake_duration = duration
        self._shake_timer = duration
    
    def add_parallax_layer(self, surface: pygame.Surface, speed: float) -> None:
        """
        Add a parallax background layer.
        
        Args:
            surface: Background surface
            speed: Parallax speed (0.0 = stationary, 1.0 = moves with camera)
        """
        self._parallax_layers.append((speed, surface))
    
    def clear_parallax_layers(self) -> None:
        """Remove all parallax layers."""
        self._parallax_layers.clear()
    
    def render_parallax(self, surface: pygame.Rect, screen: pygame.Surface) -> None:
        """
        Render parallax background layers.
        
        Args:
            surface: Area to render to (usually the entire screen)
            screen: Target surface to render on
        """
        camera_pos = self.get_position()
        
        for speed, bg_surface in self._parallax_layers:
            # Calculate parallax offset
            offset_x = camera_pos.x * (1 - speed)
            offset_y = camera_pos.y * (1 - speed)
            
            # Tile the background
            bg_width = bg_surface.get_width()
            bg_height = bg_surface.get_height()
            
            if bg_width == 0 or bg_height == 0:
                continue
            
            start_x = int(-offset_x % bg_width)
            start_y = int(-offset_y % bg_height)
            
            # Draw tiles
            x = start_x
            while x < surface.width:
                y = start_y
                while y < surface.height:
                    screen.blit(bg_surface, (surface.x + x, surface.y + y))
                    y += bg_height
                x += bg_width
    
    def set_smooth_speed(self, speed: float) -> None:
        """
        Set camera smoothing speed.
        
        Args:
            speed: Smoothing speed (0.0 = instant, 1.0 = very slow)
        """
        self._smooth_speed = max(0.0, min(1.0, speed))
    
    def get_smooth_speed(self) -> float:
        """
        Get camera smoothing speed.
        
        Returns:
            float: Current smoothing speed
        """
        return self._smooth_speed
    
    def set_deadzone_radius(self, radius: float) -> None:
        """
        Set deadzone radius for camera following.
        
        Args:
            radius: Deadzone radius in pixels
        """
        self._deadzone_radius = max(0.0, radius)
    
    def get_deadzone_radius(self) -> float:
        """
        Get deadzone radius.
        
        Returns:
            float: Current deadzone radius
        """
        return self._deadzone_radius
    
    def set_locked(self, locked: bool) -> None:
        """
        Lock or unlock camera movement.
        
        Args:
            locked: True to lock camera in place
        """
        self._is_locked = locked
    
    def is_locked(self) -> bool:
        """
        Check if camera is locked.
        
        Returns:
            bool: True if camera is locked
        """
        return self._is_locked
    
    def get_viewport_size(self) -> Tuple[int, int]:
        """
        Get viewport size.
        
        Returns:
            Tuple[int, int]: (width, height) of viewport
        """
        return (int(self._viewport_size.x), int(self._viewport_size.y))
    
    def set_viewport_size(self, width: int, height: int) -> None:
        """
        Set viewport size.
        
        Args:
            width: New viewport width
            height: New viewport height
        """
        self._viewport_size = Vector2(width, height)
    
    def reset(self) -> None:
        """Reset camera to initial state."""
        self._position = Vector2(0, 0)
        self._target_position = Vector2(0, 0)
        self._zoom = 1.0
        self._target_zoom = 1.0
        self._shake_intensity = 0.0
        self._shake_duration = 0.0
        self._shake_timer = 0.0
        self._is_locked = False