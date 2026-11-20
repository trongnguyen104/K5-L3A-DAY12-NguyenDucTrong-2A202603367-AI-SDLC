"""
headless/runner.py
Chay game KHONG giao dien, dung chung core.engine.GameWorld voi render/app.py.
Dung cho Test Contract (gia dinh - xem AGENTS.md vi PRD-0 khong cho dinh dang cu the).

Cach dung:
    python3 headless/runner.py --input tests/scenarios/scenario_win.json --steps 50

Input JSON (xem tests/scenarios/*.json de co vi du day du):
{
  "player": {"id": "may", "pos": {"x": 0, "z": 0}},
  "fireflies": [{"id": "f0", "pos": {"x": 1, "z": 0}}, ...],
  "lanterns":  [{"id": "l0", "pos": {"x": 1, "z": 0}}, ...],
  "shadows":   [{"id": "s0", "pos": {"x": 100, "z": 100}}, ...],
  "actions": [
    {"step": 1, "type": "move",   "dx": 1, "dz": 0},
    {"step": 1, "type": "pickup", "target": "f0"},
    {"step": 2, "type": "light",  "target": "l0"},
    {"step": 3, "type": "glow"},
    ...
  ]
}
Moi "step" tuong ung 1 lan goi world.update(dt) voi dt co dinh (xem DT_PER_STEP).
Cac "actions" cung step duoc thuc hien TRUOC khi goi update() cua step do.

Output: in JSON ra stdout, 1 dong cho MOI step (de giang vien doi chieu tung buoc),
        dong cuoi cung la trang thai sau khi chay het --steps hoac khi WIN/LOSE som hon.
Ma thoat: 0 neu chay het khong loi input; 2 neu file input sai dinh dang/thieu truong.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.entities import Player, Firefly, Lantern, InkShadow, Vec2
from core.engine import GameWorld

DT_PER_STEP = 0.1  # Gia dinh: moi step logic tuong duong 0.1 giay game (ghi trong AGENTS.md)


def load_world_from_input(data: dict) -> GameWorld:
    """Dung GameWorld tu du lieu JSON. Nem ValueError neu thieu truong bat buoc."""
    try:
        p = data["player"]
        player = Player(id=p["id"], pos=Vec2(p["pos"]["x"], p["pos"]["z"]))

        fireflies = [
            Firefly(id=f["id"], pos=Vec2(f["pos"]["x"], f["pos"]["z"]))
            for f in data.get("fireflies", [])
        ]
        lanterns = [
            Lantern(id=l["id"], pos=Vec2(l["pos"]["x"], l["pos"]["z"]))
            for l in data.get("lanterns", [])
        ]
        shadows = [
            InkShadow(id=s["id"], pos=Vec2(s["pos"]["x"], s["pos"]["z"]))
            for s in data.get("shadows", [])
        ]
    except KeyError as e:
        raise ValueError(f"Thieu truong bat buoc trong input JSON: {e}")

    return GameWorld(player=player, fireflies=fireflies, lanterns=lanterns, shadows=shadows)


def apply_action(world: GameWorld, action: dict):
    """Thuc hien 1 hanh dong len world. Hanh dong khong hop le se bi bo qua (khong crash)."""
    action_type = action.get("type")

    if action_type == "move":
        world.move_player(action.get("dx", 0.0), action.get("dz", 0.0))
    elif action_type == "pickup":
        world.pickup_firefly(action["target"])
    elif action_type == "light":
        world.light_lantern(action["target"])
    elif action_type == "glow":
        world.use_glow()
    else:
        print(f"[CANH BAO] Bo qua hanh dong khong xac dinh: {action_type}", file=sys.stderr)


def run(input_path: str, max_steps: int):
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[LOI] Khong doc duoc input: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        world = load_world_from_input(data)
    except ValueError as e:
        print(f"[LOI] {e}", file=sys.stderr)
        sys.exit(2)

    actions_by_step = {}
    for action in data.get("actions", []):
        step = action["step"]
        actions_by_step.setdefault(step, []).append(action)

    for step in range(1, max_steps + 1):
        if world.state != "PLAYING":
            break
        for action in actions_by_step.get(step, []):
            apply_action(world, action)
        world.update(DT_PER_STEP)

        output = {"step": step, **world.to_dict()}
        print(json.dumps(output, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chay Dao Den Long o che do headless")
    parser.add_argument("--input", required=True, help="Duong dan file input JSON")
    parser.add_argument("--steps", type=int, required=True, help="So buoc toi da chay")
    args = parser.parse_args()
    run(args.input, args.steps)
