"""
core/entities.py
Cac class thuc the game. KHONG duoc import ursina/bat ky thu vien render nao o day.
Day la logic THUAN PYTHON, chay bang `python3`, advance theo TICK CO DINH (60 tick/s).

Thay doi so voi Phase 1:
- Dung toa do 3D (x, y, z) thay vi Vec2 2D, vi Ticket-02 yeu cau kiem tra chenh cao Y
  (vd "chenh cao giua chan May va mat dat <= 1.5m") va co truc Y cho nhay/boc/dao nhieu tang.
- Moi bo dem thoi gian doi sang TICK (int), khong con giay (float), de dam bao tinh tat
  dinh tuyet doi khi chay headless (khong phu thuoc sai so dau phay dong cua dt bien thien).
- Ten trang thai Bong Muc PHAI dung chuan Test Contract v1.1: spawning, wander, chase,
  recoil, stunned (khac voi Phase 1 dung "retreating": bool).
"""

from dataclasses import dataclass, field
from .rules_v2 import (
    MAX_FLAMES,
    HIT_INVULN_TICKS,
    DASH_DURATION_TICKS,
    DASH_COOLDOWN_TICKS,
    GLOW_COOLDOWN_TICKS,
    SHADOW_RECOIL_TICKS,
    SHADOW_SPEED_DEFAULT,
    SHADOW_DETECT_RADIUS,
    SHADOW_LOSE_RADIUS,
)


@dataclass
class Vec3:
    """Toa do 3D. Truc Y huong len (chuan Ticket-02)."""
    x: float
    y: float
    z: float

    def distance_xz_to(self, other: "Vec3") -> float:
        """Khoang cach chi tinh tren mat phang XZ (bo qua chenh cao Y)."""
        return ((self.x - other.x) ** 2 + (self.z - other.z) ** 2) ** 0.5

    def distance_3d_to(self, other: "Vec3") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5

    def height_diff_to(self, other: "Vec3") -> float:
        return abs(self.y - other.y)

    def move_toward_xz(self, target: "Vec3", step: float) -> "Vec3":
        """Di chuyen toi da `step` tren mat phang XZ, giu nguyen Y hien tai."""
        dx, dz = target.x - self.x, target.z - self.z
        dist = (dx ** 2 + dz ** 2) ** 0.5
        if dist <= step or dist == 0:
            return Vec3(target.x, self.y, target.z)
        ratio = step / dist
        return Vec3(self.x + dx * ratio, self.y, self.z + dz * ratio)


# Cac trang thai Bong Muc - PHAI dung dung ten nay theo Test Contract v1.1
SHADOW_STATE_SPAWNING = "spawning"
SHADOW_STATE_WANDER = "wander"
SHADOW_STATE_CHASE = "chase"
SHADOW_STATE_RECOIL = "recoil"
SHADOW_STATE_STUNNED = "stunned"


