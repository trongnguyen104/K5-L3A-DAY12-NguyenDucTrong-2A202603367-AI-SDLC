"""Smoke test Phase 2 - kiem chung kien truc tick 60Hz va so chuan Ticket-02."""

from core.world_factory import build_night1_world
from core.engine import PlayerInput, STATE_PLAYING, STATE_WIN, STATE_LOSE_NO_FLAMES, STATE_LOSE_DAWN
from core.rules import TICK_RATE, FIREFLY_CAPACITY, LANTERN_LIGHT_COST, MOVE_SPEED, DT


def test_build_night1():
    w = build_night1_world()
    assert len(w.lanterns) == 5, f"Phai co 5 den, dang co {len(w.lanterns)}"
    assert len(w.fireflies) == 20, f"Phai co 20 dom dom luc dau, dang co {len(w.fireflies)}"
    assert len(w.shadows) == 0, "Bong Muc chua sinh luc bat dau (sinh o tick 300)"
    print("OK test_build_night1")


def test_move_speed_correct():
    """Di chuyen 1 giay (60 tick) phai di dung MOVE_SPEED=6.0 met."""
    w = build_night1_world()
    start_z = w.player.pos.z
    inp = PlayerInput(move_z=1.0)
    for _ in range(TICK_RATE):  # 1 giay = 60 tick
        w.step(inp)
    traveled = w.player.pos.z - start_z
    assert abs(traveled - MOVE_SPEED) < 0.01, f"Phai di ~6.0m sau 1s, thuc te {traveled:.3f}m"
    print(f"OK test_move_speed_correct (di chuyen {traveled:.3f}m sau 1s)")


def test_pickup_and_light_lantern():
    w = build_night1_world()
    # Dua player den vi tri dom dom dau tien, nhat du 10 con de thap 1 den
    for i in range(LANTERN_LIGHT_COST):
        w.player.pos.x, w.player.pos.y, w.player.pos.z = (
            w.fireflies[i].pos.x, w.fireflies[i].pos.y, w.fireflies[i].pos.z
        )
        w.step(PlayerInput())  # auto pickup o buoc 4
    assert w.player.light_storage == LANTERN_LIGHT_COST, \
        f"Phai mang {LANTERN_LIGHT_COST} dom dom, dang mang {w.player.light_storage}"

    # Di chuyen den gan L1 (0,0,25) va nap
    w.player.pos.x, w.player.pos.y, w.player.pos.z = 0.0, 0.0, 25.0
    w.step(PlayerInput(interact=True))
    assert w.lanterns[0].is_lit, "L1 phai sang sau khi nap du 10 dom dom"
    print("OK test_pickup_and_light_lantern")


def test_dash_distance_and_cooldown():
    """Luot 0.2s voi toc do 14 m/s phai di ~2.8m, sau do vao hoi chieu 1.5s."""
    w = build_night1_world()
    start_z = w.player.pos.z
    w.step(PlayerInput(move_z=1.0, dash_pressed=True))
    assert w.player.is_dashing, "Phai dang luot ngay tick dau tien nhan dash"
    for _ in range(11):  # tong 12 tick = 0.2s DASH_DURATION_TICKS
        w.step(PlayerInput(move_z=1.0))
    assert not w.player.is_dashing, "Phai het luot sau 12 tick (0.2s)"
    traveled = w.player.pos.z - start_z
    expected = 14.0 * 0.2  # DASH_SPEED * DASH_DURATION_S
    assert abs(traveled - expected) < 0.05, f"Phai di ~{expected}m khi luot, thuc te {traveled:.3f}m"
    assert w.player.dash_cd_ticks_left > 0, "Phai dang hoi chieu sau khi luot"
    print(f"OK test_dash_distance_and_cooldown (di {traveled:.3f}m, hoi chieu {w.player.dash_cd_ticks_left} tick)")


def test_shadow_spawns_on_schedule():
    """Bong Muc phai sinh dung tick 300 (2 con), KHONG som hon khong muon hon."""
    w = build_night1_world()
    for t in range(299):
        w.step(PlayerInput())
    assert len(w.shadows) == 0, f"Truoc tick 300 chua duoc sinh, dang co {len(w.shadows)}"
    w.step(PlayerInput())  # tick nay se la tick thu 300 (tick dem tu 0, sau step nay w.tick=300)
    assert len(w.shadows) == 2, f"Dung tick 300 phai sinh 2 Bong Muc, dang co {len(w.shadows)}"
    assert w.shadows[0].id == "S1" and w.shadows[1].id == "S2", \
        f"Id phai la S1, S2, dang la {[s.id for s in w.shadows]}"
    print("OK test_shadow_spawns_on_schedule")


def test_deterministic():
    """Cung input, cung hanh dong -> cung ket qua tuyet doi (bat buoc cho headless)."""
    w1 = build_night1_world()
    w2 = build_night1_world()
    inputs = [PlayerInput(move_x=1, move_z=0.5) for _ in range(500)]
    for inp in inputs:
        w1.step(inp)
        w2.step(inp)
    assert w1.to_dict() == w2.to_dict(), "Hai lan chay cung input phai ra cung output tuyet doi"
    print("OK test_deterministic")


def test_lose_no_flames():
    """Dung yen canh Bong Muc du lau thi phai thua vi het Ngon Lua (3 lan trung, moi lan
    cach nhau it nhat vai tick do bat tu 90 tick)."""
    w = build_night1_world()
    # Dua 1 Bong Muc toi ngay vi tri player va giu no o trang thai chase/wander lien tuc
    from core.entities import InkShadow, SHADOW_STATE_WANDER
    w.shadows.append(InkShadow(id="S1", pos=Vec3(w.player.pos.x, w.player.pos.y, w.player.pos.z)))

    max_ticks = 60 * 60  # toi da 60s de tranh vong lap vo han neu co loi
    for _ in range(max_ticks):
        w.step(PlayerInput())
        if w.state != STATE_PLAYING:
            break
    assert w.state == STATE_LOSE_NO_FLAMES, f"Phai thua do het Ngon Lua, dang la {w.state}"
    print(f"OK test_lose_no_flames (thua o tick {w.tick})")


if __name__ == "__main__":
    from core.entities import Vec3
    test_build_night1()
    test_move_speed_correct()
    test_pickup_and_light_lantern()
    test_dash_distance_and_cooldown()
    test_shadow_spawns_on_schedule()
    test_deterministic()
    test_lose_no_flames()
    print("\nTAT CA TEST PHASE 2 PASS")
