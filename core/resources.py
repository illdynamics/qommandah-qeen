"""
Resource management system for loading and caching game assets.
Handles sprite sheets, animations, and other game resources.
"""

import pygame
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from shared.constants import ASSETS_PATH, SPRITE_SIZE, ANIMATION_FPS
from shared.exceptions import ResourceLoadError


class SpriteSheet:
    """Represents a sprite sheet image with grid-based sprite extraction."""
    
    def __init__(self, filename: str, sprite_width: int = SPRITE_SIZE, sprite_height: int = SPRITE_SIZE):
        """
        Initialize a sprite sheet from an image file.
        
        Args:
            filename: Path to the sprite sheet image
            sprite_width: Width of individual sprites
            sprite_height: Height of individual sprites
        """
        self.filename = filename
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        
        try:
            full_path = os.path.join(ASSETS_PATH, filename)
            self.sheet = pygame.image.load(full_path).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            raise ResourceLoadError(f"Failed to load sprite sheet: {filename}") from e
        
        self.sheet_width = self.sheet.get_width()
        self.sheet_height = self.sheet.get_height()
        self.columns = self.sheet_width // sprite_width
        self.rows = self.sheet_height // sprite_height
        self.total_sprites = self.columns * self.rows
        
        # Cache for extracted sprites
        self._sprite_cache: Dict[Tuple[int, int], pygame.Surface] = {}
    
    def get_sprite(self, x: int, y: int) -> pygame.Surface:
        """
        Extract a single sprite from the sheet by grid coordinates.
        
        Args:
            x: Column index (0-based)
            y: Row index (0-based)
            
        Returns:
            pygame.Surface containing the sprite
        """
        cache_key = (x, y)
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        
        # Validate coordinates
        if x < 0 or x >= self.columns or y < 0 or y >= self.rows:
            raise ValueError(f"Sprite coordinates out of bounds: ({x}, {y})")
        
        # Extract sprite
        rect = pygame.Rect(
            x * self.sprite_width,
            y * self.sprite_height,
            self.sprite_width,
            self.sprite_height
        )
        sprite = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), rect)
        
        # Set pure black as transparent (colorkey)
        sprite.set_colorkey((0, 0, 0))
        
        self._sprite_cache[cache_key] = sprite
        return sprite
    
    def get_sprite_by_index(self, index: int) -> pygame.Surface:
        """
        Extract a sprite by linear index (row-major order).
        
        Args:
            index: Linear sprite index (0-based)
            
        Returns:
            pygame.Surface containing the sprite
        """
        x = index % self.columns
        y = index // self.columns
        return self.get_sprite(x, y)
    
    def get_sprites_in_row(self, row: int) -> List[pygame.Surface]:
        """
        Get all sprites in a specific row.
        
        Args:
            row: Row index (0-based)
            
        Returns:
            List of sprite surfaces
        """
        return [self.get_sprite(col, row) for col in range(self.columns)]
    
    def get_sprites_in_column(self, column: int) -> List[pygame.Surface]:
        """
        Get all sprites in a specific column.
        
        Args:
            column: Column index (0-based)
            
        Returns:
            List of sprite surfaces
        """
        return [self.get_sprite(column, row) for row in range(self.rows)]


