from enum import Enum, auto
from typing import NamedTuple, Tuple, Optional, Union, List, Dict, Any
from dataclasses import dataclass
import pygame

class Vec2i(NamedTuple):
    """Immutable 2D integer vector."""
    x: int
    y: int
    
    def __add__(self, other: 'Vec2i') -> 'Vec2i':
        """Add two vectors."""
        return Vec2i(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vec2i') -> 'Vec2i':
        """Subtract two vectors."""
        return Vec2i(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: int) -> 'Vec2i':
        """Multiply vector by scalar."""
        return Vec2i(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vec2i':
        """Divide vector by scalar."""
        return Vec2i(int(self.x / scalar), int(self.y / scalar))
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple."""
        return (self.x, self.y)
    
    @classmethod
    def from_tuple(cls, tup: Tuple[int, int]) -> 'Vec2i':
        """Create from tuple."""
        return Vec2i(tup[0], tup[1])

@dataclass
class Rect:
    """Axis-aligned rectangle with x, y, width, height."""
    x: float
    y: float
    width: float
    height: float
    
    @property
    def left(self) -> float:
        """Get left edge."""
        return self.x
    
    @property
    def top(self) -> float:
        """Get top edge."""
        return self.y
    
    @property
    def right(self) -> float:
        """Get right edge."""
        return self.x + self.width
    
    @property
    def bottom(self) -> float:
        """Get bottom edge."""
        return self.y + self.height
    
    def position(self) -> Vec2i:
        """Get top-left position."""
        return Vec2i(int(self.x), int(self.y))
    
    def size(self) -> Vec2i:
        """Get size as vector."""
        return Vec2i(int(self.width), int(self.height))
    
    def contains(self, point: Vec2i) -> bool:
        """Check if point is inside rectangle."""
        return (self.x <= point.x < self.x + self.width and 
                self.y <= point.y < self.y + self.height)
    
    def intersects(self, other: 'Rect') -> bool:
        """Check if two rectangles intersect."""
        return not (self.right <= other.left or 
                   self.left >= other.right or 
                   self.bottom <= other.top or 
                   self.top >= other.bottom)
    
    def move(self, offset: Vec2i) -> 'Rect':
        """Move rectangle by offset."""
        return Rect(self.x + offset.x, self.y + offset.y,
                   self.width, self.height)
    
    def copy(self) -> 'Rect':
        """Create a copy."""
        return Rect(self.x, self.y, self.width, self.height)

class PlayerState(Enum):
    """Player character state machine states."""
    NORMAL = auto()
    JUMPUPSTIQ = auto()
    JETTPAQ = auto()

class PowerupType(Enum):
    """Types of power-ups available in the game."""
    JUMPUPSTIQ = auto()
    JETTPAQ = auto()

class EnemyState(Enum):
    """Enemy AI state machine states."""
    IDLE = auto()
    PATROL = auto()
    CHASE = auto()
    ATTACK = auto()
    HURT = auto()
    DEAD = auto()

class Direction(Enum):
    """Cardinal directions."""
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()

class CollectibleType(Enum):
    """Types of collectible items."""
    CHIP = auto()
    FLOPPY = auto()
    MEDALLION = auto()
    BRIQ = auto()

class DoorState(Enum):
    """Door states."""
    LOCKED = auto()
    UNLOCKED = auto()
    OPEN = auto()
    CLOSED = auto()

class WoNQModeType(Enum):
    """WoNQ mode types."""
    LOW_G = auto()
    GLITCH = auto()
    MIRROR = auto()
    BULLET_TIME = auto()
    SPEEDY_BOOTS = auto()
    JUNGLIST = auto()

class CollectibleData:
    """Data container for collectible properties."""
    def __init__(self, value: int, color: Tuple[int, int, int], sprite_key: str):
        self.value = value
        self.color = color
        self.sprite_key = sprite_key

class MenuAction(Enum):
    """Menu action types."""
    START_GAME = auto()
    OPTIONS = auto()
    EXIT = auto()
    RESUME = auto()
    RESTART = auto()
    MAIN_MENU = auto()

class GameState(Enum):
    """Game state enumeration."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()

class LevelData:
    """Container for level data."""
    def __init__(self, name: str, width: int, height: int, tiles: List[List[int]], 
                 entities: List[Dict[str, Any]], modes: List[str], 
                 background: str, music: str):
        self.name = name
        self.width = width
        self.height = height
        self.tiles = tiles
        self.entities = entities
        self.modes = modes
        self.background = background
        self.music = music

# Alias for backward compatibility
Vector2 = Vec2i
PlayerStateType = PlayerState
Color = Tuple[int, int, int]