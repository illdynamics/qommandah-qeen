"""
Core game engine implementing main loop with fixed timestep.
"""

import pygame
import time
from typing import Optional
from core.scene import Scene
from core.input import InputManager


class Engine:
    """Main game engine managing the game loop, scene transitions, and fixed timestep updates."""
    
    def __init__(self, title: str = "QommandahQeen", width: int = 1280, height: int = 720, 
                 target_fps: int = 60, fixed_delta: float = 1.0/60.0, fullscreen: bool = False):
        pygame.init()
        
        self.fullscreen = fullscreen
        self.windowed_size = (width, height)
        self.game_size = (width, height)  # Logical game resolution
        self.title = title
        
        # Get native display resolution for fullscreen
        display_info = pygame.display.Info()
        self.native_size = (display_info.current_w, display_info.current_h)
        
        # Create game surface (render target at logical resolution)
        self.game_surface = pygame.Surface(self.game_size)
        
        # Setup display
        if fullscreen:
            self.screen = pygame.display.set_mode(self.native_size, pygame.FULLSCREEN)
            self._calculate_fullscreen_scaling()
        else:
            self.screen = pygame.display.set_mode((width, height), pygame.SCALED)
            self.scale_factor = 1.0
            self.render_offset = (0, 0)
        
        pygame.display.set_caption(title)
        
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.fixed_delta = fixed_delta
        
        self.current_scene: Optional[Scene] = None
        self.next_scene: Optional[Scene] = None
        
        self.running = False
        self.accumulator = 0.0
        self.last_time = 0.0
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = 0.0
        self.actual_fps = 0.0
        
        # Initialize InputManager singleton with default mappings
        self.input_manager = InputManager.get_instance()
        self.input_manager.initialize()
    
    def _calculate_fullscreen_scaling(self) -> None:
        """Calculate scaling factor and offset for fullscreen rendering."""
        # Calculate scale to fit game in screen while maintaining aspect ratio
        scale_x = self.native_size[0] / self.game_size[0]
        scale_y = self.native_size[1] / self.game_size[1]
        self.scale_factor = min(scale_x, scale_y)
        
        # Calculate centered offset
        scaled_width = int(self.game_size[0] * self.scale_factor)
        scaled_height = int(self.game_size[1] * self.scale_factor)
        self.render_offset = (
            (self.native_size[0] - scaled_width) // 2,
            (self.native_size[1] - scaled_height) // 2
        )
        
    def set_scene(self, scene: Scene) -> None:
        """Set the next scene to transition to."""
        self.next_scene = scene
        
    def _transition_scene(self) -> None:
        """Handle scene transition if a new scene is queued."""
        if self.next_scene is not None:
            if self.current_scene is not None:
                self.current_scene.cleanup()
            
            self.current_scene = self.next_scene
            self.next_scene = None
            
            if self.current_scene is not None:
                self.current_scene.setup()
    
    def run(self) -> None:
        """Start the main game loop."""
        self._transition_scene()
        if self.current_scene is None:
            raise RuntimeError("No scene set before running engine")
        
        self.running = True
        self.last_time = time.time()
        self.start_time = self.last_time
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - self.last_time
            self.last_time = current_time
            
            if delta_time > 0.25:
                delta_time = 0.25
            
            self.accumulator += delta_time
            self._process_events()
            
            while self.accumulator >= self.fixed_delta:
                self._fixed_update(self.fixed_delta)
                self.accumulator -= self.fixed_delta
            
            alpha = self.accumulator / self.fixed_delta
            self._update(delta_time, alpha)
            self._render()
            self._transition_scene()
            self._update_fps_counter(delta_time)
            self.clock.tick(self.target_fps)
        
        self._cleanup()
    
    def _process_events(self) -> None:
        # Get InputManager singleton
        from core.input import InputManager
        input_mgr = InputManager.get_instance()
        
        # Clear pressed/released states from PREVIOUS frame BEFORE processing new events
        input_mgr._key_pressed.clear()
        input_mgr._key_released.clear()
        input_mgr._mouse_pressed = [False, False, False]
        input_mgr._mouse_released = [False, False, False]
        
        # Manually process events so both InputManager and scenes get them
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            # Handle F11 for fullscreen toggle
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue
            
            # Let InputManager track key states
            input_mgr._process_event(event)
            
            # Let scene handle the event too
            if self.current_scene is not None:
                self.current_scene.handle_event(event)
        
        # Update action states after processing all events
        input_mgr._update_action_states()
    
    def _fixed_update(self, delta_time: float) -> None:
        if self.current_scene is not None:
            self.current_scene.fixed_update(delta_time)
    
    def _update(self, delta_time: float, alpha: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(delta_time, alpha)
    
    def _render(self) -> None:
        # Clear main screen with black (for letterboxing)
        self.screen.fill((0, 0, 0))
        
        # Render scene to game surface
        if self.current_scene is not None:
            self.current_scene.draw(self.game_surface)
        
        # In fullscreen mode, scale and center the game surface
        if self.fullscreen:
            scaled_width = int(self.game_size[0] * self.scale_factor)
            scaled_height = int(self.game_size[1] * self.scale_factor)
            scaled_surface = pygame.transform.scale(self.game_surface, (scaled_width, scaled_height))
            self.screen.blit(scaled_surface, self.render_offset)
        else:
            # In windowed mode with SCALED flag, just blit directly
            self.screen.blit(self.game_surface, (0, 0))
        
        pygame.display.flip()
    
    def _update_fps_counter(self, delta_time: float) -> None:
        self.frame_count += 1
        if time.time() - self.start_time >= 1.0:
            self.actual_fps = self.frame_count / (time.time() - self.start_time)
            self.frame_count = 0
            self.start_time = time.time()
    
    def _cleanup(self) -> None:
        if self.current_scene is not None:
            self.current_scene.cleanup()
        pygame.quit()
    
    def quit(self) -> None:
        """Request engine to stop running."""
        self.running = False
    
    def toggle_fullscreen(self) -> None:
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.native_size, pygame.FULLSCREEN)
            self._calculate_fullscreen_scaling()
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.SCALED)
            self.scale_factor = 1.0
            self.render_offset = (0, 0)
        pygame.display.set_caption(self.title)
    
    def is_fullscreen(self) -> bool:
        """Check if currently in fullscreen mode."""
        return self.fullscreen
    
    def get_fps(self) -> float:
        return self.actual_fps
    
    def get_screen_size(self) -> tuple[int, int]:
        """Return the logical game size (not physical screen size)."""
        return self.game_size
    
    def get_screen_center(self) -> tuple[int, int]:
        width, height = self.game_size
        return (width // 2, height // 2)
