import pygame
from typing import Optional, Tuple, List
from shared.types import Vector2
from shared.constants import (
    PROJECTILE_SPEED,
    PROJECTILE_DAMAGE,
    PROJECTILE_LIFETIME,
    PROJECTILE_SIZE,
    PROJECTILE_COLOR,
    LAYER_PROJECTILES
)
from world.entities import Entity
from world.collision import CollisionSystem, CollisionResult
from core.particles import ParticleSystem, ExplosionEmitter

class Projectile(Entity):
    """
    Projectile class handling movement, collision, and damage logic.
    """
    def __init__(
        self,
        position: Vector2,
        direction: Vector2,
        owner: Optional[Entity] = None,
        damage: int = PROJECTILE_DAMAGE,
        speed: float = PROJECTILE_SPEED,
        lifetime: float = PROJECTILE_LIFETIME,
        size: int = PROJECTILE_SIZE,
        color: Tuple[int, int, int] = PROJECTILE_COLOR
    ) -> None:
        """
        Initialize a projectile.

        Args:
            position: Starting position (center)
            direction: Normalized direction vector
            owner: Entity that fired this projectile (for collision filtering)
            damage: Damage dealt on hit
            speed: Movement speed in pixels per second
            lifetime: Time in seconds before projectile expires
            size: Diameter of projectile in pixels
            color: RGB color tuple
        """
        super().__init__(position, (size, size))
        self.direction = direction
        self.owner = owner
        self.damage = damage
        self.speed = speed
        self.lifetime = lifetime
        self.remaining_lifetime = lifetime
        self.size = size
        self.color = color
        self.velocity = Vector2(direction.x * speed, direction.y * speed)
        self.particle_system: Optional[ParticleSystem] = None
        self.trail_emitter: Optional[ExplosionEmitter] = None
        self.hit_entities: List[Entity] = []
        self.penetrating = False
        self.active = True
        self.z_index = LAYER_PROJECTILES

    def update(self, dt: float) -> None:
        """
        Update projectile position and check lifetime.

        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return

        self.remaining_lifetime -= dt
        if self.remaining_lifetime <= 0:
            self.destroy()
            return

        # Update position based on velocity
        new_x = self.position.x + self.velocity.x * dt
        new_y = self.position.y + self.velocity.y * dt
        self.set_position(new_x, new_y)

        # Update trail particles
        self._update_trail_particles()

    def _update_trail_particles(self) -> None:
        """Update trail particle effects."""
        if self.trail_emitter and self.particle_system:
            self.trail_emitter.set_position(self.position.x, self.position.y)
            self.trail_emitter.update()

    def set_particle_system(self, particle_system: ParticleSystem) -> None:
        """
        Set particle system for visual effects.

        Args:
            particle_system: Particle system instance
        """
        self.particle_system = particle_system
        self._create_trail_emitter()

    def _create_trail_emitter(self) -> None:
        """Create trail particle emitter."""
        if self.particle_system:
            self.trail_emitter = self.particle_system.create_smoke_emitter(
                (self.position.x, self.position.y)
            )
            if self.trail_emitter:
                self.trail_emitter.set_active(True)

    def check_collision(self, collision_system: CollisionSystem) -> List[CollisionResult]:
        """
        Check for collisions with world geometry.

        Args:
            collision_system: Collision system to check against

        Returns:
            List of collision results
        """
        if not self.active:
            return []
        
        rect = self.get_rect()
        return collision_system.check_tile_collision(rect)

    def check_entity_collision(self, entities: List[Entity]) -> Optional[Entity]:
        """
        Check for collisions with other entities.

        Args:
            entities: List of entities to check against

        Returns:
            First entity collided with, or None
        """
        if not self.active:
            return None
        
        projectile_rect = self.get_rect()
        for entity in entities:
            if entity == self.owner or entity in self.hit_entities:
                continue
                
            if entity.is_colliding_with(self):
                return entity
        
        return None

    def handle_collision(self, collision_results: List[CollisionResult]) -> None:
        """
        Handle collision with world geometry.

        Args:
            collision_results: List of collision results
        """
        if not collision_results:
            return
            
        self._create_impact_effect()
        self.destroy()

    def handle_entity_hit(self, entity: Entity) -> bool:
        """
        Handle hitting another entity.

        Args:
            entity: Entity that was hit

        Returns:
            True if projectile should continue, False if it should be destroyed
        """
        if not self.active:
            return False
            
        self.hit_entities.append(entity)
        self._create_impact_effect()
        
        if not self.penetrating:
            self.destroy()
            return False
            
        return True

    def _create_impact_effect(self) -> None:
        """Create visual impact effect."""
        if self.particle_system:
            explosion = self.particle_system.create_explosion(
                (self.position.x, self.position.y)
            )
            if explosion:
                explosion.create_explosion()

    def destroy(self) -> None:
        """Destroy the projectile."""
        self.active = False
        if self.trail_emitter:
            self.trail_emitter.set_active(False)
            self.trail_emitter.clear_particles()

    def render(self, surface: pygame.Surface, camera_offset: Vector2) -> None:
        """
        Render the projectile.

        Args:
            surface: Surface to render to
            camera_offset: Camera offset for screen positioning
        """
        if not self.active:
            return
            
        screen_x = self.position.x - camera_offset.x
        screen_y = self.position.y - camera_offset.y
        
        # Draw projectile as a circle
        pygame.draw.circle(
            surface,
            self.color,
            (int(screen_x), int(screen_y)),
            self.size // 2
        )
        
        # Draw trail particles if available
        if self.trail_emitter:
            self.trail_emitter.render(surface, (camera_offset.x, camera_offset.y))

    def is_active(self) -> bool:
        """
        Check if projectile is active.

        Returns:
            True if active, False otherwise
        """
        return self.active

    def get_velocity(self) -> Vector2:
        """
        Get current velocity vector.

        Returns:
            Velocity vector
        """
        return self.velocity

    def set_penetrating(self, penetrating: bool) -> None:
        """
        Set whether projectile penetrates through multiple targets.

        Args:
            penetrating: True for penetrating, False for single hit
        """
        self.penetrating = penetrating

    def get_remaining_lifetime(self) -> float:
        """
        Get remaining lifetime in seconds.

        Returns:
            Remaining lifetime
        """
        return self.remaining_lifetime

    def reset_hit_list(self) -> None:
        """Clear list of hit entities (for penetrating projectiles)."""
        self.hit_entities.clear()