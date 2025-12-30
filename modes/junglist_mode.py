"""
Junglist Mode - Implements 174 BPM pulses and beat detection.
"""

import time
import math
from typing import Any, Optional, Callable
from modes.base_mode import BaseMode


class JunglistMode(BaseMode):
    """Mode that implements 174 BPM pulses and beat detection."""
    
    def __init__(self) -> None:
        """Initialize the Junglist mode."""
        super().__init__(
            mode_id="junglist",
            display_name="Junglist",
            description="174 BPM pulses with beat detection"
        )
        
        # Beat timing constants (174 BPM = 2.9 Hz)
        self.bpm = 174
        self.beat_interval = 60.0 / self.bpm  # Seconds per beat
        
        # Beat tracking
        self._start_time: Optional[float] = None
        self._last_beat_time: Optional[float] = None
        self._beat_count: int = 0
        
        # Pulse parameters
        self.pulse_strength = 0.3  # How strong the visual pulse is (0-1)
        self.pulse_duration = 0.1  # How long the pulse lasts (seconds)
        self._pulse_start_time: Optional[float] = None
        self._current_pulse_intensity: float = 0.0
        
        # Beat detection
        self._beat_callbacks: list[Callable[[int], None]] = []
        
        # Visual effects
        self._original_gravity: Optional[float] = None
        self._beat_gravity_multiplier = 1.2
        self._normal_gravity_multiplier = 1.0
    
    def activate(self, game_state: Any) -> None:
        """
        Activate the junglist mode.
        
        Args:
            game_state: The current game state object
        """
        super().activate(game_state)
        
        # Initialize timing
        self._start_time = time.time()
        self._last_beat_time = self._start_time
        self._beat_count = 0
        
        # Store original gravity if available
        if hasattr(game_state, 'physics_world'):
            physics = game_state.physics_world
            if hasattr(physics, 'gravity'):
                self._original_gravity = physics.gravity
        
        # Register for updates
        self._register_beat_callbacks(game_state)
    
    def deactivate(self, game_state: Any) -> None:
        """
        Deactivate the junglist mode.
        
        Args:
            game_state: The current game state object
        """
        super().deactivate(game_state)
        
        # Restore original gravity
        if hasattr(self, '_original_gravity') and self._original_gravity is not None:
            if hasattr(game_state, 'physics_world'):
                physics = game_state.physics_world
                if hasattr(physics, 'gravity'):
                    physics.gravity = self._original_gravity
        
        # Clear callbacks
        self._beat_callbacks.clear()
        
        # Reset timing
        self._start_time = None
        self._last_beat_time = None
        self._beat_count = 0
        self._pulse_start_time = None
        self._current_pulse_intensity = 0.0
    
    def update(self, dt: float, game_state: Any) -> None:
        """
        Update the junglist mode with beat detection and pulses.
        
        Args:
            dt: Delta time in seconds
            game_state: The current game state object
        """
        super().update(dt, game_state)
        
        if not self.is_active or self._start_time is None:
            return
        
        current_time = time.time()
        elapsed_since_start = current_time - self._start_time
        
        # Check for beat
        if self._last_beat_time is None or \
           (current_time - self._last_beat_time) >= self.beat_interval:
            
            # Trigger beat
            self._trigger_beat(current_time, game_state)
        
        # Update pulse intensity
        self._update_pulse_intensity(current_time)
        
        # Apply visual effects based on pulse
        self._apply_visual_effects(game_state)
    
    def _trigger_beat(self, current_time: float, game_state: Any) -> None:
        """
        Trigger a beat event.
        
        Args:
            current_time: Current time in seconds
            game_state: The current game state object
        """
        self._last_beat_time = current_time
        self._beat_count += 1
        self._pulse_start_time = current_time
        
        # Call beat callbacks
        for callback in self._beat_callbacks:
            try:
                callback(self._beat_count)
            except Exception:
                pass  # Silently ignore callback errors
        
        # Apply beat effects to physics
        self._apply_beat_physics(game_state)
    
    def _update_pulse_intensity(self, current_time: float) -> None:
        """
        Update the current pulse intensity based on time.
        
        Args:
            current_time: Current time in seconds
        """
        if self._pulse_start_time is None:
            self._current_pulse_intensity = 0.0
            return
        
        time_since_pulse = current_time - self._pulse_start_time
        
        if time_since_pulse < self.pulse_duration:
            # Pulse is active - calculate intensity (ease out)
            progress = time_since_pulse / self.pulse_duration
            self._current_pulse_intensity = self.pulse_strength * (1.0 - progress)
        else:
            # Pulse is over
            self._current_pulse_intensity = 0.0
    
    def _apply_visual_effects(self, game_state: Any) -> None:
        """
        Apply visual effects based on current pulse intensity.
        
        Args:
            game_state: The current game state object
        """
        intensity = self._current_pulse_intensity
        
        # Apply screen shake if available
        if hasattr(game_state, 'camera'):
            camera = game_state.camera
            if hasattr(camera, 'shake'):
                # Scale shake by pulse intensity
                camera.shake = intensity * 5.0  # Max 5 pixels of shake
        
        # Apply color tint if available
        if hasattr(game_state, 'renderer'):
            renderer = game_state.renderer
            if hasattr(renderer, 'set_color_tint'):
                # Pulse creates a slight red tint
                red = intensity * 0.3  # Up to 30% red tint
                renderer.set_color_tint(red, 0.0, 0.0, 0.0)
    
    def _apply_beat_physics(self, game_state: Any) -> None:
        """
        Apply physics effects on beat.
        
        Args:
            game_state: The current game state object
        """
        if hasattr(game_state, 'physics_world'):
            physics = game_state.physics_world
            
            # Temporarily increase gravity on beat
            if hasattr(physics, 'gravity') and self._original_gravity is not None:
                # Store current gravity before modifying
                current_gravity = physics.gravity
                
                # Apply beat gravity multiplier
                physics.gravity = self._original_gravity * self._beat_gravity_multiplier
                
                # Schedule gravity restoration
                def restore_gravity():
                    if hasattr(physics, 'gravity'):
                        physics.gravity = current_gravity
                
                # In a real implementation, you'd use a timer/coroutine
                # For now, we'll restore on next update
                self._schedule_gravity_restoration(physics, current_gravity)
    
    def _schedule_gravity_restoration(self, physics: Any, target_gravity: float) -> None:
        """
        Schedule gravity restoration after beat effect.
        
        Args:
            physics: Physics world object
            target_gravity: Gravity value to restore to
        """
        # This would typically use a timer or coroutine
        # For simplicity, we'll restore after a short delay
        # In practice, you'd want to use the game's update loop
        pass
    
    def _register_beat_callbacks(self, game_state: Any) -> None:
        """
        Register beat callbacks with game systems.
        
        Args:
            game_state: The current game state object
        """
        # Register with player for movement sync
        if hasattr(game_state, 'player'):
            player = game_state.player
            
            def on_player_beat(beat_num: int) -> None:
                # Sync player animation or effects with beat
                if hasattr(player, 'sync_with_beat'):
                    player.sync_with_beat(beat_num)
            
            self._beat_callbacks.append(on_player_beat)
        
        # Register with particle system for beat effects
        if hasattr(game_state, 'particle_system'):
            particle_system = game_state.particle_system
            
            def on_particle_beat(beat_num: int) -> None:
                # Emit beat particles
                if hasattr(particle_system, 'emit_beat_particles'):
                    particle_system.emit_beat_particles(beat_num)
            
            self._beat_callbacks.append(on_particle_beat)
    
    def get_current_beat(self) -> int:
        """
        Get the current beat count.
        
        Returns:
            Current beat number (0 if not active)
        """
        return self._beat_count if self.is_active else 0
    
    def get_beat_progress(self) -> float:
        """
        Get progress to next beat (0 to 1).
        
        Returns:
            Progress to next beat (0 = just beat, 1 = about to beat)
        """
        if not self.is_active or self._last_beat_time is None:
            return 0.0
        
        current_time = time.time()
        time_since_beat = current_time - self._last_beat_time
        progress = time_since_beat / self.beat_interval
        
        return min(progress, 1.0)
    
    def get_pulse_intensity(self) -> float:
        """
        Get current pulse intensity.
        
        Returns:
            Current pulse intensity (0 to pulse_strength)
        """
        return self._current_pulse_intensity if self.is_active else 0.0
    
    def add_beat_callback(self, callback: Callable[[int], None]) -> None:
        """
        Add a callback to be called on each beat.
        
        Args:
            callback: Function to call with beat number
        """
        if callback not in self._beat_callbacks:
            self._beat_callbacks.append(callback)
    
    def remove_beat_callback(self, callback: Callable[[int], None]) -> None:
        """
        Remove a beat callback.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._beat_callbacks:
            self._beat_callbacks.remove(callback)