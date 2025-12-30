import pygame
import os
from typing import Optional
from core.scene import Scene
from shared.constants import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH


class MainMenu(Scene):
    """Main menu scene with background and interactive options."""
    
    def __init__(self, engine):
        super().__init__(engine)
        self.selected_index = 0
        self.menu_options = ["Start Game", "Options", "Exit"]
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.background: Optional[pygame.Surface] = None
        self._is_initialized = False
        
        # Options submenu state
        self.in_options_menu = False
        self.options_selected_index = 0
        self.options_menu_items = ["Toggle Fullscreen", "Back"]
        
    def setup(self) -> None:
        """Set up the menu scene."""
        self._load_resources()
        self._setup_fonts()
        self._is_initialized = True
        
    def _load_resources(self) -> None:
        """Load all required resources."""
        try:
            bg_path = os.path.join(ASSETS_PATH, "qq-main-menu.png")
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path).convert()
            else:
                bg_path = os.path.join(ASSETS_PATH, "qq-background1.png")
                if os.path.exists(bg_path):
                    self.background = pygame.image.load(bg_path).convert()
        except Exception as e:
            print(f"Could not load background: {e}")
            self.background = None
            
    def _setup_fonts(self) -> None:
        """Initialize font objects."""
        try:
            self.font = pygame.font.Font(None, 48)
            self.title_font = pygame.font.Font(None, 64)
        except:
            self.font = pygame.font.SysFont("Arial", 48)
            self.title_font = pygame.font.SysFont("Arial", 64)
            
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if self.in_options_menu:
                self._handle_options_input(event)
            else:
                self._handle_main_menu_input(event)
    
    def _handle_main_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input for main menu."""
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.menu_options)
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.menu_options)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self._select_option()
        elif event.key == pygame.K_ESCAPE:
            self._exit_game()
    
    def _handle_options_input(self, event: pygame.event.Event) -> None:
        """Handle input for options submenu."""
        if event.key == pygame.K_UP:
            self.options_selected_index = (self.options_selected_index - 1) % len(self.options_menu_items)
        elif event.key == pygame.K_DOWN:
            self.options_selected_index = (self.options_selected_index + 1) % len(self.options_menu_items)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self._select_options_item()
        elif event.key == pygame.K_ESCAPE:
            self.in_options_menu = False
    
    def _select_option(self) -> None:
        """Execute currently selected option."""
        option = self.menu_options[self.selected_index]
        if option == "Start Game":
            self._start_game()
        elif option == "Options":
            self._open_options()
        elif option == "Exit":
            self._exit_game()
    
    def _select_options_item(self) -> None:
        """Execute selected options menu item."""
        item = self.options_menu_items[self.options_selected_index]
        if item == "Toggle Fullscreen":
            self.engine.toggle_fullscreen()
        elif item == "Back":
            self.in_options_menu = False
                
    def _start_game(self) -> None:
        """Start the game."""
        from scenes.game_scene import GameScene
        game_scene = GameScene(self.engine, "level01")
        self.engine.set_scene(game_scene)
        
    def _open_options(self) -> None:
        """Open options submenu."""
        self.in_options_menu = True
        self.options_selected_index = 0
        
    def _exit_game(self) -> None:
        """Exit the game."""
        self.engine.quit()
        
    def fixed_update(self, delta_time: float) -> None:
        pass
        
    def update(self, delta_time: float, alpha: float) -> None:
        pass
        
    def draw(self, surface: pygame.Surface) -> None:
        """Render menu to screen."""
        screen_w, screen_h = surface.get_size()
        
        # Draw background (scaled to fit)
        if self.background:
            scaled_bg = pygame.transform.scale(self.background, (screen_w, screen_h))
            surface.blit(scaled_bg, (0, 0))
        else:
            surface.fill((30, 30, 60))
        
        if self.in_options_menu:
            self._draw_options_menu(surface)
        else:
            self._draw_menu_options(surface)
    
    def _draw_options_menu(self, surface: pygame.Surface) -> None:
        """Draw options submenu."""
        if not self.font:
            return
        
        screen_w, screen_h = surface.get_size()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Draw title
        title_surf = self.title_font.render("OPTIONS", True, (0, 255, 255))
        title_rect = title_surf.get_rect(center=(screen_w // 2, screen_h // 3))
        surface.blit(title_surf, title_rect)
        
        # Draw options
        start_y = screen_h // 2
        for i, item in enumerate(self.options_menu_items):
            color = (255, 255, 0) if i == self.options_selected_index else (255, 255, 255)
            
            display_text = item
            if item == "Toggle Fullscreen":
                status = "ON" if self.engine.is_fullscreen() else "OFF"
                display_text = f"Fullscreen: {status}"
            
            text_surf = self.font.render(display_text, True, color)
            text_rect = text_surf.get_rect(center=(screen_w // 2, start_y + i * 60))
            surface.blit(text_surf, text_rect)
        
    def _draw_menu_options(self, surface: pygame.Surface) -> None:
        """Draw all menu options - NO TITLE, background has it!"""
        if not self.font:
            return
        
        screen_w, screen_h = surface.get_size()
        center_x = screen_w // 2
        start_y = screen_h // 2
        spacing = 60
        
        for i, option in enumerate(self.menu_options):
            color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            text_rect = text_surface.get_rect(center=(center_x, start_y + i * spacing))
            surface.blit(text_surface, text_rect)
            
    def cleanup(self) -> None:
        pass