@dataclass
class Player:
    id: str
    pos: Vec3
    vel: Vec3 = field(default_factory=lambda: Vec3(0.0, 0.0, 0.0))
    grounded: bool = True
    flames: int = MAX_FLAMES                 # "Ngon Lua" - thay cho HP cua Phase 1
    light_storage: int = 0                    # so dom dom dang mang
    facing_deg: float = 0.0                    # huong quay mat (do, tinh tu +X nguoc chieu kim dong ho)

    invuln_ticks_left: int = 0                 # bat tu con lai (sau khi bi danh / hoi sinh)
    dash_cd_ticks_left: int = 0                # hoi chieu Luot con lai
    pulse_cd_ticks_left: int = 0               # hoi chieu Toa Sang con lai
    charm_ticks_left: int = 0                  # hieu luc Bua Gio con lai (Phase 2 chua lam Bua Gio)

    is_dashing: bool = False
    dash_ticks_left: int = 0                    # con bao nhieu tick nua thi het luot hien tai

    # Trang thai "roi khoi dao" (cho hoi sinh)
    is_falling_respawn: bool = False
    respawn_wait_ticks_left: int = 0

    @property
    def is_invulnerable(self) -> bool:
        return self.invuln_ticks_left > 0

    def tick_cooldowns(self):
        """Giam moi bo dem 1 tick. Goi o BUOC 2 cua vong lap (truoc khi di chuyen).
        LUU Y: KHONG tat is_dashing o day. Neu tat o day (truoc Buoc 3 di chuyen), tick
        cuoi cung cua dash se bi ap dung toc do thuong thay vi toc do dash, lam quang
        duong luot thieu 1 tick (da phat hien bang smoke test). Viec tat is_dashing duoc
        chuyen sang cuoi ham _move_player() trong engine.py, SAU KHI da di chuyen voi
        toc do dash cho tick cuoi cung nay."""
        self.invuln_ticks_left = max(0, self.invuln_ticks_left - 1)
        self.dash_cd_ticks_left = max(0, self.dash_cd_ticks_left - 1)
        self.pulse_cd_ticks_left = max(0, self.pulse_cd_ticks_left - 1)
        self.charm_ticks_left = max(0, self.charm_ticks_left - 1)
        if self.is_dashing:
            self.dash_ticks_left -= 1

    def take_hit(self, flame_loss: int):
        """Bi Bong Muc danh trung. KHONG tu dong bo qua bat tu o day - engine.py kiem tra
        is_invulnerable TRUOC khi goi ham nay (de giu entities.py don gian, khong chua
        quyet dinh nghiep vu 've viec co nen danh trung hay khong')."""
        self.flames = max(0, self.flames - flame_loss)
        self.invuln_ticks_left = HIT_INVULN_TICKS


@dataclass
class Firefly:
    id: str
    pos: Vec3
    collected: bool = False
    is_dropped: bool = False          # True neu day la dom dom ROI ra tu nguoi choi khi bi danh
    ttl_ticks_left: int = -1          # -1 = khong co han (dom dom thuong); >=0 = dom dom roi, co TTL


@dataclass
class Lantern:
    id: str
    pos: Vec3
    light_progress: int = 0            # so dom dom da nap (0..LANTERN_LIGHT_COST)
    light_cost: int = 10                # Chuan: 10 (truyen vao tu rules.LANTERN_LIGHT_COST)

    @property
    def is_lit(self) -> bool:
        return self.light_progress >= self.light_cost


@dataclass
class InkShadow:
    id: str
    pos: Vec3
    state: str = SHADOW_STATE_WANDER
    state_ticks_left: int = 0           # dung cho RECOIL/STUNNED - con bao nhieu tick o trang thai nay
    speed: float = SHADOW_SPEED_DEFAULT  # co the la 4.0 hoac 4.5 (Dem 3) - truyen vao luc tao

    # Dung cho hieu ung day lui khi bi Toa Sang (choang + knockback)
    knockback_dir: Vec3 = field(default_factory=lambda: Vec3(0.0, 0.0, 0.0))
    knockback_ticks_left: int = 0
    knockback_distance_left: float = 0.0

    def distance_xz_to(self, target: Vec3) -> float:
        return self.pos.distance_xz_to(target)

    def distance_3d_to(self, target: Vec3) -> float:
        return self.pos.distance_3d_to(target)

    def touches(self, player: Player, touch_radius_xz: float, touch_radius_y: float) -> bool:
        """Dieu kien cham theo Ticket-02: XZ <= nguong VA chenh cao Y <= nguong."""
        if self.state in (SHADOW_STATE_STUNNED, SHADOW_STATE_RECOIL, SHADOW_STATE_SPAWNING):
            return False  # Bong Muc dang choang/lui/moi sinh thi khong gay cham (gia dinh hop ly,
                            # Ticket-02 khong noi ro nhung "choang" ham y khong hanh dong duoc)
        return (
            self.distance_xz_to(player.pos) <= touch_radius_xz
            and self.pos.height_diff_to(player.pos) <= touch_radius_y
        )
