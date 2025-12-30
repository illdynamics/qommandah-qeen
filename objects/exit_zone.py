import pygame
from typing import Optional, Callable
from world.entities import Entity
from shared.constants import EXIT_ZONE_COLOR

class ExitZone(Entity):
    """Invisible trigger zone for level exit."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 zone_id: Optional[str] = None,
                 on_exit: Optional[Callable] = None):
        """Initialize exit zone.
        
        Args:
            x: X position
            y: Y position
            width: Zone width
            height: Zone height
            zone_id: Optional unique identifier
            on_exit: Optional callback when player exits
        """
        super().__init__((x, y), (width, height))
        self.zone_id = zone_id or f"exit_zone_{x}_{y}"
        self.on_exit = on_exit
        self.player_inside = False
        self.exit_triggered = False
        self.debug_visible = False
        self.permanent_visible = False
        
    def update(self, dt: float) -> None:
        """Update exit zone state."""
        pass  # No update logic needed for static zone
    
    def render(self, surface: pygame.Surface, camera_offset: tuple) -> None:
        """Render exit zone (only visible in debug mode).
        
        Args:
            surface: Pygame surface to render to
            camera_offset: Camera offset (x, y)
        """
        if self.debug_visible or self.permanent_visible:
            x = int(self.position[0] - camera_offset[0])
            y = int(self.position[1] - camera_offset[1])
            width = int(self.size[0])
            height = int(self.size[1])
            
            # Draw semi-transparent rectangle
            debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            debug_surface.fill((*EXIT_ZONE_COLOR, 128))  # 50% alpha
            surface.blit(debug_surface, (x, y))
            
            # Draw border
            pygame.draw.rect(surface, EXIT_ZONE_COLOR, (x, y, width, height), 2)
            
            # Draw "EXIT" text in center
            font = pygame.font.Font(None, 20)
            text = font.render("EXIT", True, EXIT_ZONE_COLOR)
            text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
            surface.blit(text, text_rect)
    
    def check_player_inside(self, player_rect: pygame.Rect) -> bool:
        """Check if player is inside exit zone.
        
        Args:
            player_rect: Player's rectangle
            
        Returns:
            True if player is inside, False otherwise
        """
        zone_rect = pygame.Rect(self.position[0], self.position[1], 
                               self.size[0], self.size[1])
        self.player_inside = zone_rect.colliderect(player_rect)
        return self.player_inside
    
    def trigger_exit(self) -> bool:
        """Trigger exit sequence.
        
        Returns:
            True if exit was triggered, False if already triggered
        """
        if not self.exit_triggered:
            self.exit_triggered = True
            if self.on_exit:
                self.on_exit()
            return True
        return False
    
    def reset(self) -> None:
        """Reset exit zone to initial state."""
        self.player_inside = False
        self.exit_triggered = False
    
    def set_debug_visible(self, visible: bool) -> None:
        """Set debug visibility.
        
        Args:
            visible: True to make visible in debug mode
        """
        self.debug_visible = visible
    
    def set_visible(self, visible: bool) -> None:
        """Set permanent visibility.
        
        Args:
            visible: True to make always visible
        """
        self.permanent_visible = visible
    
    def get_zone_id(self) -> str:
        """Get zone identifier.
        
        Returns:
            Zone ID string
        """
        return self.zone_id
    
    def is_player_inside(self) -> bool:
        """Check if player is currently inside zone.
        
        Returns:
            True if player inside, False otherwise
        """
        return self.player_inside
    
    def is_exit_triggered(self) -> bool:
        """Check if exit has been triggered.
        
        Returns:
            True if exit triggered, False otherwise
        """
        return self.exit_triggered
    
    def set_exit_callback(self, callback: Callable) -> None:
        """Set callback for when player exits.
        
        Args:
            callback: Function to call on exit
        """
        self.on_exit = callback