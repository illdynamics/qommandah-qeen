import pygame
import math
import os
from typing import Tuple
from core.scene import Scene
from shared.types import PowerupType
from shared.constants import ASSETS_PATH
from objects.powerup_pickup import PowerupPickup


class JettpaqPickup(PowerupPickup):
    """JettPaQ powerup pickup - enables jetpack flight."""
    
    def __init__(self, scene: Scene, pos: Tuple[float, float]) -> None:
        super().__init__(scene, pos, PowerupType.JETTPAQ)
        self.glow_phase = 0.0
        self._initialize_jettpaq_sprite()
    
    def _initialize_jettpaq_sprite(self) -> None:
        """Load JettPaQ sprite from qq-bonus-powerups.png."""
        try:
            sprite_path = os.path.join(ASSETS_PATH, "qq-bonus-powerups.png")
            if os.path.exists(sprite_path):
                sheet = pygame.image.load(sprite_path).convert_alpha()
                # Sheet is 256x128 = 4x2 grid of 64x64 cells
                # JettPaq is at cell (0,0) or (1,0)
                cell_size = 64
                frame = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (0, 0, cell_size, cell_size))
                self.sprite = pygame.transform.scale(frame, (32, 32))
            else:
                self._create_fallback_sprite()
        except Exception as e:
            print(f"Failed to load JettPaq sprite: {e}")
            self._create_fallback_sprite()
    
    def _create_fallback_sprite(self) -> None:
        """Create fallback blue jetpack icon."""
        self.sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(self.sprite, (80, 120, 255), (4, 4, 24, 24), border_radius=4)
        pygame.draw.polygon(self.sprite, (100, 150, 255), [(8, 28), (16, 32), (24, 28)])
        pygame.draw.rect(self.sprite, (255, 255, 255), (4, 4, 24, 24), 2, border_radius=4)
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.glow_phase += dt * 3.0
        if self.glow_phase >= 2 * math.pi:
            self.glow_phase -= 2 * math.pi
    
    def render(self, surface: pygame.Surface, camera_offset) -> None:
        if self.collected and self.collection_timer >= self.collection_duration:
            return
        if self._marked_for_removal:
            return
            
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        screen_x = self.position[0] - cam_x
        screen_y = self.position[1] - cam_y
        
        # Draw sprite (no glow to avoid glitching)
        surface.blit(self.sprite, (screen_x, screen_y))
    
    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.position[0], self.position[1], 32, 32)
