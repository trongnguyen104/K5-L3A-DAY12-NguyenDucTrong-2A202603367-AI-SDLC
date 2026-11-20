"""
render/app.py
Ban co giao dien (Ursina). CHI duoc goi ham cua core.engine.GameWorld roi ve lai theo
world.to_dict() - KHONG duoc tu viet logic game o day (xem AGENTS.md quy uoc #2).

Chay: python3 render/app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ursina import (
    Ursina, Entity, Text, color, camera, held_keys, time as ursina_time,
    Vec3, mouse, window, scene, Sky, DirectionalLight, AmbientLight, Circle
)

from core.entities import Player, Firefly, Lantern, InkShadow, Vec2
from core.engine import GameWorld, STATE_WIN, STATE_LOSE
from core.rules import NUM_LANTERNS, ISLAND_RADIUS

# ===== Gia dinh rieng cho ban render (khong anh huong core/) =====
PLAYER_MOVE_SPEED = 5.0   # don vi/giay, dieu khien WASD
PLAYER_JUMP_SPEED = 6.0   # toc do nhay ban dau
GRAVITY = -14.0


def build_initial_world() -> GameWorld:
    """Dung du lieu man 'Dem 1 - Dao Ben': dao tron, 5 den, dom dom rai rac, vai Bong Muc."""
    import math

    player = Player(id="may", pos=Vec2(0, 0))

    # 5 Den Long Lon dat deu quanh vong tron (gia dinh vi tri, PRD-0 khong cho toa do)
    lanterns = []
    for i in range(NUM_LANTERNS):
        angle = (2 * math.pi / NUM_LANTERNS) * i
        x = math.cos(angle) * (ISLAND_RADIUS * 0.6)
        z = math.sin(angle) * (ISLAND_RADIUS * 0.6)
        lanterns.append(Lantern(id=f"l{i}", pos=Vec2(x, z)))

    # Dom dom rai rac (gia dinh: 10 con, vi tri ngau nhien co seed co dinh de co the lap lai)
    import random
    rng = random.Random(42)  # seed co dinh -> khong pha tinh tat dinh khi can test lai
    fireflies = []
    for i in range(10):
        x = rng.uniform(-ISLAND_RADIUS * 0.8, ISLAND_RADIUS * 0.8)
        z = rng.uniform(-ISLAND_RADIUS * 0.8, ISLAND_RADIUS * 0.8)
        fireflies.append(Firefly(id=f"f{i}", pos=Vec2(x, z)))

    # Bong Muc (gia dinh: 2 con, xuat hien o ria dao)
    shadows = [
        InkShadow(id="s0", pos=Vec2(ISLAND_RADIUS * 0.9, 0)),
        InkShadow(id="s1", pos=Vec2(-ISLAND_RADIUS * 0.9, 0)),
    ]

    return GameWorld(player=player, fireflies=fireflies, lanterns=lanterns, shadows=shadows)


class GameApp:
    """Lop ket noi GameWorld (logic) voi Ursina (hien thi). Khong chua logic game."""

    def __init__(self):
        self.app = Ursina()
        window.title = "Dao Den Long - Dem 1: Dao Ben"
        window.color = color.rgb32(15, 15, 25)  # Nen troi dem toi

        # Bầu trời đêm sẫm màu
        self.sky = Sky(color=color.rgb32(18, 18, 30))

        # Ánh sáng đêm dịu mắt (dùng rgb32 để đúng dải 0-255, tránh cháy sáng 12000%)
        self.ambient_light = AmbientLight(color=color.rgba32(50, 50, 70, 255))
        self.sun = DirectionalLight(y=10, z=5, rotation=(45, -45, 0), color=color.rgba32(90, 90, 120, 255))

        self.initial_world = build_initial_world()
        self.world = build_initial_world()

        self._build_scene()
        self._build_hud()

        self.player_y_velocity = 0.0
        self.is_grounded = True

    # ---------- Dung scene tu du lieu world ----------
    def _build_scene(self):
        import math

        # 1. Mặt biển bao quanh đảo (nằm thấp hơn mặt đảo, tạo cảm giác đảo bến trên biển đêm)
        self.ocean = Entity(
            model="plane", scale=120, y=-0.5,
            color=color.rgb32(10, 15, 28),
        )

        # 2. Mặt đảo hình tròn "Đảo Bến" (màu đất pha cỏ đêm sẫm màu)
        self.ground = Entity(
            model="circle", scale=ISLAND_RADIUS * 2, rotation_x=-90, y=0,
            color=color.rgb32(35, 42, 38), double_sided=True, collider="mesh",
        )

        # 3. Viền bờ đảo (Circle rỗng mode='line' - KHÔNG che mặt đất như circle ngon đặc)
        self.border_line = Entity(
            model=Circle(resolution=64, radius=ISLAND_RADIUS, mode='line', thickness=4),
            rotation_x=-90, y=0.03,
            color=color.rgb32(230, 180, 80),
        )

        # Các cột đá / cọc mốc rải quanh mép đảo để nhìn rõ giới hạn bản đồ từ xa
        self.boundary_markers = []
        for i in range(24):
            ang = (2 * math.pi / 24) * i
            bx = math.cos(ang) * ISLAND_RADIUS
            bz = math.sin(ang) * ISLAND_RADIUS
            marker = Entity(
                model="cube", scale=(0.5, 0.8, 0.5),
                position=Vec3(bx, 0.4, bz),
                color=color.rgb32(70, 75, 80),
            )
            self.boundary_markers.append(marker)

        # 4. Đường mòn lát đá dẫn từ tâm đảo (0, 0) tới từng Đèn Lồng Lớn
        self.path_segments = []
        for l in self.world.lanterns:
            dist = (l.pos.x ** 2 + l.pos.z ** 2) ** 0.5
            angle = math.degrees(math.atan2(l.pos.x, l.pos.z))
            path = Entity(
                model="quad", scale=(1.2, dist),
                rotation_x=90, rotation_y=angle,
                position=Vec3(l.pos.x / 2, 0.015, l.pos.z / 2),
                color=color.rgb32(60, 65, 68),
            )
            self.path_segments.append(path)

        # 5. Nhân vật Mây (hình hộp màu xanh ngọc)
        self.player_entity = Entity(
            model="cube", color=color.azure, scale=(0.6, 1.0, 0.6),
            position=Vec3(self.world.player.pos.x, 0.5, self.world.player.pos.z),
        )
        camera.parent = self.player_entity
        camera.position = Vec3(0, 4, -8)
        camera.rotation_x = 20

        # 6. Đèn Lồng Lớn (Bệ đá + Thân đèn)
        self.lantern_entities = {}
        for l in self.world.lanterns:
            Entity(
                model="cube", scale=(1.4, 0.2, 1.4),
                color=color.rgb32(50, 50, 55),
                position=Vec3(l.pos.x, 0.1, l.pos.z),
            )
            ent = Entity(
                model="cube", scale=(0.8, 2.0, 0.8),
                color=color.rgb32(60, 20, 80),
                position=Vec3(l.pos.x, 1.1, l.pos.z),
            )
            self.lantern_entities[l.id] = ent

        # 7. Đom đóm (nhỏ, màu vàng rực)
        self.firefly_entities = {}
        for f in self.world.fireflies:
            ent = Entity(
                model="sphere", scale=0.3, color=color.yellow,
                position=Vec3(f.pos.x, 1.2, f.pos.z),
            )
            self.firefly_entities[f.id] = ent

        # 8. Bóng Mực (hình cầu màu tím đen)
        self.shadow_entities = {}
        for s in self.world.shadows:
            ent = Entity(
                model="sphere", scale=0.9, color=color.rgb32(30, 0, 50),
                position=Vec3(s.pos.x, 0.8, s.pos.z),
            )
            self.shadow_entities[s.id] = ent

    def _build_hud(self):
        self.hp_text = Text(text="HP: 100", position=(-0.85, 0.45), scale=1.5, color=color.red)
        self.light_text = Text(text="Anh sang: 0", position=(-0.85, 0.40), scale=1.5, color=color.yellow)
        self.lantern_text = Text(text="Den: 0/5", position=(-0.85, 0.35), scale=1.5, color=color.orange)
        self.score_text = Text(text="Diem: 0", position=(-0.85, 0.30), scale=1.5, color=color.white)
        self.state_text = Text(text="", position=(0, 0.1), scale=3, origin=(0, 0), color=color.gold)

    # ---------- Vong lap moi frame: CHI goi core, roi ve lai ----------
    def update(self):
        dt = ursina_time.dt

        if self.world.state == "PLAYING":
            self._handle_input(dt)
            self.world.update(dt)

        self._sync_entities_from_world()
        self._sync_hud_from_world()

    def _handle_input(self, dt: float):
        dx = dz = 0.0
        if held_keys["w"]:
            dz += 1
        if held_keys["s"]:
            dz -= 1
        if held_keys["d"]:
            dx += 1
        if held_keys["a"]:
            dx -= 1

        if dx or dz:
            length = (dx ** 2 + dz ** 2) ** 0.5
            dx, dz = dx / length, dz / length
            self.world.move_player(dx * PLAYER_MOVE_SPEED * dt, dz * PLAYER_MOVE_SPEED * dt)

        if held_keys["space"] and self.is_grounded:
            self.player_y_velocity = PLAYER_JUMP_SPEED
            self.is_grounded = False

        if held_keys["e"]:
            for l in self.world.lanterns:
                self.world.light_lantern(l.id)
            for f in self.world.fireflies:
                self.world.pickup_firefly(f.id)

        if held_keys["f"]:
            self.world.use_glow()

        # Nhay don gian (truc y khong thuoc core logic - chi la hieu ung hinh anh)
        self.player_y_velocity += GRAVITY * dt
        new_y = self.player_entity.y + self.player_y_velocity * dt
        if new_y <= 0.5:
            new_y = 0.5
            self.player_y_velocity = 0.0
            self.is_grounded = True
        self.player_entity.y = new_y

    def _sync_entities_from_world(self):
        p = self.world.player
        self.player_entity.x = p.pos.x
        self.player_entity.z = p.pos.z

        for l in self.world.lanterns:
            ent = self.lantern_entities[l.id]
            ent.color = color.rgb32(255, 180, 60) if l.is_lit else color.rgb32(60, 20, 80)

        for f in self.world.fireflies:
            ent = self.firefly_entities[f.id]
            ent.enabled = not f.collected

        for s in self.world.shadows:
            ent = self.shadow_entities[s.id]
            ent.x, ent.z = s.pos.x, s.pos.z
            ent.color = color.rgb32(80, 80, 100) if s.retreating else color.rgb32(30, 0, 50)

    def _sync_hud_from_world(self):
        w = self.world
        self.hp_text.text = f"HP: {w.player.hp}"
        self.light_text.text = f"Anh sang: {w.player.light_storage}"
        lit_count = sum(1 for l in w.lanterns if l.is_lit)
        self.lantern_text.text = f"Den: {lit_count}/{len(w.lanterns)}"
        self.score_text.text = f"Diem: {w.score}"

        if w.state == STATE_WIN:
            self.state_text.text = "THANG! Nhan R de choi lai"
        elif w.state == STATE_LOSE:
            self.state_text.text = "THUA! Nhan R de choi lai"
        else:
            self.state_text.text = ""

    def _reset(self):
        self.world.reset(build_initial_world())
        self.player_entity.position = Vec3(
            self.world.player.pos.x, 0.5, self.world.player.pos.z
        )


# Ursina doi hoi ham update() dinh nghia o cap module (global) - engine tu dong goi
# moi frame, KHONG duoc dinh nghia no ben trong 1 ham khac (xem GUIDE ve nguyen tac
# da kiem chung bang web search, khong doan). Vi vay bien `game` cung phai la global.
game: "GameApp" = None


def update():
    game.update()


def input(key):
    if key == "r" and game.world.state != "PLAYING":
        game._reset()


if __name__ == "__main__":
    game = GameApp()
    game.app.run()
