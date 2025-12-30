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
        self.title = title
        
        # Get native display resolution for fullscreen
        display_info = pygame.display.Info()
        self.native_size = (display_info.current_w, display_info.current_h)
        
        # Setup display
        if fullscreen:
            self.screen = pygame.display.set_mode(self.native_size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height), pygame.SCALED)
        
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
        # Get InputManager singleton and update it (this consumes pygame events)
        from core.input import InputManager
        input_mgr = InputManager.get_instance()
        
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
        self.screen.fill((0, 0, 0))
        if self.current_scene is not None:
            self.current_scene.draw(self.screen)
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
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.SCALED)
        pygame.display.set_caption(self.title)
    
    def is_fullscreen(self) -> bool:
        """Check if currently in fullscreen mode."""
        return self.fullscreen
    
    def get_fps(self) -> float:
        return self.actual_fps
    
    def get_screen_size(self) -> tuple[int, int]:
        return self.screen.get_size()
    
    def get_screen_center(self) -> tuple[int, int]:
        width, height = self.screen.get_size()
        return (width // 2, height // 2)
