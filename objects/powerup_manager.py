from typing import List
import pygame
from shared.types import PowerupType
from objects.powerup_pickup import PowerupPickup
from core.scene import Scene


class PowerupManager:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.powerups: List[PowerupPickup] = []

    def create_powerup(self, powerup_type: str, x: int, y: int):
        from objects.jettpaq_pickup import JettpaqPickup
        from objects.jumpupstiq_pickup import JumpUpstiqPickup
        pos = (x, y)
        try:
            ptype = PowerupType[powerup_type.upper()]
        except KeyError:
            print(f"Unknown powerup type: {powerup_type}")
            return
            
        if ptype == PowerupType.JETTPAQ:
            powerup = JettpaqPickup(self.scene, pos)
        elif ptype == PowerupType.JUMPUPSTIQ:
            powerup = JumpUpstiqPickup(self.scene, pos)
        else:
            return
        self.powerups.append(powerup)

    def update(self, delta_time: float):
        for powerup in self.powerups[:]:
            powerup.update(delta_time)
            if not powerup.is_active():
                self.powerups.remove(powerup)

    def check_player_collision(self, player) -> List[PowerupPickup]:
        collided = []
        player_rect = player.get_rect()
        for powerup in self.powerups:
            # Only check collision if not already collected
            if not powerup.collected and powerup.get_rect().colliderect(player_rect):
                collided.append(powerup)
        return collided

    def render(self, surface: pygame.Surface, camera_offset):
        for powerup in self.powerups:
            powerup.render(surface, camera_offset)

    def clear(self):
        self.powerups.clear()
