import pygame
import math
from typing import Tuple
from core.scene import Scene
from shared.types import PowerupType
from objects.powerup_pickup import PowerupPickup


class JumpUpstiqPickup(PowerupPickup):
    """JumpUpStiq powerup pickup - enables pogo jump."""
    
    def __init__(self, scene: Scene, pos: Tuple[float, float]) -> None:
        super().__init__(scene, pos, PowerupType.JUMPUPSTIQ)
        self.glow_phase = 0.0
        self._initialize_jumpupstiq_sprite()
    
    def _initialize_jumpupstiq_sprite(self) -> None:
        """Create the JumpUpstiq-specific sprite with red glow."""
        self.sprite = pygame.Surface((28, 28), pygame.SRCALPHA)
        # Red pogo stick icon
        pygame.draw.rect(self.sprite, (255, 80, 80), (10, 2, 8, 24), border_radius=2)
        pygame.draw.ellipse(self.sprite, (255, 120, 120), (6, 20, 16, 8))
        pygame.draw.rect(self.sprite, (255, 255, 255), (10, 2, 8, 24), 1, border_radius=2)
    
    def update(self, dt: float) -> None:
        super().update(dt)
        # Animate glow
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
        
        # Draw glow effect
        glow_intensity = int(50 + 30 * math.sin(self.glow_phase))
        glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 100, 100, glow_intensity), (20, 20), 18)
        surface.blit(glow_surf, (screen_x - 6, screen_y - 6))
        
        # Draw sprite
        surface.blit(self.sprite, (screen_x, screen_y))
