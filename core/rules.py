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

# --- Mau (HP) ---
PLAYER_MAX_HP = 100          # Gia dinh: mau toi da cua Mây
DAMAGE_PER_HIT = 10          # Gia dinh: moi lan Bong Muc cham mat 10 mau
HIT_COOLDOWN = 1.0           # Gia dinh: sau khi bi cham, bat tu (1s) truoc khi bi tru mau lan nua
                             # (tranh mot lan cham lien tuc tru het mau trong 1 frame)

# --- Anh sang / Dom dom ---
FIREFLY_PICKUP_RADIUS = 1.5  # Gia dinh: khoang cach (don vi the gioi) de nhat dom dom
LANTERN_LIGHT_RADIUS = 2.0   # Gia dinh: khoang cach de thap den


LIGHT_COST_PER_LANTERN = 1   # Gia dinh: can 1 don vi anh sang (1 dom dom) de thap 1 den

# --- Toa sang xua Bong Muc ---
GLOW_COST = 1                # Gia dinh: toa sang ton 1 don vi anh sang trong kho
GLOW_RADIUS = 5.0             # Gia dinh: ban kinh xua Bong Muc khi toa sang
GLOW_COOLDOWN = 3.0           # Gia dinh: thoi gian hoi (s) truoc khi toa sang lan tiep

# --- Bong Muc ---
SHADOW_SPEED = 2.0             # Gia dinh: toc do di chuyen (don vi/s) cua Bong Muc duoi theo Mây
SHADOW_RETREAT_TIME = 4.0      # Gia dinh: thoi gian (s) Bong Muc lui ra xa sau khi bi toa sang xua

# --- Diem so ---
SCORE_PER_FIREFLY = 10        # Gia dinh: +10 diem khi nhat 1 dom dom
SCORE_PER_LANTERN = 50        # Gia dinh: +50 diem khi thap 1 den

# --- Man choi "Dem 1 - Dao Ben" ---
NUM_LANTERNS = 5               # Co dinh theo PRD-0 (khong phai gia dinh)
ISLAND_RADIUS = 20.0            # Gia dinh: ban kinh dao tron (don vi the gioi)
