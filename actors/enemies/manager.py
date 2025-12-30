from typing import Optional, List
import pygame
from shared.types import Vec2i
from actors.player import Player
from actors.enemies.base_enemy import BaseEnemy
from actors.enemies.walqer_bot import WalqerBot
from actors.enemies.jumper_drqne import JumperDrqne
from actors.enemies.qortana_halo import QortanaHalo
from actors.enemies.qlippy import Qlippy
from actors.enemies.briq_beaver import BriqBeaver

class EnemyManager:
    def __init__(self):
        self.enemies: List[BaseEnemy] = []

    def create_enemy(self, enemy_type: str, x: int, y: int):
        position = Vec2i(x, y)
        if enemy_type == "walqer":
            enemy = WalqerBot(position)
        elif enemy_type == "jumper":
            enemy = JumperDrqne(position)
        elif enemy_type == "qortana":
            enemy = QortanaHalo(x, y)
        elif enemy_type == "qlippy":
            enemy = Qlippy(x, y)
        elif enemy_type == "briq_beaver":
            enemy = BriqBeaver(position)
        else:
            return
        self.enemies.append(enemy)

    def update(self, delta_time: float, player_position: Optional[Vec2i] = None):
        for enemy in self.enemies[:]:
            enemy.think(delta_time, player_position)
            enemy.update(delta_time)
            if not enemy.is_active():
                self.enemies.remove(enemy)

    def check_player_collision(self, player: Player) -> List[BaseEnemy]:
        collided_enemies = []
        for enemy in self.enemies:
            if enemy.get_rect().colliderect(player.get_rect()):
                collided_enemies.append(enemy)
        return collided_enemies

    def render(self, surface: pygame.Surface, camera_offset):
        for enemy in self.enemies:
            enemy.render(surface, camera_offset)

    def clear(self):
        self.enemies.clear()
