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
        self.health = 10  # 10 health bars
        self.max_health = 10
        self.score = 0
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self._invincible = False
        self._invincible_timer = 0.0
        self._invincible_duration = 2.0  # 2 seconds invincibility after hit
        self.attack_cooldown = 0.0
        self._current_state: Optional[BasePlayerState] = None
        self._states: Dict[PlayerStateType, BasePlayerState] = {}
        self._active_powerups: Dict[PowerupType, float] = {}
        self._powerup_timers: Dict[PowerupType, float] = {}  # For 2-minute countdown
        self._mode_registry: Optional[ModeRegistry] = None
        self._particle_system: Optional[ParticleSystem] = None
        self._animation_frame = 0
        self._animation_timer = 0.0
        self._facing_direction = Direction.RIGHT
        self.facing_direction = Direction.RIGHT
        self.current_animation = "idle"
        self.animation_timer = 0.0
        
        # Key/door system
        self.has_key = False
        
        # JumpUpstiq mount system - it's a pogo stick you can mount/unmount!
        self.jumpupstiq_mounted = False
        self.jumpupstiq_available = False  # True if player has collected one and can mount it
        
        # Sprite rendering
        self._sprite_sheet = None
        self._sprite_frames: Dict[str, List[pygame.Surface]] = {}
        self._sprite_size = 128  # 128x128 cells
        self._render_scale = 0.5  # Scale down for display
        self._load_sprites()
        
        # Smoke overlay - THE SIGNATURE VISUAL!
        self._smoke_overlay = SmokeOverlay((x, y - 30))
        self._smoke_cycle_timer = 0.0
        self._idle_timer = 0.0  # Track how long player has been idle
        self._idle_smoke_delay = 2.0  # Smoke starts after 2 seconds idle
        
        # Hitbox offset from sprite_data
        self.hitbox_offset_x = QOMMANDAH_QEEN_HITBOX["offset_x"]
        self.hitbox_offset_y = QOMMANDAH_QEEN_HITBOX["offset_y"]
        
        # Fuel for jetpack
        self.fuel = 100.0
        self.max_fuel = 100.0
        self.ground_level = 576  # Will be updated by collision system
        self._physics = None
        self._collision = None
        self._engine = None
        self._on_ground = True  # Start on ground - will be validated by collision check
        self._projectiles: List[Any] = []  # Player projectiles
        
        # Invincibility frames after taking damage
        self._invincible = False
        self._invincible_timer = 0.0
        self._invincible_duration = 1.5  # 1.5 seconds of invincibility
        
        self._initialize_state_machine()
        self._initialize_timers()
        self._initialize_particles()

    def _load_sprites(self) -> None:
        """Load player sprite sheets and extract animation frames."""
        try:
            # Load main sprite sheet
            filename = ASSET_FILES.get("player", "qq-qommandah-qeen.png")
            sprite_path = os.path.join(ASSETS_PATH, filename)
            
            if os.path.exists(sprite_path):
                self._sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                config = SPRITE_CONFIGS.get(filename, (128, 128, 8, 4))
                cell_w, cell_h, cols, rows = config
                self._sprite_size = cell_w
                
                # Extract frames for each animation (EXCEPT 'run' - we'll load that from walk sheet)
                for anim_name, anim_spec in QOMMANDAH_QEEN_FRAMES.items():
                    if anim_name == 'run':
                        continue  # Skip - we'll load walk sprites separately
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
            
            # Load walk sprite sheet (qq-qeen-walqin.png) for 'run' animation
            # Walk sheet is 1024x128 - only row 0 has content, cells 1-15 (15 frames)
            walk_sprite_path = os.path.join(ASSETS_PATH, "qq-qeen-walqin.png")
            if os.path.exists(walk_sprite_path):
                walk_sheet = pygame.image.load(walk_sprite_path).convert_alpha()
                
                # Walk sheet uses 64x64 cells, only row 0 cells 1-15 have content
                cell_size = 64
                
                walk_frames = []
                # Load frames from row 0, cells 1-15 (skip empty cell 0)
                for col in range(1, 16):  # Cells 1 through 15
                    x = col * cell_size
                    y = 0  # Row 0 only
                    # Extract 64x64 frame
                    small_frame = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                    small_frame.blit(walk_sheet, (0, 0), (x, y, cell_size, cell_size))
                    
                    # Create 128x128 canvas and position the 64x64 sprite
                    # Center horizontally, position at bottom half
                    frame = pygame.Surface((128, 128), pygame.SRCALPHA)
                    frame.blit(small_frame, (32, 48))
                    walk_frames.append(frame)
                
                if walk_frames:
                    self._sprite_frames['run'] = walk_frames
                    print(f"Loaded walk animation: {len(walk_frames)} frames (cells 1-15 from row 0)")
            else:
                print(f"Walk sprite not found: {walk_sprite_path}")
                
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
        
        # Update idle timer - reset if moving, increment if idle
        if abs(self.velocity.x) > 5 or abs(self.velocity.y) > 5:
            self._idle_timer = 0.0
        else:
            self._idle_timer += delta_time
        
        # Update invincibility timer
        if self._invincible:
            self._invincible_timer -= delta_time
            if self._invincible_timer <= 0:
                self._invincible = False
    
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
            # Also update the timer dict
            if powerup_type in self._powerup_timers:
                self._powerup_timers[powerup_type] = self._active_powerups[powerup_type]
            if self._active_powerups[powerup_type] <= 0:
                expired_powerups.append(powerup_type)
        
        for powerup_type in expired_powerups:
            self._remove_powerup(powerup_type)
            if powerup_type in self._powerup_timers:
                del self._powerup_timers[powerup_type]
            self._create_powerup_expiration_effect(powerup_type)
    
    def get_powerup_remaining(self, powerup_type: PowerupType) -> float:
        """Get remaining time for a powerup (0 if not active)."""
        return self._powerup_timers.get(powerup_type, 0.0)
    
    def has_powerup(self, powerup_type: PowerupType) -> bool:
        """Check if a powerup is active."""
        return powerup_type in self._active_powerups and self._active_powerups[powerup_type] > 0
    
    def _create_powerup_expiration_effect(self, powerup_type: PowerupType) -> None:
        """Create visual effect when powerup expires."""
        pass
    
    def _apply_physics(self, delta_time: float) -> None:
        """Apply physics to player movement."""
        if self._physics:
            pass
        self.position += self.velocity * delta_time
    
    def _check_boundaries(self) -> None:
        """Keep player within level boundaries (not screen!)."""
        # Don't clamp to screen - let camera follow player through level
        # Only prevent going off left edge or below ground
        if self.position.x < 0:
            self.position.x = 0
        # Y boundaries handled by collision system
    
    def _update_animation(self, delta_time: float) -> None:
        """Update player animation frame."""
        if self.current_animation in self._sprite_frames:
            frames = self._sprite_frames[self.current_animation]
            if frames:
                # Use 15 FPS for walk/run animation (15 frames = 1 sec cycle)
                if self.current_animation == 'run':
                    fps = 15  # Walk animation at 15 FPS
                else:
                    anim_spec = QOMMANDAH_QEEN_FRAMES.get(self.current_animation)
                    fps = anim_spec.fps if anim_spec else 10
                
                frame_duration = 1.0 / fps
                
                self.animation_timer += delta_time
                if self.animation_timer >= frame_duration:
                    self.animation_timer -= frame_duration
                    self._animation_frame += 1
                    # Loop all animations
                    if self._animation_frame >= len(frames):
                        self._animation_frame = 0
    
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
    
    def create_projectile(self) -> None:
        """Create a projectile in the direction player is facing."""
        from actors.projectile import Projectile
        from shared.types import Vector2
        from shared.constants import PROJECTILE_SPEED, PROJECTILE_DAMAGE
        
        # Determine direction based on facing
        direction_x = 1 if self.facing_direction == Direction.RIGHT else -1
        
        # Spawn position (in front of player)
        spawn_x = self.position.x + (self.size.x if direction_x > 0 else 0)
        spawn_y = self.position.y + self.size.y / 2
        
        projectile = Projectile(
            position=Vector2(spawn_x, spawn_y),
            direction=Vector2(direction_x, 0),
            owner=self,
            damage=PROJECTILE_DAMAGE,
            speed=PROJECTILE_SPEED,
            color=(0, 255, 100)  # Green for player projectiles
        )
        self._projectiles.append(projectile)
    
    def update_projectiles(self, delta_time: float, enemies: List[Any] = None) -> None:
        """Update all player projectiles."""
        for projectile in self._projectiles[:]:
            projectile.update(delta_time)
            
            # Remove inactive projectiles
            if not projectile.is_active():
                self._projectiles.remove(projectile)
                continue
            
            # Check collision with enemies
            if enemies:
                for enemy in enemies:
                    if enemy.is_active():
                        proj_rect = projectile.get_rect()
                        enemy_rect = enemy.get_rect()
                        if proj_rect.colliderect(enemy_rect):
                            projectile.handle_entity_hit(enemy)
                            break
    
    def render_projectiles(self, surface, camera_offset) -> None:
        """Render all player projectiles."""
        from shared.types import Vector2
        
        if hasattr(camera_offset, 'x'):
            cam = Vector2(camera_offset.x, camera_offset.y)
        else:
            cam = Vector2(camera_offset[0], camera_offset[1])
            
        for projectile in self._projectiles:
            projectile.render(surface, cam)
    
    def take_damage(self, amount: int) -> bool:
        """Apply damage to player - takes 1 health bar per hit.
        
        Args:
            amount: Amount of damage (ignored, always takes 1 bar)
            
        Returns:
            True if damage was taken, False if invincible
        """
        if self._invincible:
            return False
        
        old_health = self.health
        # Always take 1 health bar regardless of damage amount
        self.health = max(0, self.health - 1)
        print(f"[PLAYER] Took damage: {old_health} -> {self.health} ({self.health}/10 bars)")
        
        self._invincible = True
        self._invincible_timer = self._invincible_duration  # 2 seconds
        
        # Knockback
        self.velocity.y = -300  # Pop up
        
        # Visual effect
        self._create_damage_effect()
        
        if self.health <= 0:
            print("[PLAYER] DIED! Respawning...")
            self.die()
        
        return True
    
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
        from shared.constants import POWERUP_DURATION
        
        if powerup_type == PowerupType.JUMPUPSTIQ:
            # JumpUpstiq is mountable - collect it but don't auto-mount
            self.jumpupstiq_available = True
            print(f"[POWERUP] Collected JUMPUPSTIQ! Press E to mount/unmount the pogo stick!")
            # Don't activate state yet - player mounts with E key
            return
        
        # Other powerups work as timed effects
        duration = POWERUP_DURATION  # 120 seconds (2 minutes)
        self._active_powerups[powerup_type] = duration
        self._powerup_timers[powerup_type] = duration
        
        print(f"[POWERUP] Collected {powerup_type.name}! Duration: {duration}s")
        
        if powerup_type == PowerupType.JETTPAQ:
            self._apply_jettpaq()
        
        self._create_powerup_activation_effect(powerup_type)
    
    def mount_jumpupstiq(self) -> bool:
        """Mount the JumpUpstiq pogo stick. Returns True if successful."""
        if self.jumpupstiq_available and not self.jumpupstiq_mounted:
            self.jumpupstiq_mounted = True
            self.jumpupstiq_available = False  # It's now equipped, not in inventory
            # Set infinite duration for display purposes
            self._active_powerups[PowerupType.JUMPUPSTIQ] = 999999.0
            self._powerup_timers[PowerupType.JUMPUPSTIQ] = 999999.0
            self.change_state(PlayerStateType.JUMPUPSTIQ)
            print("[JUMPUPSTIQ] Mounted! Double jump height active. Press E to unmount.")
            return True
        return False
    
    def unmount_jumpupstiq(self) -> tuple:
        """Unmount the JumpUpstiq. Returns (x, y) position where it was dropped."""
        if self.jumpupstiq_mounted:
            self.jumpupstiq_mounted = False
            # Remove from active powerups
            if PowerupType.JUMPUPSTIQ in self._active_powerups:
                del self._active_powerups[PowerupType.JUMPUPSTIQ]
            if PowerupType.JUMPUPSTIQ in self._powerup_timers:
                del self._powerup_timers[PowerupType.JUMPUPSTIQ]
            self.change_state(PlayerStateType.NORMAL)
            # Return drop position (at player's feet)
            drop_x = self.position.x
            drop_y = self.position.y + self.size.y - 32  # At feet level
            print(f"[JUMPUPSTIQ] Unmounted at ({drop_x}, {drop_y}). Walk into it to pick up again!")
            return (drop_x, drop_y)
        return None
    
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
    
    def is_invincible_check(self) -> bool:
        """Check if player is currently invincible."""
        return self._invincible
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        """Render player to surface."""
        # Skip rendering every other frame if invincible (flashing effect)
        if self._invincible and int(self._invincible_timer * 10) % 2 == 0:
            return
        
        # Handle camera offset
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        # Check if we should render smoke overlay
        # Only during idle animation AND after being idle for 2+ seconds
        use_smoke_sprite = (self._smoke_overlay and 
                           self.current_animation == 'idle' and 
                           self._idle_timer >= self._idle_smoke_delay and
                           self._smoke_overlay.frames)
        
        if use_smoke_sprite:
            # Render smoke overlay at player position (smoke sprite includes player)
            smoke_pos = (self.position.x, self.position.y)
            self._smoke_overlay.update_position(smoke_pos)
            self._smoke_overlay.update()
            self._smoke_overlay.render(surface, (cam_x, cam_y))
        else:
            # Render normal player sprite
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
        
        # Try to get current animation frames
        frames = self._sprite_frames.get(self.current_animation, None)
        
        # Fallback to 'idle' if current animation not found
        if not frames:
            frames = self._sprite_frames.get('idle', None)
        
        # Render sprite if we have frames
        if frames:
            # Clamp frame index to valid range
            frame_idx = min(self._animation_frame, len(frames) - 1)
            frame_idx = max(0, frame_idx)
            
            frame = frames[frame_idx]
            
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
            if self._invincible:
                flash = int(pygame.time.get_ticks() / 100) % 2
                if flash:
                    scaled_frame.set_alpha(128)
                else:
                    scaled_frame.set_alpha(255)
            
            surface.blit(scaled_frame, (sprite_x, sprite_y))
            return
        
        # Only show fallback rectangle if absolutely no sprites loaded (debug only)
        # This should rarely happen now
        pass  # Don't draw green rectangle - just skip if no sprites

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
