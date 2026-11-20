"""Smoke test noi bo - kiem tra engine.py chay dung truoc khi giao.
Khong phai file nop, chi de tu kiem chung (GUIDE.md: 'khong co bang chung thi chua xong')."""

from core.entities import Player, Firefly, Lantern, InkShadow, Vec2
from core.engine import GameWorld, STATE_PLAYING, STATE_WIN, STATE_LOSE


def make_world():
    player = Player(id="may", pos=Vec2(0, 0))
    fireflies = [Firefly(id=f"f{i}", pos=Vec2(i, 0)) for i in range(5)]
    lanterns = [Lantern(id=f"l{i}", pos=Vec2(i, 0)) for i in range(5)]
    shadows = [InkShadow(id="s0", pos=Vec2(100, 100))]  # xa, khong anh huong test nay
    return GameWorld(player=player, fireflies=fireflies, lanterns=lanterns, shadows=shadows)


def test_pickup_and_light():
    w = make_world()
    assert w.pickup_firefly("f0") is True, "Phai nhat duoc dom dom khi du gan"
    assert w.player.light_storage == 1
    assert w.score == 10
    assert w.light_lantern("l0") is True, "Phai thap duoc den khi co anh sang + du gan"
    assert w.lanterns[0].is_lit is True
    assert w.player.light_storage == 0
    assert w.score == 60
    print("OK test_pickup_and_light")


def test_win_condition():
    w = make_world()
    for i in range(5):
        w.player.pos = Vec2(i, 0)  # di chuyen player lai gan tung dom dom/den truoc khi tuong tac
        w.pickup_firefly(f"f{i}")
        w.light_lantern(f"l{i}")
    w.update(0.1)
    assert w.state == STATE_WIN, f"Phai WIN khi thap het 5 den, dang la {w.state}"
    print("OK test_win_condition")


def test_lose_condition():
    player = Player(id="may", pos=Vec2(0, 0), hp=5)
    shadow = InkShadow(id="s0", pos=Vec2(0, 0))  # dung ngay canh player
    w = GameWorld(player=player, fireflies=[], lanterns=[Lantern(id="l0", pos=Vec2(0,0))], shadows=[shadow])
    w.update(0.1)  # 1 lan cham, tru 10 mau nhung hp chi co 5 -> clamp ve 0
    assert w.player.hp == 0, f"HP phai ve 0, dang la {w.player.hp}"
    assert w.state == STATE_LOSE, f"Phai LOSE khi het mau, dang la {w.state}"
    print("OK test_lose_condition")


def test_deterministic():
    """Cung input, cung hanh dong -> cung ket qua (yeu cau tinh tat dinh)."""
    w1 = make_world()
    w2 = make_world()
    actions = [("pickup", "f0"), ("pickup", "f1"), ("light", "l0")]
    for act, target in actions:
        if act == "pickup":
            w1.pickup_firefly(target)
            w2.pickup_firefly(target)
        else:
            w1.light_lantern(target)
            w2.light_lantern(target)
        w1.update(0.1)
        w2.update(0.1)
    assert w1.to_dict() == w2.to_dict(), "Hai lan chay cung input phai ra cung output"
    print("OK test_deterministic")


if __name__ == "__main__":
    test_pickup_and_light()
    test_win_condition()
    test_lose_condition()
    test_deterministic()
    print("\nTAT CA TEST PASS")
