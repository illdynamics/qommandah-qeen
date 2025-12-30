import pygame
from typing import List, Optional, Tuple
from core.resources import ResourceManager
from shared.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_HEIGHT, HUD_MARGIN,
    HUD_FONT_SIZE, HUD_TEXT_COLOR, HUD_BG_COLOR,
    HUD_ICON_SIZE, HUD_FUEL_BAR_WIDTH, HUD_FUEL_BAR_HEIGHT,
    HUD_FUEL_FULL_COLOR, HUD_FUEL_LOW_COLOR,
    HUD_SCORE_LABEL, HUD_FUEL_LABEL, HUD_MODES_LABEL,
    HUD_PLAYER_STATE_LABEL, HUD_HEALTH_BAR_WIDTH, HUD_HEALTH_BAR_HEIGHT,
    HUD_HEALTH_FULL_COLOR, HUD_HEALTH_LOW_COLOR
)
from shared.types import PlayerState, WoNQModeType
from core.particles import ParticleSystem, Particle

class HUD:
    """Heads-Up Display for showing game status information."""
    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize the HUD.
        
        Args:
            resource_manager: Resource manager for loading fonts and images
        """
        self.resource_manager = resource_manager
        self.font = self._load_font()
        self.icons = self._load_icons()
        self.score = 0
        self.fuel = 0.0
        self.max_fuel = 100.0
        self.active_modes: List[str] = []
        self.player_state: Optional[PlayerState] = None
        self.health = 100
        self.max_health = 100
        self.particle_system = ParticleSystem()
        self.mode_effects: dict = {}
        self._initialize_mode_effects()

    def _load_font(self) -> pygame.font.Font:
        """Load the HUD font."""
        try:
            return self.resource_manager.get_font("default", HUD_FONT_SIZE)
        except KeyError:
            return pygame.font.Font(None, HUD_FONT_SIZE)

    def _load_icons(self) -> dict:
        """Load HUD icons from resources."""
        icons = {}
        # Load mode icons
        for mode_type in WoNQModeType:
            icon_name = f"icon_{mode_type.name.lower()}"
            try:
                icons[icon_name] = self.resource_manager.get_image(icon_name)
            except KeyError:
                # Create placeholder icon
                icons[icon_name] = pygame.Surface((HUD_ICON_SIZE, HUD_ICON_SIZE))
                icons[icon_name].fill((100, 100, 200))
        # Load player state icons
        for state in PlayerState:
            icon_name = f"icon_{state.name.lower()}"
            try:
                icons[icon_name] = self.resource_manager.get_image(icon_name)
            except KeyError:
                icons[icon_name] = pygame.Surface((HUD_ICON_SIZE, HUD_ICON_SIZE))
                icons[icon_name].fill((200, 100, 100))
        return icons

    def _initialize_mode_effects(self) -> None:
        """Initialize visual effects for different modes."""
        self.mode_effects = {
            "low_g": {"color": (100, 200, 255), "particle_type": "float"},
            "mirror": {"color": (255, 100, 200), "particle_type": "mirror"},
            "speedy_boots": {"color": (255, 200, 100), "particle_type": "speed"},
            "bullet": {"color": (200, 100, 255), "particle_type": "slow"},
            "junglist": {"color": (100, 255, 100), "particle_type": "beat"}
        }

    def update(self, score: int, fuel: float, max_fuel: float, 
               active_modes: List[str], player_state_name: Optional[str] = None,
               health: int = 100, max_health: int = 100) -> None:
        """
        Update HUD values.
        
        Args:
            score: Current score
            fuel: Current fuel amount
            max_fuel: Maximum fuel capacity
            active_modes: List of active mode names
            player_state_name: Current player state name (optional)
            health: Current health
            max_health: Maximum health
        """
        self.score = score
        self.fuel = fuel
        self.max_fuel = max_fuel
        self.active_modes = active_modes
        self.player_state_name = player_state_name
        self.health = health
        self.max_health = max_health
        
        # Update particle effects for active modes
        self._update_mode_particles()

    def _update_mode_particles(self) -> None:
        """Update particle effects for active modes."""
        self.particle_system.update()
        
        # Add particles for each active mode
        for mode in self.active_modes:
            if mode in self.mode_effects:
                effect = self.mode_effects[mode]
                # Create particles at random positions along top of HUD
                if pygame.time.get_ticks() % 30 == 0:  # Every 30ms
                    x = pygame.time.get_ticks() % SCREEN_WIDTH
                    y = HUD_HEIGHT // 2
                    self._create_mode_particle(x, y, effect)

    def _create_mode_particle(self, x: int, y: int, effect: dict) -> None:
        """Create a particle for mode visual effect."""
        color = effect["color"]
        particle_type = effect["particle_type"]
        
        if particle_type == "float":
            self.particle_system.create_smoke_emitter((x, y))
        elif particle_type == "beat":
            # Create pulsing particle for junglist mode
            self.particle_system.create_explosion((x, y))

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the HUD to the given surface.
        
        Args:
            surface: Pygame surface to render onto
        """
        # Draw HUD background
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT)
        pygame.draw.rect(surface, HUD_BG_COLOR, hud_rect)
        
        # Draw separator line
        pygame.draw.line(surface, (100, 100, 100), (0, HUD_HEIGHT), 
                        (SCREEN_WIDTH, HUD_HEIGHT), 2)
        
        # Calculate positions for HUD elements
        x_pos = HUD_MARGIN
        y_pos = HUD_MARGIN
        
        # Render score
        self._render_score(surface, x_pos, y_pos)
        x_pos += 150
        
        # Render health bar
        self._render_health_bar(surface, x_pos, y_pos)
        x_pos += HUD_HEALTH_BAR_WIDTH + HUD_MARGIN
        
        # Render fuel gauge
        self._render_fuel_gauge(surface, x_pos, y_pos)
        x_pos += HUD_FUEL_BAR_WIDTH + HUD_MARGIN
        
        # Render player state
        if self.player_state_name:
            self._render_player_state(surface, x_pos, y_pos)
            x_pos += 120
        
        # Render active modes
        self._render_active_modes(surface, x_pos, y_pos)
        
        # Render particle effects
        self.particle_system.render(surface, (0, 0))

    def _render_score(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render the score display."""
        score_text = f"{HUD_SCORE_LABEL}: {self.score}"
        score_surface = self.font.render(score_text, True, HUD_TEXT_COLOR)
        surface.blit(score_surface, (x, y))
        
        # Add subtle glow effect for high scores
        if self.score > 1000:
            glow_surface = self.font.render(score_text, True, (255, 255, 100))
            surface.blit(glow_surface, (x + 1, y + 1))

    def _render_health_bar(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render health bar."""
        # Draw background
        bg_rect = pygame.Rect(x, y, HUD_HEALTH_BAR_WIDTH, HUD_HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect)
        
        # Calculate health percentage
        health_percent = self.health / self.max_health
        health_width = int(HUD_HEALTH_BAR_WIDTH * health_percent)
        
        # Choose color based on health
        if health_percent > 0.5:
            health_color = HUD_HEALTH_FULL_COLOR
        elif health_percent > 0.25:
            health_color = (255, 200, 0)  # Yellow for medium health
        else:
            health_color = HUD_HEALTH_LOW_COLOR
            
        # Draw health bar
        health_rect = pygame.Rect(x, y, health_width, HUD_HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, health_color, health_rect)
        
        # Draw border
        pygame.draw.rect(surface, HUD_TEXT_COLOR, bg_rect, 1)
        
        # Draw health text
        health_text = f"{self.health}/{self.max_health}"
        text_surface = self.font.render(health_text, True, HUD_TEXT_COLOR)
        text_x = x + (HUD_HEALTH_BAR_WIDTH - text_surface.get_width()) // 2
        text_y = y + (HUD_HEALTH_BAR_HEIGHT - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

    def _render_fuel_gauge(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render the fuel gauge."""
        # Draw background
        bg_rect = pygame.Rect(x, y, HUD_FUEL_BAR_WIDTH, HUD_FUEL_BAR_HEIGHT)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect)
        
        # Calculate fuel percentage
        fuel_percent = self.fuel / self.max_fuel if self.max_fuel > 0 else 0
        fuel_width = int(HUD_FUEL_BAR_WIDTH * fuel_percent)
        
        # Choose color based on fuel level
        fuel_color = HUD_FUEL_FULL_COLOR if fuel_percent > 0.3 else HUD_FUEL_LOW_COLOR
        
        # Draw fuel bar
        fuel_rect = pygame.Rect(x, y, fuel_width, HUD_FUEL_BAR_HEIGHT)
        pygame.draw.rect(surface, fuel_color, fuel_rect)
        
        # Add gradient effect
        for i in range(fuel_width):
            alpha = int(255 * (i / fuel_width)) if fuel_width > 0 else 0
            gradient_rect = pygame.Rect(x + i, y, 1, HUD_FUEL_BAR_HEIGHT)
            gradient_color = (
                min(255, fuel_color[0] + alpha // 3),
                min(255, fuel_color[1] + alpha // 3),
                min(255, fuel_color[2] + alpha // 3)
            )
            pygame.draw.rect(surface, gradient_color, gradient_rect)
        
        # Draw border
        pygame.draw.rect(surface, HUD_TEXT_COLOR, bg_rect, 1)
        
        # Draw fuel text
        fuel_text = f"{HUD_FUEL_LABEL}: {int(self.fuel)}/{int(self.max_fuel)}"
        text_surface = self.font.render(fuel_text, True, HUD_TEXT_COLOR)
        text_x = x + (HUD_FUEL_BAR_WIDTH - text_surface.get_width()) // 2
        text_y = y + (HUD_FUEL_BAR_HEIGHT - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

    def _render_player_state(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render player state information."""
        if not self.player_state_name:
            return
            
        state_name = self.player_state_name.replace("_", " ").title()
        state_text = f"{HUD_PLAYER_STATE_LABEL}: {state_name}"
        text_surface = self.font.render(state_text, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (x, y))
        
        # Draw state icon if available
        icon_name = f"icon_{self.player_state_name.lower()}"
        if icon_name in self.icons:
            icon = self.icons[icon_name]
            icon_y = y + text_surface.get_height() + 5
            surface.blit(icon, (x, icon_y))

    def _render_active_modes(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render active modes display."""
        if not self.active_modes:
            return
            
        modes_text = f"{HUD_MODES_LABEL}:"
        text_surface = self.font.render(modes_text, True, HUD_TEXT_COLOR)
        surface.blit(text_surface, (x, y))
        
        # Render mode icons
        icon_y = y + text_surface.get_height() + 5
        icon_x = x
        
        for mode in self.active_modes:
            icon_name = f"icon_{mode.lower()}"
            if icon_name in self.icons:
                icon = self.icons[icon_name]
                # Apply visual effect based on mode
                if mode in self.mode_effects:
                    effect_color = self.mode_effects[mode]["color"]
                    # Create a colored overlay for the icon
                    overlay = pygame.Surface((HUD_ICON_SIZE, HUD_ICON_SIZE), pygame.SRCALPHA)
                    overlay.fill((*effect_color, 100))
                    icon_copy = icon.copy()
                    icon_copy.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    surface.blit(icon_copy, (icon_x, icon_y))
                else:
                    surface.blit(icon, (icon_x, icon_y))
                
                # Add pulsing effect for active modes
                pulse = (pygame.time.get_ticks() % 1000) / 1000
                pulse_alpha = int(100 + 155 * abs(pulse - 0.5))
                pulse_surface = pygame.Surface((HUD_ICON_SIZE, HUD_ICON_SIZE), pygame.SRCALPHA)
                pulse_surface.fill((255, 255, 255, pulse_alpha))
                surface.blit(pulse_surface, (icon_x, icon_y), special_flags=pygame.BLEND_RGBA_ADD)
                
                icon_x += HUD_ICON_SIZE + 5

    def get_height(self) -> int:
        """Get the height of the HUD."""
        return HUD_HEIGHT

    def clear(self) -> None:
        """Clear all HUD values."""
        self.score = 0
        self.fuel = 0.0
        self.max_fuel = 100.0
        self.active_modes = []
        self.player_state = None
        self.health = 100
        self.max_health = 100
        self.particle_system.clear_all()