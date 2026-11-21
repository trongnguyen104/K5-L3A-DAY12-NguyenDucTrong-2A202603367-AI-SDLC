"""
core/engine.py
Logic game thuan Python - KHONG import ursina o day.
Phase 2 (Ticket-02): chuyen sang kien truc TICK CO DINH 60Hz thay vi dt bien thien.

QUAN TRONG - Thu tu xu ly trong MOI tick (bat buoc theo Ticket-02 Phan 1, KHONG duoc
doi thu tu vi se lam sai ket qua khi so sanh voi test an):
  1. Doc input (xu ly pause truoc; neu vua tam dung thi dung buoc o day)
  2. Giam cac bo dem (thoi gian, hoi chieu, bat tu, choang, bua, TTL dom dom roi)
  3. Di chuyen May (nhay, luot, buc nhay, gio) roi kiem tra roi khoi dao
  4. Nhat dom dom va bua
  5. Tuong tac voi den
  6. Cap nhat vung an toan
  7. Toa Sang
  8. Di chuyen Bong Muc va Gio Lac
  9. Cham: Gio Lac cuop truoc, roi Bong Muc gay hit (theo id tang dan)
  10. Sinh dom dom, Bong Muc, Gio Lac theo lich
  11. Xet thang/thua

Pham vi Phase 2 hien tai: CHI lam Dem 1 (Dao Ben), CHUA lam Gio Lac, Bua Gio, Dem 2/3
(ghi trong AGENTS.md ly do thoi gian). Cac buoc 4,5 ve Gio Lac/Bua Gio duoc BO QUA
(khong co thuc the do), buoc 9 chi con "Bong Muc gay hit theo id tang dan".
"""

from dataclasses import dataclass, field
from .entities import (
    Player, Firefly, Lantern, InkShadow, Vec3,
    SHADOW_STATE_SPAWNING, SHADOW_STATE_WANDER, SHADOW_STATE_CHASE,
    SHADOW_STATE_RECOIL, SHADOW_STATE_STUNNED,
)
from .rules_v2 import (
    DT, TICK_RATE,
    MOVE_SPEED, JUMP_VELOCITY, GRAVITY,
    DASH_SPEED, DASH_DURATION_TICKS, DASH_COOLDOWN_TICKS,
    FIREFLY_CAPACITY, FIREFLY_PICKUP_RADIUS_XZ, FIREFLY_PICKUP_RADIUS_Y,
    FIREFLY_MAX_COUNT, FIREFLY_SPAWN_INTERVAL_TICKS,
    LANTERN_LIGHT_COST, LANTERN_INTERACT_RADIUS,
    SAFE_ZONE_RADIUS, SAFE_ZONE_PUSH_OUT_TICKS,
    GLOW_COST, GLOW_RADIUS, GLOW_COOLDOWN_TICKS, GLOW_CENTER_OFFSET_Y,
    GLOW_STUN_TICKS, GLOW_KNOCKBACK_TICKS, GLOW_KNOCKBACK_DISTANCE,
    SHADOW_DETECT_RADIUS, SHADOW_LOSE_RADIUS,
    SHADOW_TOUCH_RADIUS_XZ, SHADOW_TOUCH_RADIUS_Y,
    SHADOW_RECOIL_DISTANCE, SHADOW_RECOIL_TICKS,
    NIGHT1_SHADOW_INITIAL_COUNT, NIGHT1_SHADOW_INITIAL_TICK,
    NIGHT1_SHADOW_SPAWN_INTERVAL_TICKS, NIGHT1_SHADOW_MAX_COUNT,
    NIGHT1_SHADOW_SPAWN_MIN_DIST_TO_PLAYER,
    HIT_FLAME_LOSS, HIT_DROP_RING_MIN, HIT_DROP_RING_MAX,
    HIT_DROPPED_FIREFLY_TTL_TICKS, HIT_INVULN_TICKS,
    FALL_Y_THRESHOLD, FALL_FLAME_LOSS, FALL_RESPAWN_WAIT_TICKS, FALL_RESPAWN_INVULN_TICKS,
    MAX_FLAMES, NIGHT_DURATION_S,
    SCORE_PER_FIREFLY_DEPOSIT, SCORE_PER_LANTERN_LIT, SCORE_PER_SHADOW_PULSE_HIT,
    SCORE_TIME_BONUS_PER_SECOND, SCORE_FLAME_BONUS,
    PLAYER_SPAWN_NIGHT1,
    night1_lantern_positions, night1_firefly_spawn_points, night1_shadow_spawn_points,
)

