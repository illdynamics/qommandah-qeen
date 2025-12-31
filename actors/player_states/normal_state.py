from typing import Optional, Tuple
from .base_state import BasePlayerState
from shared.constants import GRAVITY, PLAYER_JUMP_FORCE, PLAYER_MOVE_SPEED, PLAYER_TERMINAL_VELOCITY
from shared.types import Direction
from core.input import InputManager
from world.physics import apply_gravity, apply_friction, clamp_velocity
import pygame

class NormalState(BasePlayerState):
    """Player normal state with basic movement, idle, and attack capabilities."""
    def __init__(self, player: 'Player'):
        """Initialize normal state.
        
        Args:
            player: The player instance this state belongs to
        """
        super().__init__(player)
        self.is_jumping = False
        self.is_attacking = False
        self.attack_cooldown = 0.0
        self.jump_cooldown = 0.0

    def enter(self) -> None:
        """Initialize normal state."""
        super().enter()
        self.is_jumping = False
        self.is_attacking = False
        self.attack_cooldown = 0.0
        self.jump_cooldown = 0.0
        self._update_animation()

    def exit(self) -> None:
        """Clean up normal state."""
        pass

    def update(self, dt: float) -> None:
        """Update normal state logic.
        
        Args:
            dt: Delta time in seconds
        """
        super().update(dt)
        self._update_timers(dt)
        self._apply_gravity(dt)
        self._apply_friction(dt)
        self._clamp_velocity()
        self._check_ground_collision()
        self._update_animation()

    def _update_timers(self, dt: float) -> None:
        """Update cooldown timers."""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        # Reset attack animation after a short time
        if self.is_attacking and self.attack_cooldown < 0.3:
            self.is_attacking = False
            self._update_animation()

    def handle_input(self) -> None:
        """Handle input in normal state."""
        input_manager = InputManager.get_instance()
        
        # Check for held keys (continuous movement)
        if input_manager.is_action_down("move_left"):
            self._move(Direction.LEFT)
        elif input_manager.is_action_down("move_right"):
            self._move(Direction.RIGHT)
        else:
            # No movement - apply strong friction to stop quickly
            self.player.velocity.x *= 0.5
        
        if input_manager.is_action_pressed("jump"):
            self._jump()
        
        if input_manager.is_action_pressed("attack"):
            self._attack()

    def _move(self, direction: Direction) -> None:
        """Move player in specified direction.
        
        Args:
            direction: Direction to move
        """
        if direction == Direction.LEFT:
            self.player.velocity.x = -PLAYER_MOVE_SPEED
            self.player.facing_direction = Direction.LEFT
        elif direction == Direction.RIGHT:
            self.player.velocity.x = PLAYER_MOVE_SPEED
            self.player.facing_direction = Direction.RIGHT
        self._update_animation()

    def _jump(self) -> bool:
        """Make player jump.
        
        Returns:
            True if jump was successful
        """
        # Can jump if on ground and not already jumping
        on_ground = getattr(self.player, '_on_ground', True)
        can_jump = (self.jump_cooldown <= 0 and 
                    (not self.is_jumping or on_ground))
        
        if can_jump and on_ground:
            # Apply upward velocity (negative Y = up in pygame)
            self.player.velocity.y = PLAYER_JUMP_FORCE  # Use constant from shared/constants.py
            self.is_jumping = True
            self.player._on_ground = False
            self.jump_cooldown = 0.3
            self._update_animation()
            return True
        return False

    def _attack(self) -> None:
        """Perform attack action - shoot projectile."""
        if self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_cooldown = 0.5
            self._update_animation()
            # Create projectile
            self.player.create_projectile()

    def _apply_gravity(self, dt: float) -> None:
        """Apply gravity to player."""
        self.player.velocity.y += GRAVITY * dt

    def _apply_friction(self, dt: float) -> None:
        """Apply friction to horizontal movement."""
        if abs(self.player.velocity.x) > 0:
            self.player.velocity.x *= 0.7  # Reduced from 0.9 for quicker stops
            if abs(self.player.velocity.x) < 10:
                self.player.velocity.x = 0

    def _clamp_velocity(self) -> None:
        """Clamp velocity to terminal velocity."""
        if self.player.velocity.y > PLAYER_TERMINAL_VELOCITY:
            self.player.velocity.y = PLAYER_TERMINAL_VELOCITY

    def _check_ground_collision(self) -> None:
        """Check tile collisions in all directions."""
        from shared.constants import TILE_SIZE
        
        if not (self.player._collision and hasattr(self.player._collision, 'tilemap') and self.player._collision.tilemap):
            # Fallback to ground_level check
            if self.player.position.y >= self.player.ground_level - self.player.size.y:
                self.player.position.y = self.player.ground_level - self.player.size.y
                self.player.velocity.y = 0
                self.is_jumping = False
                self.player._on_ground = True
            return
        
        tilemap = self.player._collision.tilemap
        
        # Get player bounds in tile coordinates
        left_tile = int(self.player.position.x // TILE_SIZE)
        right_tile = int((self.player.position.x + self.player.size.x - 1) // TILE_SIZE)
        top_tile = int(self.player.position.y // TILE_SIZE)
        bottom_tile = int((self.player.position.y + self.player.size.y) // TILE_SIZE)
        
        # === CEILING COLLISION (when jumping UP) ===
        if self.player.velocity.y < 0:
            # Check tiles at head level
            head_y = int(self.player.position.y // TILE_SIZE)
            for tx in range(left_tile, right_tile + 1):
                if 0 <= tx < tilemap.width and 0 <= head_y < tilemap.height:
                    if tilemap.is_solid(tx, head_y):
                        # Hit ceiling - stop upward movement
                        self.player.position.y = (head_y + 1) * TILE_SIZE
                        self.player.velocity.y = 0
                        break
        
        # === GROUND COLLISION (when falling DOWN) ===
        if self.player.velocity.y >= 0:
            feet_y = int((self.player.position.y + self.player.size.y) // TILE_SIZE)
            for tx in range(left_tile, right_tile + 1):
                if 0 <= tx < tilemap.width and 0 <= feet_y < tilemap.height:
                    if tilemap.is_solid(tx, feet_y):
                        # Land on ground
                        self.player.position.y = feet_y * TILE_SIZE - self.player.size.y
                        self.player.velocity.y = 0
                        self.is_jumping = False
                        self.player._on_ground = True
                        self._update_animation()
                        return
        
        # === HORIZONTAL COLLISIONS ===
        # Only check true walls (vertical obstacles), not platforms
        # Use player center for cleaner collision
        center_y = int((self.player.position.y + self.player.size.y / 2) // TILE_SIZE)
        
        # Left collision - check one tile to the left
        if self.player.velocity.x < 0:
            left_x = int(self.player.position.x // TILE_SIZE)
            if 0 <= left_x < tilemap.width and 0 <= center_y < tilemap.height:
                if tilemap.is_solid(left_x, center_y):
                    self.player.position.x = (left_x + 1) * TILE_SIZE
                    self.player.velocity.x = 0
        
        # Right collision - check one tile to the right
        if self.player.velocity.x > 0:
            right_x = int((self.player.position.x + self.player.size.x) // TILE_SIZE)
            if 0 <= right_x < tilemap.width and 0 <= center_y < tilemap.height:
                if tilemap.is_solid(right_x, center_y):
                    self.player.position.x = right_x * TILE_SIZE - self.player.size.x
                    self.player.velocity.x = 0
        
        # Check if still on ground (for next frame)
        feet_y = int((self.player.position.y + self.player.size.y + 1) // TILE_SIZE)
        on_ground = False
        for tx in range(left_tile, right_tile + 1):
            if 0 <= tx < tilemap.width and 0 <= feet_y < tilemap.height:
                if tilemap.is_solid(tx, feet_y):
                    on_ground = True
                    break
        
        if not on_ground and self.player.velocity.y >= 0:
            self.player._on_ground = False

    def _update_animation(self) -> None:
        """Update player animation based on state."""
        if self.is_attacking:
            animation_name = 'shoot'  # Changed from 'attack' to match sprite data
        elif self.is_jumping:
            if self.player.velocity.y > 0:
                animation_name = 'fall'  # Falling down
            else:
                animation_name = 'jump'  # Going up
        elif abs(self.player.velocity.x) > 0.1:
            animation_name = 'run'
        else:
            animation_name = 'idle'
        
        if hasattr(self.player, 'current_animation') and self.player.current_animation != animation_name:
            self.player.current_animation = animation_name
            # Reset BOTH timer AND frame index when changing animations!
            self.player.animation_timer = 0.0
            self.player._animation_frame = 0
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the normal state player."""
        self.player.render_current_animation(surface, camera_offset)

    def get_state_name(self) -> str:
        """Get state name.
        
        Returns:
            String identifier for this state
        """
        return "NormalState"