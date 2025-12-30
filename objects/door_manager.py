from typing import List
import pygame
from objects.door import Door
from core.scene import Scene
from shared.constants import TILE_SIZE


class DoorManager:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.doors: List[Door] = []

    def create_door(self, door_type: str, x: int, y: int):
        """Create a door at the given position.
        
        Args:
            door_type: Type of door (e.g., 'exit', 'locked', etc.)
            x: X position in pixels
            y: Y position in pixels
        """
        width = TILE_SIZE
        height = TILE_SIZE * 2
        
        if door_type == "exit":
            required_key_id = "none"
        elif door_type == "locked":
            required_key_id = "key_default"
        else:
            required_key_id = f"key_{door_type}"
        
        door_id = f"door_{door_type}_{x}_{y}"
        door = Door(x, y, width, height, required_key_id, door_id)
        self.doors.append(door)

    def update(self, delta_time: float):
        for door in self.doors:
            door.update(delta_time)

    def check_player_collision(self, player) -> List[Door]:
        collided = []
        player_rect = player.get_rect()
        for door in self.doors:
            door_rect = pygame.Rect(door.position[0], door.position[1], 
                                    door.size[0], door.size[1])
            if door_rect.colliderect(player_rect):
                collided.append(door)
        return collided

    def render(self, surface: pygame.Surface, camera_offset):
        if hasattr(camera_offset, 'x'):
            offset = (camera_offset.x, camera_offset.y)
        else:
            offset = (camera_offset[0], camera_offset[1])
        
        for door in self.doors:
            door.render(surface, offset)

    def clear(self):
        self.doors.clear()
