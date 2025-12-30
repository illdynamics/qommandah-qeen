import pygame
from typing import Optional, Callable
from core.engine import Engine
from core.resources import ResourceManager


# Define colors locally to avoid import issues
COLORS = {
    "WHITE": (255, 255, 255),
    "YELLOW": (255, 220, 0),
    "BLACK": (0, 0, 0),
    "GRAY": (128, 128, 128)
}


class PauseMenu:
    """Pause menu overlay that appears during gameplay."""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.resource_manager = ResourceManager()
        self.visible = False
        self.selected_index = 0
        self.options = ["Resume", "Restart", "Main Menu"]
        self.option_callbacks = {
            0: self.resume_game,
            1: self.restart_game,
            2: self.return_to_main_menu
        }
        self.option_positions = []
        self.font = None
        self.title_font = None
        self.overlay_surface = None
        self.title_text = "PAUSED"
        self.option_height = 50
        self.title_margin = 80
        self.option_spacing = 60
        self.initialized = False
        
    def initialize(self) -> None:
        if self.initialized:
            return
        self._setup_fonts()
        self.initialized = True
        
    def _setup_fonts(self) -> None:
        try:
            self.font = pygame.font.SysFont(None, 36)
            self.title_font = pygame.font.SysFont(None, 64)
        except Exception:
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 64)
            
    def _create_overlay(self, screen_width: int, screen_height: int) -> pygame.Surface:
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        return overlay
        
    def _calculate_option_positions(self, screen_width: int, screen_height: int) -> list:
        screen_center_x = screen_width // 2
        screen_center_y = screen_height // 2
        
        total_height = len(self.options) * self.option_spacing
        start_y = screen_center_y - (total_height // 2) + self.title_margin
        
        positions = []
        for i in range(len(self.options)):
            y_pos = start_y + (i * self.option_spacing)
            positions.append((screen_center_x, y_pos))
        return positions
            
    def show(self) -> None:
        if not self.initialized:
            self.initialize()
        self.visible = True
        self.selected_index = 0
        
    def hide(self) -> None:
        self.visible = False
        
    def toggle(self) -> None:
        if self.visible:
            self.hide()
        else:
            self.show()
            
    def is_paused(self) -> bool:
        return self.visible
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.resume_game()
                return True
            elif event.key == pygame.K_UP:
                self._move_selection(-1)
                return True
            elif event.key == pygame.K_DOWN:
                self._move_selection(1)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._select_option()
                return True
                
        return False
        
    def _move_selection(self, direction: int) -> None:
        self.selected_index = (self.selected_index + direction) % len(self.options)
            
    def _select_option(self) -> None:
        callback = self.option_callbacks.get(self.selected_index)
        if callback:
            callback()
            
    def resume_game(self) -> None:
        self.hide()
        
    def restart_game(self) -> None:
        self.hide()
        print("Restart game requested")
        
    def return_to_main_menu(self) -> None:
        self.hide()
        print("Return to main menu requested")
        
    def update(self, dt: float) -> None:
        pass
        
    def render(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.initialized:
            return
        
        screen_width = surface.get_width()
        screen_height = surface.get_height()
            
        # Draw overlay
        overlay = self._create_overlay(screen_width, screen_height)
        surface.blit(overlay, (0, 0))
        
        # Calculate positions dynamically
        option_positions = self._calculate_option_positions(screen_width, screen_height)
        
        # Draw title
        if self.title_font:
            title_surface = self.title_font.render(self.title_text, True, COLORS["WHITE"])
            title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
            surface.blit(title_surface, title_rect)
            
        # Draw options
        for i, (option_text, (x, y)) in enumerate(zip(self.options, option_positions)):
            if self.font:
                color = COLORS["YELLOW"] if i == self.selected_index else COLORS["WHITE"]
                option_surface = self.font.render(option_text, True, color)
                option_rect = option_surface.get_rect(center=(x, y))
                surface.blit(option_surface, option_rect)
                
                # Draw selection indicators
                if i == self.selected_index:
                    indicator_left = pygame.Rect(x - 120, y - 2, 20, 4)
                    indicator_right = pygame.Rect(x + 100, y - 2, 20, 4)
                    pygame.draw.rect(surface, COLORS["YELLOW"], indicator_left)
                    pygame.draw.rect(surface, COLORS["YELLOW"], indicator_right)
