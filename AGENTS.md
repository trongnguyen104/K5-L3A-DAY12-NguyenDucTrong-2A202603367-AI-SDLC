# AGENTS.md — Đảo Đèn Lồng (Phase 1)

## Dự án
Game 3D "Đảo Đèn Lồng". Phase 1: 1 màn "Đêm 1 – Đảo Bến", 5 Đèn Lồng Lớn.
Python 3.10 + Ursina. Chạy trên Ubuntu 22.04 (ưu tiên) hoặc Windows 10.

## Lệnh
```bash
# Cài đặt
pip install ursina

# Chạy game có giao diện
python3 render/app.py

# Chạy test logic (core/)
python3 _smoke_test.py

# Chạy headless (Test Contract)
python3 headless/runner.py --input tests/scenarios/scenario_win.json --steps 50
```

## Quy ước bắt buộc
1. **`core/` KHÔNG được `import ursina`** hoặc bất kỳ thư viện render nào. Đây là logic thuần Python, phải chạy được bằng `python3` không cần GPU/màn hình.
2. **`render/app.py` KHÔNG chứa logic game** (không tự trừ máu, không tự set `is_lit`). Nó chỉ gọi hàm của `core.engine.GameWorld` rồi vẽ lại theo `to_dict()`.
3. **`headless/runner.py` dùng chung `core.engine.GameWorld`** với `render/app.py` — đảm bảo bằng chứng headless khớp hành vi bản có giao diện.
4. Mọi hằng số (máu, sát thương, bán kính...) nằm trong `core/rules.py`, không hardcode rải rác.

## Giả định đã đặt (PRD-0 không cho số liệu — xem core/rules.py)
PRD-0 Phase 1 không nêu con số cụ thể cho: máu tối đa, sát thương/lần chạm, bán kính nhặt/thắp đèn, chi phí & bán kính tỏa sáng, điểm số mỗi hành động. Toàn bộ số liệu trong `core/rules.py` là **giả định tự đặt**, đã ghi chú ngay trong file đó. Khi trợ giảng/giảng viên làm rõ số liệu thật, sửa trong `core/rules.py` và chạy lại `_smoke_test.py` + các scenario trong `tests/scenarios/`.

## Test Contract (giả định — PRD-0 chưa cho định dạng cụ thể)
- Lệnh: `python3 headless/runner.py --input <file.json> --steps <N>`
- Input: JSON gồm trạng thái ban đầu + danh sách hành động theo bước
- Output: JSON in ra stdout, gồm state/score/player/lanterns/fireflies/shadows (xem `GameWorld.to_dict()`)
- Tính tất định: cùng input + cùng hành động → luôn cùng output (đã kiểm chứng ở `test_deterministic` trong `_smoke_test.py`)

## Điều cấm
- Không dùng `random` không seed trong `core/` (phá tính tất định của Test Contract).
- Không sửa `core/engine.py` để "test luôn pass" — nếu test sai, sửa test kèm lý do (GUIDE.md mục 5).
- Không commit API key / `.env`.

## Khi agent sai lặp lại
Cập nhật file này thêm 1 dòng quy ước mới, không viết lại từ đầu.
