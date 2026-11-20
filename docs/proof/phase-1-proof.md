# Bằng Chứng Kiểm Chứng (Proof of Verification) — Phase 1

> **Tag:** `phase-1`  
> **Cam kết:** Bằng chứng thật 100%, chạy trực tiếp từ mã nguồn và hoàn toàn khớp với commit ở tag `phase-1`.

---

## 1. Bảng đối chiếu yêu cầu và bằng chứng

| Yêu cầu chính (PRD-0) | Cách kiểm chứng | Bằng chứng thực nghiệm | Kết quả |
|---|---|---|---|
| **Tách biệt Core Logic (không GPU/màn hình)** | Chạy `python _smoke_test.py` không cần display/Ursina | Terminal log mục 2 | **ĐẠT** |
| **Cơ chế nhặt đom đóm & thắp đèn** | Kịch bản `scenario_pickup.json` qua `runner.py` | Terminal log mục 3.1 | **ĐẠT** |
| **Điều kiện Thắng (5 đèn sáng)** | Kịch bản `scenario_win.json` qua `runner.py` | Terminal log mục 3.2 | **ĐẠT** |
| **Điều kiện Thua (Hết máu khi va chạm)** | Kịch bản `scenario_lose.json` qua `runner.py` | Terminal log mục 3.3 | **ĐẠT** |
| **Tính tất định (Determinism)** | `test_deterministic` chạy 2 lần cùng input/action | Terminal log mục 2 | **ĐẠT** |
| **Game 3D chơi được có giao diện** | Chạy `python render/app.py` | Ursina window khởi tạo thành công | **ĐẠT** |

---

## 2. Kết quả chạy Smoke Test (`_smoke_test.py`)

Lệnh thực thi:
```bash
python _smoke_test.py
```

Output:
```text
OK test_pickup_and_light
OK test_win_condition
OK test_lose_condition
OK test_deterministic

TAT CA TEST PASS
```

---

## 3. Kết quả chạy Headless Runner (Test Contract)

### 3.1. Kịch bản Nhặt đom đóm & Thắp đèn (`tests/scenarios/scenario_pickup.json`)
Lệnh:
```bash
python headless/runner.py --input tests/scenarios/scenario_pickup.json --steps 4
```
Output:
```json
{"step": 1, "state": "PLAYING", "score": 10, "player": {"pos": {"x": 1, "z": 0}, "hp": 100, "light_storage": 1}, "lanterns": [{"id": "l0", "is_lit": false}, {"id": "l1", "is_lit": false}], "fireflies": [{"id": "f0", "collected": true}, {"id": "f1", "collected": false}], "shadows": [{"id": "s0", "pos": {"x": 99.85929108041599, "z": 99.85786977819797}, "retreating": false}]}
{"step": 2, "state": "PLAYING", "score": 20, "player": {"pos": {"x": 2, "z": 0}, "hp": 100, "light_storage": 2}, "lanterns": [{"id": "l0", "is_lit": false}, {"id": "l1", "is_lit": false}], "fireflies": [{"id": "f0", "collected": true}, {"id": "f1", "collected": true}], "shadows": [{"id": "s0", "pos": {"x": 99.71930640104667, "z": 99.71502619401629}, "retreating": false}]}
{"step": 3, "state": "PLAYING", "score": 70, "player": {"pos": {"x": 3, "z": 0}, "hp": 100, "light_storage": 1}, "lanterns": [{"id": "l0", "is_lit": true}, {"id": "l1", "is_lit": false}], "fireflies": [{"id": "f0", "collected": true}, {"id": "f1", "collected": true}], "shadows": [{"id": "s0", "pos": {"x": 99.58005798184448, "z": 99.57146478642466}, "retreating": false}]}
{"step": 4, "state": "PLAYING", "score": 70, "player": {"pos": {"x": 3, "z": 0}, "hp": 100, "light_storage": 1}, "lanterns": [{"id": "l0", "is_lit": true}, {"id": "l1", "is_lit": false}], "fireflies": [{"id": "f0", "collected": true}, {"id": "f1", "collected": true}], "shadows": [{"id": "s0", "pos": {"x": 99.44080956264229, "z": 99.42790337883302}, "retreating": false}]}
```

### 3.2. Kịch bản Thắng (`tests/scenarios/scenario_win.json`)
Lệnh:
```bash
python headless/runner.py --input tests/scenarios/scenario_win.json --steps 50
```
Output (bước kết thúc):
```json
{"step": 5, "state": "WIN", "score": 300, "player": {"pos": {"x": 4, "z": 0}, "hp": 100, "light_storage": 0}, "lanterns": [{"id": "l0", "is_lit": true}, {"id": "l1", "is_lit": true}, {"id": "l2", "is_lit": true}, {"id": "l3", "is_lit": true}, {"id": "l4", "is_lit": true}], "fireflies": [{"id": "f0", "collected": true}, {"id": "f1", "collected": true}, {"id": "f2", "collected": true}, {"id": "f3", "collected": true}, {"id": "f4", "collected": true}], "shadows": [{"id": "s0", "pos": {"x": 99.43864286085443, "z": 99.43003734126565}, "retreating": false}]}
```

### 3.3. Kịch bản Thua (`tests/scenarios/scenario_lose.json`)
Lệnh:
```bash
python headless/runner.py --input tests/scenarios/scenario_lose.json --steps 100
```
Output (bước kết thúc khi HP về 0):
```json
{"step": 100, "state": "LOSE", "score": 0, "player": {"pos": {"x": 0, "z": 0}, "hp": 0, "light_storage": 0}, "lanterns": [{"id": "l0", "is_lit": false}], "fireflies": [], "shadows": [{"id": "s0", "pos": {"x": 0, "z": 0}, "retreating": false}]}
```
