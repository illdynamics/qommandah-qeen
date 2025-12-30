"""
Player class with state management and powerup integration.
Handles movement modes: Normal, JumpUpStiQ (pogo), JettPaQ (jetpack).
Features continuous smoke Q overlay during idle/run states.
"""
import pygame
import os
from typing import Optional, Dict, Any, List, Tuple
from shared.types import Direction, PowerupType, PlayerState as PlayerStateType, Vec2i
from shared.sprite_data import get_sprite_spec, QOMMANDAH_QEEN_FRAMES, QOMMANDAH_QEEN_HITBOX
from shared.exceptions import InvalidStateError
from shared.constants import ASSETS_PATH, ASSET_FILES, SPRITE_CONFIGS
from actors.player_states.base_state import BasePlayerState
from actors.player_states.normal_state import NormalState
from actors.player_states.jumpupstiq_state import JumpUpStiqState
from actors.player_states.jettpaq_state import JettpaqState
from core.time import Time
from core.input import InputManager
from world.physics import PhysicsBody
from modes.registry import ModeRegistry
from core.particles import ParticleSystem
from actors.smoke_overlay import SmokeOverlay
from objects.collectible import Collectible


class Player:
    """Main player character class with state management and sprite rendering."""
    
    def __init__(self, x: float, y: float) -> None:
        """Initialize player at position (x, y)."""
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.size = pygame.Vector2(QOMMANDAH_QEEN_HITBOX["width"], QOMMANDAH_QEEN_HITBOX["height"])
        self.health = 3  # 3 HP as per spec
        self.max_health = 3
        self.score = 0
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.attack_cooldown = 0.0
        self._current_state: Optional[BasePlayerState] = None
        self._states: Dict[PlayerStateType, BasePlayerState] = {}
        self._active_powerups: Dict[PowerupType, float] = {}
        self._mode_registry: Optional[ModeRegistry] = None
        self._particle_system: Optional[ParticleSystem] = None
        self._animation_frame = 0
        self._animation_timer = 0.0
        self._facing_direction = Direction.RIGHT
        self.facing_direction = Direction.RIGHT
        self.current_animation = "idle"
        self.animation_timer = 0.0
        
        # Sprite rendering
        self._sprite_sheet = None
        self._sprite_frames: Dict[str, List[pygame.Surface]] = {}
        self._sprite_size = 128  # 128x128 cells
        self._render_scale = 0.5  # Scale down for display
        self._load_sprites()
        
        # Smoke overlay - THE SIGNATURE VISUAL!
        self._smoke_overlay = SmokeOverlay((x, y - 30))
        self._smoke_cycle_timer = 0.0
        
        # Hitbox offset from sprite_data
        self.hitbox_offset_x = QOMMANDAH_QEEN_HITBOX["offset_x"]
        self.hitbox_offset_y = QOMMANDAH_QEEN_HITBOX["offset_y"]
        
        # Fuel for jetpack
        self.fuel = 100.0
        self.max_fuel = 100.0
        self.ground_level = 500
        self._physics = None
        self._collision = None
        self._engine = None
        
        self._initialize_state_machine()
        self._initialize_timers()
        self._initialize_particles()

    def _load_sprites(self) -> None:
        """Load player sprite sheet and extract animation frames."""
        try:
            filename = ASSET_FILES.get("player", "qq-qommandah-qeen.png")
            sprite_path = os.path.join(ASSETS_PATH, filename)
            
            if os.path.exists(sprite_path):
                self._sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                config = SPRITE_CONFIGS.get(filename, (128, 128, 8, 4))
                cell_w, cell_h, cols, rows = config
                self._sprite_size = cell_w
                
                # Extract frames for each animation
                for anim_name, anim_spec in QOMMANDAH_QEEN_FRAMES.items():
                    frames = []
                    row = anim_spec.row
                    for i in range(anim_spec.frames):
                        col = anim_spec.start_col + i
                        if col < cols and row < rows:
                            x = col * cell_w
                            y = row * cell_h
                            frame = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                            frame.blit(self._sprite_sheet, (0, 0), (x, y, cell_w, cell_h))
                            frames.append(frame)
                    if frames:
                        self._sprite_frames[anim_name] = frames
                
                print(f"Loaded player sprites: {list(self._sprite_frames.keys())}")
            else:
                print(f"Player sprite not found: {sprite_path}")
        except Exception as e:
            print(f"Error loading player sprites: {e}")

    def set_engine_references(self, engine, physics_system, collision_system, mode_registry):
        self._engine = engine
        self._physics = physics_system
        self._collision = collision_system
        self._mode_registry = mode_registry
    
    @property
    def current_state(self) -> Optional[BasePlayerState]:
        return self._current_state
    
    def _initialize_state_machine(self) -> None:
        """Initialize the player state machine with all available states."""
        self._states[PlayerStateType.NORMAL] = NormalState(self)
        self._states[PlayerStateType.JUMPUPSTIQ] = JumpUpStiqState(self)
        self._states[PlayerStateType.JETTPAQ] = JettpaqState(self)
        self._current_state = self._states[PlayerStateType.NORMAL]
        self._current_state.enter()
    
    def _initialize_timers(self) -> None:
        """Initialize all player timers."""
        self._timers: Dict[str, float] = {
            "invincibility": 0.0,
            "attack_cooldown": 0.0,
            "powerup_jumpupstiq": 0.0,
            "powerup_jettpaq": 0.0
        }
    
    def _initialize_particles(self) -> None:
        """Initialize particle system for visual effects."""
        self._particles: List[Any] = []
    
    def set_mode_registry(self, mode_registry: ModeRegistry) -> None:
        """Set reference to mode registry for WoNQmodes."""
        self._mode_registry = mode_registry
    
    def change_state(self, new_state: PlayerStateType) -> None:
        """Change to a new player state."""
        if self._current_state:
            self._current_state.exit()
        
        self._current_state = self._states.get(new_state)
        if self._current_state:
            self._current_state.enter()
            self._trigger_state_change_effects()
        else:
            raise InvalidStateError(f"Invalid player state: {new_state}")
    
    def _trigger_state_change_effects(self) -> None:
        """Trigger visual and audio effects on state change."""
        pass
    
    def update(self, delta_time: float) -> None:
        """Update player logic."""
        # Handle input FIRST
        if self._current_state:
            self._current_state.handle_input()
            self._current_state.update(delta_time)
        
        self._update_timers(delta_time)
        self._update_powerups(delta_time)
        self._apply_physics(delta_time)
        self._check_boundaries()
        self._update_animation(delta_time)
        self._update_particles(delta_time)
    
    def _update_timers(self, delta_time: float) -> None:
        """Update all active timers."""
        for timer_name in list(self._timers.keys()):
            if self._timers[timer_name] > 0:
                self._timers[timer_name] -= delta_time
                if self._timers[timer_name] <= 0:
                    self._handle_timer_expiration(timer_name)
    
    def _handle_timer_expiration(self, timer_name: str) -> None:
        """Handle timer expiration with effects."""
        if timer_name == "invincibility":
            self.is_invincible = False
            self._create_invincibility_end_effect()
        elif timer_name == "attack_cooldown":
            self._create_attack_ready_effect()
    
    def _create_invincibility_end_effect(self) -> None:
        """Create visual effect when invincibility ends."""
        pass
    
    def _create_attack_ready_effect(self) -> None:
        """Create visual effect when attack cooldown ends."""
        pass
    
    def _update_powerups(self, delta_time: float) -> None:
        """Update active powerup durations."""
        expired_powerups = []
        for powerup_type, duration in self._active_powerups.items():
            self._active_powerups[powerup_type] = duration - delta_time
            if self._active_powerups[powerup_type] <= 0:
                expired_powerups.append(powerup_type)
        
        for powerup_type in expired_powerups:
            self._remove_powerup(powerup_type)
            self._create_powerup_expiration_effect(powerup_type)
    
    def _create_powerup_expiration_effect(self, powerup_type: PowerupType) -> None:
        """Create visual effect when powerup expires."""
        pass
    
    def _apply_physics(self, delta_time: float) -> None:
        """Apply physics to player movement."""
        if self._physics:
            pass
        self.position += self.velocity * delta_time
    
    def _check_boundaries(self) -> None:
        """Keep player within screen boundaries."""
        if self._engine:
            screen_width, screen_height = self._engine.get_screen_size()
            self.position.x = max(0, min(self.position.x, screen_width - self.size.x))
            self.position.y = max(0, min(self.position.y, screen_height - self.size.y))
    
    def _update_animation(self, delta_time: float) -> None:
        """Update player animation frame."""
        if self.current_animation in self._sprite_frames:
            frames = self._sprite_frames[self.current_animation]
            if frames:
                anim_spec = QOMMANDAH_QEEN_FRAMES.get(self.current_animation)
                fps = anim_spec.fps if anim_spec else 10
                frame_duration = 1.0 / fps
                
                self.animation_timer += delta_time
                if self.animation_timer >= frame_duration:
                    self.animation_timer -= frame_duration
                    self._animation_frame += 1
                    if self._animation_frame >= len(frames):
                        if anim_spec and anim_spec.loop:
                            self._animation_frame = 0
                        else:
                            self._animation_frame = len(frames) - 1
    
    def _update_particles(self, delta_time: float) -> None:
        """Update particle effects."""
        for particle in self._particles[:]:
            particle.update(delta_time)
            if not particle.is_active():
                self._particles.remove(particle)
    
    def handle_input(self) -> None:
        """Handle player input based on current state."""
        if self._current_state:
            self._current_state.handle_input()
    
    def move(self, direction: Direction) -> None:
        """Move player in specified direction."""
        if self._current_state:
            self._current_state._move(direction)
    
    def jump(self) -> bool:
        """Make player jump. Returns True if jump was successful."""
        if self._current_state:
            return self._current_state._jump()
        return False
    
    def dash(self) -> bool:
        """Make player dash. Returns True if dash was successful."""
        if isinstance(self._current_state, JettpaqState):
            return self._current_state._activate_dash()
        return False
    
    def shoot(self) -> bool:
        """Shoot projectile. Returns True if shot was fired."""
        if self._current_state:
            return self._current_state._attack()
        return False
    
    def _create_shoot_effect(self) -> None:
        """Create visual effect when shooting."""
        pass
    
    def take_damage(self, amount: int) -> None:
        """Apply damage to player."""
        if self.is_invincible:
            return
        
        self.health = max(0, self.health - amount)
        self.is_invincible = True
        self._timers["invincibility"] = 1.0
        self._create_damage_effect()
        
        if self.health <= 0:
            self.die()
    
    def _create_damage_effect(self) -> None:
        """Create visual effect when taking damage."""
        pass
    
    def die(self) -> None:
        """Handle player death."""
        self._create_death_effect()
        self.reset()
    
    def _create_death_effect(self) -> None:
        """Create visual effect when player dies."""
        pass
    
    def collect(self, collectible: Collectible) -> None:
        """Collect a collectible item."""
        self.score += collectible.value
        self._create_collection_effect(collectible)
    
    def _create_collection_effect(self, collectible: Collectible) -> None:
        """Create visual effect when collecting item."""
        pass
    
    def _apply_powerup(self, powerup_type: PowerupType) -> None:
        """Apply a powerup effect."""
        duration = 10.0
        self._active_powerups[powerup_type] = duration
        
        if powerup_type == PowerupType.JUMPUPSTIQ:
            self._apply_jumpupstiq()
        elif powerup_type == PowerupType.JETTPAQ:
            self._apply_jettpaq()
        
        self._create_powerup_activation_effect(powerup_type)
    
    def _create_powerup_activation_effect(self, powerup_type: PowerupType) -> None:
        """Create visual effect when activating powerup."""
        pass
    
    def _remove_powerup(self, powerup_type: PowerupType) -> None:
        """Remove a powerup effect."""
        if powerup_type in self._active_powerups:
            del self._active_powerups[powerup_type]
        
        if powerup_type == PowerupType.JUMPUPSTIQ:
            self.change_state(PlayerStateType.NORMAL)
        elif powerup_type == PowerupType.JETTPAQ:
            self.change_state(PlayerStateType.NORMAL)
    
    def _apply_jumpupstiq(self) -> None:
        """Apply jumpupstiq powerup."""
        self.change_state(PlayerStateType.JUMPUPSTIQ)
    
    def _apply_jettpaq(self) -> None:
        """Apply jettpaq powerup."""
        self.change_state(PlayerStateType.JETTPAQ)
    
    def get_rect(self) -> pygame.Rect:
        """Get player collision rectangle."""
        return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render player to surface."""
        if self._current_state:
            self._current_state.render(surface, camera_offset)
        
        # Render particles
        for particle in self._particles:
            particle.render(surface, camera_offset)
    
    def render_current_animation(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render the player's current animation frame."""
        # Handle both tuple and Vector2 camera_offset
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        # Calculate screen position
        screen_x = self.position.x - cam_x
        screen_y = self.position.y - cam_y
        
        # Get current animation frames
        if self.current_animation in self._sprite_frames:
            frames = self._sprite_frames[self.current_animation]
            if frames and self._animation_frame < len(frames):
                frame = frames[self._animation_frame]
                
                # Scale down the sprite for display (128 -> 64)
                scaled_size = int(self._sprite_size * self._render_scale)
                scaled_frame = pygame.transform.scale(frame, (scaled_size, scaled_size))
                
                # Flip if facing left
                if self.facing_direction == Direction.LEFT:
                    scaled_frame = pygame.transform.flip(scaled_frame, True, False)
                
                # Center the sprite on the hitbox
                sprite_x = screen_x - (scaled_size - self.size.x) // 2
                sprite_y = screen_y - (scaled_size - self.size.y) // 2
                
                # Apply invincibility flash effect
                if self.is_invincible:
                    flash = int(pygame.time.get_ticks() / 100) % 2
                    if flash:
                        scaled_frame.set_alpha(128)
                    else:
                        scaled_frame.set_alpha(255)
                
                surface.blit(scaled_frame, (sprite_x, sprite_y))
                return
        
        # Fallback to colored rectangle if no sprite available
        color = (0, 200, 100)  # Green for player (not red!)
        if self.is_invincible:
            color = (255, 255, 0) if int(pygame.time.get_ticks() / 100) % 2 else (0, 200, 100)
        
        rect = pygame.Rect(screen_x, screen_y, self.size.x, self.size.y)
        pygame.draw.rect(surface, color, rect)
        
        # Draw a small indicator for direction
        if self.facing_direction == Direction.RIGHT:
            pygame.draw.polygon(surface, (255, 255, 255), [
                (screen_x + self.size.x, screen_y + self.size.y // 2),
                (screen_x + self.size.x - 10, screen_y + self.size.y // 2 - 5),
                (screen_x + self.size.x - 10, screen_y + self.size.y // 2 + 5),
            ])
        else:
            pygame.draw.polygon(surface, (255, 255, 255), [
                (screen_x, screen_y + self.size.y // 2),
                (screen_x + 10, screen_y + self.size.y // 2 - 5),
                (screen_x + 10, screen_y + self.size.y // 2 + 5),
            ])

    def reset(self) -> None:
        """Reset player to initial state."""
        self.health = self.max_health
        self.score = 0
        self.is_invincible = False
        self._timers.clear()
        self._initialize_timers()
        self._active_powerups.clear()
        self._particles.clear()
        self.change_state(PlayerStateType.NORMAL)
