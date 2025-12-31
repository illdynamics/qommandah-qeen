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
from actors.enemies.hover_squid import HoverSquid

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
        elif enemy_type == "hover_squid":
            enemy = HoverSquid(position)
        else:
            return
        self.enemies.append(enemy)

    def update(self, delta_time: float, player_position = None):
        # Convert player position to Vec2i if it's not already
        player_pos = None
        if player_position is not None:
            if hasattr(player_position, 'x') and hasattr(player_position, 'y'):
                player_pos = Vec2i(int(player_position.x), int(player_position.y))
            else:
                player_pos = player_position
        
        for enemy in self.enemies[:]:
            enemy.think(delta_time, player_pos)
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

    def get_all_enemies(self) -> List[BaseEnemy]:
        """Get all active enemies."""
        return self.enemies

    def clear(self):
        self.enemies.clear()
