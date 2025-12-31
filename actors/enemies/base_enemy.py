import pygame
import random
import os
from typing import Optional, Dict, Any, Tuple, List
from shared.types import Vec2i, EnemyState, Direction
from shared.sprite_data import get_sprite_spec, get_animation_spec, SPRITE_REGISTRY
from shared.constants import ASSETS_PATH, ASSET_FILES, SPRITE_CONFIGS
from world.entities import Entity
from world.physics import PhysicsBody
from core.resources import ResourceManager
from core.time import Time

class BaseEnemy(Entity):
    """
    Base class for all enemy entities in the game.
    Provides common functionality like health management, state handling,
    sprite rendering, and AI thinking framework.
    """
    
    # Class-level sprite cache to avoid reloading
    _sprite_cache: Dict[str, pygame.Surface] = {}
    _frame_cache: Dict[str, Dict[str, List[pygame.Surface]]] = {}
    
    def __init__(
        self,
        position: Vec2i,
        health: int = 100,
        damage: int = 10,
        speed: float = 1.0,
        attack_range: float = 50.0,
        detection_range: float = 200.0,
        sprite_key: str = "walqer_bot"
    ) -> None:
        """
        Initialize a new enemy instance.
        
        Args:
            position: Starting position of the enemy
            health: Initial health points
            damage: Damage dealt to player on contact
            speed: Movement speed multiplier
            attack_range: Range at which enemy can attack
            detection_range: Range at which enemy detects player
            sprite_key: Key to look up sprite in ASSET_FILES
        """
        super().__init__(position, (32, 32))
        self._health = health
        self._max_health = health
        self._damage = damage
        self._speed = speed
        self._attack_range = attack_range
        self._detection_range = detection_range
        self._state = EnemyState.PATROL  # Start patrolling immediately
        self._direction = Direction.RIGHT
        self._patrol_points: List[Vec2i] = []
        self._current_patrol_index = 0
        self._state_timers: Dict[EnemyState, float] = {}
        self._hurt_timer = 0.0
        self._death_timer = 0.0
        self._attack_cooldown = 0.0
        self._physics_body = PhysicsBody(position, Vec2i(32, 32))
        self._velocity = Vec2i(0, 0)
        self._knockback_velocity = Vec2i(0, 0)
        self._is_grounded = False
        
        # Sprite rendering
        self._sprite_key = sprite_key
        self._sprite_sheet = None
        self._sprite_frames: Dict[str, List[pygame.Surface]] = {}
        self._sprite_size = 128
        self._render_scale = 0.5
        self._current_animation = "idle"
        self._animation_frame = 0
        self._animation_timer = 0.0
        
        # Load sprites
        self._load_sprites()

    def _load_sprites(self) -> None:
        """Load enemy sprite sheet and extract animation frames."""
        # Check class-level cache first
        if self._sprite_key in BaseEnemy._frame_cache:
            self._sprite_frames = BaseEnemy._frame_cache[self._sprite_key]
            return
        
        try:
            filename = ASSET_FILES.get(self._sprite_key)
            if not filename:
                return
                
            sprite_path = os.path.join(ASSETS_PATH, filename)
            
            if os.path.exists(sprite_path):
                # Use cached sheet if available
                if filename in BaseEnemy._sprite_cache:
                    self._sprite_sheet = BaseEnemy._sprite_cache[filename]
                else:
                    self._sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                    BaseEnemy._sprite_cache[filename] = self._sprite_sheet
                
                config = SPRITE_CONFIGS.get(filename, (128, 128, 8, 4))
                cell_w, cell_h, cols, rows = config
                self._sprite_size = cell_w
                
                # Get animations for this enemy type
                anim_frames = SPRITE_REGISTRY.get(self._sprite_key, {})
                
                # Extract frames for each animation
                for anim_name, anim_spec in anim_frames.items():
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
                
                # Cache the frames
                BaseEnemy._frame_cache[self._sprite_key] = self._sprite_frames
                
        except Exception as e:
            print(f"Error loading enemy sprites for {self._sprite_key}: {e}")

    def think(self, delta_time: float, player_position: Optional[Vec2i] = None) -> None:
        """
        Main AI thinking method to be overridden by specific enemies.
        Base class just handles timers - subclasses handle state logic.
        """
        self._update_timers(delta_time)
        
        # Dead state is always handled here
        if self._state == EnemyState.DEAD:
            self.handle_dead_state(delta_time)
            return
        
        # Hurt state is handled here - enemy can't move while stunned
        if self._state == EnemyState.HURT:
            self.handle_hurt_state(delta_time)
            return
        
        # Let subclass handle all other state logic via their overridden think()
        # This allows WalqerBot etc. to control their own patrol/chase behavior
        if self._state == EnemyState.IDLE:
            self.handle_idle_state(delta_time, player_position)
        elif self._state == EnemyState.PATROL:
            self.handle_patrol_state(delta_time, player_position)
        elif self._state == EnemyState.CHASE:
            self.handle_chase_state(delta_time, player_position)
        elif self._state == EnemyState.ATTACK:
            self.handle_attack_state(delta_time, player_position)

    def _update_timers(self, delta_time: float) -> None:
        """Update all active timers."""
        if self._hurt_timer > 0:
            self._hurt_timer -= delta_time
            if self._hurt_timer <= 0:
                self.change_state(EnemyState.IDLE)
                
        if self._death_timer > 0:
            self._death_timer -= delta_time
            if self._death_timer <= 0:
                self.destroy()
                
        if self._attack_cooldown > 0:
            self._attack_cooldown -= delta_time

    def handle_idle_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        pass

    def handle_patrol_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        if not self._patrol_points:
            self.change_state(EnemyState.IDLE)
            return
            
        target = self._patrol_points[self._current_patrol_index]
        distance = ((target.x - self.position.x) ** 2 + (target.y - self.position.y) ** 2) ** 0.5
        
        if distance < 5.0:
            self._current_patrol_index = (self._current_patrol_index + 1) % len(self._patrol_points)
            target = self._patrol_points[self._current_patrol_index]
            
        self._move_toward(target, delta_time)

    def handle_chase_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        if not player_position:
            self.change_state(EnemyState.PATROL if self._patrol_points else EnemyState.IDLE)
            return
            
        distance = ((player_position.x - self.position.x) ** 2 + 
                   (player_position.y - self.position.y) ** 2) ** 0.5
        
        if distance <= self._attack_range:
            self.change_state(EnemyState.ATTACK)
        else:
            self._move_toward(player_position, delta_time)

    def handle_attack_state(self, delta_time: float, player_position: Optional[Vec2i]) -> None:
        if not player_position:
            self.change_state(EnemyState.PATROL if self._patrol_points else EnemyState.IDLE)
            return
            
        distance = ((player_position.x - self.position.x) ** 2 + 
                   (player_position.y - self.position.y) ** 2) ** 0.5
        
        if distance > self._attack_range:
            self.change_state(EnemyState.CHASE)
        elif self._attack_cooldown <= 0:
            self.perform_attack()

    def handle_hurt_state(self, delta_time: float) -> None:
        pass

    def handle_dead_state(self, delta_time: float) -> None:
        pass

    def _move_toward(self, target: Vec2i, delta_time: float) -> None:
        """Move toward target position."""
        dx = target.x - self.position.x
        dy = target.y - self.position.y
        
        if dx > 0:
            self._direction = Direction.RIGHT
        elif dx < 0:
            self._direction = Direction.LEFT
            
        move_speed = self._speed * 100 * delta_time
        if abs(dx) > move_speed:
            self.position = Vec2i(
                self.position.x + (move_speed if dx > 0 else -move_speed),
                self.position.y
            )
        else:
            self.position = Vec2i(target.x, self.position.y)

    def change_state(self, new_state: EnemyState) -> None:
        """Change the enemy's current state."""
        old_state = self._state
        self._state = new_state
        
        # Reset animation when state changes
        self._current_animation = self.get_animation_for_state()
        self._animation_frame = 0
        self._animation_timer = 0.0
        
        if new_state == EnemyState.HURT:
            self._hurt_timer = 1.0  # Stunned for 1 second when hit
        elif new_state == EnemyState.DEAD:
            self._death_timer = 1.0

    def can_detect_player(self, player_position: Vec2i) -> bool:
        """Check if enemy can detect the player.
        
        Enemy can only see player if:
        1. Player is within detection range
        2. Player is in FRONT of enemy (based on facing direction)
        """
        # Check distance first
        distance = ((player_position.x - self.position.x) ** 2 + 
                   (player_position.y - self.position.y) ** 2) ** 0.5
        if distance > self._detection_range:
            return False
        
        # Check if player is in front of enemy based on facing direction
        dx = player_position.x - self.position.x
        
        if self._direction == Direction.RIGHT:
            # Facing right - can only see player if they're to the RIGHT (dx > 0)
            return dx > 0
        else:
            # Facing left - can only see player if they're to the LEFT (dx < 0)
            return dx < 0

    def take_damage(self, amount: int, knockback: Optional[Vec2i] = None) -> None:
        """Apply damage to the enemy."""
        if self._state == EnemyState.DEAD:
            return
            
        self._health -= amount
        self.on_damage_taken(amount)
        
        if knockback:
            self._knockback_velocity = knockback
            
        if self._health <= 0:
            self.change_state(EnemyState.DEAD)
        else:
            self.change_state(EnemyState.HURT)
    
    def on_damage_taken(self, amount: int) -> None:
        """Called when enemy takes damage. Can be overridden."""
        pass
    
    def alert_to_player(self, player_position: Vec2i) -> None:
        """Alert enemy to player position (e.g., when shot from behind)."""
        # Turn to face the player
        dx = player_position.x - self.position.x
        self._direction = Direction.RIGHT if dx > 0 else Direction.LEFT

    def perform_attack(self) -> None:
        """Perform attack action. Must be overridden by specific enemies."""
        self._attack_cooldown = 1.0

    def move(self, movement: Vec2i) -> None:
        """Move the enemy by the specified vector."""
        self.position = Vec2i(
            self.position.x + movement.x,
            self.position.y + movement.y
        )

    def update(self, delta_time: float) -> None:
        """Update enemy state and animations."""
        # Apply knockback
        if self._knockback_velocity != Vec2i(0, 0):
            self.move(self._knockback_velocity)
            self._knockback_velocity = Vec2i(
                int(self._knockback_velocity.x * 0.9),
                int(self._knockback_velocity.y * 0.9)
            )
            
        # Update animation
        self._update_animation(delta_time)

    def _update_animation(self, delta_time: float) -> None:
        """Update animation frame."""
        animation_name = self.get_animation_for_state()
        if not animation_name:
            return
            
        if self._current_animation != animation_name:
            self._current_animation = animation_name
            self._animation_frame = 0
            self._animation_timer = 0.0
            
        # Advance frame
        if self._current_animation in self._sprite_frames:
            frames = self._sprite_frames[self._current_animation]
            if frames:
                self._animation_timer += delta_time
                if self._animation_timer >= 0.1:  # 10 FPS
                    self._animation_timer = 0
                    self._animation_frame = (self._animation_frame + 1) % len(frames)

    def get_animation_for_state(self) -> Optional[str]:
        """Get the animation name for the current state."""
        state_to_animation = {
            EnemyState.IDLE: "idle",
            EnemyState.PATROL: "walk",
            EnemyState.CHASE: "walk",
            EnemyState.ATTACK: "shoot",
            EnemyState.HURT: "hurt",
            EnemyState.DEAD: "dead"
        }
        return state_to_animation.get(self._state, "idle")

    def render(self, surface: pygame.Surface, camera_offset) -> None:
        """Render the enemy with sprites."""
        # Handle both tuple and Vector2 camera_offset
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        screen_x = self.position.x - cam_x
        screen_y = self.position.y - cam_y
        
        # Try to render sprite
        if self._current_animation in self._sprite_frames:
            frames = self._sprite_frames[self._current_animation]
            if frames and self._animation_frame < len(frames):
                frame = frames[self._animation_frame]
                
                # Scale down sprite
                scaled_size = int(self._sprite_size * self._render_scale)
                scaled_frame = pygame.transform.scale(frame, (scaled_size, scaled_size))
                
                # Flip if facing left
                if self._direction == Direction.LEFT:
                    scaled_frame = pygame.transform.flip(scaled_frame, True, False)
                
                # Flash red when hurt
                if self._state == EnemyState.HURT:
                    scaled_frame.fill((255, 100, 100), special_flags=pygame.BLEND_MULT)
                
                # Center sprite on position
                sprite_x = screen_x - (scaled_size - 32) // 2
                sprite_y = screen_y - (scaled_size - 32) // 2
                
                surface.blit(scaled_frame, (sprite_x, sprite_y))
                
                # Render health bar if not full
                if self._health < self._max_health:
                    self.render_health_bar(surface, camera_offset)
                return
        
        # Fallback to colored rectangle
        rect = pygame.Rect(screen_x, screen_y, 32, 32)
        
        # Different colors for different states
        if self._state == EnemyState.DEAD:
            color = (100, 100, 100)
        elif self._state == EnemyState.HURT:
            color = (255, 128, 0)
        elif self._state == EnemyState.ATTACK:
            color = (255, 0, 0)
        elif self._state == EnemyState.CHASE:
            color = (255, 100, 100)
        else:
            color = (200, 50, 50)
        
        pygame.draw.rect(surface, color, rect)
        
        # Direction indicator
        if self._direction == Direction.RIGHT:
            pygame.draw.polygon(surface, (255, 255, 255), [
                (screen_x + 32, screen_y + 16),
                (screen_x + 26, screen_y + 12),
                (screen_x + 26, screen_y + 20),
            ])
        else:
            pygame.draw.polygon(surface, (255, 255, 255), [
                (screen_x, screen_y + 16),
                (screen_x + 6, screen_y + 12),
                (screen_x + 6, screen_y + 20),
            ])
        
        # Render health bar if not full
        if self._health < self._max_health:
            self.render_health_bar(surface, camera_offset)

    def render_health_bar(self, surface: pygame.Surface, camera_offset) -> None:
        """Render a health bar above the enemy."""
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        health_percent = self._health / self._max_health
        bar_width = 30
        bar_height = 4
        bar_x = self.position.x - cam_x + 1
        bar_y = self.position.y - cam_y - 8
        
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        fill_width = int(bar_width * health_percent)
        if health_percent > 0.5:
            color = (0, 255, 0)
        elif health_percent > 0.25:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
            
        pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))

    def get_save_data(self) -> Dict[str, Any]:
        return {
            'position': (self.position.x, self.position.y),
            'health': self._health,
            'max_health': self._max_health,
            'state': self._state.value,
            'direction': self._direction.value
        }

    def load_save_data(self, data: Dict[str, Any]) -> None:
        self.position = Vec2i(data['position'][0], data['position'][1])
        self._health = data['health']
        self._max_health = data['max_health']
        self._state = EnemyState(data['state'])
        self._direction = Direction(data['direction'])

    def set_patrol_points(self, points: List[Vec2i]) -> None:
        """Set patrol points for this enemy."""
        self._patrol_points = points
        if points and self._state == EnemyState.IDLE:
            self.change_state(EnemyState.PATROL)

    def get_health(self) -> int:
        return self._health

    def get_max_health(self) -> int:
        return self._max_health

    def is_alive(self) -> bool:
        return self._state != EnemyState.DEAD

    def get_state(self) -> EnemyState:
        return self._state

    def get_direction(self) -> Direction:
        return self._direction
    
    @property
    def damage(self) -> int:
        return self._damage
    
    @property
    def speed(self) -> float:
        return self._speed
    
    @property
    def attack_range(self) -> float:
        return self._attack_range
    
    @property
    def detection_range(self) -> float:
        return self._detection_range
    
    @property
    def health(self) -> int:
        return self._health
    
    @health.setter
    def health(self, value: int) -> None:
        self._health = value
    
    @property
    def hurt_timer(self) -> float:
        return self._hurt_timer
    
    @property
    def death_timer(self) -> float:
        return self._death_timer
    
    @property
    def direction(self) -> Direction:
        return self._direction
    
    @direction.setter
    def direction(self, value: Direction) -> None:
        self._direction = value
