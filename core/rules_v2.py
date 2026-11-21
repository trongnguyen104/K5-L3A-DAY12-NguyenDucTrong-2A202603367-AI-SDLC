"""
core/rules.py
Hang so game - Phase 2 (Ticket-02, Test Contract v1.1).
"""

import math

# --- Tick ---
TICK_RATE = 60                  # Chuan: logic chay 60 tick/giay
DT = 1.0 / TICK_RATE            # Chuan: dt co dinh moi tick

# --- Di chuyen ---
MOVE_SPEED = 6.0                 # Chuan: 6.0 m/s
MOVE_ACCEL_TIME_S = 0.1          # Chuan: tang toc/dung trong <= 0.1s

# --- Nhay ---
JUMP_VELOCITY = 7.0              # Chuan: 7.0 m/s
GRAVITY = -20.0                  # Chuan: -20 m/s^2

# --- Luot (Dash) - tinh nang moi ---
DASH_SPEED = 14.0
DASH_DURATION_S = 0.2
DASH_COOLDOWN_S = 1.5             # tinh tu LUC BAT DAU luot
DASH_DURATION_TICKS = round(DASH_DURATION_S * TICK_RATE)     # = 12 ticks
DASH_COOLDOWN_TICKS = round(DASH_COOLDOWN_S * TICK_RATE)     # = 90 ticks

# --- Dom dom ---
FIREFLY_CAPACITY = 10
FIREFLY_PICKUP_RADIUS_XZ = 1.0
FIREFLY_PICKUP_RADIUS_Y = 1.5
FIREFLY_INITIAL_COUNT = 20
FIREFLY_MAX_COUNT = 30
FIREFLY_SPAWN_INTERVAL_TICKS = 240

# --- Den long ---
LANTERN_LIGHT_COST = 10           # can 10 dom dom de thap day 1 den (nap duoc nhieu lan)
LANTERN_INTERACT_RADIUS = 2.0

# --- Vung an toan quanh den da sang ---
SAFE_ZONE_RADIUS = 6.0
SAFE_ZONE_PUSH_OUT_TICKS = 30

# --- Toa Sang (Glow / Pulse) ---
GLOW_COST = 3
GLOW_RADIUS = 5.0                  # ban kinh 5m (3D)
GLOW_COOLDOWN_S = 3.0
GLOW_COOLDOWN_TICKS = round(GLOW_COOLDOWN_S * TICK_RATE)   # = 180 ticks
GLOW_CENTER_OFFSET_Y = 0.8          # tam = chan May + 0.8m
GLOW_STUN_TICKS = 120
GLOW_KNOCKBACK_TICKS = 15
GLOW_KNOCKBACK_DISTANCE = 4.0

# --- Bong Muc ---
SHADOW_SPEED_DEFAULT = 4.0            # Dem 1, 2
SHADOW_SPEED_NIGHT3 = 4.5              # Dem 3
SHADOW_DETECT_RADIUS = 12.0
SHADOW_LOSE_RADIUS = 18.0
SHADOW_TOUCH_RADIUS_XZ = 1.0
SHADOW_TOUCH_RADIUS_Y = 1.5
SHADOW_RECOIL_DISTANCE = 2.0
SHADOW_RECOIL_TICKS = 60

# --- Lich sinh Bong Muc Dem 1 (Dao Ben) ---
NIGHT1_SHADOW_INITIAL_COUNT = 2
NIGHT1_SHADOW_INITIAL_TICK = 300          # giay thu 5 * 60 tick/s
NIGHT1_SHADOW_SPAWN_INTERVAL_TICKS = 480   # tick 300 + 480k
NIGHT1_SHADOW_MAX_COUNT = 6

# --- Hau qua khi bi Bong Muc danh trung ---
HIT_FLAME_LOSS = 1
HIT_DROP_RING_MIN = 1.5
HIT_DROP_RING_MAX = 2.5
HIT_DROPPED_FIREFLY_TTL_TICKS = 480
HIT_INVULN_TICKS = 90

# --- Roi khoi dao ---
FALL_Y_THRESHOLD = -10.0
FALL_FLAME_LOSS = 1                        # bo qua bat tu
FALL_RESPAWN_WAIT_TICKS = 60
FALL_RESPAWN_INVULN_TICKS = 90

# --- Mau (Ngon Lua) ---
MAX_FLAMES = 3                              # hoi day dau moi Dem

# --- Thoi gian moi Dem (giay) ---
NIGHT_DURATION_S = {1: 300, 2: 330, 3: 360}

# --- Diem so (chuan hoa) ---
SCORE_PER_FIREFLY_DEPOSIT = 10              # +10 moi dom dom NAP vao den
SCORE_PER_LANTERN_LIT = 100                  # +100 moi den thap xong
SCORE_PER_SHADOW_PULSE_HIT = 5               # +5 moi Bong Muc trung Toa Sang (moi con moi lan)
SCORE_TIME_BONUS_PER_SECOND = 2              # + floor(giay con lai) x 2 khi thang
SCORE_FLAME_BONUS = 50                        # +50 x Ngon Lua con lai khi thang

# --- Ban do Dem 1 - Dao Ben (chuan hoa lai, THAY doi so voi Phase 1) ---
ISLAND_RADIUS = 40.0                          # doi tu 20 (Phase 1) -> 40 (chuan)
NUM_LANTERNS = 5


def night1_lantern_positions():
    """Chuan: 5 vi tri den CO DINH (khong con deu nhau quanh vong tron nhu Phase 1)."""
    return {
        "L1": (0.0, 0.0, 25.0),
        "L2": (23.8, 0.0, 7.7),
        "L3": (14.7, 0.0, -20.2),
        "L4": (-14.7, 0.0, -20.2),
        "L5": (-23.8, 0.0, 7.7),
    }


def night1_firefly_spawn_points():
    """Chuan: 8 diem ban kinh 12m (moi 45 do) + 16 diem ban kinh 33m (moi 22.5 do)."""
    points = []
    for i in range(8):
        angle = math.radians(45 * i)
        points.append((math.cos(angle) * 12.0, 0.0, math.sin(angle) * 12.0))
    for i in range(16):
        angle = math.radians(22.5 * i)
        points.append((math.cos(angle) * 33.0, 0.0, math.sin(angle) * 33.0))
    return points


NIGHT1_SHADOW_SPAWN_MIN_DIST_TO_PLAYER = 15.0  # Chuan: diem spawn phai cach nguoi choi >= 15m
                                                  # LUC SPAWN (loc runtime, khong phai co dinh truoc)


def night1_shadow_spawn_points():
    """Chuan: 12 diem CO DINH tren ban kinh 37m (moi 30 do, bat dau 15 do: 15,45,75,...).
    Dieu kien '>=15m voi nguoi choi' KHONG loc o day vi day la vi tri tinh; phai loc
    runtime trong core/engine.py tai thoi diem spawn thuc te (nguoi choi co the da di chuyen)."""
    points = []
    for i in range(12):
        angle = math.radians(15 + 30 * i)
        points.append((math.cos(angle) * 37.0, 0.0, math.sin(angle) * 37.0))
    return points


PLAYER_SPAWN_NIGHT1 = (0.0, 0.0, 0.0)  # xuat phat (0,0,0), quay mat ve +Z