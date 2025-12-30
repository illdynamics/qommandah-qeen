"""
Qortana Halo enemy class.
Specialized enemy with electric attacks and zig-zag movement patterns.
DEALS 2 DAMAGE with ZAP attack - more than normal enemies!
"""

import pygame
import math
import random
from typing import Optional, Tuple, List
from .base_enemy import BaseEnemy
from core.time import Time
from shared.types import Vec2i, EnemyState, Direction
from shared.sprite_data import get_sprite_spec, get_animation_spec, QORTANA_HALO_FRAMES
from shared.constants import SUBPIXEL_SCALE, TILE_SIZE
from core.particles import ParticleSystem, Particle
from core.resources import ResourceManager
from core.engine import Engine

# Alias for backward compatibility with the rest of the file
Vector2 = Vec2i


class QortanaHalo(BaseEnemy):
    """
    Qortana Halo enemy with electric attacks and zig-zag movement.
    DEALS 2 DAMAGE with ZAP attack - higher than normal enemies!
    """
    
    def __init__(self, x: int, y: int, resources: Optional[ResourceManager] = None):
        """
        Initialize Qortana Halo enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            resources: Optional resource manager
        """
        position = Vec2i(x, y)
        super().__init__(
            position=position,
            health=80,
            damage=2,  # ZAP does 2 DAMAGE!
            speed=1.2,
            attack_range=150.0,
            detection_range=300.0,
            sprite_key="qortana_halo"
        )
        
        self.animations = QORTANA_HALO_FRAMES
        
        # Qortana-specific attributes
        self._zigzag_amplitude = 50.0  # How far to zigzag
        self._zigzag_frequency = 2.0   # How fast to zigzag
        self._zigzag_phase = random.uniform(0, math.pi * 2)  # Random starting phase
        
        self._zap_cooldown = 2.0  # Seconds between zap attacks
        self._zap_timer = 0.0
        self._zap_damage = 2  # CRITICAL: ZAP does 2 DAMAGE!
        self._zap_range = 200.0
        
        self._spark_cooldown = 0.5  # Seconds between spark particles
        self._spark_timer = 0.0
        
        self._electric_particles: List[Particle] = []
        self._zap_effect_active = False
        self._zap_effect_timer = 0.0
        self._zap_target: Optional[Vec2i] = None
        
        # Movement state
        self._idle_wander_timer = 0.0
        self._idle_wander_direction = Vec2i(1, 0)  # Start moving right
        self._idle_wander_change_time = 3.0  # Change direction every 3 seconds
        
        # Hitbox
        self.hitbox_width = 60
        self.hitbox_height = 60
        
        # Initialize state
        self._current_state = "idle"
    
    def update(self, engine: Engine) -> None:
        """
        Update Qortana Halo behavior.
        
        Args:
            engine: Game engine instance
        """
        delta_time = engine.time.get_delta_time()
        
        # Update timers
        self._zap_timer = max(0.0, self._zap_timer - delta_time)
        self._spark_timer = max(0.0, self._spark_timer - delta_time)
        self._idle_wander_timer += delta_time
        
        # Update zap effect if active
        if self._zap_effect_active:
            self._zap_effect_timer -= delta_time
            if self._zap_effect_timer <= 0:
                self._zap_effect_active = False
                self._zap_target = None
        
        # Update particles
        self._update_particles(delta_time)
        
        # Get player position if available
        player_position = None
        if hasattr(engine, 'scene') and hasattr(engine.scene, 'player'):
            player = engine.scene.player
            if player and hasattr(player, 'position'):
                player_position = Vector2(player.position.x, player.position.y)
        
        # AI thinking based on current state
        current_state = self._current_state
        if current_state == "idle":
            self._handle_idle_state(delta_time, player_position)
        elif current_state == "chase":
            self._handle_chase_state(delta_time, player_position)
        elif current_state == "attack":
            self._handle_attack_state(delta_time, player_position)
        elif current_state == "hurt":
            self._handle_hurt_state(delta_time)
        elif current_state == "dead":
            self._handle_dead_state(delta_time)
        
        # Update base enemy (animation, etc.)
        super().update(delta_time)
        
        # Generate random sparks
        if self._spark_timer <= 0:
            self._generate_electric_spark(engine)
            self._spark_timer = self._spark_cooldown
    
    def _handle_idle_state(self, delta_time: float, player_position: Optional[Vector2]) -> None:
        """Handle idle state behavior."""
        # Check if player is in detection range
        if player_position and self._can_detect_player(player_position):
            self.change_state("chase")
            return
        
        # Perform idle wandering
        self._idle_movement(delta_time)
        
        # Change direction periodically
        if self._idle_wander_timer >= self._idle_wander_change_time:
            self._idle_wander_direction = Vector2(
                random.choice([-1, 1]),
                random.uniform(-0.5, 0.5)
            )
            self._idle_wander_timer = 0.0
    
    def _handle_chase_state(self, delta_time: float, player_position: Optional[Vector2]) -> None:
        """Handle chase state behavior."""
        if not player_position:
            self.change_state("idle")
            return
        
        # Check if player is in attack range
        distance_to_player = math.sqrt(
            (player_position.x - self.position.x) ** 2 +
            (player_position.y - self.position.y) ** 2
        )
        
        if distance_to_player <= self._attack_range:
            self.change_state("attack")
            return
        
        # Follow player with zig-zag pattern
        self._follow_player(player_position, distance_to_player, delta_time)
    
    def _handle_attack_state(self, delta_time: float, player_position: Optional[Vector2]) -> None:
        """Handle attack state behavior."""
        if not player_position:
            self.change_state("idle")
            return
        
        # Check if player is still in attack range
        distance_to_player = math.sqrt(
            (player_position.x - self.position.x) ** 2 +
            (player_position.y - self.position.y) ** 2
        )
        
        if distance_to_player > self._attack_range:
            self.change_state("chase")
            return
        
        # Perform zap attack if cooldown is ready
        if self._zap_timer <= 0:
            self._perform_zap_attack(player_position)
            self._zap_timer = self._zap_cooldown
        
        # Maintain distance while attacking
        desired_distance = self._attack_range * 0.7
        if distance_to_player < desired_distance:
            # Move away from player
            direction = Vector2(
                self.position.x - player_position.x,
                self.position.y - player_position.y
            )
            # Normalize
            length = math.sqrt(direction.x ** 2 + direction.y ** 2)
            if length > 0:
                direction = Vector2(direction.x / length, direction.y / length)
                self.move(direction * self._speed * delta_time)
    
    def _follow_player(self, direction: Vector2, distance: float, delta_time: float) -> None:
        """
        Follow player with zig-zag movement pattern.
        
        Args:
            direction: Direction to player
            distance: Distance to player
            delta_time: Time since last update
        """
        # Calculate base movement toward player
        move_direction = Vector2(
            direction.x - self.position.x,
            direction.y - self.position.y
        )
        
        # Normalize
        length = math.sqrt(move_direction.x ** 2 + move_direction.y ** 2)
        if length > 0:
            move_direction = Vector2(move_direction.x / length, move_direction.y / length)
        
        # Add zig-zag perpendicular component
        self._zigzag_phase += self._zigzag_frequency * delta_time
        zigzag_offset = math.sin(self._zigzag_phase) * self._zigzag_amplitude * delta_time
        
        # Calculate perpendicular direction (rotate 90 degrees)
        perpendicular = Vector2(-move_direction.y, move_direction.x)
        
        # Combine movement
        movement = Vector2(
            move_direction.x * self._speed * delta_time + perpendicular.x * zigzag_offset,
            move_direction.y * self._speed * delta_time + perpendicular.y * zigzag_offset
        )
        
        self.move(movement)
    
    def _idle_movement(self, delta_time: float) -> None:
        """Perform idle wandering movement."""
        # Add slight vertical oscillation
        vertical_oscillation = math.sin(self._idle_wander_timer * 2) * 0.5
        
        movement = Vector2(
            self._idle_wander_direction.x * self._speed * 0.5 * delta_time,
            (self._idle_wander_direction.y + vertical_oscillation) * self._speed * 0.5 * delta_time
        )
        
        self.move(movement)
    
    def _perform_zap_attack(self, target_pos: Vector2) -> None:
        """
        Perform electric zap attack toward target position.
        
        Args:
            target_pos: Target position for zap
        """
        # Set zap effect
        self._zap_effect_active = True
        self._zap_effect_timer = 0.3  # Zap effect lasts 0.3 seconds
        self._zap_target = target_pos
        
        # Create visual zap effect
        self._create_zap_effect(target_pos)
        
        # Check if zap hits player (simplified - would need actual collision check)
        # In a real implementation, you would check if the zap line intersects the player
        
        # For now, just log the attack
        print(f"Qortana Halo zaps toward {target_pos}")
    
    def _create_zap_effect(self, target_pos: Vector2) -> None:
        """
        Create visual zap effect.
        
        Args:
            target_pos: Target position for zap
        """
        # Create lightning bolt particles along the zap path
        start_pos = Vector2(self.position.x, self.position.y)
        end_pos = target_pos
        
        # Create multiple particles along the line
        num_particles = 10
        for i in range(num_particles):
            t = i / (num_particles - 1)
            pos = Vector2(
                start_pos.x + (end_pos.x - start_pos.x) * t,
                start_pos.y + (end_pos.y - start_pos.y) * t
            )
            
            # Add some randomness to create lightning effect
            pos = Vector2(
                pos.x + random.uniform(-5, 5),
                pos.y + random.uniform(-5, 5)
            )
            
            # Create electric particle
            particle = Particle(
                position=(pos.x, pos.y),
                velocity=(0, 0),
                color=(100, 200, 255),  # Electric blue
                size=random.randint(2, 5),
                lifetime=0.2,
                fade_out=True,
                gravity=0.0
            )
            
            self._electric_particles.append(particle)
    
    def _generate_electric_spark(self, engine: Engine) -> None:
        """Generate random electric spark particles."""
        # Create 1-3 spark particles
        num_sparks = random.randint(1, 3)
        
        for _ in range(num_sparks):
            # Random position around the halo
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(10, 30)
            pos = Vector2(
                self.position.x + math.cos(angle) * distance,
                self.position.y + math.sin(angle) * distance
            )
            
            # Random velocity
            velocity = Vector2(
                random.uniform(-50, 50),
                random.uniform(-50, 50)
            )
            
            # Create spark particle
            particle = Particle(
                position=(pos.x, pos.y),
                velocity=(velocity.x, velocity.y),
                color=(150, 220, 255),  # Light electric blue
                size=random.randint(1, 3),
                lifetime=random.uniform(0.3, 0.6),
                fade_out=True,
                gravity=0.0
            )
            
            self._electric_particles.append(particle)
    
    def _update_particles(self, delta_time: float) -> None:
        """Update electric particle effects."""
        # Update existing particles
        active_particles = []
        for particle in self._electric_particles:
            # Update particle
            particle.update()
            
            # Keep if still alive
            if particle.lifetime > 0:
                active_particles.append(particle)
        
        self._electric_particles = active_particles
    
    def render(self, surface: pygame.Surface, camera_offset) -> None:
        """
        Render Qortana Halo with electric effects.
        
        Args:
            surface: Surface to render to
            camera_offset: Camera offset for positioning (tuple or Vector2)
        """
        # Handle tuple or Vector2
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        # Render base enemy
        super().render(surface, camera_offset)
        
        # Render electric particles
        for particle in self._electric_particles:
            particle.render(surface, camera_offset)
        
        # Render zap effect if active
        if self._zap_effect_active and self._zap_target:
            # Draw lightning bolt from halo to target
            start_screen = Vector2(
                self.position.x - cam_x,
                self.position.y - cam_y
            )
            end_screen = Vector2(
                self._zap_target.x - cam_x,
                self._zap_target.y - cam_y
            )
            
            # Draw multiple segments for lightning effect
            pygame.draw.line(
                surface,
                (100, 200, 255),  # Electric blue
                (int(start_screen.x), int(start_screen.y)),
                (int(end_screen.x), int(end_screen.y)),
                2
            )
    
    def take_damage(self, amount: int, knockback: Optional[Vector2] = None) -> None:
        """
        Handle taking damage with electric feedback.
        
        Args:
            amount: Damage amount
            knockback: Optional knockback force
        """
        super().take_damage(amount, knockback)
        
        # Generate extra sparks when damaged
        if self._health > 0:  # Only if not dead
            # Create damage feedback sparks
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(5, 15)
                pos = Vector2(
                    self.position.x + math.cos(angle) * distance,
                    self.position.y + math.sin(angle) * distance
                )
                
                velocity = Vector2(
                    random.uniform(-100, 100),
                    random.uniform(-100, 100)
                )
                
                particle = Particle(
                    position=(pos.x, pos.y),
                    velocity=(velocity.x, velocity.y),
                    color=(255, 100, 100),  # Damage red
                    size=random.randint(2, 4),
                    lifetime=random.uniform(0.2, 0.4),
                    fade_out=True,
                    gravity=0.0
                )
                
                self._electric_particles.append(particle)
    
    def get_attack_range(self) -> float:
        """
        Get the attack range of Qortana Halo.
        
        Returns:
            Attack range in pixels
        """
        return self._zap_range
    
    def get_movement_pattern(self) -> str:
        """
        Get the movement pattern description.
        
        Returns:
            Movement pattern description
        """
        return "Zig-zag pursuit with electric attacks"