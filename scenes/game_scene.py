import pygame
import os
from typing import Optional, Dict, Any, List
from core.engine import Engine
from core.scene import Scene
from core.camera import Camera
from core.resources import ResourceManager
from core.time import Time
from core.input import InputManager
from world.level_loader import LevelLoader
from world.tiles import TileManager
from world.physics import PhysicsSystem
from world.collision import CollisionSystem
from actors.player import Player
from actors.enemies import EnemyManager
from objects.collectible_manager import CollectibleManager
from objects.powerup_manager import PowerupManager
from objects.door_manager import DoorManager
from objects.hazard_manager import HazardManager
from objects.key_pickup import KeyPickup
from objects.door import Door
from ui.hud import HUD
from ui.pause_menu import PauseMenu
from shared.types import Vec2i, DoorState
from modes.registry import ModeRegistry
from shared.constants import *
from shared.types import GameState, LevelData, Vector2


class GameScene(Scene):
    """Main gameplay scene that manages all game systems and entities."""
    
    def __init__(self, engine: Engine, level_name: str = "level01"):
        """Initialize the game scene with specified level."""
        super().__init__(engine)
        self.level_name = level_name
        self.game_state = GameState.PLAYING
        self.level_complete = False
        self.level_complete_timer = 0.0
        self.level_complete_duration = 2.0
        
        # Core systems
        self.resource_manager = None
        self.time_manager = None
        self.input_manager = None
        
        # World systems
        self.level_loader = None
        self.tile_manager = None
        self.physics_system = None
        self.collision_system = None
        
        # Entities
        self.player = None
        self.enemy_manager = None
        self.collectible_manager = None
        self.powerup_manager = None
        self.door_manager = None
        self.hazard_manager = None
        self.key_pickups: List[KeyPickup] = []
        self.doors: List[Door] = []
        self.current_room = 1  # Current room/background number
        
        # UI
        self.hud = None
        self.pause_menu = None
        self.is_paused = False
        
        # Modes
        self.mode_registry = None
        
        # Level data
        self.level_data = None
        self.camera = None
        
        # Background
        self.background_surface: Optional[pygame.Surface] = None
        self.background_parallax = 0.5  # Parallax factor (0 = static, 1 = follows camera)
        
    def setup(self) -> None:
        """Initialize all game systems and load the level."""
        # Initialize core systems
        self.resource_manager = ResourceManager()
        self.time_manager = Time()
        # Use the singleton InputManager - same one the player states use
        self.input_manager = InputManager.get_instance()
        if not self.input_manager.is_initialized():
            self.input_manager.initialize()
        
        # Initialize world systems
        self.level_loader = LevelLoader()
        self.tile_manager = TileManager(self.resource_manager)
        self.physics_system = PhysicsSystem()
        self.collision_system = CollisionSystem(self.tile_manager)
        
        # Initialize entity managers
        self.enemy_manager = EnemyManager()
        self.collectible_manager = CollectibleManager(self)
        self.powerup_manager = PowerupManager(self)
        self.door_manager = DoorManager(self)
        self.hazard_manager = HazardManager()
        
        # Initialize UI
        self.hud = HUD(self.resource_manager)
        self.pause_menu = PauseMenu(self.engine)
        self.pause_menu.initialize()
        
        # Set up pause menu callbacks
        self.pause_menu.option_callbacks[1] = self.restart_level  # Restart
        self.pause_menu.option_callbacks[2] = self.return_to_menu  # Main Menu
        
        # Initialize modes
        self.mode_registry = ModeRegistry()
        
        # Load the level
        self.load_level(self.level_name)
        
    def load_level(self, level_name: str) -> None:
        """Load a level by name."""
        try:
            # Load level data
            self.level_data = self.level_loader.load_level(level_name)
            
            # Setup tile manager
            self.tile_manager.load_tiles(self.level_data.tiles)
            
            # Load background
            self._load_background()
            
            # Create camera
            screen_size = self.get_screen_size()
            world_size = (self.level_data.width * TILE_SIZE, 
                         self.level_data.height * TILE_SIZE)
            self.camera = Camera(screen_size, world_size)
            
            # Spawn entities
            self.spawn_entities_from_level_data()
            
            # Apply level modes
            self.apply_level_modes()
            
            # Update HUD
            self.hud.update(0, 100, 100, [], None)
            
        except Exception as e:
            print(f"Error loading level {level_name}: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to empty level
            self.level_data = LevelData("Empty", 40, 20, 
                                       [[1]*40 for _ in range(20)], 
                                       [], [], "default", "none")
            screen_size = self.get_screen_size()
            world_size = (self.level_data.width * TILE_SIZE, 
                         self.level_data.height * TILE_SIZE)
            self.camera = Camera(screen_size, world_size)
    
    def _load_background(self) -> None:
        """Load the background image based on level data."""
        import os
        
        if not self.level_data:
            return
        
        bg_name = self.level_data.background
        
        # Map background names to files
        bg_mapping = {
            "default": "qq-background1.png",
            "background1": "qq-background1.png",
            "background2": "qq-background2.png",
            "background3": "qq-background3.png",
            "background4": "qq-background4.png",
            "1": "qq-background1.png",
            "2": "qq-background2.png",
            "3": "qq-background3.png",
            "4": "qq-background4.png",
        }
        
        bg_filename = bg_mapping.get(bg_name, "qq-background1.png")
        bg_path = os.path.join(ASSETS_PATH, bg_filename)
        
        try:
            if os.path.exists(bg_path):
                self.background_surface = pygame.image.load(bg_path).convert()
                print(f"Loaded background: {bg_filename}")
            else:
                print(f"Background file not found: {bg_path}")
                self.background_surface = None
        except Exception as e:
            print(f"Error loading background {bg_filename}: {e}")
            self.background_surface = None
    
    def spawn_entities_from_level_data(self) -> None:
        """Spawn all entities defined in the level data."""
        if not self.level_data or not self.level_data.entities:
            return
            
        for entity_data in self.level_data.entities:
            entity_type = entity_data.get("type", "")
            x = entity_data.get("x", 0) * TILE_SIZE
            y = entity_data.get("y", 0) * TILE_SIZE
            
            try:
                if entity_type == "player":
                    # Spawn Y is the tile ABOVE ground, place player on top of next row
                    # Ground level will be found by collision system
                    self.player = Player(x, y)
                    # Ensure player starts stable
                    self.player.velocity.y = 0
                    self.player._on_ground = True
                    self.player.set_engine_references(
                        self.engine, 
                        self.physics_system, 
                        self.collision_system, 
                        self.mode_registry
                    )
                    if self.camera:
                        self.camera.set_target(self.player.position)
                        
                elif entity_type == "enemy":
                    enemy_type = entity_data.get("subtype", "walqer")
                    # Adjust Y: sprite (64px) is larger than hitbox (32px), centered
                    # So sprite extends 16px below hitbox. Move enemy down 16px.
                    adjusted_y = y + 16  # Half tile down so sprite feet touch ground
                    self.enemy_manager.create_enemy(enemy_type, x, adjusted_y)
                    
                elif entity_type == "collectible":
                    collectible_type = entity_data.get("subtype", "briq")
                    self.collectible_manager.create_collectible(collectible_type, x, y)
                    
                elif entity_type == "powerup":
                    powerup_type = entity_data.get("subtype", "jumpupstiq")
                    self.powerup_manager.create_powerup(powerup_type, x, y)
                    
                elif entity_type == "door":
                    door_type = entity_data.get("subtype", "exit")
                    target_room = entity_data.get("target_room", 2)
                    door = Door(x, y, 64, 96, target_room=target_room)
                    self.doors.append(door)
                    
                elif entity_type == "key":
                    key_id = entity_data.get("key_id", "default")
                    key = KeyPickup(x, y, key_id)
                    self.key_pickups.append(key)
                    
                elif entity_type == "hazard":
                    hazard_type = entity_data.get("subtype", "spike")
                    self.hazard_manager.create_hazard(hazard_type, x, y)
            except Exception as e:
                print(f"Error spawning {entity_type}: {e}")
    
    def apply_level_modes(self) -> None:
        """Apply level-specific game modes."""
        if not self.level_data or not self.level_data.modes:
            return
            
        for mode_name in self.level_data.modes:
            try:
                self.mode_registry.activate_mode(mode_name)
            except Exception as e:
                print(f"Error activating mode {mode_name}: {e}")
    
    def fixed_update(self, delta_time: float) -> None:
        pass

    def update(self, delta_time: float, alpha: float) -> None:
        """Update all game systems and entities."""
        # Don't update game when paused
        if self.is_paused:
            return
            
        # Check if level is complete
        if self.level_complete:
            self.check_level_completion(delta_time)
            return
            
        # Update time manager
        if self.time_manager:
            self.time_manager.update()
            
        # NOTE: Don't call input_manager.update() or player.handle_input() here!
        # The engine's _process_events() handles input clearing.
        # player.update() calls state.handle_input() internally.
        
        # Update modes
        if self.mode_registry:
            self.mode_registry.update_modes(delta_time)
            
        # Update player
        if self.player:
            self.player.update(delta_time)
            if self.camera:
                self.camera.set_target(self.player.position)
            # Update player projectiles and check enemy collisions
            enemies = self.enemy_manager.get_all_enemies() if self.enemy_manager else []
            self.player.update_projectiles(delta_time, enemies)
                
        # Update enemy manager
        if self.enemy_manager:
            self.enemy_manager.update(delta_time, self.player.position if self.player else None)
            
        # Update collectible manager
        if self.collectible_manager:
            self.collectible_manager.update(delta_time)
            
        # Update powerup manager
        if self.powerup_manager:
            self.powerup_manager.update(delta_time)
            
        # Update door manager
        if self.door_manager:
            self.door_manager.update(delta_time)
        
        # Update key pickups
        for key in self.key_pickups:
            if not key.is_collected():
                key.update(delta_time)
        
        # Update doors
        for door in self.doors:
            door.update(delta_time)
            
        # Update hazard manager
        if self.hazard_manager:
            self.hazard_manager.update(delta_time)
            
        # Update camera
        if self.camera:
            self.camera.update(delta_time)
            
        # Handle collisions
        self.handle_collisions()
        
        # Update HUD
        if self.hud and self.player:
            active_modes = []
            if self.mode_registry:
                active_modes = [mode.get_mode_type().name for mode in self.mode_registry.get_active_modes()]
            state_name = "Normal"
            if self.player.current_state:
                state_name = self.player.current_state.get_state_name()
            
            # Get powerup remaining times
            from shared.types import PowerupType
            jettpaq_remaining = self.player.get_powerup_remaining(PowerupType.JETTPAQ) if hasattr(self.player, 'get_powerup_remaining') else 0.0
            
            # JumpUpstiq shows in UI when available OR mounted
            jumpupstiq_remaining = 0.0
            if hasattr(self.player, 'jumpupstiq_available') and self.player.jumpupstiq_available:
                jumpupstiq_remaining = 999.0  # Show full bar when available (not mounted yet)
            elif hasattr(self.player, 'jumpupstiq_mounted') and self.player.jumpupstiq_mounted:
                jumpupstiq_remaining = 999.0  # Show full bar when mounted
            
            self.hud.update(
                self.player.score,
                self.player.health,
                self.player.max_health,
                active_modes,
                state_name,
                has_key=getattr(self.player, 'has_key', False),
                jettpaq_remaining=jettpaq_remaining,
                jumpupstiq_remaining=jumpupstiq_remaining
            )
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        # If paused, let pause menu handle events FIRST
        if self.is_paused:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.toggle_pause()
                return
            self.pause_menu.handle_event(event)
            # Check if pause menu closed itself (resume was selected)
            if not self.pause_menu.visible:
                self.is_paused = False
            return
        
        # ESC key toggles pause menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()
                return
            elif event.key == pygame.K_p:
                self.toggle_pause()
                return
            elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                # Enter/E key - interact: mount/unmount JumpUpstiq OR use doors
                self._handle_interact()
                return
    
    def _handle_interact(self) -> None:
        """Handle interact key press - JumpUpstiq mount/unmount or door interaction."""
        if not self.player:
            return
        
        # Priority 1: If JumpUpstiq is mounted, unmount it
        if self.player.jumpupstiq_mounted:
            drop_pos = self.player.unmount_jumpupstiq()
            if drop_pos:
                # Create a new JumpUpstiq pickup at the drop position
                self._create_jumpupstiq_pickup(drop_pos[0], drop_pos[1])
            return
        
        # Priority 2: If JumpUpstiq is available (collected but not mounted), mount it
        if self.player.jumpupstiq_available:
            self.player.mount_jumpupstiq()
            return
        
        # Priority 3: Try to interact with doors
        self._try_enter_door()
    
    def _create_jumpupstiq_pickup(self, x: float, y: float) -> None:
        """Create a JumpUpstiq pickup at the specified position."""
        from objects.jumpupstiq_pickup import JumpUpstiqPickup
        pickup = JumpUpstiqPickup(self, (int(x), int(y)))
        if self.powerup_manager:
            self.powerup_manager.powerups.append(pickup)
            print(f"[JUMPUPSTIQ] Dropped at ({int(x)}, {int(y)})")
    
    def _try_enter_door(self) -> None:
        """Try to open and enter a nearby door."""
        if not self.player:
            return
            
        player_rect = pygame.Rect(
            self.player.position.x, self.player.position.y,
            self.player.size.x, self.player.size.y
        )
        
        for door in self.doors:
            door_rect = pygame.Rect(door.position[0], door.position[1], door.size[0], door.size[1])
            if player_rect.colliderect(door_rect):
                if door.get_state() == DoorState.UNLOCKED:
                    # Start door opening animation
                    door.open_door()
                    print("[DOOR] Opening door...")
                elif door.can_enter():
                    # Door is fully open, transition to next room
                    self._transition_to_room(door.get_target_room())
                    return
    
    def _transition_to_room(self, room_number: int) -> None:
        """Transition to a different room (change background)."""
        print(f"[ROOM] Transitioning to room {room_number}...")
        self.current_room = room_number
        
        # Load new background
        bg_key = f"background{room_number}"
        if bg_key in ASSET_FILES:
            bg_path = os.path.join(ASSETS_PATH, ASSET_FILES[bg_key])
            if os.path.exists(bg_path):
                self.background_surface = pygame.image.load(bg_path).convert()
                self.background_surface = pygame.transform.scale(
                    self.background_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)
                )
                print(f"[ROOM] Loaded background: {bg_key}")
        
        # Reset player position (could be customized per room)
        if self.player:
            self.player.position.x = 100
            self.player.position.y = 400
            self.player.velocity.x = 0
            self.player.velocity.y = 0
        
        # Clear collected keys for new room
        self.player.has_key = False
        
        # Reset doors for this room
        for door in self.doors:
            door.reset()

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_menu.show()
        else:
            self.pause_menu.hide()
    
    def restart_level(self) -> None:
        """Restart the current level."""
        self.pause_menu.hide()
        self.is_paused = False
        # Clear input states to prevent stale data
        input_manager = InputManager.get_instance()
        input_manager.clear()
        # Clear and reload
        self.cleanup()
        self.setup()
    
    def return_to_menu(self) -> None:
        """Return to main menu."""
        self.pause_menu.hide()
        self.is_paused = False
        from ui.main_menu import MainMenu
        self.engine.set_scene(MainMenu(self.engine))
    
    def handle_collisions(self) -> None:
        """Handle all collision detection and resolution."""
        if not self.player:
            return
            
        # Check player collisions with collectibles
        if self.collectible_manager:
            collected = self.collectible_manager.check_player_collision(self.player)
            for collectible in collected:
                self.player.score += collectible.get_value()
                collectible.mark_for_removal()
                
        # Check player collisions with powerups
        if self.powerup_manager:
            from shared.types import PowerupType
            powerups = self.powerup_manager.check_player_collision(self.player)
            for powerup in powerups:
                if powerup.powerup_type == PowerupType.JUMPUPSTIQ:
                    # JumpUpstiq: Just mark as available, don't auto-mount
                    # Player can mount it with E key
                    if not self.player.jumpupstiq_available and not self.player.jumpupstiq_mounted:
                        self.player.jumpupstiq_available = True
                        print("[JUMPUPSTIQ] Picked up! Press E to mount the pogo stick.")
                    powerup.mark_for_removal()
                else:
                    # Other powerups auto-apply
                    self.player._apply_powerup(powerup.powerup_type)
                    powerup.mark_for_removal()
        
        # Check player collisions with key pickups
        player_rect = pygame.Rect(
            self.player.position.x, self.player.position.y,
            self.player.size.x, self.player.size.y
        )
        for key in self.key_pickups:
            if not key.is_collected():
                if player_rect.colliderect(key.get_rect()):
                    key.collect()
                    self.player.has_key = True
                    print(f"[KEY] Player collected key!")
        
        # Check player collisions with doors (our new Door objects)
        for door in self.doors:
            door_rect = pygame.Rect(door.position[0], door.position[1], door.size[0], door.size[1])
            if player_rect.colliderect(door_rect):
                # If player has key and door is locked, unlock it
                if self.player.has_key and door.get_state() == DoorState.LOCKED:
                    door.unlock()
                    print("[DOOR] Door unlocked!")
                    
        # Check player collisions with hazards
        if self.hazard_manager:
            hazards = self.hazard_manager.check_player_collision(self.player)
            for hazard in hazards:
                if hasattr(hazard, 'apply_damage'):
                    damage = hazard.apply_damage()
                    self.player.take_damage(damage)
                    
        # Check player collisions with enemies
        if self.player and self.enemy_manager:
            enemies = self.enemy_manager.check_player_collision(self.player)
            for enemy in enemies:
                if hasattr(enemy, 'damage') and enemy.damage > 0:
                    damage_taken = self.player.take_damage(enemy.damage)
                    if damage_taken:
                        print(f"[DAMAGE] Player hit by enemy for {enemy.damage} damage! Health: {self.player.health}")
        
        # Check player projectiles vs enemies
        if self.player and self.enemy_manager:
            player_pos = Vec2i(int(self.player.position.x), int(self.player.position.y))
            for projectile in self.player._projectiles[:]:  # Copy list to allow removal
                if not projectile.active:
                    continue
                proj_rect = pygame.Rect(
                    projectile.position.x - projectile.projectile_size // 2,
                    projectile.position.y - projectile.projectile_size // 2,
                    projectile.projectile_size,
                    projectile.projectile_size
                )
                for enemy in self.enemy_manager.enemies[:]:
                    if proj_rect.colliderect(enemy.get_rect()):
                        # Hit enemy!
                        enemy.take_damage(projectile.damage)
                        # Alert enemy to player position (they know where the shot came from!)
                        if hasattr(enemy, 'alert_to_player'):
                            enemy.alert_to_player(player_pos)
                        projectile.active = False
                        # Remove dead enemies
                        if enemy.health <= 0:
                            self.enemy_manager.enemies.remove(enemy)
                            self.player.score += 100  # Score for kill
                        break
    
    def check_level_completion(self, delta_time: float) -> None:
        """Check if level is complete and handle transition."""
        self.level_complete_timer += delta_time
        
        if self.level_complete_timer >= self.level_complete_duration:
            self.transition_to_next_level()
    
    def complete_level(self) -> None:
        """Mark level as complete and start completion sequence."""
        self.level_complete = True
        self.level_complete_timer = 0.0
        self.game_state = GameState.LEVEL_COMPLETE
        
        if self.player:
            self.player.velocity.x = 0
            self.player.velocity.y = 0
    
    def transition_to_next_level(self) -> None:
        """Transition to the next level or victory screen."""
        from ui.main_menu import MainMenu
        self.engine.set_scene(MainMenu(self.engine))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Render all game entities and UI."""
        # Clear screen with sky color (fallback if no background)
        surface.fill((40, 60, 120))
        
        if not self.camera:
            font = pygame.font.Font(None, 48)
            text = font.render("Level Loading...", True, (255, 255, 255))
            surface.blit(text, (100, 100))
            return
        
        # Render background with parallax
        self._render_background(surface)
            
        # Get camera offset as tuple (TOP-LEFT for rendering)
        camera_offset_vec = self.camera.get_offset()
        if hasattr(camera_offset_vec, 'x'):
            camera_offset = (camera_offset_vec.x, camera_offset_vec.y)
        else:
            camera_offset = (camera_offset_vec[0], camera_offset_vec[1])
        
        # Render tiles
        if self.tile_manager:
            self.tile_manager.render(surface, camera_offset)
            
        # Render hazards
        if self.hazard_manager:
            self.hazard_manager.render(surface, camera_offset)
            
        # Render collectibles
        if self.collectible_manager:
            self.collectible_manager.render(surface, camera_offset)
            
        # Render powerups
        if self.powerup_manager:
            self.powerup_manager.render(surface, camera_offset)
        
        # Render key pickups
        for key in self.key_pickups:
            if not key.is_collected():
                key.render(surface, camera_offset)
        
        # Render doors (our sprite-based doors)
        for door in self.doors:
            door.render(surface, camera_offset)
            
        # Render enemies
        if self.enemy_manager:
            self.enemy_manager.render(surface, camera_offset)
            
        # Render player
        if self.player:
            self.player.render(surface, camera_offset)
            # Render player projectiles
            self.player.render_projectiles(surface, camera_offset)
            
        # Render level complete overlay
        if self.level_complete:
            self.render_level_complete_overlay(surface)
            
        # Render HUD (always on top)
        if self.hud:
            self.hud.render(surface)
            
        # Render pause menu overlay (on very top)
        if self.is_paused and self.pause_menu:
            self.pause_menu.render(surface)
    
    def _render_background(self, surface: pygame.Surface) -> None:
        """Render the background with parallax scrolling."""
        if not self.background_surface or not self.camera:
            return
        
        # Get screen and background dimensions
        screen_width, screen_height = surface.get_size()
        bg_width = self.background_surface.get_width()
        bg_height = self.background_surface.get_height()
        
        # Calculate world size for parallax
        if self.level_data:
            world_width = self.level_data.width * TILE_SIZE
            world_height = self.level_data.height * TILE_SIZE
        else:
            world_width = screen_width
            world_height = screen_height
        
        # Get camera offset
        camera_offset_vec = self.camera.get_offset()
        if hasattr(camera_offset_vec, 'x'):
            cam_x, cam_y = camera_offset_vec.x, camera_offset_vec.y
        else:
            cam_x, cam_y = camera_offset_vec[0], camera_offset_vec[1]
        
        # Calculate parallax offset
        # When camera is at 0, show left of background
        # When camera is at max, show right of background
        max_cam_x = max(0, world_width - screen_width)
        max_cam_y = max(0, world_height - screen_height)
        
        # Calculate how much of the background to scroll
        bg_scroll_range_x = max(0, bg_width - screen_width)
        bg_scroll_range_y = max(0, bg_height - screen_height)
        
        # Calculate background position based on camera (with parallax factor)
        if max_cam_x > 0:
            bg_x = -int((cam_x / max_cam_x) * bg_scroll_range_x * self.background_parallax)
        else:
            bg_x = 0
        
        if max_cam_y > 0:
            bg_y = -int((cam_y / max_cam_y) * bg_scroll_range_y * self.background_parallax)
        else:
            bg_y = 0
        
        # Scale background to fit screen height if needed
        if bg_height < screen_height:
            scale_factor = screen_height / bg_height
            scaled_width = int(bg_width * scale_factor)
            scaled_bg = pygame.transform.scale(self.background_surface, (scaled_width, screen_height))
            
            # Tile horizontally if needed
            x = bg_x
            while x < screen_width:
                surface.blit(scaled_bg, (x, 0))
                x += scaled_width
        else:
            # Tile the background to cover the screen
            y = bg_y
            while y < screen_height:
                x = bg_x
                while x < screen_width:
                    surface.blit(self.background_surface, (x, y))
                    x += bg_width
                y += bg_height
    
    def render_level_complete_overlay(self, surface: pygame.Surface) -> None:
        """Render level complete overlay animation."""
        overlay = pygame.Surface(self.get_screen_size(), pygame.SRCALPHA)
        alpha = min(200, int(255 * (self.level_complete_timer / self.level_complete_duration)))
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        text = font.render("LEVEL COMPLETE!", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.get_screen_center())
        surface.blit(text, text_rect)
    
    def cleanup(self) -> None:
        """Clean up resources when scene is destroyed."""
        if self.enemy_manager:
            self.enemy_manager.clear()
        if self.collectible_manager:
            self.collectible_manager.clear()
        if self.powerup_manager:
            self.powerup_manager.clear()
        if self.door_manager:
            self.door_manager.clear()
        if self.hazard_manager:
            self.hazard_manager.clear()
        if self.mode_registry:
            self.mode_registry.clear_all_modes()
    
    def get_player(self) -> Optional[Player]:
        return self.player
    
    def get_camera(self) -> Optional[Camera]:
        return self.camera
    
    def get_tile_manager(self) -> Optional[TileManager]:
        return self.tile_manager
    
    def get_game_state(self) -> GameState:
        return self.game_state
    
    def set_game_state(self, state: GameState) -> None:
        self.game_state = state
    
    def is_level_complete(self) -> bool:
        return self.level_complete
