"""
Tile system for parsing and managing tile data.
Handles tile definitions, collisions, and rendering properties.
"""

from typing import Dict, List, Tuple, Optional, Any
from shared.types import Vector2
import pygame
import random
from enum import Enum
from core.resources import ResourceManager
from shared.constants import TILE_SIZE


class TileType(Enum):
    EMPTY = 0
    SOLID = 1


class TileSet:
    """Represents a tileset with sprite extraction."""
    
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.tiles: Dict[int, Dict[str, Any]] = {}
        self.collision_regions: List[Tuple[int, int, int, int]] = []
        self.section_regions: Dict[str, Tuple[int, int, int, int]] = {}
        
    def parse_section_region(self, section_data: Dict[str, Any]) -> None:
        section_id = section_data.get("id", "")
        x = section_data.get("x", 0)
        y = section_data.get("y", 0)
        width = section_data.get("width", 0)
        height = section_data.get("height", 0)
        self.section_regions[section_id] = (x, y, width, height)
        
    def add_tile(self, tile_id: int, properties: Dict[str, Any]) -> None:
        self.tiles[tile_id] = {
            "id": tile_id,
            "collidable": properties.get("collidable", False),
            "texture": properties.get("texture", None),
            "damage": properties.get("damage", 0),
            "friction": properties.get("friction", 0.8),
            "properties": properties.copy()
        }
        
    def get_tile_properties(self, tile_id: int) -> Optional[Dict[str, Any]]:
        return self.tiles.get(tile_id)
    
    def is_tile_collidable(self, tile_id: int) -> bool:
        tile_props = self.get_tile_properties(tile_id)
        if not tile_props:
            # Default: tiles with id > 0 are solid
            return tile_id > 0
        return tile_props.get("collidable", False)
    
    def get_tile_friction(self, tile_id: int) -> float:
        tile_props = self.get_tile_properties(tile_id)
        if not tile_props:
            return 0.8
        return tile_props.get("friction", 0.8)
    
    def add_collision_region(self, x: int, y: int, width: int, height: int) -> None:
        self.collision_regions.append((x, y, width, height))
        
    def check_collision(self, position: Vector2, size: Vector2) -> bool:
        rect1 = pygame.Rect(int(position.x), int(position.y), int(size.x), int(size.y))
        for region in self.collision_regions:
            rect2 = pygame.Rect(*region)
            if rect1.colliderect(rect2):
                return True
        return False
    
    def get_tile_at_position(self, position: Vector2, tilemap: List[List[int]]) -> Optional[int]:
        if not tilemap:
            return None
        tile_x = int(position.x) // self.tile_size
        tile_y = int(position.y) // self.tile_size
        if (0 <= tile_y < len(tilemap) and 0 <= tile_x < len(tilemap[tile_y])):
            return tilemap[tile_y][tile_x]
        return None
    
    def clear(self) -> None:
        self.tiles.clear()
        self.collision_regions.clear()
        self.section_regions.clear()


