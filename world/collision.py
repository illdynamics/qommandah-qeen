"""
Collision detection and resolution system.
Implements AABB collision detection with slide resolution.
"""

import pygame
from typing import Tuple, Optional, List
from shared.types import Rect, Vector2
from world.tiles import TileType


class CollisionResult:
    """Result of a collision check."""
    
    def __init__(self):
        self.collided = False
        self.normal = Vector2(0, 0)
        self.depth = 0.0
        self.tile_type = TileType.EMPTY
        self.position = Vector2(0, 0)
    
    def __bool__(self):
        return self.collided


def check_aabb_collision(rect1: Rect, rect2: Rect) -> bool:
    """
    Check if two axis-aligned bounding boxes are colliding.
    
    Args:
        rect1: First rectangle
        rect2: Second rectangle
        
    Returns:
        True if rectangles are colliding
    """
    return (rect1.x < rect2.x + rect2.width and
            rect1.x + rect1.width > rect2.x and
            rect1.y < rect2.y + rect2.height and
            rect1.y + rect1.height > rect2.y)


def get_aabb_collision_details(rect1: Rect, rect2: Rect) -> Optional[CollisionResult]:
    """
    Get detailed collision information between two AABBs.
    
    Args:
        rect1: First rectangle
        rect2: Second rectangle
        
    Returns:
        CollisionResult with details, or None if no collision
    """
    if not check_aabb_collision(rect1, rect2):
        return None
    
    result = CollisionResult()
    result.collided = True
    
    # Calculate overlap on both axes
    dx = (rect1.x + rect1.width / 2) - (rect2.x + rect2.width / 2)
    dy = (rect1.y + rect1.height / 2) - (rect2.y + rect2.height / 2)
    
    # Calculate overlap on each axis
    overlap_x = (rect1.width / 2 + rect2.width / 2) - abs(dx)
    overlap_y = (rect1.height / 2 + rect2.height / 2) - abs(dy)
    
    # Collision normal is the axis with smallest penetration
    if overlap_x < overlap_y:
        result.depth = overlap_x
        result.normal = Vector2(1 if dx > 0 else -1, 0)
    else:
        result.depth = overlap_y
        result.normal = Vector2(0, 1 if dy > 0 else -1)
    
    return result


def resolve_tile_collision(
    entity_rect: Rect,
    tile_rect: Rect,
    velocity: Vector2
) -> Tuple[Vector2, Vector2]:
    """
    Resolve collision between an entity and a tile with slide response.
    
    Args:
        entity_rect: Entity's bounding rectangle
        tile_rect: Tile's bounding rectangle
        velocity: Entity's velocity
        
    Returns:
        Tuple of (new_position_offset, new_velocity)
    """
    if not check_aabb_collision(entity_rect, tile_rect):
        return Vector2(0, 0), velocity
    
    collision = get_aabb_collision_details(entity_rect, tile_rect)
    if not collision:
        return Vector2(0, 0), velocity
    
    # Calculate slide response
    if collision.normal.x != 0:
        # Horizontal collision
        velocity.x = 0
        offset_x = collision.normal.x * collision.depth
        return Vector2(offset_x, 0), velocity
    else:
        # Vertical collision
        velocity.y = 0
        offset_y = collision.normal.y * collision.depth
        return Vector2(0, offset_y), velocity


def check_point_in_rect(point: Vector2, rect: Rect) -> bool:
    """
    Check if a point is inside a rectangle.
    
    Args:
        point: Point to check
        rect: Rectangle to check against
        
    Returns:
        True if point is inside rectangle
    """
    return (rect.x <= point.x <= rect.x + rect.width and
            rect.y <= point.y <= rect.y + rect.height)


