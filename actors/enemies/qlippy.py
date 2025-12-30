"""
Qlippy enemy class.
The MOST ANNOYING enemy - spawns blocking dialogue popups!
Does NO DAMAGE but blocks player movement with "helpful" tips.
"""

import pygame
import random
from typing import Optional, List, Tuple
from .base_enemy import BaseEnemy
from shared.types import Vec2i, EnemyState, Direction
from shared.constants import (
    TILE_SIZE,
    SUBPIXEL_SCALE,
)
from shared.sprite_data import get_sprite_spec, get_animation_spec, QLIPPY_FRAMES
from core.resources import ResourceManager
from core.time import Time


# Qlippy's annoying dialogue options
QLIPPY_DIALOGUES = [
    "It looks like you're trying to jump! Would you like help?",
    "Did you know? Pressing LEFT moves you LEFT!",
    "TIP: Enemies can hurt you. Avoid them!",
    "I see you're playing a game. Need assistance?",
    "PROTIP: The floor is usually at the bottom!",
    "Would you like me to search the web for 'how to play platformers'?",
    "It seems you're alive! Keep it up!",
    "Remember: Gravity pulls DOWN. You're welcome!",
    "Need help? I'm ALWAYS here for you!",
    "Fun fact: This is a video game!",
]


class Qlippy(BaseEnemy):
    """
    Qlippy enemy - the digital assistant nobody asked for.
    
    Behavior:
    - Floats around looking for players to "help"
    - Spawns blocking dialogue popups when near player
    - Does NO DAMAGE - only annoys
    - Can be dismissed by shooting or waiting
    - Has 1 HP (very fragile ego)
    """
    
    def __init__(self, x: int, y: int, resources: Optional[ResourceManager] = None):
        """Initialize Qlippy at position."""
        super().__init__(
            position=Vec2i(x, y),
            health=1,
            damage=0,
            speed=0.6,
            attack_range=100,
            detection_range=150,
            sprite_key="qlippy"
        )
        
        self.animations = QLIPPY_FRAMES
        
        # Qlippy-specific properties
        self.detection_range = 150  # Range to detect player
        self.popup_cooldown = 5.0   # Seconds between popups
        self.popup_timer = 0.0
        self.popup_duration = 3.0   # How long popup stays
        self.popup_active = False
        self.current_dialogue = ""
        
        # Movement
        self.float_speed = 60       # Slow floating
        self.bob_amplitude = 8      # Floating bob amount
        self.bob_speed = 2.0
        self.bob_offset = 0.0
        
        # Target tracking
        self.target_player = None
        self.follow_distance = 80   # Stay this far from player
        
        # Hitbox (smaller than sprite)
        self.hitbox_width = 48
        self.hitbox_height = 60
        self.hitbox_offset_x = 26
        self.hitbox_offset_y = 30
        
        # State
        self.current_animation = "idle"
        self.animation_timer = 0.0
        self.dismissed = False
        self.dismiss_timer = 0.0
        
    def think(self, delta_time: float, player_pos: Optional[Vec2i] = None):
        """
        Qlippy AI think function.
        
        Args:
            delta_time: Time since last frame
            player_pos: Player's current position
        """
        if self.state == EnemyState.DEAD:
            return
            
        # Update timers
        self.popup_timer = max(0, self.popup_timer - delta_time)
        self.animation_timer += delta_time
        self.bob_offset += self.bob_speed * delta_time
        
        # Handle dismiss animation
        if self.dismissed:
            self.dismiss_timer += delta_time
            if self.dismiss_timer > 0.5:
                self.dismissed = False
                self.popup_active = False
            return
        
        if player_pos is None:
            self._idle_behavior(delta_time)
            return
            
        # Calculate distance to player
        dx = player_pos.x - self.physics_body.pos_x // SUBPIXEL_SCALE
        dy = player_pos.y - self.physics_body.pos_y // SUBPIXEL_SCALE
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance < self.detection_range:
            self._follow_behavior(delta_time, dx, dy, distance)
            
            # Try to spawn popup
            if not self.popup_active and self.popup_timer <= 0:
                self._spawn_popup()
        else:
            self._idle_behavior(delta_time)
            self.popup_active = False
            
    def _idle_behavior(self, delta_time: float):
        """Idle floating behavior."""
        self.state = EnemyState.IDLE
        self.current_animation = "idle"
        
        # Gentle floating motion
        import math
        self.physics_body.vel_y = int(math.sin(self.bob_offset) * self.bob_amplitude * SUBPIXEL_SCALE)
        
    def _follow_behavior(self, delta_time: float, dx: float, dy: float, distance: float):
        """Follow player behavior - creepily hovering nearby."""
        self.state = EnemyState.CHASE
        
        if self.popup_active:
            self.current_animation = "talk"
        else:
            self.current_animation = "popup" if distance < self.follow_distance else "idle"
        
        # Move toward player but maintain distance
        if distance > self.follow_distance + 20:
            # Move closer
            speed = self.float_speed * SUBPIXEL_SCALE
            if distance > 0:
                self.physics_body.vel_x = int((dx / distance) * speed)
                self.physics_body.vel_y = int((dy / distance) * speed)
        elif distance < self.follow_distance - 20:
            # Back away slightly
            speed = self.float_speed * SUBPIXEL_SCALE * 0.5
            if distance > 0:
                self.physics_body.vel_x = int(-(dx / distance) * speed)
                self.physics_body.vel_y = int(-(dy / distance) * speed)
        else:
            # Hover in place with bob
            import math
            self.physics_body.vel_x = 0
            self.physics_body.vel_y = int(math.sin(self.bob_offset) * self.bob_amplitude * SUBPIXEL_SCALE)
            
        # Face player
        self.facing = Direction.LEFT if dx < 0 else Direction.RIGHT
        
    def _spawn_popup(self):
        """Spawn an annoying dialogue popup."""
        self.popup_active = True
        self.popup_timer = self.popup_cooldown
        self.current_dialogue = random.choice(QLIPPY_DIALOGUES)
        self.current_animation = "popup"
        
    def dismiss_popup(self):
        """Dismiss the current popup (player action)."""
        if self.popup_active:
            self.dismissed = True
            self.dismiss_timer = 0.0
            self.current_animation = "dismiss"
            
    def get_popup_rect(self) -> Optional[pygame.Rect]:
        """
        Get the blocking popup rectangle if active.
        
        Returns:
            Rect of popup area or None
        """
        if not self.popup_active:
            return None
            
        # Popup appears above Qlippy
        popup_width = 200
        popup_height = 80
        x = self.physics_body.pos_x // SUBPIXEL_SCALE - popup_width // 2
        y = self.physics_body.pos_y // SUBPIXEL_SCALE - popup_height - 20
        
        return pygame.Rect(x, y, popup_width, popup_height)
        
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Render Qlippy and popup.
        
        Args:
            surface: Surface to render to
            camera_offset: Camera offset for scrolling
        """
        # First, render the sprite using base class method
        super().render(surface, camera_offset)
        
        # Then render popup overlay if active
        if self.popup_active and not self.dismissed:
            # Get screen position
            if hasattr(camera_offset, 'x'):
                cam_x, cam_y = camera_offset.x, camera_offset.y
            else:
                cam_x, cam_y = camera_offset[0], camera_offset[1]
                
            screen_x = self.position.x - cam_x
            screen_y = self.position.y - cam_y
            self._render_popup(surface, int(screen_x), int(screen_y))
            
    def _render_popup(self, surface: pygame.Surface, x: int, y: int):
        """Render the dialogue popup."""
        popup_width = 200
        popup_height = 80
        popup_x = x - popup_width // 2
        popup_y = y - popup_height - 40
        
        # Popup background
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        pygame.draw.rect(surface, (240, 240, 200), popup_rect)
        pygame.draw.rect(surface, (100, 100, 100), popup_rect, 2)
        
        # Speech tail
        tail_points = [
            (x - 10, popup_y + popup_height),
            (x + 10, popup_y + popup_height),
            (x, popup_y + popup_height + 15)
        ]
        pygame.draw.polygon(surface, (240, 240, 200), tail_points)
        pygame.draw.lines(surface, (100, 100, 100), False, 
                         [(x - 10, popup_y + popup_height), (x, popup_y + popup_height + 15), 
                          (x + 10, popup_y + popup_height)], 2)
        
        # Text (simplified - would use font in full implementation)
        # For now just draw a placeholder
        text_rect = pygame.Rect(popup_x + 10, popup_y + 10, popup_width - 20, popup_height - 20)
        pygame.draw.rect(surface, (200, 200, 180), text_rect)
        
    def take_damage(self, amount: int) -> bool:
        """
        Qlippy takes damage - very fragile!
        
        Args:
            amount: Damage amount
            
        Returns:
            True if Qlippy died
        """
        self.health -= amount
        if self.health <= 0:
            self.state = EnemyState.DEAD
            self.current_animation = "dismiss"  # Use dismiss as death anim
            return True
        return False
        
    def get_collision_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(
            self.physics_body.pos_x // SUBPIXEL_SCALE - self.hitbox_width // 2,
            self.physics_body.pos_y // SUBPIXEL_SCALE - self.hitbox_height // 2,
            self.hitbox_width,
            self.hitbox_height
        )
