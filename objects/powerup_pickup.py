import pygame
import math
from typing import Tuple
from core.scene import Scene
from shared.types import PowerupType
from shared.constants import (
    POWERUP_DURATION,
    POWERUP_ANIMATION_SPEED,
    POWERUP_BOB_SPEED,
    POWERUP_BOB_HEIGHT,
    LAYER_POWERUPS
)
from objects.base_object import BaseObject


class PowerupPickup(BaseObject):
    """Base class for powerup pickups."""
    
    def __init__(self, scene: Scene, pos: Tuple[float, float], powerup_type: PowerupType) -> None:
        super().__init__(scene, pos)
        self.powerup_type = powerup_type
        
        self.bob_phase = 0.0
        self.bob_speed = POWERUP_BOB_SPEED
        self.bob_height = POWERUP_BOB_HEIGHT
        self.animation_timer = 0.0
        self.current_frame = 0
        
        self.collected = False
        self.collection_timer = 0.0
        self.collection_duration = 0.5
        self.original_position = pos
        
        self._initialize_sprite()
        self.z_index = LAYER_POWERUPS

    def _initialize_sprite(self) -> None:
        """Initialize the powerup pickup sprite."""
        colors = {
            PowerupType.JUMPUPSTIQ: (255, 100, 100),  # Red
            PowerupType.JETTPAQ: (100, 100, 255),    # Blue
        }
        color = colors.get(self.powerup_type, (200, 200, 200))
        
        self.sprite = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.rect(self.sprite, color, (2, 2, 20, 20), border_radius=4)
        pygame.draw.rect(self.sprite, (255, 255, 255), (2, 2, 20, 20), 2, border_radius=4)

    def update(self, dt: float) -> None:
        """Update powerup pickup state."""
        if self.collected:
            self._process_collection(dt)
            return
        self._update_bob_motion(dt)

    def _update_bob_motion(self, dt: float) -> None:
        """Update bobbing motion."""
        self.bob_phase += dt * self.bob_speed
        if self.bob_phase >= 2 * math.pi:
            self.bob_phase -= 2 * math.pi
        bob_offset = math.sin(self.bob_phase) * self.bob_height
        self.position = (self.original_position[0], self.original_position[1] + bob_offset)

    def _process_collection(self, dt: float) -> None:
        """Process post-collection effects."""
        self.collection_timer += dt
        if self.collection_timer >= self.collection_duration:
            self._active = False
            self._marked_for_removal = True

    def mark_for_removal(self) -> None:
        """Mark this powerup as collected."""
        self.collected = True
        self.collection_timer = 0.0

    def render(self, surface: pygame.Surface, camera_offset) -> None:
        """Render the powerup pickup."""
        if not self._active or self._marked_for_removal:
            return
        if self.collected and self.collection_timer >= self.collection_duration:
            return
        
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        elif hasattr(camera_offset, '__getitem__'):
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        else:
            cam_x, cam_y = 0, 0
            
        screen_x = self.position[0] - cam_x
        screen_y = self.position[1] - cam_y
        surface.blit(self.sprite, (screen_x, screen_y))

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.position[0], self.position[1], 24, 24)

    def is_active(self) -> bool:
        """Check if powerup is still active."""
        if self._marked_for_removal:
            return False
        if self.collected:
            return self.collection_timer < self.collection_duration
        return self._active
