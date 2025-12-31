"""
Q-shaped smoke ring animation overlay.
THE SIGNATURE VISUAL - plays continuously during idle/run states!
Uses actual sprites from qq-qeen-smoqin.png
"""

import pygame
import os
from typing import Tuple, List, Optional
from shared.constants import ASSETS_PATH
from shared.sprite_data import SMOQIN_FRAMES, SMOQIN_CONFIG

class SmokeOverlay:
    """Q-shaped smoke ring animation overlay using actual sprites."""
    
    def __init__(self, position: Tuple[float, float]):
        """
        Initialize smoke overlay.
        
        Args:
            position: Starting position (center of Q)
        """
        self.position = pygame.Vector2(position)
        self.active = True
        
        # Animation state
        self.current_animation = "smoke_idle"
        self.frames: List[pygame.Surface] = []
        self.current_frame = 0
        self.frame_timer = 0.0
        self.animation_speed = 0.25  # seconds per frame
        
        # Offset from player - should be 0 to render at same position
        self.offset_x = 0
        self.offset_y = 0
        
        # Load sprites
        self._load_sprites()
        
    def _load_sprites(self) -> None:
        """Load smoke animation frames from sprite sheet."""
        try:
            sprite_path = os.path.join(ASSETS_PATH, "qq-qeen-smoqin.png")
            if not os.path.exists(sprite_path):
                print(f"Smoke sprite not found: {sprite_path}")
                self._create_fallback_frames()
                return
                
            sheet = pygame.image.load(sprite_path).convert_alpha()
            
            # Get animation spec
            anim_spec = SMOQIN_FRAMES.get(self.current_animation)
            if not anim_spec:
                print(f"Animation spec not found: {self.current_animation}")
                self._create_fallback_frames()
                return
            
            # Extract frames
            self.frames = []
            for i in range(anim_spec.frames):
                x = (anim_spec.start_col + i) * anim_spec.frame_width
                y = anim_spec.row * anim_spec.frame_height
                
                frame = pygame.Surface((anim_spec.frame_width, anim_spec.frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (x, y, anim_spec.frame_width, anim_spec.frame_height))
                
                # Scale down to 64x64 for display
                scaled = pygame.transform.scale(frame, (64, 64))
                self.frames.append(scaled)
            
            self.animation_speed = 1.0 / anim_spec.fps
            print(f"Loaded {len(self.frames)} smoke frames")
            
        except Exception as e:
            print(f"Error loading smoke sprites: {e}")
            self._create_fallback_frames()
    
    def _create_fallback_frames(self) -> None:
        """Create simple fallback frames if sprites can't load."""
        self.frames = []
        # Create 4 simple circle frames with different alphas
        for i in range(4):
            frame = pygame.Surface((64, 64), pygame.SRCALPHA)
            alpha = 60 + i * 30
            pygame.draw.circle(frame, (200, 200, 200, alpha), (32, 32), 20 + i * 5, 3)
            self.frames.append(frame)
        
    def update_position(self, new_position: Tuple[float, float]) -> None:
        """
        Update overlay position to follow target.
        
        Args:
            new_position: New center position
        """
        self.position = pygame.Vector2(new_position)
        
    def update(self, dt: float = None) -> None:
        """Update smoke animation."""
        if not self.active or not self.frames:
            return
        
        # Use fixed dt if not provided
        if dt is None:
            dt = 1.0 / 60.0
            
        self.frame_timer += dt
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """
        Render smoke overlay.
        
        Args:
            surface: Target surface
            camera_offset: Camera offset for screen positioning
        """
        if not self.active or not self.frames:
            return
        
        # Handle both tuple and Vector2 camera offsets
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        # Calculate screen position - center the 64x64 sprite on the hitbox (48x64)
        # This matches the centering in player.render_current_animation
        sprite_size = 64
        hitbox_w, hitbox_h = 48, 64  # From QOMMANDAH_QEEN_HITBOX
        
        screen_x = self.position.x - cam_x - (sprite_size - hitbox_w) // 2
        screen_y = self.position.y - cam_y - (sprite_size - hitbox_h) // 2
        
        # Draw current frame
        frame = self.frames[self.current_frame]
        surface.blit(frame, (screen_x, screen_y))
        
    def reset(self, position: Tuple[float, float]) -> None:
        """
        Reset smoke overlay to start new animation.
        
        Args:
            position: New position for smoke
        """
        self.position = pygame.Vector2(position)
        self.current_frame = 0
        self.frame_timer = 0.0
        self.active = True
        
    def is_animation_complete(self) -> bool:
        """Always returns False since smoke loops continuously."""
        return False
        
    def get_remaining_time(self) -> float:
        """Get remaining animation time (always returns positive for looping)."""
        return 1.0
        
    def set_duration(self, duration: float) -> None:
        """Set animation duration (affects speed)."""
        if duration > 0:
            self.animation_speed = duration / max(1, len(self.frames))
        
    def set_active(self, active: bool) -> None:
        """Set whether smoke is active."""
        self.active = active
