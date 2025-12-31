import pygame
import os
from typing import Optional, List
from shared.types import DoorState
from shared.constants import DOOR_CLOSED, DOOR_OPEN, DOOR_UNLOCKED, DOOR_LOCKED, ASSETS_PATH
from world.entities import Entity
from shared.exceptions import InvalidDoorStateError

class Door(Entity):
    """Door entity requiring specific keys to unlock. Uses sprite animation."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 required_key_id: str = "default", door_id: Optional[str] = None,
                 target_room: int = 1):
        """Initialize door with position, size, and key requirement.
        
        Args:
            x: X position
            y: Y position
            width: Door width
            height: Door height
            required_key_id: ID of key required to unlock
            door_id: Optional unique identifier for the door
            target_room: Room number to transition to when entering
        """
        super().__init__((x, y), (width, height))
        self.required_key_id = required_key_id
        self.door_id = door_id or f"door_{x}_{y}"
        self.state = DoorState.LOCKED
        self.visible = True
        self.open_progress = 0.0
        self.open_speed = 2.0  # frames per second for animation
        self.target_room = target_room
        
        # Animation
        self._frames: List[pygame.Surface] = []
        self._current_frame = 0
        self._animation_timer = 0.0
        self._is_opening = False
        self._load_sprites()
    
    def _load_sprites(self) -> None:
        """Load door sprite animation from qq-door-open.png."""
        door_path = os.path.join(ASSETS_PATH, "qq-door-open.png")
        if os.path.exists(door_path):
            door_sheet = pygame.image.load(door_path).convert_alpha()
            # Door sheet is 768x128 = 6 frames of 128x128
            for i in range(6):
                x = i * 128
                frame = pygame.Surface((128, 128), pygame.SRCALPHA)
                frame.blit(door_sheet, (0, 0), (x, 0, 128, 128))
                # Scale to fit door size
                frame = pygame.transform.scale(frame, (int(self.size[0]), int(self.size[1])))
                self._frames.append(frame)
            print(f"Loaded door sprites: {len(self._frames)} frames")
    
    def update(self, dt: float) -> None:
        """Update door state and animation."""
        if self._is_opening and self._frames:
            self._animation_timer += dt
            frame_duration = 1.0 / (self.open_speed * 6)  # Time per frame
            
            if self._animation_timer >= frame_duration:
                self._animation_timer -= frame_duration
                self._current_frame += 1
                
                if self._current_frame >= len(self._frames):
                    self._current_frame = len(self._frames) - 1
                    self._is_opening = False
                    self.state = DoorState.OPEN
    
    def render(self, surface: pygame.Surface, camera_offset: tuple) -> None:
        """Render door to surface with camera offset."""
        if not self.visible:
            return
            
        x = int(self.position[0] - camera_offset[0])
        y = int(self.position[1] - camera_offset[1])
        
        if self._frames and self._current_frame < len(self._frames):
            surface.blit(self._frames[self._current_frame], (x, y))
        else:
            # Fallback to colored rectangle
            width = int(self.size[0])
            height = int(self.size[1])
            colors = {
                DoorState.LOCKED: (200, 50, 50),
                DoorState.UNLOCKED: (50, 200, 50),
                DoorState.OPEN: (50, 50, 200)
            }
            color = colors.get(self.state, (128, 128, 128))
            pygame.draw.rect(surface, color, (x, y, width, height))
            pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
    
    def unlock(self, key_id: str = None) -> bool:
        """Attempt to unlock door with key."""
        if key_id is None or key_id == self.required_key_id:
            self.state = DoorState.UNLOCKED
            return True
        return False
    
    def open_door(self) -> None:
        """Start door opening animation."""
        if self.state == DoorState.UNLOCKED:
            self._is_opening = True
            self._current_frame = 0
            self._animation_timer = 0.0
    
    def close_door(self) -> None:
        """Close the door (changes state to LOCKED)."""
        self.state = DoorState.LOCKED
        self._current_frame = 0
        self._is_opening = False
    
    def reset(self) -> None:
        """Reset door to initial locked state."""
        self.state = DoorState.LOCKED
        self.open_progress = 0.0
        self._current_frame = 0
        self._is_opening = False
    
    def get_state(self) -> DoorState:
        """Get current door state."""
        return self.state
    
    def set_state(self, state: DoorState) -> None:
        """Set door state."""
        self.state = state
    
    def is_unlocked(self) -> bool:
        """Check if door is unlocked."""
        return self.state == DoorState.UNLOCKED or self.state == DoorState.OPEN
    
    def is_open(self) -> bool:
        """Check if door is open."""
        return self.state == DoorState.OPEN
    
    def can_enter(self) -> bool:
        """Check if player can enter the door."""
        return self.state == DoorState.OPEN and not self._is_opening
    
    def get_target_room(self) -> int:
        """Get the room number this door leads to."""
        return self.target_room
    
    def get_required_key(self) -> str:
        """Get required key ID."""
        return self.required_key_id
    
    def get_door_id(self) -> str:
        """Get door identifier."""
        return self.door_id
    
    def set_visible(self, visible: bool) -> None:
        """Set door visibility."""
        self.visible = visible
    
    def is_visible(self) -> bool:
        """Check if door is visible."""
        return self.visible
    
    def get_open_progress(self) -> float:
        """Get door opening progress (0.0 to 1.0)."""
        if self._frames:
            return self._current_frame / (len(self._frames) - 1)
        return 0.0