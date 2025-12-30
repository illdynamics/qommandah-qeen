from typing import List
import pygame
from shared.types import CollectibleType
from objects.collectible import Collectible
from core.scene import Scene


class CollectibleManager:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.collectibles: List[Collectible] = []

    def create_collectible(self, collectible_type: str, x: int, y: int):
        pos = (x, y)
        try:
            ctype = CollectibleType[collectible_type.upper()]
        except KeyError:
            print(f"Unknown collectible type: {collectible_type}")
            return
        collectible = Collectible(self.scene, pos, ctype)
        self.collectibles.append(collectible)

    def update(self, delta_time: float):
        for collectible in self.collectibles[:]:
            collectible.update(delta_time)
            if not collectible.is_active():
                self.collectibles.remove(collectible)

    def check_player_collision(self, player) -> List[Collectible]:
        collided = []
        player_rect = player.get_rect()
        for collectible in self.collectibles:
            if not collectible.collected and collectible.get_rect().colliderect(player_rect):
                collided.append(collectible)
        return collided

    def render(self, surface: pygame.Surface, camera_offset):
        for collectible in self.collectibles:
            collectible.render(surface, camera_offset)

    def clear(self):
        self.collectibles.clear()
