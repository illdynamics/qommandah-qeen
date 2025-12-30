import pygame
import math
import random
from typing import Optional, Tuple, List
from core.time import Time
from shared.types import Color, Rect
from shared.constants import (
    HAZARD_DAMAGE,
    HAZARD_SPIKE_DAMAGE,
    HAZARD_ACID_DAMAGE,
    HAZARD_LASER_DAMAGE,
    HAZARD_SPIKE_COLOR,
    HAZARD_ACID_COLOR,
    HAZARD_LASER_COLOR,
    HAZARD_SPIKE_WIDTH,
    HAZARD_SPIKE_HEIGHT,
    HAZARD_ACID_WIDTH,
    HAZARD_ACID_HEIGHT,
    HAZARD_LASER_WIDTH,
    HAZARD_LASER_HEIGHT,
    HAZARD_ANIMATION_SPEED,
    HAZARD_BLINK_INTERVAL,
    HAZARD_LASER_CYCLE_TIME
)
from world.entities import Entity
from world.collision import CollisionSystem

class Hazard(Entity):
    """Base class for all hazard objects."""
    def __init__(self, x: float, y: float, width: float, height: float, hazard_type: str):
        """
        Initialize a hazard.
        
        Args:
            x: X position
            y: Y position
            width: Width of hazard
            height: Height of hazard
            hazard_type: Type of hazard ('spike', 'acid', 'laser')
        """
        super().__init__((x, y), (width, height))
        self.hazard_type = hazard_type
        self.active = True
        self.blink_timer = 0.0
        self.animation_timer = 0.0
        self._damage_value = self._get_damage_value()
        self._color_value = self._get_color_value()
        
    def _get_damage_value(self) -> int:
        """Get damage value based on hazard type."""
        if self.hazard_type == 'spike':
            return HAZARD_SPIKE_DAMAGE
        elif self.hazard_type == 'acid':
            return HAZARD_ACID_DAMAGE
        elif self.hazard_type == 'laser':
            return HAZARD_LASER_DAMAGE
        else:
            return HAZARD_DAMAGE
            
    def _get_color_value(self) -> Color:
        """Get color based on hazard type."""
        if self.hazard_type == 'spike':
            return HAZARD_SPIKE_COLOR
        elif self.hazard_type == 'acid':
            return HAZARD_ACID_COLOR
        elif self.hazard_type == 'laser':
            return HAZARD_LASER_COLOR
        else:
            return (255, 0, 0)  # Default red
            
    def update(self, dt: float) -> None:
        """Update hazard state."""
        if not self.active:
            return
            
        self.blink_timer += dt
        self.animation_timer += dt * HAZARD_ANIMATION_SPEED
        
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the hazard."""
        if not self.active:
            return
            
        # Calculate screen position
        screen_x = self.position[0] - camera_offset[0]
        screen_y = self.position[1] - camera_offset[1]
        
        # Create drawing rectangle
        draw_rect = pygame.Rect(
            int(screen_x),
            int(screen_y),
            int(self.size[0]),
            int(self.size[1])
        )
        
        # Apply blinking effect
        if self.blink_timer % (HAZARD_BLINK_INTERVAL * 2) < HAZARD_BLINK_INTERVAL:
            # Render based on hazard type
            if self.hazard_type == 'spike':
                self._render_spike(surface, draw_rect)
            elif self.hazard_type == 'acid':
                self._render_acid(surface, draw_rect)
            elif self.hazard_type == 'laser':
                self._render_laser(surface, draw_rect)
            else:
                # Default rectangle rendering
                pygame.draw.rect(surface, self._color_value, draw_rect)
                
    def _render_spike(self, surface: pygame.Surface, draw_rect: pygame.Rect) -> None:
        """Render spike hazard with triangle points."""
        # Draw base rectangle
        pygame.draw.rect(surface, self._color_value, draw_rect)
        
        # Draw spike triangles on top
        spike_height = draw_rect.height // 3
        for i in range(3):
            x_offset = draw_rect.width * i // 3
            points = [
                (draw_rect.left + x_offset, draw_rect.bottom),
                (draw_rect.left + x_offset + draw_rect.width // 6, draw_rect.top),
                (draw_rect.left + x_offset + draw_rect.width // 3, draw_rect.bottom)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), points)
            
    def _render_acid(self, surface: pygame.Surface, draw_rect: pygame.Rect) -> None:
        """Render acid hazard with bubbling effect."""
        # Draw acid pool
        pygame.draw.rect(surface, self._color_value, draw_rect)
        
        # Draw bubbles based on animation timer
        bubble_count = 5
        for i in range(bubble_count):
            phase = (self.animation_timer + i * 0.5) % (2 * math.pi)
            bubble_size = 3 + int(2 * math.sin(phase))
            bubble_x = draw_rect.left + int(draw_rect.width * (0.2 + 0.6 * (i / bubble_count)))
            bubble_y = draw_rect.top + int(draw_rect.height * 0.5 + 5 * math.sin(phase))
            
            pygame.draw.circle(
                surface,
                (200, 255, 200),
                (bubble_x, bubble_y),
                bubble_size
            )
            
    def _render_laser(self, surface: pygame.Surface, draw_rect: pygame.Rect) -> None:
        """Render laser hazard with beam effect."""
        # Draw laser beam with pulsing effect
        pulse_intensity = 0.5 + 0.5 * math.sin(self.animation_timer * 5)
        pulse_color = (
            int(self._color_value[0] * pulse_intensity),
            int(self._color_value[1] * pulse_intensity),
            int(self._color_value[2] * pulse_intensity)
        )
        
        pygame.draw.rect(surface, pulse_color, draw_rect)
        
        # Draw laser ends
        end_size = min(draw_rect.width, draw_rect.height) // 3
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (draw_rect.left + end_size // 2, draw_rect.centery),
            end_size // 2
        )
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (draw_rect.right - end_size // 2, draw_rect.centery),
            end_size // 2
        )
        
    def check_collision(self, other_rect: Rect) -> bool:
        """Check if another rect collides with this hazard."""
        if not self.active:
            return False
            
        hazard_rect = pygame.Rect(
            int(self.position[0]),
            int(self.position[1]),
            int(self.size[0]),
            int(self.size[1])
        )
        
        other_pygame_rect = pygame.Rect(
            int(other_rect.position[0]),
            int(other_rect.position[1]),
            int(other_rect.size[0]),
            int(other_rect.size[1])
        )
        
        return hazard_rect.colliderect(other_pygame_rect)
        
    def apply_damage(self) -> int:
        """Apply damage to player/entity."""
        return self._damage_value
        
    def toggle_active(self, active: bool) -> None:
        """Toggle hazard active state."""
        self.active = active
        
    def reset(self) -> None:
        """Reset hazard to initial state."""
        self.active = True
        self.blink_timer = 0.0
        self.animation_timer = 0.0


class SpikeHazard(Hazard):
    """Spike hazard that damages on contact."""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, HAZARD_SPIKE_WIDTH, HAZARD_SPIKE_HEIGHT, 'spike')
        
    def update(self, dt: float) -> None:
        """Update spike hazard."""
        super().update(dt)


class AcidHazard(Hazard):
    """Acid hazard that damages over time."""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, HAZARD_ACID_WIDTH, HAZARD_ACID_HEIGHT, 'acid')
        self.damage_timer = 0.0
        
    def update(self, dt: float) -> None:
        """Update acid hazard."""
        super().update(dt)
        self.damage_timer += dt
        
    def apply_damage(self) -> int:
        """Apply acid damage with timing."""
        # Acid applies damage every second
        if self.damage_timer >= 1.0:
            self.damage_timer = 0.0
            return self._damage_value
        return 0


class LaserHazard(Hazard):
    """Laser hazard that cycles on/off."""
    def __init__(self, x: float, y: float, horizontal: bool = True):
        width = HAZARD_LASER_WIDTH if horizontal else HAZARD_LASER_HEIGHT
        height = HAZARD_LASER_HEIGHT if horizontal else HAZARD_LASER_WIDTH
        super().__init__(x, y, width, height, 'laser')
        self.horizontal = horizontal
        self.cycle_timer = 0.0
        self.firing = False
        self.warmup_timer = 0.0
        
    def update(self, dt: float) -> None:
        """Update laser hazard with cycling."""
        super().update(dt)
        
        self.cycle_timer += dt
        cycle_progress = (self.cycle_timer % HAZARD_LASER_CYCLE_TIME) / HAZARD_LASER_CYCLE_TIME
        
        # Laser is on for first half of cycle, off for second half
        was_firing = self.firing
        self.firing = cycle_progress < 0.5
        
        # Handle warmup when starting to fire
        if self.firing and not was_firing:
            self.warmup_timer = 0.0
        elif self.firing:
            self.warmup_timer += dt
            
    def check_collision(self, other_rect: Rect) -> bool:
        """Check collision only when laser is firing and warmed up."""
        if not self.active or not self.firing or self.warmup_timer < 0.5:
            return False
            
        return super().check_collision(other_rect)
        
    def _render_laser(self, surface: pygame.Surface, draw_rect: pygame.Rect) -> None:
        """Render laser hazard with beam effect and warmup indicator."""
        if not self.firing:
            # Draw inactive laser
            pygame.draw.rect(surface, (100, 100, 100), draw_rect)
            return
            
        # Draw warmup indicator
        if self.warmup_timer < 0.5:
            warmup_progress = self.warmup_timer / 0.5
            warmup_color = (
                int(100 + 155 * warmup_progress),
                int(100 + 155 * warmup_progress),
                100
            )
            pygame.draw.rect(surface, warmup_color, draw_rect)
        else:
            # Draw active laser beam
            pulse_intensity = 0.5 + 0.5 * math.sin(self.animation_timer * 10)
            pulse_color = (
                int(self._color_value[0] * pulse_intensity),
                int(self._color_value[1] * pulse_intensity),
                int(self._color_value[2] * pulse_intensity)
            )
            
            pygame.draw.rect(surface, pulse_color, draw_rect)
            
            # Draw laser ends
            end_size = min(draw_rect.width, draw_rect.height) // 3
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (draw_rect.left + end_size // 2, draw_rect.centery),
                end_size // 2
            )
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (draw_rect.right - end_size // 2, draw_rect.centery),
                end_size // 2
            )


class HazardSystem:
    """System for managing all hazards in a level."""
    def __init__(self):
        self.hazards: List[Hazard] = []
        
    def add_hazard(self, hazard: Hazard) -> None:
        """Add a hazard to the system."""
        self.hazards.append(hazard)
        
    def create_spike(self, x: float, y: float) -> SpikeHazard:
        """Create and add a spike hazard."""
        hazard = SpikeHazard(x, y)
        self.add_hazard(hazard)
        return hazard
        
    def create_acid(self, x: float, y: float) -> AcidHazard:
        """Create and add an acid hazard."""
        hazard = AcidHazard(x, y)
        self.add_hazard(hazard)
        return hazard
        
    def create_laser(self, x: float, y: float, horizontal: bool = True) -> LaserHazard:
        """Create and add a laser hazard."""
        hazard = LaserHazard(x, y, horizontal)
        self.add_hazard(hazard)
        return hazard
        
    def update(self, dt: float) -> None:
        """Update all hazards."""
        for hazard in self.hazards:
            hazard.update(dt)
            
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render all hazards."""
        for hazard in self.hazards:
            hazard.render(surface, camera_offset)
            
    def check_hazard_collisions(self, entity_rect: Rect) -> Optional[Hazard]:
        """Check if entity collides with any hazard."""
        for hazard in self.hazards:
            if hazard.check_collision(entity_rect):
                return hazard
        return None
        
    def clear_hazards(self) -> None:
        """Clear all hazards from the system."""
        self.hazards.clear()
        
    def reset_hazards(self) -> None:
        """Reset all hazards to initial state."""
        for hazard in self.hazards:
            hazard.reset()
            
    def get_hazard_count(self) -> int:
        """Get total number of hazards."""
        return len(self.hazards)
        
    def get_active_hazards(self) -> List[Hazard]:
        """Get list of active hazards."""
        return [hazard for hazard in self.hazards if hazard.active]