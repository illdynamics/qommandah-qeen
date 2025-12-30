"""
Particle system for visual effects.
Handles particle emission, movement, and rendering.
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from core.time import Time
from shared.constants import COLORS, ParticleConstants


class Particle:
    """Individual particle with physics and rendering."""
    
    def __init__(
        self,
        position: Tuple[float, float],
        velocity: Tuple[float, float],
        color: Tuple[int, int, int],
        size: int,
        lifetime: float,
        fade_out: bool = True,
        gravity: float = 0.0
    ):
        self.position = list(position)
        self.velocity = list(velocity)
        self.color = color
        self.original_color = color
        self.size = size
        self.original_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.fade_out = fade_out
        self.gravity = gravity
        self.active = True
    
    def update(self) -> bool:
        """Update particle position and lifetime. Returns True if particle is still active."""
        if not self.active:
            return False
        
        self.lifetime -= Time.delta_time
        if self.lifetime <= 0:
            self.active = False
            return False
        
        # Apply gravity
        self.velocity[1] += self.gravity * Time.delta_time
        
        # Update position
        self.position[0] += self.velocity[0] * Time.delta_time
        self.position[1] += self.velocity[1] * Time.delta_time
        
        return True
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render particle to surface with camera offset."""
        if not self.active:
            return
        
        # Calculate alpha based on lifetime if fading
        alpha = 255
        if self.fade_out:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        # Calculate size based on lifetime
        current_size = int(self.size * (self.lifetime / self.max_lifetime))
        current_size = max(1, current_size)
        
        # Create color with alpha
        if alpha < 255:
            color = (*self.color, alpha)
            particle_surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (current_size, current_size), current_size)
        else:
            color = self.color
            particle_surf = pygame.Surface((current_size * 2, current_size * 2))
            particle_surf.set_colorkey((0, 0, 0))
            pygame.draw.circle(particle_surf, color, (current_size, current_size), current_size)
        
        # Calculate screen position
        screen_x = int(self.position[0] - camera_offset[0] - current_size)
        screen_y = int(self.position[1] - camera_offset[1] - current_size)
        
        # Draw particle
        surface.blit(particle_surf, (screen_x, screen_y))


class ParticleEmitter:
    """Emitter that creates and manages particles."""
    
    def __init__(self, position: Tuple[float, float], active: bool = True):
        self.position = list(position)
        self.particles: List[Particle] = []
        self.active = active
        self.emission_rate = 0.0
        self.emission_timer = 0.0
    
    def update(self):
        """Update all particles and emission timer."""
        # Update existing particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Handle emission
        if self.active and self.emission_rate > 0:
            self.emission_timer += Time.delta_time
            particles_to_emit = int(self.emission_timer * self.emission_rate)
            
            for _ in range(particles_to_emit):
                self.emit_particle()
            
            self.emission_timer -= particles_to_emit / self.emission_rate
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render all particles."""
        for particle in self.particles:
            particle.render(surface, camera_offset)
    
    def emit_particle(self):
        """Create a new particle. Override in subclasses."""
        pass
    
    def set_position(self, x: float, y: float):
        """Update emitter position."""
        self.position = [x, y]
    
    def set_active(self, active: bool):
        """Activate or deactivate emission."""
        self.active = active
    
    def clear_particles(self):
        """Remove all particles."""
        self.particles.clear()


class SmokeEmitter(ParticleEmitter):
    """Emitter for smoke/dust particles."""
    
    def __init__(self, position: Tuple[float, float], active: bool = True):
        super().__init__(position, active)
        self.emission_rate = ParticleConstants.SMOKE_EMISSION_RATE
    
    def emit_particle(self):
        """Create a smoke particle."""
        # Random velocity
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(ParticleConstants.SMOKE_MIN_SPEED, ParticleConstants.SMOKE_MAX_SPEED)
        velocity = [
            math.cos(angle) * speed,
            math.sin(angle) * speed - ParticleConstants.SMOKE_RISE_SPEED
        ]
        
        # Random color variation
        base_color = ParticleConstants.SMOKE_COLOR
        color_variation = random.randint(-20, 20)
        color = (
            max(0, min(255, base_color[0] + color_variation)),
            max(0, min(255, base_color[1] + color_variation)),
            max(0, min(255, base_color[2] + color_variation))
        )
        
        # Random size and lifetime
        size = random.randint(
            ParticleConstants.SMOKE_MIN_SIZE,
            ParticleConstants.SMOKE_MAX_SIZE
        )
        lifetime = random.uniform(
            ParticleConstants.SMOKE_MIN_LIFETIME,
            ParticleConstants.SMOKE_MAX_LIFETIME
        )
        
        particle = Particle(
            position=self.position.copy(),
            velocity=velocity,
            color=color,
            size=size,
            lifetime=lifetime,
            fade_out=True,
            gravity=ParticleConstants.SMOKE_GRAVITY
        )
        
        self.particles.append(particle)


class ExplosionEmitter(ParticleEmitter):
    """Emitter for explosion effects."""
    
    def __init__(self, position: Tuple[float, float]):
        super().__init__(position, active=False)  # One-time explosion
        self.create_explosion()
    
    def create_explosion(self):
        """Create all explosion particles at once."""
        particle_count = ParticleConstants.EXPLOSION_PARTICLE_COUNT
        
        for _ in range(particle_count):
            # Random angle and speed
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(
                ParticleConstants.EXPLOSION_MIN_SPEED,
                ParticleConstants.EXPLOSION_MAX_SPEED
            )
            
            velocity = [
                math.cos(angle) * speed,
                math.sin(angle) * speed
            ]
            
            # Random color from explosion palette
            color_idx = random.randint(0, len(ParticleConstants.EXPLOSION_COLORS) - 1)
            color = ParticleConstants.EXPLOSION_COLORS[color_idx]
            
            # Random size and lifetime
            size = random.randint(
                ParticleConstants.EXPLOSION_MIN_SIZE,
                ParticleConstants.EXPLOSION_MAX_SIZE
            )
            lifetime = random.uniform(
                ParticleConstants.EXPLOSION_MIN_LIFETIME,
                ParticleConstants.EXPLOSION_MAX_LIFETIME
            )
            
            particle = Particle(
                position=self.position.copy(),
                velocity=velocity,
                color=color,
                size=size,
                lifetime=lifetime,
                fade_out=True,
                gravity=ParticleConstants.EXPLOSION_GRAVITY
            )
            
            self.particles.append(particle)


class ParticleSystem:
    """Main particle system that manages all emitters."""
    
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
    
    def update(self):
        """Update all emitters and remove inactive ones."""
        active_emitters = []
        
        for emitter in self.emitters:
            emitter.update()
            
            # Keep emitter if it has particles or is still active
            if emitter.particles or emitter.active:
                active_emitters.append(emitter)
        
        self.emitters = active_emitters
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        """Render all emitters."""
        for emitter in self.emitters:
            emitter.render(surface, camera_offset)
    
    def create_smoke_emitter(self, position: Tuple[float, float]) -> SmokeEmitter:
        """Create and return a smoke emitter."""
        emitter = SmokeEmitter(position)
        self.emitters.append(emitter)
        return emitter
    
    def create_explosion(self, position: Tuple[float, float]) -> ExplosionEmitter:
        """Create and return an explosion emitter."""
        emitter = ExplosionEmitter(position)
        self.emitters.append(emitter)
        return emitter
    
    def clear_all(self):
        """Remove all emitters and particles."""
        self.emitters.clear()