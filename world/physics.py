"""
Integer-only physics system for game entities.
Implements physics bodies, gravity, and friction calculations.
"""

from typing import Tuple, Optional
from shared.types import Vector2


class PhysicsBody:
    """
    Integer-only physics body for game entities.
    All position and velocity values are stored as integers.
    """
    
    def __init__(self, position: Vector2, size: Vector2):
        """
        Initialize a new physics body.
        
        Args:
            position: Initial position (will be converted to integers)
            size: Body size (will be converted to integers)
        """
        self.position = Vector2(int(position.x), int(position.y))
        self.size = Vector2(int(size.x), int(size.y))
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.grounded = False
        self.mass = 1
        self.friction_coefficient = 0.8
        
    def update(self, delta_time: float) -> None:
        """
        Update physics body position based on velocity and acceleration.
        
        Args:
            delta_time: Time since last update in seconds
        """
        # Apply acceleration to velocity
        self.velocity.x += int(self.acceleration.x * delta_time)
        self.velocity.y += int(self.acceleration.y * delta_time)
        
        # Update position
        self.position.x += int(self.velocity.x * delta_time)
        self.position.y += int(self.velocity.y * delta_time)
        
        # Reset acceleration for next frame
        self.acceleration.x = 0
        self.acceleration.y = 0
        
    def apply_force(self, force: Vector2) -> None:
        """
        Apply a force to the physics body (F = ma).
        
        Args:
            force: Force vector to apply
        """
        self.acceleration.x += int(force.x / self.mass)
        self.acceleration.y += int(force.y / self.mass)
        
    def set_velocity(self, velocity: Vector2) -> None:
        """
        Set the body's velocity directly.
        
        Args:
            velocity: New velocity vector
        """
        self.velocity = Vector2(int(velocity.x), int(velocity.y))
        
    def get_bounds(self) -> Tuple[int, int, int, int]:
        """
        Get the body's bounding box as integers.
        
        Returns:
            Tuple of (x, y, width, height) as integers
        """
        return (int(self.position.x), int(self.position.y), 
                int(self.size.x), int(self.size.y))


def apply_gravity(body: PhysicsBody, gravity_strength: int = 980) -> None:
    """
    Apply gravity force to a physics body.
    
    Args:
        body: Physics body to apply gravity to
        gravity_strength: Strength of gravity in pixels/second² (default: 980)
    """
    if not body.grounded:
        body.acceleration.y += gravity_strength


def apply_friction(body: PhysicsBody, friction_coefficient: Optional[float] = None) -> None:
    """
    Apply friction to a physics body's horizontal movement.
    
    Args:
        body: Physics body to apply friction to
        friction_coefficient: Friction coefficient (0.0-1.0). 
                              Uses body's coefficient if None.
    """
    if friction_coefficient is None:
        friction_coefficient = body.friction_coefficient
        
    # Clamp friction coefficient
    friction_coefficient = max(0.0, min(1.0, friction_coefficient))
    
    # Apply friction to horizontal velocity
    if body.grounded:
        body.velocity.x = int(body.velocity.x * (1.0 - friction_coefficient))
        
        # Snap to zero if velocity is very small
        if abs(body.velocity.x) < 10:
            body.velocity.x = 0


def check_collision(body_a: PhysicsBody, body_b: PhysicsBody) -> bool:
    """
    Check for collision between two physics bodies using integer math.
    
    Args:
        body_a: First physics body
        body_b: Second physics body
        
    Returns:
        True if bodies are colliding, False otherwise
    """
    a_x, a_y, a_w, a_h = body_a.get_bounds()
    b_x, b_y, b_w, b_h = body_b.get_bounds()
    
    return (a_x < b_x + b_w and
            a_x + a_w > b_x and
            a_y < b_y + b_h and
            a_y + a_h > b_y)


def resolve_collision(body_a: PhysicsBody, body_b: PhysicsBody) -> None:
    """
    Resolve collision between two physics bodies.
    Simple resolution that pushes body_a out of body_b.
    
    Args:
        body_a: Body to resolve collision for
        body_b: Other body in collision
    """
    a_x, a_y, a_w, a_h = body_a.get_bounds()
    b_x, b_y, b_w, b_h = body_b.get_bounds()
    
    # Calculate overlap on each axis
    overlap_x = min(a_x + a_w, b_x + b_w) - max(a_x, b_x)
    overlap_y = min(a_y + a_h, b_y + b_h) - max(a_y, b_y)
    
    # Resolve along the axis of least penetration
    if overlap_x < overlap_y:
        # Resolve on X axis
        if a_x < b_x:
            body_a.position.x = b_x - a_w
        else:
            body_a.position.x = b_x + b_w
            
        # Reverse X velocity
        body_a.velocity.x = -int(body_a.velocity.x * 0.5)
        
    else:
        # Resolve on Y axis
        if a_y < b_y:
            body_a.position.y = b_y - a_h
            body_a.grounded = True
        else:
            body_a.position.y = b_y + b_h
            
        # Reverse Y velocity
        body_a.velocity.y = -int(body_a.velocity.y * 0.5)
        if body_a.velocity.y > 0:
            body_a.grounded = True


def clamp_velocity(body: PhysicsBody, max_speed: int) -> None:
    """
    Clamp a body's velocity to a maximum speed.
    
    Args:
        body: Physics body to clamp
        max_speed: Maximum speed in pixels/second
    """
    # Calculate current speed
    speed_squared = body.velocity.x * body.velocity.x + body.velocity.y * body.velocity.y
    max_speed_squared = max_speed * max_speed
    
    if speed_squared > max_speed_squared:
        # Normalize and scale to max speed
        import math
        speed = math.sqrt(speed_squared)
        scale = max_speed / speed
        
        body.velocity.x = int(body.velocity.x * scale)
        body.velocity.y = int(body.velocity.y * scale)

class PhysicsSystem:
    def __init__(self, gravity_strength: int = 980):
        self.bodies: list[PhysicsBody] = []
        self.gravity_strength = gravity_strength

    def add_body(self, body: PhysicsBody):
        self.bodies.append(body)

    def remove_body(self, body: PhysicsBody):
        if body in self.bodies:
            self.bodies.remove(body)

    def update(self, delta_time: float):
        for body in self.bodies:
            apply_gravity(body, self.gravity_strength)
            body.update(delta_time)