"""
core/engine.py
Logic game thuan Python - KHONG import ursina o day.
Day la lop duoc dung CHUNG boi:
  - render/app.py   (ban co giao dien, goi engine moi frame)
  - headless/runner.py (ban khong giao dien, goi engine theo Test Contract)
Nho vay bang chung headless se khop voi hanh vi ban co giao dien (GUIDE.md muc 5).
"""

from dataclasses import dataclass, field
from core.entities import Player, Firefly, Lantern, InkShadow, Vec2
from core.rules import (
    FIREFLY_PICKUP_RADIUS,
    LANTERN_LIGHT_RADIUS,
    LIGHT_COST_PER_LANTERN,
    GLOW_COST,
    GLOW_RADIUS,
    GLOW_COOLDOWN,
    SCORE_PER_FIREFLY,
    SCORE_PER_LANTERN,
    DAMAGE_PER_HIT,
)

# Cac trang thai game co the co
STATE_PLAYING = "PLAYING"
STATE_WIN = "WIN"
STATE_LOSE = "LOSE"


@dataclass
class GameWorld:
    player: Player
    fireflies: list[Firefly] = field(default_factory=list)
    lanterns: list[Lantern] = field(default_factory=list)
    shadows: list[InkShadow] = field(default_factory=list)
    score: int = 0
    state: str = STATE_PLAYING

    # ---------- Vong lap chinh ----------
    def update(self, dt: float):
        """Goi moi frame (ban co giao dien) hoac moi buoc (ban headless)."""
        if self.state != STATE_PLAYING:
            return
        self.player.tick_cooldowns(dt)
        self._update_shadows(dt)
        self._check_collisions()
        self._check_win_lose()

    def _update_shadows(self, dt: float):
        for shadow in self.shadows:
            shadow.move_toward(self.player.pos, dt)

    def _check_collisions(self):
        for shadow in self.shadows:
            if shadow.touches(self.player):
                self.player.take_damage(DAMAGE_PER_HIT)

    # ---------- Hanh dong nguoi choi ----------
    def move_player(self, dx: float, dz: float):
        """Di chuyen nhan vat theo huong (dx, dz) da chuan hoa * toc do * dt o lop goi."""
        if self.state != STATE_PLAYING:
            return
        self.player.pos = Vec2(self.player.pos.x + dx, self.player.pos.z + dz)

    def pickup_firefly(self, firefly_id: str) -> bool:
        """Nhat dom dom neu du gan va chua nhat. Tra ve True neu nhat thanh cong."""
        if self.state != STATE_PLAYING:
            return False
        for f in self.fireflies:
            if f.id == firefly_id and not f.collected:
                if f.pos.distance_to(self.player.pos) <= FIREFLY_PICKUP_RADIUS:
                    f.collected = True
                    self.player.light_storage += 1
                    self.score += SCORE_PER_FIREFLY
                    return True
        return False

    def light_lantern(self, lantern_id: str) -> bool:
        """Thap den neu du gan, den chua sang, va du anh sang trong kho."""
        if self.state != STATE_PLAYING:
            return False
        for l in self.lanterns:
            if l.id == lantern_id and not l.is_lit:
                close_enough = l.pos.distance_to(self.player.pos) <= LANTERN_LIGHT_RADIUS
                has_light = self.player.light_storage >= LIGHT_COST_PER_LANTERN
                if close_enough and has_light:
                    l.is_lit = True
                    self.player.light_storage -= LIGHT_COST_PER_LANTERN
                    self.score += SCORE_PER_LANTERN
                    self._check_win_lose()
                    return True
        return False

    def use_glow(self) -> bool:
        """Toa sang xua Bong Muc trong ban kinh. Tra ve True neu kich hoat thanh cong."""
        if self.state != STATE_PLAYING:
            return False
        if self.player.light_storage < GLOW_COST or self.player.glow_cooldown_left > 0:
            return False
        self.player.light_storage -= GLOW_COST
        self.player.glow_cooldown_left = GLOW_COOLDOWN
        for shadow in self.shadows:
            if shadow.distance_to(self.player.pos) <= GLOW_RADIUS:
                shadow.retreat()
        return True

    # ---------- Kiem tra thang / thua ----------
    def _check_win_lose(self):
        if all(l.is_lit for l in self.lanterns):
            self.state = STATE_WIN
        elif self.player.hp <= 0:
            self.state = STATE_LOSE

    def reset(self, initial_state: "GameWorld"):
        """Choi lai: nap lai trang thai ban dau (dung cho yeu cau 'choi lai sau thang/thua')."""
        self.player = initial_state.player
        self.fireflies = initial_state.fireflies
        self.lanterns = initial_state.lanterns
        self.shadows = initial_state.shadows
        self.score = 0
        self.state = STATE_PLAYING

    # ---------- Xuat trang thai (dung cho headless output / HUD) ----------
    def to_dict(self) -> dict:
        return {
            "state": self.state,
            "score": self.score,
            "player": {
                "pos": {"x": self.player.pos.x, "z": self.player.pos.z},
                "hp": self.player.hp,
                "light_storage": self.player.light_storage,
            },
            "lanterns": [
                {"id": l.id, "is_lit": l.is_lit} for l in self.lanterns
            ],
            "fireflies": [
                {"id": f.id, "collected": f.collected} for f in self.fireflies
            ],
            "shadows": [
                {"id": s.id, "pos": {"x": s.pos.x, "z": s.pos.z}, "retreating": s.retreating}
                for s in self.shadows
            ],
        }
