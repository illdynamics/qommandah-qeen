"""
QommandahQeen HUD - Sprite-based UI elements
Health bar (10 steps), Key indicator, Powerup bars (5 segments each)
"""
import pygame
import os
from typing import List, Optional, Tuple
from core.resources import ResourceManager
from shared.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH, POWERUP_DURATION, POWERUP_BAR_SEGMENTS
)
from shared.types import PlayerState, PowerupType


class HUD:
    """Heads-Up Display with sprite-based UI elements."""
    
    def __init__(self, resource_manager: ResourceManager):
        """Initialize the HUD with sprite assets."""
        self.resource_manager = resource_manager
        
        # State
        self.score = 0
        self.health = 10
        self.max_health = 10
        self.has_key = False
        self.jettpaq_remaining = 0.0  # Seconds remaining
        self.jumpupstiq_remaining = 0.0  # Seconds remaining
        self.player_state_name = "Normal"
        self.active_modes: List[str] = []
        
        # Load sprite assets
        self._health_frames: List[pygame.Surface] = []
        self._key_icon: Optional[pygame.Surface] = None
        self._key_empty: Optional[pygame.Surface] = None
        self._jettpaq_frames: List[pygame.Surface] = []
        self._jumpupstiq_frames: List[pygame.Surface] = []
        
        self._load_sprites()
        self._load_font()
    
    def _load_font(self) -> None:
        """Load the HUD font."""
        try:
            self.font = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        except:
            self.font = pygame.font.SysFont("arial", 24)
            self.font_small = pygame.font.SysFont("arial", 18)
    
    def _load_sprites(self) -> None:
        """Load all HUD sprite sheets."""
        # Load health UI - 512x384, 4x3 grid of 128x128 = 12 frames
        # We'll use frames 0-10 for health states (10 = full, 0 = empty)
        health_path = os.path.join(ASSETS_PATH, "qq-health-ui.png")
        if os.path.exists(health_path):
            health_sheet = pygame.image.load(health_path).convert_alpha()
            for row in range(3):
                for col in range(4):
                    x, y = col * 128, row * 128
                    frame = pygame.Surface((128, 128), pygame.SRCALPHA)
                    frame.blit(health_sheet, (0, 0), (x, y, 128, 128))
                    # Scale down for HUD
                    frame = pygame.transform.scale(frame, (48, 48))
                    self._health_frames.append(frame)
            print(f"Loaded health UI: {len(self._health_frames)} frames")
        
        # Load key UI - 256x192, 4x3 grid of 64x64
        # Row 2 has the key UI icons (cells 0-3)
        key_path = os.path.join(ASSETS_PATH, "qq-key-object.png")
        if os.path.exists(key_path):
            key_sheet = pygame.image.load(key_path).convert_alpha()
            # Key icon (when player has key) - cell (1,0) or (2,0)
            key_frame = pygame.Surface((64, 64), pygame.SRCALPHA)
            key_frame.blit(key_sheet, (0, 0), (64, 0, 64, 64))
            self._key_icon = pygame.transform.scale(key_frame, (32, 32))
            # Empty key slot - cell (0,2) or just create a dim version
            empty_frame = pygame.Surface((64, 64), pygame.SRCALPHA)
            empty_frame.blit(key_sheet, (0, 0), (0, 128, 64, 64))
            self._key_empty = pygame.transform.scale(empty_frame, (32, 32))
            print("Loaded key UI sprites")
        
        # Load powerups UI - 512x384, 4x3 grid of 128x128 = 12 frames
        # Row 0: JettPaq bars (5 states + empty = 6 frames: cols 0-3 row 0, cols 0-1 row 1)
        # Row 1-2: Jumpupstiq bars (5 states + empty = 6 frames)
        powerups_path = os.path.join(ASSETS_PATH, "qq-powerups-ui.png")
        if os.path.exists(powerups_path):
            powerups_sheet = pygame.image.load(powerups_path).convert_alpha()
            
            # Load JettPaq frames (first 6 cells: row 0 cols 0-3, row 1 cols 0-1)
            for i in range(6):
                row = i // 4
                col = i % 4
                x, y = col * 128, row * 128
                frame = pygame.Surface((128, 128), pygame.SRCALPHA)
                frame.blit(powerups_sheet, (0, 0), (x, y, 128, 128))
                frame = pygame.transform.scale(frame, (48, 48))
                self._jettpaq_frames.append(frame)
            
            # Load Jumpupstiq frames (next 6 cells: row 1 cols 2-3, row 2 cols 0-3)
            indices = [(1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3)]
            for row, col in indices:
                x, y = col * 128, row * 128
                frame = pygame.Surface((128, 128), pygame.SRCALPHA)
                frame.blit(powerups_sheet, (0, 0), (x, y, 128, 128))
                frame = pygame.transform.scale(frame, (48, 48))
                self._jumpupstiq_frames.append(frame)
            
            print(f"Loaded powerup UI: {len(self._jettpaq_frames)} jettpaq, {len(self._jumpupstiq_frames)} jumpupstiq")
    
    def update(self, score: int, health: int, max_health: int,
               active_modes: List[str], player_state_name: Optional[str] = None,
               has_key: bool = False, jettpaq_remaining: float = 0.0,
               jumpupstiq_remaining: float = 0.0) -> None:
        """Update HUD values."""
        self.score = score
        self.health = health
        self.max_health = max_health
        self.active_modes = active_modes
        self.player_state_name = player_state_name or "Normal"
        self.has_key = has_key
        self.jettpaq_remaining = jettpaq_remaining
        self.jumpupstiq_remaining = jumpupstiq_remaining
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the HUD to the given surface."""
        # Draw semi-transparent background
        hud_bg = pygame.Surface((SCREEN_WIDTH, 70), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 180))
        surface.blit(hud_bg, (0, 0))
        
        # Render health bar (top left)
        self._render_health(surface, 10, 10)
        
        # Render score (next to health)
        self._render_score(surface, 70, 15)
        
        # Render key indicator (after score)
        self._render_key(surface, 200, 15)
        
        # Render powerup bars if active (right side)
        x_pos = SCREEN_WIDTH - 60
        if self.jettpaq_remaining > 0:
            self._render_powerup_bar(surface, x_pos, 10, "jettpaq", self.jettpaq_remaining)
            x_pos -= 55
        if self.jumpupstiq_remaining > 0:
            self._render_powerup_bar(surface, x_pos, 10, "jumpupstiq", self.jumpupstiq_remaining)
        
        # Render player state (center-right)
        self._render_state(surface, SCREEN_WIDTH - 200, 45)
    
    def _render_health(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render health bar using sprite frames."""
        if not self._health_frames:
            # Fallback to simple bar
            pygame.draw.rect(surface, (255, 0, 0), (x, y, 50, 10))
            health_width = int(50 * (self.health / self.max_health))
            pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, 10))
            return
        
        # Select frame based on health (0 = empty, max = full)
        # With 10 health bars, frame index = health (0-10)
        frame_idx = min(self.health, len(self._health_frames) - 1)
        frame_idx = max(0, frame_idx)
        
        if frame_idx < len(self._health_frames):
            surface.blit(self._health_frames[frame_idx], (x, y))
    
    def _render_score(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render score display."""
        score_text = f"SCORE:: {self.score}"
        text_surface = self.font.render(score_text, True, (255, 255, 255))
        surface.blit(text_surface, (x, y))
    
    def _render_key(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render key indicator."""
        if self.has_key and self._key_icon:
            surface.blit(self._key_icon, (x, y))
        elif self._key_empty:
            # Draw dimmed key slot
            surface.blit(self._key_empty, (x, y))
    
    def _render_powerup_bar(self, surface: pygame.Surface, x: int, y: int,
                           powerup_type: str, remaining: float) -> None:
        """Render powerup bar with segments."""
        # Calculate which segment (0-5, where 5 = full, 0 = empty)
        # POWERUP_DURATION = 120 seconds, 5 segments = 24 seconds each
        segment_duration = POWERUP_DURATION / POWERUP_BAR_SEGMENTS
        segments_remaining = int(remaining / segment_duration)
        segments_remaining = min(POWERUP_BAR_SEGMENTS, max(0, segments_remaining))
        
        frames = self._jettpaq_frames if powerup_type == "jettpaq" else self._jumpupstiq_frames
        
        if frames and segments_remaining < len(frames):
            # Frame 0 = empty, Frame 5 = full
            # So we use frame index = segments_remaining
            surface.blit(frames[segments_remaining], (x, y))
        else:
            # Fallback: draw simple bar
            bar_width = 48
            bar_height = 48
            pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height))
            fill_height = int(bar_height * (remaining / POWERUP_DURATION))
            color = (0, 200, 255) if powerup_type == "jettpaq" else (255, 200, 0)
            pygame.draw.rect(surface, color, (x, y + bar_height - fill_height, bar_width, fill_height))
    
    def _render_state(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Render player state name."""
        state_text = f"STATE:: {self.player_state_name}"
        text_surface = self.font_small.render(state_text, True, (200, 200, 200))
        surface.blit(text_surface, (x, y))
    
    def get_height(self) -> int:
        """Get the height of the HUD."""
        return 70
    
    def clear(self) -> None:
        """Clear all HUD values."""
        self.score = 0
        self.health = 10
        self.max_health = 10
        self.has_key = False
        self.jettpaq_remaining = 0.0
        self.jumpupstiq_remaining = 0.0
        self.active_modes = []
        self.player_state_name = "Normal"
