from typing import List, Optional
import pygame
from shared.types import Rect
from objects.hazard import Hazard, SpikeHazard, AcidHazard, LaserHazard

class HazardManager:
    def __init__(self):
        self.hazards: List[Hazard] = []

    def create_hazard(self, hazard_type: str, x: int, y: int):
        if hazard_type == "spike":
            hazard = SpikeHazard(x, y)
        elif hazard_type == "acid":
            hazard = AcidHazard(x, y)
        elif hazard_type == "laser":
            hazard = LaserHazard(x, y)
        else:
            return
        self.hazards.append(hazard)

    def update(self, delta_time: float):
        for hazard in self.hazards:
            hazard.update(delta_time)

    def check_player_collision(self, player: 'Player') -> List[Hazard]:
        collided = []
        for hazard in self.hazards:
            if hazard.check_collision(player.get_rect()):
                collided.append(hazard)
        return collided

    def render(self, surface: pygame.Surface, camera_offset: tuple[int, int]):
        for hazard in self.hazards:
            hazard.render(surface, camera_offset)

    def clear(self):
        self.hazards.clear()
