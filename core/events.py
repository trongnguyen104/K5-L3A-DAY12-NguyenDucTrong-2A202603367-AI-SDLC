"""
core/events.py
Cac su kien trong game (Events Enum).
Dung de theo doi hanh dong, phat am thanh, hoac hieu ung ma khong lam ban logic loi.
"""

from enum import Enum


class GameEvent(str, Enum):
    PICKUP_FIREFLY = "PICKUP_FIREFLY"
    LIGHT_LANTERN = "LIGHT_LANTERN"
    HIT_BY_SHADOW = "HIT_BY_SHADOW"
    USE_GLOW = "USE_GLOW"
    WIN = "WIN"
    LOSE = "LOSE"
