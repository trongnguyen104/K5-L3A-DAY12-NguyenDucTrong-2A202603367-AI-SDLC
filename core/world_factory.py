"""
core/world_factory.py
Dung GameWorld cho tung Dem theo ban do chuan Ticket-02.
Tach rieng khoi engine.py de engine.py chi con logic thuan, khong lan sang du lieu man choi.
"""

from .entities import Player, Firefly, Lantern, InkShadow, Vec3
from .engine import GameWorld
from .rules import (
    night1_lantern_positions, night1_firefly_spawn_points,
    LANTERN_LIGHT_COST, FIREFLY_INITIAL_COUNT, PLAYER_SPAWN_NIGHT1,
)


def build_night1_world() -> GameWorld:
    """Dung 'Dem 1 - Dao Ben' theo ban do chuan (Phan 2 Ticket-02).
    Bong Muc CHUA sinh san (lich sinh: 2 con tai tick 300) - world khoi tao khong co
    Bong Muc nao, engine.step() se tu sinh dung lich khi chay."""
    sx, sy, sz = PLAYER_SPAWN_NIGHT1
    player = Player(id="may", pos=Vec3(sx, sy, sz))

    lanterns = [
        Lantern(id=lid, pos=Vec3(x, y, z), light_cost=LANTERN_LIGHT_COST)
        for lid, (x, y, z) in night1_lantern_positions().items()
    ]

    all_spawn_points = night1_firefly_spawn_points()
    fireflies = [
        Firefly(id=f"f{i}", pos=Vec3(x, y, z))
        for i, (x, y, z) in enumerate(all_spawn_points[:FIREFLY_INITIAL_COUNT])
    ]

    return GameWorld(player=player, fireflies=fireflies, lanterns=lanterns, shadows=[], night=1)
