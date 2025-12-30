import pygame
import math
import random
from typing import Optional, Tuple
from core.time import Time
from shared.types import Rect
from shared.constants import (
    HAZARD_ACID_DAMAGE,
    HAZARD_ACID_COLOR,
    HAZARD_ACID_WIDTH,
    HAZARD_ACID_HEIGHT,
    HAZARD_ANIMATION_SPEED
)
from .base_enemy import BaseEnemy
class AcidHazard(BaseEnemy):
    """Acid hazard with bubbling animation and damage over time."""
    def __init__(
        self,
        position: Tuple[float, float]
    ) -> None:
        """
        Initialize acid hazard.
        
        Args:
            position: Starting position (x, y)
        """
        super().__init__(position, health=1, damage=HAZARD_ACID_DAMAGE)
        self.width = HAZARD_ACID_WIDTH
        self.height = HAZARD_ACID_HEIGHT
        self.color = HAZARD_ACID_COLOR
        self.bubbles = []
        self.bubble_timer = 0.0
        self._initialize_bubbles()
    def _initialize_bubbles(self) -> None:
        """Initialize bubble particles."""
        self.bubbles = []
        for _ in range(10):
            bubble = {
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'size': random.uniform(2, 6),
                'speed': random.uniform(0.5, 1.5),
                'phase': random.uniform(0, math.pi * 2)
            }
            self.bubbles.append(bubble)
    def think(self, delta_time: float, player_position: Optional[Tuple[float, float]] = None) -> None:
        """
        Update bubble animation.
        
        Args:
            delta_time: Time since last frame
            player_position: Not used for hazards
        """
        self.bubble_timer += delta_time * HAZARD_ANIMATION_SPEED
        for bubble in self.bubbles:
            bubble['y'] -= bubble['speed'] * delta_time
            bubble['x'] += math.sin(bubble['phase'] + self.bubble_timer) * 0.5
            if bubble['y'] < 0:
                bubble['y'] = self.height
                bubble['x'] = random.uniform(0, self.width)
    def update(self, delta_time: float) -> None:
        """
        Update hazard state.
        
        Args:
            delta_time: Time since last frame
        """
        self.think(delta_time)
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """
        Render acid hazard with bubbling effect.
        
        Args:
            surface: Surface to render to
            camera_offset: Camera offset for positioning
        """
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]
        acid_rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, self.color, acid_rect)
        for bubble in self.bubbles:
            bubble_x = screen_x + bubble['x']
            bubble_y = screen_y + bubble['y']
            bubble_size = bubble['size']
            bubble_color = (
                min(255, self.color[0] + 50),
                min(255, self.color[1] + 50),
                min(255, self.color[2] + 50)
            )
            pygame.draw.circle(surface, bubble_color, (int(bubble_x), int(bubble_y)), int(bubble_size))
    def check_collision(self, other_rect: Rect) -> bool:
        """
        Check if another rect collides with this acid.
        
        Args:
            other_rect: Rectangle to check collision with
            
        Returns:
            True if colliding
        """
        acid_rect = Rect(
            self.position[0],
            self.position[1],
            self.position[0] + self.width,
            self.position[1] + self.height
        )
        return acid_rect.intersects(other_rect)
    def apply_damage(self) -> int:
        """
        Apply acid damage over time.
        
        Returns:
            Damage amount (applies every second)
        """
        return self.damage