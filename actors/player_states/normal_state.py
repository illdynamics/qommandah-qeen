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

    def handle_input(self) -> None:
        """Handle input in normal state."""
        input_manager = InputManager.get_instance()
        
        # Check for held keys (continuous movement)
        if input_manager.is_action_down("move_left"):
            self._move(Direction.LEFT)
        elif input_manager.is_action_down("move_right"):
            self._move(Direction.RIGHT)
        else:
            # No movement - apply friction
            self.player.velocity.x *= 0.85
        
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
        if self.jump_cooldown <= 0 and not self.is_jumping:
            self.player.velocity.y = -PLAYER_JUMP_FORCE
            self.is_jumping = True
            self.jump_cooldown = 0.2
            self._update_animation()
            return True
        return False

    def _attack(self) -> None:
        """Perform attack action."""
        if self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_cooldown = 0.5
            self._update_animation()

    def _apply_gravity(self, dt: float) -> None:
        """Apply gravity to player."""
        self.player.velocity.y += GRAVITY * dt

    def _apply_friction(self, dt: float) -> None:
        """Apply friction to horizontal movement."""
        if abs(self.player.velocity.x) > 0:
            self.player.velocity.x *= 0.9
            if abs(self.player.velocity.x) < 0.1:
                self.player.velocity.x = 0

    def _clamp_velocity(self) -> None:
        """Clamp velocity to terminal velocity."""
        if self.player.velocity.y > PLAYER_TERMINAL_VELOCITY:
            self.player.velocity.y = PLAYER_TERMINAL_VELOCITY

    def _check_ground_collision(self) -> None:
        """Check if player is on ground."""
        if self.player.position.y >= self.player.ground_level:
            self.player.position.y = self.player.ground_level
            self.player.velocity.y = 0
            self.is_jumping = False
            self._update_animation()

    def _update_animation(self) -> None:
        """Update player animation based on state."""
        if self.is_attacking:
            animation_name = 'attack'
        elif self.is_jumping:
            animation_name = 'jump'
        elif abs(self.player.velocity.x) > 0.1:
            animation_name = 'run'
        else:
            animation_name = 'idle'
        
        if hasattr(self.player, 'current_animation') and self.player.current_animation != animation_name:
            self.player.current_animation = animation_name
            if hasattr(self.player, 'animation_timer'):
                self.player.animation_timer = 0.0
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the normal state player."""
        self.player.render_current_animation(surface, camera_offset)

    def get_state_name(self) -> str:
        """Get state name.
        
        Returns:
            String identifier for this state
        """
        return "NormalState"