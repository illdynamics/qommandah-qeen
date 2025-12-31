"""
Key pickup object - collecting grants ability to open doors.
Uses qq-key-object.png sprite sheet.
"""
import pygame
import os
from typing import Optional, List, Tuple
from shared.constants import ASSETS_PATH, TILE_SIZE
from world.entities import Entity


class KeyPickup(Entity):
    """Collectible key that allows player to open doors."""
    
    def __init__(self, x: int, y: int, key_id: str = "default"):
        """Initialize key pickup.
        
        Args:
            x: X position
            y: Y position
            key_id: Unique identifier for this key (matches door requirements)
        """
        super().__init__((x, y), (32, 32))
        self.key_id = key_id
        self.collected = False
        self.visible = True
        
        # Animation
        self._frames: List[pygame.Surface] = []
        self._current_frame = 0
        self._animation_timer = 0.0
        self._animation_fps = 8.0
        self._bob_offset = 0.0
        self._bob_speed = 2.0
        self._bob_height = 4.0
        
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """Load key sprite from qq-key-object.png."""
        key_path = os.path.join(ASSETS_PATH, "qq-key-object.png")
        if os.path.exists(key_path):
            key_sheet = pygame.image.load(key_path).convert_alpha()
            # Key sheet is 256x192, 4x3 grid of 64x64
            # Use cells from row 0-1 that have content (cells 1,0 and 2,0)
            for col in [1, 2]:
                x = col * 64
                y = 0
                frame = pygame.Surface((64, 64), pygame.SRCALPHA)
                frame.blit(key_sheet, (0, 0), (x, y, 64, 64))
                # Scale to pickup size
                frame = pygame.transform.scale(frame, (32, 32))
                self._frames.append(frame)
            
            # If we only got 2 frames, that's fine for a simple bob animation
            if not self._frames:
                # Fallback - try different cells
                for row in range(3):
                    for col in range(4):
                        x, y = col * 64, row * 64
                        frame = pygame.Surface((64, 64), pygame.SRCALPHA)
                        frame.blit(key_sheet, (0, 0), (x, y, 64, 64))
                        # Check if frame has content
                        if frame.get_at((32, 32))[3] > 0:
                            frame = pygame.transform.scale(frame, (32, 32))
                            self._frames.append(frame)
                            if len(self._frames) >= 2:
                                break
                    if len(self._frames) >= 2:
                        break
            
            print(f"Loaded key sprites: {len(self._frames)} frames")
    
    def update(self, delta_time: float) -> None:
        """Update key animation and bobbing."""
        if self.collected:
            return
        
        # Update animation frame
        if self._frames:
            self._animation_timer += delta_time
            frame_duration = 1.0 / self._animation_fps
            if self._animation_timer >= frame_duration:
                self._animation_timer -= frame_duration
                self._current_frame = (self._current_frame + 1) % len(self._frames)
        
        # Update bobbing
        import math
        self._bob_offset = math.sin(pygame.time.get_ticks() * 0.001 * self._bob_speed * math.pi) * self._bob_height
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render key to surface."""
        if not self.visible or self.collected:
            return
        
        x = int(self.position[0] - camera_offset[0])
        y = int(self.position[1] - camera_offset[1] + self._bob_offset)
        
        if self._frames and self._current_frame < len(self._frames):
            surface.blit(self._frames[self._current_frame], (x, y))
        else:
            # Fallback - golden key shape
            pygame.draw.circle(surface, (255, 215, 0), (x + 16, y + 8), 8)
            pygame.draw.rect(surface, (255, 215, 0), (x + 12, y + 8, 8, 20))
            pygame.draw.rect(surface, (255, 215, 0), (x + 8, y + 20, 4, 4))
            pygame.draw.rect(surface, (255, 215, 0), (x + 16, y + 24, 4, 4))
    
    def collect(self) -> str:
        """Mark key as collected and return key_id.
        
        Returns:
            The key_id that was collected
        """
        self.collected = True
        self.visible = False
        return self.key_id
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def is_collected(self) -> bool:
        """Check if key has been collected."""
        return self.collected
    
    def get_key_id(self) -> str:
        """Get the key identifier."""
        return self.key_id
    
    def reset(self) -> None:
        """Reset key to uncollected state."""
        self.collected = False
        self.visible = True