def get_swept_aabb_collision(
    moving_rect: Rect,
    velocity: Vector2,
    static_rect: Rect
) -> Optional[CollisionResult]:
    """
    Perform swept AABB collision detection for moving objects.
    
    Args:
        moving_rect: Moving object's rectangle
        velocity: Moving object's velocity
        static_rect: Static object's rectangle
        
    Returns:
        CollisionResult with time of impact, or None if no collision
    """
    # Expand static rect by moving rect's dimensions
    expanded_rect = Rect(
        static_rect.x - moving_rect.width / 2,
        static_rect.y - moving_rect.height / 2,
        static_rect.width + moving_rect.width,
        static_rect.height + moving_rect.height
    )
    
    # Calculate ray from moving rect center to expanded rect
    ray_origin = Vector2(
        moving_rect.x + moving_rect.width / 2,
        moving_rect.y + moving_rect.height / 2
    )
    
    ray_end = Vector2(
        ray_origin.x + velocity.x,
        ray_origin.y + velocity.y
    )
    
    # Perform ray-rectangle intersection
    t_near = Vector2(
        (expanded_rect.x - ray_origin.x) / velocity.x if velocity.x != 0 else float('inf'),
        (expanded_rect.y - ray_origin.y) / velocity.y if velocity.y != 0 else float('inf')
    )
    
    t_far = Vector2(
        ((expanded_rect.x + expanded_rect.width) - ray_origin.x) / velocity.x if velocity.x != 0 else float('inf'),
        ((expanded_rect.y + expanded_rect.height) - ray_origin.y) / velocity.y if velocity.y != 0 else float('inf')
    )
    
    # Swap if needed
    if t_near.x > t_far.x:
        t_near.x, t_far.x = t_far.x, t_near.x
    if t_near.y > t_far.y:
        t_near.y, t_far.y = t_far.y, t_near.y
    
    # Find earliest and latest collision times
    t_enter = max(t_near.x, t_near.y)
    t_exit = min(t_far.x, t_far.y)
    
    # No collision if:
    # 1. t_enter > t_exit (ray misses)
    # 2. t_exit < 0 (moving away)
    # 3. t_enter > 1 (collision happens beyond this frame)
    if t_enter > t_exit or t_exit < 0 or t_enter > 1:
        return None
    
    result = CollisionResult()
    result.collided = True
    
    # Determine collision normal
    if t_near.x > t_near.y:
        if velocity.x < 0:
            result.normal = Vector2(1, 0)
        else:
            result.normal = Vector2(-1, 0)
    else:
        if velocity.y < 0:
            result.normal = Vector2(0, 1)
        else:
            result.normal = Vector2(0, -1)
    
    result.depth = 1 - t_enter
    return result