STATE_PLAYING = "PLAYING"
STATE_WIN = "WIN"
STATE_LOSE_NO_FLAMES = "LOSE_NO_FLAMES"   # Chuan: ly do thua "no_flames"
STATE_LOSE_DAWN = "LOSE_DAWN"              # Chuan: ly do thua "dawn" (het gio)
STATE_PAUSED = "PAUSED"


@dataclass
class PlayerInput:
    """Input 1 tick. dash/pause kich hoat khi chuyen False->True (xu ly o ngoai engine,
    o day engine chi nhan gia tri da duoc xac dinh la 'vua nhan' hay chua)."""
    move_x: float = 0.0   # -1..1, huong di chuyen truc X
    move_z: float = 0.0   # -1..1, huong di chuyen truc Z
    jump: bool = False
    dash_pressed: bool = False     # True CHI o tick vua chuyen False->True
    interact: bool = False          # nut "E" - nap anh sang vao den
    pulse_pressed: bool = False     # nut Toa Sang
    pause_pressed: bool = False     # True CHI o tick vua chuyen False->True


@dataclass
class GameWorld:
    player: Player
    fireflies: list = field(default_factory=list)
    lanterns: list = field(default_factory=list)
    shadows: list = field(default_factory=list)

    night: int = 1
    tick: int = 0
    score: int = 0
    state: str = STATE_PLAYING
    is_paused: bool = False

    # Cac su kien phat sinh trong tick vua roi (de headless/runner.py doc ra, giong
    # yeu cau Test Contract v1.1 "Su kien moi"). Duoc xoa va nap lai moi tick.
    events: list = field(default_factory=list)

    # Trang thai noi bo cho vung an toan: id Bong Muc -> so tick con bi day ra
    _safe_push_out: dict = field(default_factory=dict)
    # Id Bong Muc tiep theo se sinh (S1, S2, ...)
    _next_shadow_num: int = 1
    _next_firefly_num: int = 0  # dung khi sinh them dom dom moi

    def __post_init__(self):
        self._time_left_s = NIGHT_DURATION_S.get(self.night, 300)

    # ==================== VONG LAP CHINH - 1 TICK ====================
    def step(self, player_input: PlayerInput):
        """Chay dung 1 tick logic (1/60 giay). Day la ham DUY NHAT dieu khien thu tu
        11 buoc bat buoc cua Ticket-02."""
        self.events = []

        # Tang tick NGAY O DAU (truoc khi xu ly), de "self.tick" trong toan bo 11 buoc
        # phan anh dung "day la tick thu may dang duoc xu ly" (vd tick=300 nghia la day
        # la tick thu 300, dung luc Ticket-02 yeu cau sinh Bong Muc). Da phat hien loi
        # lech 1 tick khi tang o CUOI ham (smoke test test_shadow_spawns_on_schedule).
        self.tick += 1

        # --- Buoc 1: Doc input (xu ly pause truoc) ---
        if player_input.pause_pressed:
            self.is_paused = not self.is_paused
            self.events.append({"type": "paused" if self.is_paused else "resumed"})
            if self.is_paused:
                return  # "vua tam dung thi dung buoc o day"

        if self.is_paused:
            return  # dang tam dung: tick tang nhung moi thu khac dung yen

        if self.state != STATE_PLAYING:
            return

        # --- Buoc 2: Giam cac bo dem ---
        self.player.tick_cooldowns()
        self._tick_dropped_fireflies()
        self._tick_shadow_timers()
        self._time_left_s -= DT

        # --- Buoc 3: Di chuyen May (nhay, luot) roi kiem tra roi khoi dao ---
        self._move_player(player_input)
        self._check_fall_off_island()

        # --- Buoc 4: Nhat dom dom (chua lam bua - Phase 2 scope hien tai) ---
        self._auto_pickup_fireflies()

        # --- Buoc 5: Tuong tac voi den ---
        if player_input.interact:
            self._interact_lantern()

        # --- Buoc 6: Cap nhat vung an toan ---
        self._update_safe_zones()

        # --- Buoc 7: Toa Sang ---
        if player_input.pulse_pressed:
            self._try_pulse()

        # --- Buoc 8: Di chuyen Bong Muc (chua co Gio Lac - Phase 2 scope hien tai) ---
        self._move_shadows()

        # --- Buoc 9: Cham (chua co Gio Lac cuop - chi con Bong Muc gay hit) ---
        self._check_shadow_hits()

        # --- Buoc 10: Sinh dom dom, Bong Muc theo lich ---
        self._spawn_fireflies_if_due()
        self._spawn_shadows_if_due()

        # --- Buoc 11: Xet thang/thua ---
        self._check_win_lose()

    # ==================== BUOC 2: Bo dem ====================
    def _tick_dropped_fireflies(self):
        for f in self.fireflies:
            if f.is_dropped and f.ttl_ticks_left > 0:
                f.ttl_ticks_left -= 1
                if f.ttl_ticks_left <= 0:
                    f.collected = True  # het han -> coi nhu bien mat (khong nhat duoc nua)

    def _tick_shadow_timers(self):
        for s in self.shadows:
            if s.state in (SHADOW_STATE_STUNNED, SHADOW_STATE_RECOIL, SHADOW_STATE_SPAWNING):
                s.state_ticks_left -= 1
                if s.knockback_ticks_left > 0:
                    s.knockback_ticks_left -= 1
                if s.state_ticks_left <= 0:
                    s.state = SHADOW_STATE_WANDER
                    s.state_ticks_left = 0

    # ==================== BUOC 3: Di chuyen ====================
    def _move_player(self, player_input: PlayerInput):
        p = self.player
        if p.is_falling_respawn:
            return  # dang cho hoi sinh, khong di chuyen duoc

        # Kich hoat Luot (Dash) neu vua nhan va het hoi chieu.
        # LUU Y: tick_cooldowns() (Buoc 2) chay TRUOC buoc nay (Buoc 3) trong cung 1 tick,
        # nen tick kich hoat se khong duoc tru boi tick_cooldowns(). Phai tru ngay -1 o day
        # de dash keo dai DUNG 12 tick (0.2s), khong phai 13 tick. Da phat hien bang
        # smoke test (_smoke_test_v2.py::test_dash_distance_and_cooldown).
        if player_input.dash_pressed and p.dash_cd_ticks_left <= 0 and not p.is_dashing:
            p.is_dashing = True
            p.dash_ticks_left = DASH_DURATION_TICKS - 1
            p.dash_cd_ticks_left = DASH_COOLDOWN_TICKS  # tinh tu LUC BAT DAU luot (dung chuan)
            self.events.append({"type": "dash"})
            # Huong luot = huong dang di chuyen; neu dung yen, dung huong dang quay mat
            if player_input.move_x or player_input.move_z:
                length = (player_input.move_x ** 2 + player_input.move_z ** 2) ** 0.5
                p._dash_dir = (player_input.move_x / length, player_input.move_z / length)
            else:
                import math
                rad = math.radians(p.facing_deg)
                p._dash_dir = (math.cos(rad), math.sin(rad))

        if p.is_dashing:
            dx, dz = p._dash_dir
            speed = DASH_SPEED
        else:
            dx, dz = player_input.move_x, player_input.move_z
            length = (dx ** 2 + dz ** 2) ** 0.5
            if length > 0:
                dx, dz = dx / length, dz / length
            speed = MOVE_SPEED

        if dx or dz:
            p.pos = Vec3(p.pos.x + dx * speed * DT, p.pos.y, p.pos.z + dz * speed * DT)
            import math
            p.facing_deg = math.degrees(math.atan2(dz, dx))

        # Tat is_dashing SAU KHI da di chuyen voi toc do dash cho tick nay (xem ghi chu
        # trong entities.py::tick_cooldowns ve ly do khong tat o Buoc 2).
        if p.is_dashing and p.dash_ticks_left <= 0:
            p.is_dashing = False

        # Nhay + trong luc (don gian hoa: chi truc Y, chua co buc nhay/gio - Dem 1 khong can)
        if player_input.jump and p.grounded:
            p.vel = Vec3(p.vel.x, JUMP_VELOCITY, p.vel.z)
            p.grounded = False

        if not p.grounded:
            new_vy = p.vel.y + GRAVITY * DT
            new_y = p.pos.y + new_vy * DT
            if new_y <= 0.0:
                new_y = 0.0
                new_vy = 0.0
                p.grounded = True
            p.pos = Vec3(p.pos.x, new_y, p.pos.z)
            p.vel = Vec3(p.vel.x, new_vy, p.vel.z)

    def _check_fall_off_island(self):
        p = self.player
        if p.pos.y < FALL_Y_THRESHOLD and not p.is_falling_respawn:
            p.is_falling_respawn = True
            p.respawn_wait_ticks_left = FALL_RESPAWN_WAIT_TICKS
            p.light_storage = 0  # mat toan bo dom dom
            p.flames = max(0, p.flames - FALL_FLAME_LOSS)
            self.events.append({"type": "player_hit", "lost": "fall"})
            return

        if p.is_falling_respawn:
            p.respawn_wait_ticks_left -= 1
            if p.respawn_wait_ticks_left <= 0:
                sx, sy, sz = PLAYER_SPAWN_NIGHT1
                p.pos = Vec3(sx, sy, sz)
                p.vel = Vec3(0.0, 0.0, 0.0)
                p.grounded = True
                p.is_falling_respawn = False
                p.invuln_ticks_left = FALL_RESPAWN_INVULN_TICKS

    # ==================== BUOC 4: Nhat dom dom ====================
    def _auto_pickup_fireflies(self):
        p = self.player
        if p.light_storage >= FIREFLY_CAPACITY:
            return
        for f in self.fireflies:
            if f.collected:
                continue
            if p.light_storage >= FIREFLY_CAPACITY:
                break
            close_xz = f.pos.distance_xz_to(p.pos) <= FIREFLY_PICKUP_RADIUS_XZ
            close_y = f.pos.height_diff_to(p.pos) <= FIREFLY_PICKUP_RADIUS_Y
            if close_xz and close_y:
                f.collected = True
                p.light_storage += 1

    # ==================== BUOC 5: Tuong tac den ====================
    def _interact_lantern(self):
        p = self.player
        if p.light_storage <= 0:
            return
        # Chi xet den chua sang; chon den gan nhat, bang nhau thi id nho hon
        candidates = [l for l in self.lanterns if not l.is_lit
                      and l.pos.distance_xz_to(p.pos) <= LANTERN_INTERACT_RADIUS]
        if not candidates:
            return
        target = min(candidates, key=lambda l: (l.pos.distance_xz_to(p.pos), l.id))

        missing = target.light_cost - target.light_progress
        amount = min(p.light_storage, missing)
        target.light_progress += amount
        p.light_storage -= amount
        self.score += amount * SCORE_PER_FIREFLY_DEPOSIT
        if target.is_lit:
            self.score += SCORE_PER_LANTERN_LIT
            self.events.append({"type": "lantern_lit", "lantern_id": target.id})

    # ==================== BUOC 6: Vung an toan ====================
    def _update_safe_zones(self):
        lit_lanterns = [l for l in self.lanterns if l.is_lit]
        for s in self.shadows:
            if s.state in (SHADOW_STATE_STUNNED, SHADOW_STATE_RECOIL, SHADOW_STATE_SPAWNING):
                continue
            for l in lit_lanterns:
                dist = s.pos.distance_xz_to(l.pos)
                if dist < SAFE_ZONE_RADIUS:
                    # Bi day ra mep neu MOI vao vung (lan dau phat hien o trong)
                    if s.id not in self._safe_push_out:
                        self._safe_push_out[s.id] = SAFE_ZONE_PUSH_OUT_TICKS
                    # Day ra mep: dua no ra dung bien ban kinh SAFE_ZONE_RADIUS
                    if self._safe_push_out.get(s.id, 0) > 0:
                        s.pos = s.pos.move_toward_xz(
                            Vec3(
                                l.pos.x + (s.pos.x - l.pos.x) / max(dist, 0.001) * SAFE_ZONE_RADIUS,
                                s.pos.y,
                                l.pos.z + (s.pos.z - l.pos.z) / max(dist, 0.001) * SAFE_ZONE_RADIUS,
                            ),
                            999.0,  # tuc thi, khong gioi han toc do day ra (don gian hoa)
                        )
                        self._safe_push_out[s.id] -= 1
                elif s.id in self._safe_push_out:
                    del self._safe_push_out[s.id]

    # ==================== BUOC 7: Toa Sang ====================
    def _try_pulse(self):
        p = self.player
        if p.light_storage < GLOW_COST or p.pulse_cd_ticks_left > 0:
            return
        p.light_storage -= GLOW_COST
        p.pulse_cd_ticks_left = GLOW_COOLDOWN_TICKS
        center = Vec3(p.pos.x, p.pos.y + GLOW_CENTER_OFFSET_Y, p.pos.z)

        for s in self.shadows:
            if s.pos.distance_3d_to(center) <= GLOW_RADIUS:
                s.state = SHADOW_STATE_STUNNED
                s.state_ticks_left = GLOW_STUN_TICKS
                s.knockback_ticks_left = GLOW_KNOCKBACK_TICKS
                dist_xz = s.pos.distance_xz_to(center)
                if dist_xz > 0.0001:
                    s.knockback_dir = Vec3(
                        (s.pos.x - center.x) / dist_xz, 0.0, (s.pos.z - center.z) / dist_xz
                    )
                else:
                    s.knockback_dir = Vec3(1.0, 0.0, 0.0)  # trung vi tri -> day theo +X (chuan)
                s.knockback_distance_left = GLOW_KNOCKBACK_DISTANCE
                self.score += SCORE_PER_SHADOW_PULSE_HIT
                self.events.append({"type": "shadow_pulsed", "shadow_id": s.id})

    # ==================== BUOC 8: Di chuyen Bong Muc ====================
    def _move_shadows(self):
        p = self.player
        for s in self.shadows:
            if s.state == SHADOW_STATE_STUNNED:
                # Dang choang: neu con knockback thi van bi day, khong tu di chuyen
                if s.knockback_ticks_left > 0 and s.knockback_distance_left > 0:
                    step = min(s.knockback_distance_left / max(s.knockback_ticks_left, 1),
                               s.knockback_distance_left)
                    s.pos = Vec3(
                        s.pos.x + s.knockback_dir.x * step,
                        s.pos.y,
                        s.pos.z + s.knockback_dir.z * step,
                    )
                    s.knockback_distance_left -= step
                continue
            if s.state in (SHADOW_STATE_RECOIL, SHADOW_STATE_SPAWNING):
                continue

            dist_to_player = s.pos.distance_xz_to(p.pos)
            if s.state == SHADOW_STATE_WANDER and dist_to_player <= SHADOW_DETECT_RADIUS:
                s.state = SHADOW_STATE_CHASE
            elif s.state == SHADOW_STATE_CHASE and dist_to_player > SHADOW_LOSE_RADIUS:
                s.state = SHADOW_STATE_WANDER

            if s.state == SHADOW_STATE_CHASE:
                step = s.speed * DT
                s.pos = s.pos.move_toward_xz(p.pos, step)
            # wander: Phase 2 pham vi hien tai chua lam di chuyen lon xon luc wander
            # (Ticket-02 khong cho cong thuc wander cu the - se ghi vao assumptions.md)

    # ==================== BUOC 9: Cham ====================
    def _check_shadow_hits(self):
        p = self.player
        if p.is_invulnerable or p.is_falling_respawn:
            return
        # "xet theo id tang dan"
        for s in sorted(self.shadows, key=lambda sh: sh.id):
            if s.touches(p, SHADOW_TOUCH_RADIUS_XZ, SHADOW_TOUCH_RADIUS_Y):
                p.take_hit(HIT_FLAME_LOSS)
                self._drop_fireflies_on_hit()
                s.state = SHADOW_STATE_RECOIL
                s.state_ticks_left = SHADOW_RECOIL_TICKS
                dist_xz = s.pos.distance_xz_to(p.pos)
                if dist_xz > 0.0001:
                    away = Vec3((s.pos.x - p.pos.x) / dist_xz, 0.0, (s.pos.z - p.pos.z) / dist_xz)
                else:
                    away = Vec3(1.0, 0.0, 0.0)
                s.pos = Vec3(
                    s.pos.x + away.x * SHADOW_RECOIL_DISTANCE,
                    s.pos.y,
                    s.pos.z + away.z * SHADOW_RECOIL_DISTANCE,
                )
                self.events.append({"type": "player_hit", "shadow_id": s.id, "lost": "flame"})
                break  # "toi da 1 lan mat Ngon Lua moi tick"

    def _drop_fireflies_on_hit(self):
        import math
        import random
        p = self.player
        drop_count = p.light_storage // 2  # floor(dang mang / 2)
        if drop_count <= 0:
            return
        p.light_storage -= drop_count
        rng = random.Random(self.tick)  # seed = tick hien tai -> TAT DINH (cung tick luon ra cung vi tri)
        for i in range(drop_count):
            angle = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(HIT_DROP_RING_MIN, HIT_DROP_RING_MAX)
            fx = p.pos.x + math.cos(angle) * r
            fz = p.pos.z + math.sin(angle) * r
            self._next_firefly_num += 1
            self.fireflies.append(Firefly(
                id=f"drop{self._next_firefly_num}",
                pos=Vec3(fx, 0.0, fz),
                is_dropped=True,
                ttl_ticks_left=HIT_DROPPED_FIREFLY_TTL_TICKS,
            ))

    # ==================== BUOC 10: Sinh theo lich ====================
    def _spawn_fireflies_if_due(self):
        if self.tick <= 0 or self.tick % FIREFLY_SPAWN_INTERVAL_TICKS != 0:
            return
        active_count = sum(1 for f in self.fireflies if not f.collected)
        if active_count >= FIREFLY_MAX_COUNT:
            return
        all_points = night1_firefly_spawn_points()
        occupied = {(round(f.pos.x, 1), round(f.pos.z, 1)) for f in self.fireflies if not f.collected}
        for (x, y, z) in all_points:
            if (round(x, 1), round(z, 1)) not in occupied:
                self._next_firefly_num += 1
                self.fireflies.append(Firefly(id=f"f_extra{self._next_firefly_num}", pos=Vec3(x, y, z)))
                return  # chi sinh 1 con moi lan dung lich

    def _spawn_shadows_if_due(self):
        active_count = len(self.shadows)
        if active_count >= NIGHT1_SHADOW_MAX_COUNT:
            return
        if self.tick == NIGHT1_SHADOW_INITIAL_TICK:
            self._spawn_shadows_at_schedule(NIGHT1_SHADOW_INITIAL_COUNT)
        elif (self.tick > NIGHT1_SHADOW_INITIAL_TICK
              and (self.tick - NIGHT1_SHADOW_INITIAL_TICK) % NIGHT1_SHADOW_SPAWN_INTERVAL_TICKS == 0):
            self._spawn_shadows_at_schedule(1)

    def _spawn_shadows_at_schedule(self, count: int):
        all_points = night1_shadow_spawn_points()
        valid_points = [
            (x, y, z) for (x, y, z) in all_points
            if Vec3(x, y, z).distance_xz_to(self.player.pos) >= NIGHT1_SHADOW_SPAWN_MIN_DIST_TO_PLAYER
        ]
        for _ in range(count):
            if not valid_points or len(self.shadows) >= NIGHT1_SHADOW_MAX_COUNT:
                return  # "het diem hop le thi bo luot"
            x, y, z = valid_points.pop(0)
            shadow_id = f"S{self._next_shadow_num}"
            self._next_shadow_num += 1
            self.shadows.append(InkShadow(id=shadow_id, pos=Vec3(x, y, z)))

    # ==================== BUOC 11: Thang/thua ====================
    def _check_win_lose(self):
        if self.player.flames <= 0:
            self.state = STATE_LOSE_NO_FLAMES
            return
        if all(l.is_lit for l in self.lanterns):
            self.state = STATE_WIN
            self.score += int(max(0, self._time_left_s)) * SCORE_TIME_BONUS_PER_SECOND
            self.score += self.player.flames * SCORE_FLAME_BONUS
            return
        if self._time_left_s <= 0:
            self.state = STATE_LOSE_DAWN

    # ==================== Xuat trang thai (headless / HUD) ====================
    def to_dict(self) -> dict:
        p = self.player
        return {
            "tick": self.tick,
            "night": self.night,
            "state": self.state,
            "score": self.score,
            "time_left_s": round(max(0.0, self._time_left_s), 3),
            "player": {
                "pos": {"x": p.pos.x, "y": p.pos.y, "z": p.pos.z},
                "vel": {"x": p.vel.x, "y": p.vel.y, "z": p.vel.z},
                "grounded": p.grounded,
                "flames": p.flames,
                "light_storage": p.light_storage,
                "invuln_ticks": p.invuln_ticks_left,
                "dash_cd_ticks": p.dash_cd_ticks_left,
                "pulse_cd_ticks": p.pulse_cd_ticks_left,
                "charm_ticks": p.charm_ticks_left,
            },
            "lanterns": [
                {"id": l.id, "is_lit": l.is_lit, "progress": l.light_progress}
                for l in self.lanterns
            ],
            "fireflies": [
                {"id": f.id, "collected": f.collected, "kind": "dropped" if f.is_dropped else "random",
                 "ttl_s": round(f.ttl_ticks_left / TICK_RATE, 3) if f.ttl_ticks_left >= 0 else None}
                for f in self.fireflies
            ],
            "shadows": [
                {"id": s.id, "pos": {"x": s.pos.x, "y": s.pos.y, "z": s.pos.z}, "state": s.state,
                 "state_ticks_left": s.state_ticks_left}
                for s in self.shadows
            ],
        }
