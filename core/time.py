import pygame
from typing import Optional

class Time:
    """
    Singleton time manager for the game.
    
    Provides:
    - Delta time (frame-to-frame time difference)
    - Global time scale (for slow-motion, pause effects)
    - Fixed physics timestep management
    - Frame rate limiting
    """
    _instance = None
    
    def __new__(cls) -> 'Time':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the time manager."""
        if hasattr(self, '_initialized'):
            return
            
        self._clock = pygame.time.Clock()
        self._delta_time = 0.0
        self._total_time = 0.0
        self._frame_count = 0
        self._time_scale = 1.0
        self._paused = False
        
        # Fixed timestep for physics
        self._fixed_delta_time = 1.0 / 60.0  # 60 FPS physics
        self._accumulator = 0.0
        
        # FPS limiting
        self._target_fps = 60
        self._actual_fps = 0.0
        self._fps_update_timer = 0.0
        self._fps_update_interval = 0.5  # Update FPS every 0.5 seconds
        
        self._initialized = True
    
    def update(self) -> None:
        """
        Update time values for the current frame.
        Should be called once per frame in the main loop.
        """
        # Get raw delta time
        raw_delta = self._clock.tick(self._target_fps) / 1000.0  # Convert ms to seconds
        
        # Apply time scale and pause
        if self._paused:
            self._delta_time = 0.0
        else:
            self._delta_time = raw_delta * self._time_scale
        
        # Update total time (only when not paused)
        if not self._paused:
            self._total_time += self._delta_time
        
        self._frame_count += 1
        
        # Update accumulator for fixed timestep
        if not self._paused:
            self._accumulator += self._delta_time
        
        # Update FPS counter
        self._fps_update_timer += raw_delta
        if self._fps_update_timer >= self._fps_update_interval:
            self._actual_fps = self._clock.get_fps()
            self._fps_update_timer = 0.0
    
    def get_delta_time(self) -> float:
        """
        Get the scaled delta time for this frame.
        
        Returns:
            float: Time in seconds since last frame, scaled by time_scale
        """
        return self._delta_time
    
    def get_fixed_delta_time(self) -> float:
        """
        Get the fixed timestep for physics updates.
        
        Returns:
            float: Fixed physics timestep in seconds
        """
        return self._fixed_delta_time
    
    def get_time_scale(self) -> float:
        """
        Get the current global time scale.
        
        Returns:
            float: Current time scale (1.0 = normal speed)
        """
        return self._time_scale
    
    def set_time_scale(self, scale: float) -> None:
        """
        Set the global time scale.
        
        Args:
            scale: Time scale multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
        """
        self._time_scale = max(0.0, scale)
    
    def get_total_time(self) -> float:
        """
        Get total elapsed game time.
        
        Returns:
            float: Total time in seconds since game start
        """
        return self._total_time
    
    def get_frame_count(self) -> int:
        """
        Get total number of frames rendered.
        
        Returns:
            int: Frame count since game start
        """
        return self._frame_count
    
    def get_fps(self) -> float:
        """
        Get current frames per second.
        
        Returns:
            float: Current FPS
        """
        return self._actual_fps
    
    def set_target_fps(self, fps: int) -> None:
        """
        Set target FPS for frame rate limiting.
        
        Args:
            fps: Target frames per second
        """
        self._target_fps = max(1, fps)
    
    def get_target_fps(self) -> int:
        """
        Get target FPS.
        
        Returns:
            int: Target frames per second
        """
        return self._target_fps
    
    def is_paused(self) -> bool:
        """
        Check if time is paused.
        
        Returns:
            bool: True if time is paused
        """
        return self._paused
    
    def set_paused(self, paused: bool) -> None:
        """
        Pause or unpause time.
        
        Args:
            paused: True to pause, False to unpause
        """
        self._paused = paused
    
    def toggle_pause(self) -> None:
        """Toggle pause state."""
        self._paused = not self._paused
    
    def should_do_physics_update(self) -> bool:
        """
        Check if a physics update should be performed this frame.
        Uses fixed timestep with accumulator.
        
        Returns:
            bool: True if physics should update
        """
        if self._paused:
            return False
        return self._accumulator >= self._fixed_delta_time
    
    def get_physics_updates_this_frame(self) -> int:
        """
        Get number of physics updates needed this frame.
        Handles catch-up for slow frames.
        
        Returns:
            int: Number of physics updates to perform
        """
        if self._paused:
            return 0
        
        updates = 0
        while self._accumulator >= self._fixed_delta_time:
            self._accumulator -= self._fixed_delta_time
            updates += 1
        
        # Prevent spiral of death by limiting updates per frame
        max_updates = 5
        if updates > max_updates:
            self._accumulator = 0.0
            updates = max_updates
        
        return updates
    
    def reset_accumulator(self) -> None:
        """Reset the physics accumulator (useful when loading new levels)."""
        self._accumulator = 0.0
    
    def get_interpolation_factor(self) -> float:
        """
        Get interpolation factor for smooth rendering between physics updates.
        
        Returns:
            float: Interpolation factor (0.0 to 1.0)
        """
        if self._fixed_delta_time > 0:
            return self._accumulator / self._fixed_delta_time
        return 0.0