class TileManager:
    def __init__(self, resource_manager: ResourceManager):
        self.resource_manager = resource_manager
        self.tileset = None
        self.tile_data = []
        self.width = 0
        self.height = 0
        self.tile_size = TILE_SIZE

    def load_tiles(self, tile_data: list, tileset_name: str = "tilesets"):
        self.tile_data = tile_data
        self.width = len(tile_data[0]) if tile_data and tile_data[0] else 0
        self.height = len(tile_data)
        
        # Try to load tileset sprite sheet - use objects-tilesets (64x64 grid)
        tileset_files = [
            "qq-objects-tilesets.png",  # Main tileset (512x512 = 8x8 grid of 64x64)
            "qq-tilesets-simple.png",   # Fallback simple tiles
            "qq-tilesets.png"           # Original fallback
        ]
        
        self.tileset = None
        for tileset_file in tileset_files:
            try:
                # Use 64x64 for tilesets (they get scaled to 32x32 for rendering)
                self.tileset = self.resource_manager.load_sprite_sheet(
                    tileset_name, tileset_file, 64, 64
                )
                print(f"Loaded tileset: {tileset_file}")
                break
            except Exception as e:
                continue
        
        if not self.tileset:
            print("Warning: No tileset loaded, using colored fallback")

    def get_tile(self, x: int, y: int) -> int:
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.tile_data[y][x]
        return 0
    
    def is_solid(self, x: int, y: int) -> bool:
        """Check if tile at grid position is solid."""
        tile_id = self.get_tile(x, y)
        return tile_id > 0  # All non-zero tiles are solid
    
    def is_solid_at_pixel(self, px: float, py: float) -> bool:
        """Check if position in pixels is solid."""
        grid_x = int(px // self.tile_size)
        grid_y = int(py // self.tile_size)
        return self.is_solid(grid_x, grid_y)

    def render(self, surface: pygame.Surface, camera_offset):
        # Handle both tuple and Vector2
        if hasattr(camera_offset, 'x'):
            cam_x, cam_y = camera_offset.x, camera_offset.y
        else:
            cam_x, cam_y = camera_offset[0], camera_offset[1]
        
        start_col = max(0, int(cam_x // self.tile_size))
        start_row = max(0, int(cam_y // self.tile_size))
        end_col = min(self.width, start_col + (surface.get_width() // self.tile_size) + 2)
        end_row = min(self.height, start_row + (surface.get_height() // self.tile_size) + 2)

        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                if 0 <= y < self.height and 0 <= x < self.width:
                    tile_id = self.tile_data[y][x]
                    if tile_id > 0:
                        screen_x = int(x * self.tile_size - cam_x)
                        screen_y = int(y * self.tile_size - cam_y)
                        
                        # Try sprite from tileset first
                        rendered = False
                        if self.tileset:
                            try:
                                sprite = self.tileset.get_sprite_by_index(tile_id - 1)
                                if sprite:
                                    # Scale 64x64 sprite to 32x32 tile size
                                    if sprite.get_width() != self.tile_size:
                                        sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
                                    surface.blit(sprite, (screen_x, screen_y))
                                    rendered = True
                            except (IndexError, Exception):
                                pass
                        
                        # Fallback to colored rectangle with texture
                        if not rendered:
                            # Pick color based on tile_id
                            base_colors = {
                                1: (100, 80, 60),    # Brown rock
                                2: (70, 70, 85),     # Gray stone
                                3: (80, 130, 50),    # Green (grass top)
                                4: (130, 100, 60),   # Tan (dirt)
                                5: (50, 50, 70),     # Dark stone
                            }
                            color = base_colors.get(tile_id, (100, 80, 60))
                            
                            rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                            pygame.draw.rect(surface, color, rect)
                            
                            # Add simple texture pattern
                            highlight = tuple(min(255, c + 20) for c in color)
                            shadow = tuple(max(0, c - 30) for c in color)
                            
                            # Top and left edges lighter
                            pygame.draw.line(surface, highlight, (screen_x, screen_y), (screen_x + self.tile_size - 1, screen_y))
                            pygame.draw.line(surface, highlight, (screen_x, screen_y), (screen_x, screen_y + self.tile_size - 1))
                            
                            # Bottom and right edges darker  
                            pygame.draw.line(surface, shadow, (screen_x, screen_y + self.tile_size - 1), (screen_x + self.tile_size - 1, screen_y + self.tile_size - 1))
                            pygame.draw.line(surface, shadow, (screen_x + self.tile_size - 1, screen_y), (screen_x + self.tile_size - 1, screen_y + self.tile_size - 1))
                            
                            # Add some noise dots for texture
                            random.seed(x * 1000 + y)  # Consistent per tile
                            for _ in range(5):
                                px = screen_x + random.randint(4, self.tile_size - 4)
                                py = screen_y + random.randint(4, self.tile_size - 4)
                                pygame.draw.circle(surface, shadow, (px, py), 1)

    def clear(self) -> None:
        self.tile_data = []
        self.tileset = None
        self.width = 0
        self.height = 0
