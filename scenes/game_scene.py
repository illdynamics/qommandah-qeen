import pygame
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
from ui.hud import HUD
from ui.pause_menu import PauseMenu
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
        
        # UI
        self.hud = None
        self.pause_menu = None
        self.is_paused = False
        
        # Modes
        self.mode_registry = None
        
        # Level data
        self.level_data = None
        self.camera = None
        
    def setup(self) -> None:
        """Initialize all game systems and load the level."""
        # Initialize core systems
        self.resource_manager = ResourceManager()
        self.time_manager = Time()
        self.input_manager = InputManager()
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
                    self.player = Player(x, y)
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
                    self.enemy_manager.create_enemy(enemy_type, x, y)
                    
                elif entity_type == "collectible":
                    collectible_type = entity_data.get("subtype", "briq")
                    self.collectible_manager.create_collectible(collectible_type, x, y)
                    
                elif entity_type == "powerup":
                    powerup_type = entity_data.get("subtype", "jumpupstiq")
                    self.powerup_manager.create_powerup(powerup_type, x, y)
                    
                elif entity_type == "door":
                    door_type = entity_data.get("subtype", "exit")
                    self.door_manager.create_door(door_type, x, y)
                    
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
            
        # Update input
        if self.input_manager:
            self.input_manager.update()
            
        # Handle player input
        if self.player:
            self.player.handle_input()
        
        # Update modes
        if self.mode_registry:
            self.mode_registry.update_modes(delta_time)
            
        # Update player
        if self.player:
            self.player.update(delta_time)
            if self.camera:
                self.camera.set_target(self.player.position)
                
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
            self.hud.update(
                self.player.score,
                self.player.health * 33,  # Convert 3 HP to percentage
                100,  # Max health percentage
                active_modes,
                state_name
            )
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        # ESC key toggles pause menu
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()
                return
            elif event.key == pygame.K_p:
                self.toggle_pause()
                return
        
        # If paused, let pause menu handle events
        if self.is_paused:
            self.pause_menu.handle_event(event)
            # Check if pause menu closed itself (resume was selected)
            if not self.pause_menu.visible:
                self.is_paused = False
            return

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
            powerups = self.powerup_manager.check_player_collision(self.player)
            for powerup in powerups:
                self.player._apply_powerup(powerup.powerup_type)
                powerup.mark_for_removal()
                
        # Check player collisions with doors
        if self.door_manager:
            doors = self.door_manager.check_player_collision(self.player)
            for door in doors:
                if door.is_open():
                    self.complete_level()
                    
        # Check player collisions with hazards
        if self.hazard_manager:
            hazards = self.hazard_manager.check_player_collision(self.player)
            for hazard in hazards:
                if hasattr(hazard, 'apply_damage'):
                    damage = hazard.apply_damage()
                    self.player.take_damage(damage)
                    
        # Check player collisions with enemies
        if self.enemy_manager:
            enemies = self.enemy_manager.check_player_collision(self.player)
            for enemy in enemies:
                if hasattr(enemy, 'damage'):
                    self.player.take_damage(enemy.damage)
    
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
        # Clear screen with sky color
        surface.fill((40, 60, 120))
        
        if not self.camera:
            font = pygame.font.Font(None, 48)
            text = font.render("Level Loading...", True, (255, 255, 255))
            surface.blit(text, (100, 100))
            return
            
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
            
        # Render doors
        if self.door_manager:
            self.door_manager.render(surface, camera_offset)
            
        # Render enemies
        if self.enemy_manager:
            self.enemy_manager.render(surface, camera_offset)
            
        # Render player
        if self.player:
            self.player.render(surface, camera_offset)
            
        # Render level complete overlay
        if self.level_complete:
            self.render_level_complete_overlay(surface)
            
        # Render HUD (always on top)
        if self.hud:
            self.hud.render(surface)
            
        # Render pause menu overlay (on very top)
        if self.is_paused and self.pause_menu:
            self.pause_menu.render(surface)
    
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
