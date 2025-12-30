"""
Main menu scene implementation.
"""
import pygame
from typing import Optional, List, Tuple
from core.scene import Scene
from core.engine import Engine
from core.resources import ResourceManager
from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS
from shared.types import MenuAction

class MenuItem:
    """Represents a single menu option."""
    def __init__(self, text: str, action: MenuAction, position: Tuple[int, int]):
        """
        Initialize a menu item.
        
        Args:
            text: Display text for the menu item
            action: Action to perform when selected
            position: (x, y) position for rendering
        """
        self.text = text
        self.action = action
        self.position = position
        self.is_selected = False
        self.is_hovered = False

class MenuScene(Scene):
    """Main menu scene with interactive menu options."""
    def __init__(self, engine: Engine):
        """
        Initialize the menu scene.
        
        Args:
            engine: The game engine instance
        """
        super().__init__(engine)
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0
        self.font_large: Optional[pygame.font.Font] = None
        self.font_small: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.background: Optional[pygame.Surface] = None
        self.music_playing = False
        self.initialized = False

    def setup(self) -> None:
        """Set up the menu scene resources and initialize menu items."""
        self._load_resources()
        self._create_menu_items()
        self._play_menu_music()
        self.initialized = True

    def _load_resources(self) -> None:
        """Load all required resources for the menu."""
        resource_manager = ResourceManager()
        self.font_large = resource_manager.load_font("menu_large", 36)
        self.font_small = resource_manager.load_font("menu_small", 24)
        self.title_font = resource_manager.load_font("title", 48)
        
        try:
            background_image = resource_manager.load_image("main_menu_background", "qq-main-menu.png")
            self.background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            self.background = self.create_surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill(COLORS["black"])

    def _create_menu_items(self) -> None:
        """Create the menu items with their positions."""
        center_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        
        items = [
            ("Start Game", MenuAction.START_GAME),
            ("Options", MenuAction.OPTIONS),
            ("Exit", MenuAction.EXIT)
        ]
        
        for i, (text, action) in enumerate(items):
            y = start_y + i * 60
            item = MenuItem(text, action, (center_x, y))
            self.menu_items.append(item)
        
        if self.menu_items:
            self.menu_items[0].is_selected = True

    def _play_menu_music(self) -> None:
        """Start playing menu music if available."""
        try:
            resource_manager = ResourceManager()
            music = resource_manager.load_sound("menu_music", "music/menu.ogg")
            pygame.mixer.music.load("assets/music/menu.ogg")
            pygame.mixer.music.play(-1)
            self.music_playing = True
        except Exception:
            self.music_playing = False

    def _stop_menu_music(self) -> None:
        """Stop playing menu music."""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    def cleanup(self) -> None:
        """Clean up menu scene resources."""
        self._stop_menu_music()
        self.menu_items.clear()
        self.initialized = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle input events for menu navigation.
        
        Args:
            event: Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self._move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self._move_selection(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_current_item()
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_click(event.pos)

    def _move_selection(self, direction: int) -> None:
        """
        Move menu selection up or down.
        
        Args:
            direction: -1 for up, 1 for down
        """
        if not self.menu_items:
            return
            
        self.menu_items[self.selected_index].is_selected = False
        self.selected_index = (self.selected_index + direction) % len(self.menu_items)
        self.menu_items[self.selected_index].is_selected = True

    def _select_current_item(self) -> None:
        """Execute the action of the currently selected menu item."""
        if self.menu_items:
            item = self.menu_items[self.selected_index]
            self._execute_menu_action(item.action)

    def _execute_menu_action(self, action: MenuAction) -> None:
        """
        Execute a menu action.
        
        Args:
            action: Menu action to execute
        """
        if action == MenuAction.START_GAME:
            self.request_scene_change("game")
        elif action == MenuAction.OPTIONS:
            print("Options menu not implemented")
        elif action == MenuAction.EXIT:
            self.get_engine().quit()

    def _handle_mouse_hover(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Handle mouse hover over menu items.
        
        Args:
            mouse_pos: Current mouse position (x, y)
        """
        for i, item in enumerate(self.menu_items):
            text_rect = self._get_text_rect(item.text, item.position[0], item.position[1])
            was_hovered = item.is_hovered
            item.is_hovered = text_rect.collidepoint(mouse_pos)
            
            if item.is_hovered and not was_hovered:
                self.selected_index = i
                for other_item in self.menu_items:
                    other_item.is_selected = False
                item.is_selected = True

    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Handle mouse click on menu items.
        
        Args:
            mouse_pos: Mouse click position (x, y)
        """
        for item in self.menu_items:
            text_rect = self._get_text_rect(item.text, item.position[0], item.position[1])
            if text_rect.collidepoint(mouse_pos):
                self._execute_menu_action(item.action)
                break

    def _get_text_rect(self, text: str, x: int, y: int) -> pygame.Rect:
        """Get rectangle for text rendering."""
        if not self.font_large:
            return pygame.Rect(x, y, 0, 0)
        
        text_surface = self.font_large.render(text, True, COLORS["white"])
        text_rect = text_surface.get_rect(center=(x, y))
        return text_rect

    def fixed_update(self, delta_time: float) -> None:
        """
        Update menu scene with fixed timestep.
        
        Args:
            delta_time: Fixed timestep duration
        """
        pass

    def update(self, delta_time: float, alpha: float) -> None:
        """
        Update menu scene with variable timestep.
        
        Args:
            delta_time: Variable timestep duration
            alpha: Interpolation factor for rendering
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the menu scene to the given surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        if self.background:
            surface.blit(self.background, (0, 0))
        
        self._draw_title(surface)
        self._draw_menu_options(surface)

    def _draw_title(self, surface: pygame.Surface) -> None:
        """Draw the game title."""
        if not self.title_font:
            return
            
        # Title is now in the background image - no text needed
        pass

    def _draw_menu_options(self, surface: pygame.Surface) -> None:
        """Draw all menu options."""
        if not self.font_large:
            return
            
        for item in self.menu_items:
            color = COLORS["yellow"] if item.is_selected else COLORS["white"]
            if item.is_hovered and not item.is_selected:
                color = COLORS["cyan"]
            
            text_surface = self.font_large.render(item.text, True, color)
            text_rect = text_surface.get_rect(center=item.position)
            surface.blit(text_surface, text_rect)

    def request_scene_change(self, scene_name: str) -> None:
        """
        Request a scene change.
        
        Args:
            scene_name: Name of the scene to transition to
        """
        engine = self.get_engine()
        if scene_name == "game":
            from scenes.game_scene import GameScene
            game_scene = GameScene(engine)
            engine.set_scene(game_scene)

    def is_initialized(self) -> bool:
        """
        Check if the scene has been initialized.
        
        Returns:
            True if scene has been set up, False otherwise
        """
        return self.initialized

    def get_menu_items(self) -> List[MenuItem]:
        """
        Get the list of menu items.
        
        Returns:
            List of MenuItem objects
        """
        return self.menu_items

    def get_selected_item(self) -> Optional[MenuItem]:
        """
        Get the currently selected menu item.
        
        Returns:
            Selected MenuItem or None if no items
        """
        if self.menu_items and 0 <= self.selected_index < len(self.menu_items):
            return self.menu_items[self.selected_index]
        return None

    def is_music_playing(self) -> bool:
        """
        Check if menu music is playing.
        
        Returns:
            True if music is playing, False otherwise
        """
        return self.music_playing