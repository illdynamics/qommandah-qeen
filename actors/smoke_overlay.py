"""
Q-shaped smoke ring animation overlay.
THE SIGNATURE VISUAL - plays continuously during idle/run states!
"""

import pygame
import math
from typing import Tuple, List, Optional
from core.time import Time
from shared.types import Vec2i
from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from shared.sprite_data import SMOQIN_FRAMES, SMOQIN_CONFIG

class SmokeOverlay:
    """Q-shaped smoke ring animation overlay."""
    
    def __init__(self, position: Tuple[float, float]):
        """
        Initialize smoke overlay.
        
        Args:
            position: Starting position (center of Q)
        """
        self.position = pygame.Vector2(position)
        self.duration = 2.0
        self.elapsed_time = 0.0
        self.active = True
        
        # Particle system for Q shape
        self.particles: List[dict] = []
        
        # Animation parameters
        self.max_radius = 50.0
        self.particle_count = 36  # Number of particles in Q shape
        self.particle_size = 4
        self.particle_color = (200, 200, 200)
        
        self._create_particles()
        
    def _create_particles(self) -> None:
        """Create initial particle positions for Q shape."""
        self.particles = []
        angle_step = (2 * math.pi) / self.particle_count
        
        for i in range(self.particle_count):
            # Calculate position on circle
            angle = i * angle_step
            radius = self.max_radius * 0.5  # Start at half radius
            
            # Create particle
            particle = {
                'angle': angle,
                'radius': radius,
                'target_radius': self.max_radius,
                'size': self.particle_size,
                'alpha': 180,
                'speed': 0.5 + (i % 3) * 0.2,  # Vary speed slightly
                'phase': i * 0.1  # Stagger animation
            }
            self.particles.append(particle)
            
    def update_position(self, new_position: Tuple[float, float]) -> None:
        """
        Update overlay position to follow target.
        
        Args:
            new_position: New center position
        """
        self.position = pygame.Vector2(new_position)
        
    def update(self) -> None:
        """Update smoke animation."""
        if not self.active:
            return
            
        dt = Time().get_delta_time()
        self.elapsed_time += dt
        
        # Update particle animations
        progress = self.elapsed_time / self.duration
        
        for particle in self.particles:
            # Expand radius
            if progress < 0.7:
                particle['radius'] = particle['radius'] + (particle['target_radius'] - particle['radius']) * 0.1
                
            # Fade out
            if progress > 0.5:
                fade_progress = (progress - 0.5) / 0.5
                particle['alpha'] = int(180 * (1.0 - fade_progress))
                
            # Add subtle movement
            particle['angle'] += particle['speed'] * dt * 0.5
            
        # Deactivate if animation complete
        if self.elapsed_time >= self.duration:
            self.active = False
            
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)) -> None:
        """
        Render smoke overlay.
        
        Args:
            surface: Target surface
            camera_offset: Camera offset for screen positioning
        """
        if not self.active:
            return
            
        # Calculate screen position
        screen_x = self.position.x - camera_offset[0]
        screen_y = self.position.y - camera_offset[1]
        
        # Draw each particle
        for particle in self.particles:
            # Calculate particle position
            angle = particle['angle']
            radius = particle['radius']
            
            pos_x = screen_x + math.cos(angle) * radius
            pos_y = screen_y + math.sin(angle) * radius
            
            # Draw tail of Q (last few particles)
            particle_index = self.particles.index(particle)
            if particle_index >= self.particle_count - 6:
                # Draw tail extending outward
                tail_length = 20
                tail_x = pos_x + math.cos(angle + math.pi/4) * tail_length
                tail_y = pos_y + math.sin(angle + math.pi/4) * tail_length
                
                # Draw line for tail
                color = (*self.particle_color, particle['alpha'])
                pygame.draw.line(surface, color, (pos_x, pos_y), (tail_x, tail_y), 2)
            
            # Draw particle
            color = (*self.particle_color, particle['alpha'])
            pygame.draw.circle(surface, color, (int(pos_x), int(pos_y)), particle['size'])
            
    def reset(self, position: Tuple[float, float]) -> None:
        """
        Reset smoke overlay to start new animation.
        
        Args:
            position: New position for smoke
        """
        self.position = pygame.Vector2(position)
        self.elapsed_time = 0.0
        self.active = True
        self._create_particles()
        
    def is_animation_complete(self) -> bool:
        """
        Check if smoke animation has completed.
        
        Returns:
            True if animation is complete
        """
        return self.elapsed_time >= self.duration or not self.active
        
    def get_remaining_time(self) -> float:
        """
        Get remaining animation time.
        
        Returns:
            Remaining time in seconds
        """
        return max(0.0, self.duration - self.elapsed_time)
        
    def set_duration(self, duration: float) -> None:
        """
        Set animation duration.
        
        Args:
            duration: New duration in seconds
        """
        self.duration = max(0.1, duration)
        
    def set_particle_count(self, count: int) -> None:
        """
        Set number of particles.
        
        Args:
            count: New particle count
        """
        self.particle_count = max(8, count)
        self._create_particles()
        
    def set_radius(self, radius: float) -> None:
        """
        Set Q shape radius.
        
        Args:
            radius: New radius in pixels
        """
        self.max_radius = max(10.0, radius)
        for particle in self.particles:
            particle['target_radius'] = self.max_radius
