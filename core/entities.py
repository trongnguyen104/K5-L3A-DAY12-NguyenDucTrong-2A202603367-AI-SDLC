"""
core/entities.py
Cac class thuc the game. KHONG duoc import ursina/bat ky thu vien render nao o day.
Day la logic THUAN PYTHON, phai chay duoc bang `python3` khong can man hinh/GPU.
"""

from dataclasses import dataclass, field
from core.rules import PLAYER_MAX_HP, HIT_COOLDOWN, SHADOW_SPEED, SHADOW_RETREAT_TIME


@dataclass
class Vec2:
    """Toa do 2D don gian (x, z) - du cho logic di chuyen tren mat dao."""
    x: float
    z: float

    def distance_to(self, other: "Vec2") -> float:
        return ((self.x - other.x) ** 2 + (self.z - other.z) ** 2) ** 0.5

    def move_toward(self, target: "Vec2", step: float) -> "Vec2":
        """Tra ve vi tri moi, di chuyen toi `target` toi da `step` don vi."""
        dx, dz = target.x - self.x, target.z - self.z
        dist = (dx ** 2 + dz ** 2) ** 0.5
        if dist <= step or dist == 0:
            return Vec2(target.x, target.z)
        ratio = step / dist
        return Vec2(self.x + dx * ratio, self.z + dz * ratio)


@dataclass
class Player:
    id: str
    pos: Vec2
    hp: int = PLAYER_MAX_HP
    light_storage: int = 0          # so dom dom dang giu (dung de thap den / toa sang)
    hit_cooldown_left: float = 0.0  # con bao nhieu giay nua moi bi tru mau tiep
    glow_cooldown_left: float = 0.0
    is_glowing: bool = False

    def take_damage(self, amount: int):
        if self.hit_cooldown_left <= 0:
            self.hp = max(0, self.hp - amount)
            self.hit_cooldown_left = HIT_COOLDOWN

    def tick_cooldowns(self, dt: float):
        self.hit_cooldown_left = max(0.0, self.hit_cooldown_left - dt)
        self.glow_cooldown_left = max(0.0, self.glow_cooldown_left - dt)


@dataclass
class Firefly:
    id: str
    pos: Vec2
    collected: bool = False


@dataclass
class Lantern:
    id: str
    pos: Vec2
    is_lit: bool = False


@dataclass
class InkShadow:
    id: str
    pos: Vec2
    retreating: bool = False
    retreat_time_left: float = 0.0

    def move_toward(self, target: Vec2, dt: float):
        """Duoi theo player, tru khi dang lui (retreating) sau khi bi toa sang xua."""
        if self.retreating:
            self.retreat_time_left -= dt
            if self.retreat_time_left <= 0:
                self.retreating = False
            return  # dung yen / khong duoi khi dang lui (gia dinh don gian cho Phase 1)
        step = SHADOW_SPEED * dt
        self.pos = self.pos.move_toward(target, step)

    def retreat(self):
        self.retreating = True
        self.retreat_time_left = SHADOW_RETREAT_TIME

    def distance_to(self, target: Vec2) -> float:
        return self.pos.distance_to(target)

    def touches(self, player: Player, touch_radius: float = 1.0) -> bool:
        return (not self.retreating) and self.pos.distance_to(player.pos) <= touch_radius
