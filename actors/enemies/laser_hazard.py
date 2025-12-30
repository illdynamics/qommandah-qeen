import pygame
import math
from typing import Optional, Tuple
from core.time import Time
from shared.types import Rect
from shared.constants import (
    HAZARD_LASER_DAMAGE,
    HAZARD_LASER_COLOR,
    HAZARD_LASER_WIDTH,
    HAZARD_LASER_HEIGHT,
    HAZARD_LASER_CYCLE_TIME
)
from .base_enemy import BaseEnemy
class LaserHazard(BaseEnemy):
    """Laser hazard that cycles on/off with visual beam effect."""
    def __init__(
        self,
        position: Tuple[float, float],
        horizontal: bool = True,
        cycle_time: float = HAZARD_LASER_CYCLE_TIME
    ) -> None:
        """
        Initialize laser hazard.
        
        Args:
            position: Starting position (x, y)
            horizontal: True for horizontal laser, False for vertical
            cycle_time: Time for on/off cycle in seconds
        """
        super().__init__(position, health=1, damage=HAZARD_LASER_DAMAGE)
        self.horizontal = horizontal
        self.cycle_time = cycle_time
        self.cycle_timer = 0.0
        self.active = False
        self.beam_width = HAZARD_LASER_WIDTH if horizontal else HAZARD_LASER_HEIGHT
        self.beam_height = HAZARD_LASER_HEIGHT if horizontal else HAZARD_LASER_WIDTH
        self.color = HAZARD_LASER_COLOR
        self.pulse_intensity = 0.0
    def think(self, delta_time: float, player_position: Optional[Tuple[float, float]] = None) -> None:
        """
        Update laser cycle timing.
        
        Args:
            delta_time: Time since last frame
            player_position: Not used for hazards
        """
        self.cycle_timer += delta_time
        if self.cycle_timer >= self.cycle_time:
            self.cycle_timer = 0.0
            self.active = not self.active
        if self.active:
            self.pulse_intensity = (math.sin(self.cycle_timer * 10) + 1) / 2
        else:
            self.pulse_intensity = 0.0
    def update(self, delta_time: float) -> None:
        """
        Update hazard state.
        
        Args:
            delta_time: Time since last frame
        """
        self.think(delta_time)
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """
        Render laser hazard with beam effect.
        
        Args:
            surface: Surface to render to
            camera_offset: Camera offset for positioning
        """
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]
        if self.active:
            intensity = int(255 * self.pulse_intensity)
            pulse_color = (
                min(255, self.color[0] + intensity),
                min(255, self.color[1] + intensity),
                min(255, self.color[2] + intensity)
            )
            beam_rect = pygame.Rect(
                screen_x,
                screen_y,
                self.beam_width,
                self.beam_height
            )
            pygame.draw.rect(surface, pulse_color, beam_rect)
            glow_rect = pygame.Rect(
                screen_x - 2,
                screen_y - 2,
                self.beam_width + 4,
                self.beam_height + 4
            )
            pygame.draw.rect(surface, (255, 255, 255, 100), glow_rect, 2)
        else:
            inactive_rect = pygame.Rect(
                screen_x,
                screen_y,
                self.beam_width,
                self.beam_height
            )
            pygame.draw.rect(surface, (100, 100, 100, 100), inactive_rect)
    def check_collision(self, other_rect: Rect) -> bool:
        """
        Check if another rect collides with this laser.
        
        Args:
            other_rect: Rectangle to check collision with
            
        Returns:
            True if colliding and laser is active
        """
        if not self.active:
            return False
        laser_rect = Rect(
            self.position[0],
            self.position[1],
            self.position[0] + self.beam_width,
            self.position[1] + self.beam_height
        )
        return laser_rect.intersects(other_rect)
    def apply_damage(self) -> int:
        """
        Get damage value when laser hits.
        
        Returns:
            Damage amount
        """
        return self.damage