class Animation:
    """Manages animation sequences with timing and frame cycling."""
    
    def __init__(self, frames: List[pygame.Surface], fps: float = ANIMATION_FPS, loop: bool = True):
        """
        Initialize an animation with frames and timing.
        
        Args:
            frames: List of sprite surfaces for the animation
            fps: Frames per second for animation speed
            loop: Whether the animation should loop
        """
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.frame_count = len(frames)
        
        if self.frame_count == 0:
            raise ValueError("Animation must have at least one frame")
        
        self.frame_duration = 1.0 / fps if fps > 0 else 0
        self.current_frame_index = 0
        self.current_time = 0.0
        self.is_playing = True
        self.is_finished = False
    
    def update(self, delta_time: float):
        """
        Update animation timing and advance frames.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.is_playing or self.is_finished:
            return
        
        self.current_time += delta_time
        
        # Calculate how many frames to advance
        frames_to_advance = int(self.current_time / self.frame_duration)
        if frames_to_advance > 0:
            self.current_time -= frames_to_advance * self.frame_duration
            self.current_frame_index += frames_to_advance
            
            if self.loop:
                self.current_frame_index %= self.frame_count
            else:
                if self.current_frame_index >= self.frame_count:
                    self.current_frame_index = self.frame_count - 1
                    self.is_finished = True
    
    def get_current_frame(self) -> pygame.Surface:
        """
        Get the current frame of the animation.
        
        Returns:
            Current sprite surface
        """
        return self.frames[self.current_frame_index]
    
    def reset(self):
        """Reset animation to initial state."""
        self.current_frame_index = 0
        self.current_time = 0.0
        self.is_finished = False
        self.is_playing = True
    
    def pause(self):
        """Pause the animation."""
        self.is_playing = False
    
    def play(self):
        """Play or resume the animation."""
        self.is_playing = True
    
    def set_fps(self, fps: float):
        """
        Change animation speed.
        
        Args:
            fps: New frames per second
        """
        self.fps = max(0.1, fps)  # Prevent division by zero
        self.frame_duration = 1.0 / self.fps if self.fps > 0 else 0


class ResourceManager:
    """Singleton manager for loading and caching game resources."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.sprite_sheets: Dict[str, SpriteSheet] = {}
        self.animations: Dict[str, Animation] = {}
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[Tuple[str, int], pygame.font.Font] = {}
        self.data_files: Dict[str, Any] = {}
        
        self._initialized = True
    
    def load_sprite_sheet(self, name: str, filename: str, sprite_width: int = SPRITE_SIZE, sprite_height: int = SPRITE_SIZE) -> SpriteSheet:
        """
        Load and cache a sprite sheet.
        
        Args:
            name: Unique identifier for the sprite sheet
            filename: Path to the sprite sheet image
            sprite_width: Width of individual sprites
            sprite_height: Height of individual sprites
            
        Returns:
            Loaded SpriteSheet instance
        """
        if name in self.sprite_sheets:
            return self.sprite_sheets[name]
        
        try:
            sprite_sheet = SpriteSheet(filename, sprite_width, sprite_height)
            self.sprite_sheets[name] = sprite_sheet
            return sprite_sheet
        except Exception as e:
            raise ResourceLoadError(f"Failed to load sprite sheet '{name}': {e}") from e
    
    def get_sprite_sheet(self, name: str) -> SpriteSheet:
        """
        Retrieve a cached sprite sheet.
        
        Args:
            name: Sprite sheet identifier
            
        Returns:
            Cached SpriteSheet instance
            
        Raises:
            KeyError: If sprite sheet not found
        """
        if name not in self.sprite_sheets:
            raise KeyError(f"Sprite sheet '{name}' not loaded")
        return self.sprite_sheets[name]
    
    def create_animation(self, name: str, sprite_sheet_name: str, frame_indices: List[int], fps: float = ANIMATION_FPS, loop: bool = True) -> Animation:
        """
        Create an animation from a sprite sheet.
        
        Args:
            name: Unique identifier for the animation
            sprite_sheet_name: Name of the sprite sheet to use
            frame_indices: List of sprite indices to use as frames
            fps: Animation speed in frames per second
            loop: Whether animation should loop
            
        Returns:
            Created Animation instance
        """
        sprite_sheet = self.get_sprite_sheet(sprite_sheet_name)
        frames = [sprite_sheet.get_sprite_by_index(idx) for idx in frame_indices]
        
        animation = Animation(frames, fps, loop)
        self.animations[name] = animation
        return animation
    
    def get_animation(self, name: str) -> Animation:
        """
        Retrieve a cached animation.
        
        Args:
            name: Animation identifier
            
        Returns:
            Cached Animation instance
            
        Raises:
            KeyError: If animation not found
        """
        if name not in self.animations:
            raise KeyError(f"Animation '{name}' not loaded")
        return self.animations[name]
    
    def load_image(self, name: str, filename: str) -> pygame.Surface:
        """
        Load and cache a standalone image.
        
        Args:
            name: Unique identifier for the image
            filename: Path to the image file
            
        Returns:
            Loaded image surface
        """
        if name in self.images:
            return self.images[name]
        
        try:
            full_path = os.path.join(ASSETS_PATH, filename)
            image = pygame.image.load(full_path).convert_alpha()
            self.images[name] = image
            return image
        except Exception as e:
            raise ResourceLoadError(f"Failed to load image '{name}': {e}") from e
    
    def get_image(self, name: str) -> pygame.Surface:
        """
        Retrieve a cached image.
        
        Args:
            name: Image identifier
            
        Returns:
            Cached image surface
            
        Raises:
            KeyError: If image not found
        """
        if name not in self.images:
            # If not found, try to load it using the name as filename
            from shared.constants import ASSET_FILES
            if name in ASSET_FILES:
                self.load_image(name, ASSET_FILES[name])
            else:
                raise KeyError(f"Image '{name}' not loaded and no default filename found in ASSET_FILES")
        return self.images[name]
    
    def load_sound(self, name: str, filename: str) -> pygame.mixer.Sound:
        """
        Load and cache a sound effect.
        
        Args:
            name: Unique identifier for the sound
            filename: Path to the sound file
            
        Returns:
            Loaded sound object
        """
        if name in self.sounds:
            return self.sounds[name]
        
        try:
            full_path = os.path.join(ASSETS_PATH, filename)
            sound = pygame.mixer.Sound(full_path)
            self.sounds[name] = sound
            return sound
        except Exception as e:
            raise ResourceLoadError(f"Failed to load sound '{name}': {e}") from e
    
    def get_sound(self, name: str) -> pygame.mixer.Sound:
        """
        Retrieve a cached sound.
        
        Args:
            name: Sound identifier
            
        Returns:
            Cached sound object
            
        Raises:
            KeyError: If sound not found
        """
        if name not in self.sounds:
            raise KeyError(f"Sound '{name}' not loaded")
        return self.sounds[name]
    
    def load_font(self, name: str, size: int, filename: Optional[str] = None) -> pygame.font.Font:
        """
        Load and cache a font.
        
        Args:
            name: Font name or identifier
            size: Font size in points
            filename: Optional path to font file (uses system font if None)
            
        Returns:
            Loaded font object
        """
        cache_key = (name, size)
        if cache_key in self.fonts:
            return self.fonts[cache_key]
        
        try:
            if filename:
                full_path = os.path.join(ASSETS_PATH, filename)
                font = pygame.font.Font(full_path, size)
            else:
                font = pygame.font.SysFont(name, size)
            
            self.fonts[cache_key] = font
            return font
        except Exception as e:
            raise ResourceLoadError(f"Failed to load font '{name}': {e}") from e
    
    def get_font(self, name: str, size: int) -> pygame.font.Font:
        """
        Retrieve a cached font.
        
        Args:
            name: Font name or identifier
            size: Font size in points
            
        Returns:
            Cached font object
            
        Raises:
            KeyError: If font not found
        """
        cache_key = (name, size)
        if cache_key not in self.fonts:
            raise KeyError(f"Font '{name}' size {size} not loaded")
        return self.fonts[cache_key]
    
    def load_json(self, name: str, filename: str) -> Any:
        """
        Load and cache JSON data.
        
        Args:
            name: Unique identifier for the data
            filename: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        if name in self.data_files:
            return self.data_files[name]
        
        try:
            full_path = os.path.join(ASSETS_PATH, filename)
            with open(full_path, 'r') as f:
                data = json.load(f)
            
            self.data_files[name] = data
            return data
        except Exception as e:
            raise ResourceLoadError(f"Failed to load JSON '{name}': {e}") from e
    
    def get_json(self, name: str) -> Any:
        """
        Retrieve cached JSON data.
        
        Args:
            name: Data identifier
            
        Returns:
            Cached JSON data
            
        Raises:
            KeyError: If data not found
        """
        if name not in self.data_files:
            raise KeyError(f"JSON data '{name}' not loaded")
        return self.data_files[name]
    
    def clear_cache(self):
        """Clear all cached resources."""
        self.sprite_sheets.clear()
        self.animations.clear()
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.data_files.clear()
    
    def unload_resource(self, resource_type: str, name: str) -> bool:
        """
        Unload a specific resource.
        
        Args:
            resource_type: Type of resource ('sprite_sheet', 'animation', 'image', 'sound', 'font', 'json')
            name: Resource identifier
            
        Returns:
            True if resource was unloaded, False if not found
        """
        resource_map = {
            'sprite_sheet': self.sprite_sheets,
            'animation': self.animations,
            'image': self.images,
            'sound': self.sounds,
            'font': self.fonts,
            'json': self.data_files
        }
        
        if resource_type not in resource_map:
            raise ValueError(f"Invalid resource type: {resource_type}")
        
        if name in resource_map[resource_type]:
            del resource_map[resource_type][name]
            return True
        
        return False