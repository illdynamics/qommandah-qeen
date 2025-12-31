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
        """Load collectible sprite from sprite sheet."""
        import os
        from shared.constants import ASSETS_PATH
        
        display_size = 28  # Slightly larger display size
        
        try:
            sprite_path = os.path.join(ASSETS_PATH, "qq-items-collectibles.png")
            if os.path.exists(sprite_path):
                sheet = pygame.image.load(sprite_path).convert_alpha()
                
                # Sprite sheet is 512x128 = 8 columns x 2 rows of 64x64 cells
                cell_size = 64
                
                # Map collectible type to sprite position (col, row)
                sprite_positions = {
                    CollectibleType.CHIP: (0, 0),       # First item
                    CollectibleType.FLOPPY: (1, 0),    # Second item  
                    CollectibleType.MEDALLION: (2, 0), # Third item
                    CollectibleType.BRIQ: (3, 0),      # Fourth item
                }
                
                col, row = sprite_positions.get(self.collectible_type, (0, 0))
                
                # Extract sprite from sheet
                src_x = col * cell_size
                src_y = row * cell_size
                
                # Create surface and blit the cell
                frame = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), (src_x, src_y, cell_size, cell_size))
                
                # Scale to display size
                self.sprite = pygame.transform.scale(frame, (display_size, display_size))
                self.frames = [self.sprite]
                self.current_frame = 0
                self.frame_timer = 0.0
            else:
                raise Exception("Sprite sheet not found")
                
        except Exception as e:
            print(f"Failed to load collectible sprite: {e}")
            # Fallback to colored shapes
            self._create_fallback_sprite(display_size)
        
        self.rect = self.sprite.get_rect()
        self.rect.x = int(self.position[0])
        self.rect.y = int(self.position[1])
    
    def _create_fallback_sprite(self, size: int) -> None:
        """Create fallback colored sprite if loading fails."""
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if self.collectible_type == CollectibleType.CHIP:
            # Green chip
            pygame.draw.rect(self.sprite, (0, 200, 0), (2, 2, size-4, size-4))
            pygame.draw.rect(self.sprite, (0, 255, 0), (2, 2, size-4, size-4), 2)
        elif self.collectible_type == CollectibleType.FLOPPY:
            # Purple floppy
            pygame.draw.rect(self.sprite, (150, 0, 200), (2, 2, size-4, size-4))
            pygame.draw.rect(self.sprite, (200, 100, 255), (4, 3, size-8, 5))
        elif self.collectible_type == CollectibleType.MEDALLION:
            # Gold medallion
            pygame.draw.circle(self.sprite, (200, 150, 0), (size//2, size//2), size//2 - 2)
            pygame.draw.circle(self.sprite, (255, 200, 50), (size//2, size//2), size//2 - 2, 2)
        else:
            # Orange briq
            pygame.draw.rect(self.sprite, (200, 100, 0), (2, 3, size-4, size-5))
            pygame.draw.rect(self.sprite, (255, 150, 50), (2, 3, size-4, size-5), 2)
        
        self.frames = [self.sprite]
        self.current_frame = 0
        self.frame_timer = 0.0
        
        self.rect = self.sprite.get_rect()
        self.rect.x = int(self.position[0])
        self.rect.y = int(self.position[1])
    
    def update(self, dt: float) -> None:
        if self.collected:
            self._process_collection(dt)
        else:
            self._update_bob_motion(dt)
            self._update_animation(dt)
    
    def _update_animation(self, dt: float) -> None:
        """Animate collectible frames with a subtle shimmer."""
        if hasattr(self, 'frames') and len(self.frames) > 1:
            self.frame_timer += dt
            if self.frame_timer >= 0.4:  # Slower shimmer (~2.5 fps)
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.sprite = self.frames[self.current_frame]
    
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
