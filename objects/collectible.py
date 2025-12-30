from typing import Optional, Tuple
import pygame
import math
from core.scene import Scene
from shared.types import CollectibleType, CollectibleData
from shared.constants import (
    COLLECTIBLE_CHIP,
    COLLECTIBLE_FLOPPY,
    COLLECTIBLE_MEDALLION,
    COLLECTIBLE_SCORE_VALUES,
    COLLECTIBLE_ANIMATION_SPEED,
    COLLECTIBLE_BOB_SPEED,
    COLLECTIBLE_BOB_HEIGHT,
    LAYER_COLLECTIBLES
)
from objects.base_object import BaseObject


class Collectible(BaseObject):
    """A collectible score item (chip, floppy, medallion, briq)."""
    
    def __init__(self, scene: Scene, pos: Tuple[float, float], collectible_type: CollectibleType) -> None:
        super().__init__(scene, pos)
        self.collectible_type = collectible_type
        self.collectible_data = self._fetch_collectible_data()
        self.bob_offset = 0.0
        self.bob_phase = 0.0
        self.collected = False
        self.collection_timer = 0.0
        self.z_index = LAYER_COLLECTIBLES
        self.original_position = pos
        
        self._initialize_sprite()
    
    def _fetch_collectible_data(self) -> CollectibleData:
        if self.collectible_type == CollectibleType.CHIP:
            return CollectibleData(
                value=COLLECTIBLE_SCORE_VALUES.get("chip", 100),
                color=(100, 200, 100),
                sprite_key="collectible_chip"
            )
        elif self.collectible_type == CollectibleType.FLOPPY:
            return CollectibleData(
                value=COLLECTIBLE_SCORE_VALUES.get("floppy", 500),
                color=(200, 100, 200),
                sprite_key="collectible_floppy"
            )
        elif self.collectible_type == CollectibleType.MEDALLION:
            return CollectibleData(
                value=COLLECTIBLE_SCORE_VALUES.get("medallion", 1000),
                color=(255, 215, 0),
                sprite_key="collectible_medallion"
            )
        elif self.collectible_type == CollectibleType.BRIQ:
            return CollectibleData(
                value=50,
                color=(200, 150, 100),
                sprite_key="collectible_briq"
            )
        else:
            return CollectibleData(
                value=10,
                color=(255, 255, 255),
                sprite_key="collectible_default"
            )
    
    def _initialize_sprite(self) -> None:
        # Create fallback sprite (colored circle)
        self.sprite = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.sprite, self.collectible_data.color, (12, 12), 10)
        pygame.draw.circle(self.sprite, (255, 255, 255), (12, 12), 10, 2)
        
        # Try to load actual sprite
        try:
            if hasattr(self.scene, 'resource_manager') and self.scene.resource_manager:
                loaded = self.scene.resource_manager.get_image(self.collectible_data.sprite_key)
                if loaded:
                    self.sprite = loaded
        except (AttributeError, KeyError, Exception):
            pass
        
        self.rect = self.sprite.get_rect()
        self.rect.x = int(self.position[0])
        self.rect.y = int(self.position[1])
    
    def update(self, dt: float) -> None:
        if self.collected:
            self._process_collection(dt)
        else:
            self._update_bob_motion(dt)
    
    def _update_bob_motion(self, dt: float) -> None:
        self.bob_phase += COLLECTIBLE_BOB_SPEED * dt
        if self.bob_phase >= 2 * math.pi:
            self.bob_phase -= 2 * math.pi
        self.bob_offset = math.sin(self.bob_phase) * COLLECTIBLE_BOB_HEIGHT
        
        self.rect.x = int(self.original_position[0])
        self.rect.y = int(self.original_position[1] + self.bob_offset)
        self.position = (self.original_position[0], self.original_position[1] + self.bob_offset)
    
    def _collect(self) -> None:
        if not self.collected:
            self.collected = True
            self.collection_timer = 0.5
    
    def _process_collection(self, dt: float) -> None:
        self.collection_timer -= dt
        if self.collection_timer <= 0:
            self.mark_for_removal()
    
    def render(self, surface: pygame.Surface, camera_offset) -> None:
        if self.collected:
            return
        
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        draw_x = self.rect.x - cam_x
        draw_y = self.rect.y - cam_y
        surface.blit(self.sprite, (draw_x, draw_y))
    
    def get_rect(self) -> pygame.Rect:
        return self.rect
    
    def get_collision_rect(self) -> pygame.Rect:
        return self.rect
    
    def collision_rect(self) -> pygame.Rect:
        return self.get_collision_rect()
    
    def get_value(self) -> int:
        return self.collectible_data.value