class CollisionSystem:
    """Manages collision detection and resolution."""
    
    def __init__(self, tilemap):
        """
        Initialize collision system.
        
        Args:
            tilemap: Reference to the tilemap for tile collisions
        """
        self.tilemap = tilemap
        self.static_colliders = []
        self.dynamic_colliders = []
    
    def add_static_collider(self, rect: Rect, tile_type: TileType = TileType.SOLID):
        """
        Add a static collider to the system.
        
        Args:
            rect: Collider rectangle
            tile_type: Type of tile for collision response
        """
        self.static_colliders.append((rect, tile_type))
    
    def add_dynamic_collider(self, rect: Rect):
        """
        Add a dynamic collider to the system.
        
        Args:
            rect: Collider rectangle
        """
        self.dynamic_colliders.append(rect)
    
    def clear_dynamic_colliders(self):
        """Clear all dynamic colliders."""
        self.dynamic_colliders.clear()
    
    def check_tile_collision(self, rect: Rect) -> List[CollisionResult]:
        """
        Check collision with tiles at a given position.
        
        Args:
            rect: Rectangle to check
            
        Returns:
            List of collision results
        """
        results = []
        
        if not self.tilemap:
            return results
        
        # Get tiles that overlap with the rectangle
        start_x = max(0, int(rect.x // self.tilemap.tile_size))
        end_x = min(self.tilemap.width, int((rect.x + rect.width) // self.tilemap.tile_size) + 1)
        start_y = max(0, int(rect.y // self.tilemap.tile_size))
        end_y = min(self.tilemap.height, int((rect.y + rect.height) // self.tilemap.tile_size) + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tilemap.get_tile(x, y)
                
                # Only check solid tiles
                if tile_type == TileType.SOLID:
                    tile_rect = Rect(
                        x * self.tilemap.tile_size,
                        y * self.tilemap.tile_size,
                        self.tilemap.tile_size,
                        self.tilemap.tile_size
                    )
                    
                    collision = get_aabb_collision_details(rect, tile_rect)
                    if collision:
                        collision.tile_type = tile_type
                        collision.position = Vector2(x, y)
                        results.append(collision)
        
        return results
    
    def check_static_collision(self, rect: Rect) -> List[CollisionResult]:
        """
        Check collision with static colliders.
        
        Args:
            rect: Rectangle to check
            
        Returns:
            List of collision results
        """
        results = []
        
        for static_rect, tile_type in self.static_colliders:
            collision = get_aabb_collision_details(rect, static_rect)
            if collision:
                collision.tile_type = tile_type
                results.append(collision)
        
        return results
    
    def check_dynamic_collision(self, rect: Rect) -> List[CollisionResult]:
        """
        Check collision with dynamic colliders.
        
        Args:
            rect: Rectangle to check
            
        Returns:
            List of collision results
        """
        results = []
        
        for dynamic_rect in self.dynamic_colliders:
            collision = get_aabb_collision_details(rect, dynamic_rect)
            if collision:
                results.append(collision)
        
        return results
    
    def resolve_all_collisions(
        self,
        entity_rect: Rect,
        velocity: Vector2
    ) -> Tuple[Vector2, Vector2, List[CollisionResult]]:
        """
        Resolve all collisions for an entity.
        
        Args:
            entity_rect: Entity's rectangle
            velocity: Entity's velocity
            
        Returns:
            Tuple of (position_correction, new_velocity, collisions)
        """
        # Check tile collisions
        tile_collisions = self.check_tile_collision(entity_rect)
        
        # Check static collisions
        static_collisions = self.check_static_collision(entity_rect)
        
        # Combine all collisions
        all_collisions = tile_collisions + static_collisions
        
        if not all_collisions:
            return Vector2(0, 0), velocity, []
        
        # Sort collisions by depth (shallowest first for proper resolution)
        all_collisions.sort(key=lambda c: c.depth)
        
        position_correction = Vector2(0, 0)
        new_velocity = velocity.copy()
        
        # Resolve each collision
        for collision in all_collisions:
            # Create temporary rect for this collision resolution
            temp_rect = Rect(
                entity_rect.x + position_correction.x,
                entity_rect.y + position_correction.y,
                entity_rect.width,
                entity_rect.height
            )
            
            # Create tile rect for resolution
            if collision.tile_type == TileType.SOLID:
                tile_rect = Rect(
                    collision.position.x * self.tilemap.tile_size,
                    collision.position.y * self.tilemap.tile_size,
                    self.tilemap.tile_size,
                    self.tilemap.tile_size
                )
                
                offset, vel = resolve_tile_collision(temp_rect, tile_rect, new_velocity)
                position_correction += offset
                new_velocity = vel
        
        return position_correction, new_velocity, all_collisions
    
    def raycast(
        self,
        origin: Vector2,
        direction: Vector2,
        distance: float
    ) -> Optional[Tuple[Vector2, CollisionResult]]:
        """
        Cast a ray and return first collision.
        
        Args:
            origin: Ray origin
            direction: Ray direction (normalized)
            distance: Maximum ray distance
            
        Returns:
            Tuple of (hit_position, collision_result) or None
        """
        if direction.length() == 0:
            return None
        
        # Normalize direction
        dir_normalized = direction.normalize()
        
        # Step through the ray
        step_size = self.tilemap.tile_size / 4 if self.tilemap else 1
        current_pos = origin.copy()
        
        for _ in range(int(distance / step_size)):
            current_pos += dir_normalized * step_size
            
            # Check if we've hit a solid tile
            if self.tilemap:
                tile_x = int(current_pos.x // self.tilemap.tile_size)
                tile_y = int(current_pos.y // self.tilemap.tile_size)
                
                if (0 <= tile_x < self.tilemap.width and 
                    0 <= tile_y < self.tilemap.height):
                    
                    tile_type = self.tilemap.get_tile(tile_x, tile_y)
                    if tile_type == TileType.SOLID:
                        result = CollisionResult()
                        result.collided = True
                        result.position = Vector2(tile_x, tile_y)
                        result.tile_type = tile_type
                        return current_pos, result
            
            # Check static colliders
            test_rect = Rect(current_pos.x - 1, current_pos.y - 1, 2, 2)
            static_collisions = self.check_static_collision(test_rect)
            if static_collisions:
                return current_pos, static_collisions[0]
        
        return None